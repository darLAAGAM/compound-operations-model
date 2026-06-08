"""Delete Ledger — tracks RTBF deletions with propagation status.

Each deletion targets a subject_id (resolved from email/phone/etc via the
Subject Registry) and creates a ledger entry. A propagation worker touches
every store and marks each column done. Until all columns are done, the
deletion is PENDING and reportable via `operai-init ingest forget --status`.

Realistic SLAs (by column):
    evidence_done:      <5 min
    retrieval_done:     <5 min
    qmd_reindex_done:   <15 min (cron tick)
    summaries_done:     <1h
    logs_done:          <24h (log rotation)
    backups_done:       <30d (backup retention)
    llm_provider_done:  <30d without ZDR, immediate with ZDR
"""
from __future__ import annotations
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from operai_init.ingest.storage import open_db, EncryptedDB

SCHEMA = """
CREATE TABLE IF NOT EXISTS deletions (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_id        TEXT NOT NULL,
    requested_at      TEXT NOT NULL,
    triggered_by      TEXT NOT NULL,   -- founder|rtbf|retention|source_mutation
    reason            TEXT,
    -- Per-store propagation
    evidence_done     INTEGER DEFAULT 0,
    retrieval_done    INTEGER DEFAULT 0,
    qmd_reindex_done  INTEGER DEFAULT 0,
    summaries_done    INTEGER DEFAULT 0,
    logs_done         INTEGER DEFAULT 0,
    backups_done      INTEGER DEFAULT 0,
    llm_provider_done INTEGER DEFAULT 0,
    completed_at      TEXT,
    last_error        TEXT
);

CREATE INDEX IF NOT EXISTS idx_deletions_pending
    ON deletions(subject_id)
    WHERE completed_at IS NULL;
"""

STORES = [
    "evidence_done", "retrieval_done", "qmd_reindex_done",
    "summaries_done", "logs_done", "backups_done", "llm_provider_done",
]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _db_path(home: Path) -> Path:
    return home / "state" / "delete-ledger.db.enc"


@dataclass
class Deletion:
    id: int
    subject_id: str
    requested_at: str
    triggered_by: str
    reason: Optional[str]
    status: dict[str, bool]       # store → done
    completed_at: Optional[str]
    last_error: Optional[str]


class DeleteLedger:
    def __init__(self, home: Path):
        self.home = home
        self.path = _db_path(home)
        with open_db(self.path, SCHEMA):
            pass

    def _db(self) -> EncryptedDB:
        return EncryptedDB(self.path)

    def record(self, subject_id: str, *, triggered_by: str, reason: str | None = None) -> int:
        with self._db() as db:
            cur = db.execute(
                "INSERT INTO deletions (subject_id, requested_at, triggered_by, reason) VALUES (?, ?, ?, ?)",
                (subject_id, _now(), triggered_by, reason),
            )
            db.commit()
            return cur.lastrowid

    def mark_store_done(self, deletion_id: int, store: str) -> None:
        if store not in STORES:
            raise ValueError(f"unknown store: {store}")
        with self._db() as db:
            db.execute(f"UPDATE deletions SET {store} = 1 WHERE id = ?", (deletion_id,))
            # If all columns are done, set completed_at
            row = db.execute(
                f"SELECT {','.join(STORES)} FROM deletions WHERE id = ?", (deletion_id,)
            ).fetchone()
            if row and all(row[s] for s in STORES):
                db.execute("UPDATE deletions SET completed_at = ? WHERE id = ?", (_now(), deletion_id))
            db.commit()

    def mark_error(self, deletion_id: int, error: str) -> None:
        with self._db() as db:
            db.execute("UPDATE deletions SET last_error = ? WHERE id = ?", (error, deletion_id))
            db.commit()

    def pending(self) -> list[Deletion]:
        with self._db() as db:
            rows = db.execute(
                "SELECT * FROM deletions WHERE completed_at IS NULL ORDER BY requested_at ASC"
            ).fetchall()
        return [self._row_to_deletion(r) for r in rows]

    def get(self, deletion_id: int) -> Optional[Deletion]:
        with self._db() as db:
            row = db.execute("SELECT * FROM deletions WHERE id = ?", (deletion_id,)).fetchone()
        return self._row_to_deletion(row) if row else None

    def all_for_subject(self, subject_id: str) -> list[Deletion]:
        with self._db() as db:
            rows = db.execute(
                "SELECT * FROM deletions WHERE subject_id = ? ORDER BY requested_at DESC",
                (subject_id,),
            ).fetchall()
        return [self._row_to_deletion(r) for r in rows]

    def stats(self) -> dict:
        with self._db() as db:
            pending = db.execute(
                "SELECT COUNT(*) AS n FROM deletions WHERE completed_at IS NULL"
            ).fetchone()["n"]
            done = db.execute(
                "SELECT COUNT(*) AS n FROM deletions WHERE completed_at IS NOT NULL"
            ).fetchone()["n"]
        return {"pending": pending, "completed": done}

    def _row_to_deletion(self, row) -> Deletion:
        return Deletion(
            id=row["id"],
            subject_id=row["subject_id"],
            requested_at=row["requested_at"],
            triggered_by=row["triggered_by"],
            reason=row["reason"],
            status={s: bool(row[s]) for s in STORES},
            completed_at=row["completed_at"],
            last_error=row["last_error"],
        )
