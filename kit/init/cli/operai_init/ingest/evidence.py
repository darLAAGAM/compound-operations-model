"""Evidence Store — encrypted, TTL-bounded, not indexed.

Original (pre-sanitization) canonical docs live here for audit purposes only.
Never read by agents. Never indexed by QMD. Accessed only via
`operai-init ingest audit` (admin).

Uses SQLCipher (via storage.py). One DB file per source.
TTL enforced by a daily prune job (scheduled via operai-init ingest schedule).
"""
from __future__ import annotations
import hashlib
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional

from operai_init.ingest.storage import open_db, EncryptedDB

SCHEMA = """
CREATE TABLE IF NOT EXISTS evidence (
    doc_id       TEXT PRIMARY KEY,
    source       TEXT NOT NULL,
    source_ref   TEXT NOT NULL,
    kind         TEXT,
    ingested_at  TEXT NOT NULL,
    retention_until TEXT NOT NULL,
    content_hash TEXT,
    canonical    BLOB,   -- JSON blob of CanonicalDoc (encrypted-at-rest via SQLCipher)
    subjects     TEXT    -- comma-separated subject_ids mentioned
);

CREATE INDEX IF NOT EXISTS idx_evidence_retention ON evidence(retention_until);
CREATE INDEX IF NOT EXISTS idx_evidence_source    ON evidence(source, source_ref);
"""


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _db_path(home: Path, source: str) -> Path:
    return home / "state" / f"evidence-{source}.db.enc"


class EvidenceStore:
    """One instance per source. Keeps them physically isolated."""

    def __init__(self, home: Path, source: str, *, retention_days: int = 90):
        if retention_days < 30 or retention_days > 365:
            raise ValueError("retention_days must be between 30 and 365")
        self.home = home
        self.source = source
        self.path = _db_path(home, source)
        self.retention_days = retention_days
        with open_db(self.path, SCHEMA):
            pass

    def _db(self) -> EncryptedDB:
        return EncryptedDB(self.path)

    def store(self, doc_id: str, source_ref: str, kind: str, canonical: dict, subjects: list[str]) -> None:
        now = _now()
        expires = now + timedelta(days=self.retention_days)
        canonical_blob = json.dumps(canonical).encode("utf-8")
        content_hash = hashlib.sha256(canonical_blob).hexdigest()
        with self._db() as db:
            db.execute(
                "INSERT OR REPLACE INTO evidence "
                "(doc_id, source, source_ref, kind, ingested_at, retention_until, content_hash, canonical, subjects) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    doc_id, self.source, source_ref, kind,
                    now.isoformat(), expires.isoformat(), content_hash,
                    canonical_blob, ",".join(subjects),
                ),
            )
            db.commit()

    def delete(self, doc_id: str) -> bool:
        with self._db() as db:
            cur = db.execute("DELETE FROM evidence WHERE doc_id = ?", (doc_id,))
            db.commit()
            return cur.rowcount > 0

    def delete_by_subject(self, subject_id: str) -> int:
        """Delete all evidence referencing this subject. Returns count deleted."""
        with self._db() as db:
            # subjects is CSV — match with surrounding separators to avoid partial matches
            cur = db.execute(
                "DELETE FROM evidence WHERE subjects = ? OR subjects LIKE ? OR subjects LIKE ? OR subjects LIKE ?",
                (
                    subject_id,
                    f"{subject_id},%",
                    f"%,{subject_id}",
                    f"%,{subject_id},%",
                ),
            )
            db.commit()
            return cur.rowcount

    def prune_expired(self) -> int:
        """Delete rows whose retention_until has passed. Returns count."""
        now = _now().isoformat()
        with self._db() as db:
            cur = db.execute("DELETE FROM evidence WHERE retention_until < ?", (now,))
            db.commit()
            return cur.rowcount

    def stats(self) -> dict:
        with self._db() as db:
            row = db.execute("SELECT COUNT(*) AS n, MIN(ingested_at) AS oldest, MAX(ingested_at) AS newest FROM evidence").fetchone()
        return {"source": self.source, "rows": row["n"], "oldest": row["oldest"], "newest": row["newest"]}

    # Admin-only read path for audit
    def fetch(self, doc_id: str) -> Optional[dict]:
        with self._db() as db:
            row = db.execute("SELECT * FROM evidence WHERE doc_id = ?", (doc_id,)).fetchone()
        if not row:
            return None
        return {
            "doc_id":        row["doc_id"],
            "source":        row["source"],
            "source_ref":    row["source_ref"],
            "kind":          row["kind"],
            "ingested_at":   row["ingested_at"],
            "retention_until": row["retention_until"],
            "canonical":     json.loads(row["canonical"]),
            "subjects":      row["subjects"].split(",") if row["subjects"] else [],
        }
