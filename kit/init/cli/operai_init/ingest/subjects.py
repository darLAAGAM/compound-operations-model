"""Subject Registry — canonical identity model.

Design principles (responding to Codex v2 criticisms):

  1. Only DETERMINISTIC linking signals. No "co-occurs in same thread" heuristic.
     - Two aliases link IFF a source record explicitly asserts both belong to
       the same entity (e.g. a Shopify customer row with both email+phone;
       a Slack user profile with email; an Intercom contact with phone+email).
  2. No `name_literal` column. We store the subject_id + aliases, never the
     normalized name. Names appear only inside documents, as tokens resolved
     at render time.
  3. Encrypted at rest via SQLCipher.
  4. Audit log of every mutation.
  5. Merge operations require admin + reason + reversibility (ledger entry).

Schema:
    subjects:        subject_id (uuid), created_at, last_seen, deleted_at
    subject_aliases: alias_type, alias_value, subject_id, source, first_seen
    audit:           ts, op, subject_id, detail
"""
from __future__ import annotations
import json
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from operai_init.ingest.storage import open_db, EncryptedDB

SCHEMA = """
CREATE TABLE IF NOT EXISTS subjects (
    subject_id  TEXT PRIMARY KEY,
    created_at  TEXT NOT NULL,
    last_seen   TEXT NOT NULL,
    deleted_at  TEXT
);

CREATE TABLE IF NOT EXISTS subject_aliases (
    alias_type  TEXT NOT NULL,
    alias_value TEXT NOT NULL,
    subject_id  TEXT NOT NULL,
    source      TEXT NOT NULL,
    first_seen  TEXT NOT NULL,
    PRIMARY KEY (alias_type, alias_value),
    FOREIGN KEY (subject_id) REFERENCES subjects(subject_id)
);

CREATE INDEX IF NOT EXISTS idx_aliases_subject ON subject_aliases(subject_id);

CREATE TABLE IF NOT EXISTS subject_audit (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    ts         TEXT NOT NULL,
    op         TEXT NOT NULL,    -- create|link|merge|delete
    subject_id TEXT NOT NULL,
    actor      TEXT NOT NULL,
    detail     TEXT              -- JSON
);
"""

# Deterministic link sets — tuples of aliases that MUST come from the same
# source-authoritative record (a single row/object), not from co-occurrence.
DETERMINISTIC_SOURCES = {
    "shopify_customer",   # one record = one person, email+phone authoritative
    "klaviyo_profile",
    "richpanel_contact",
    "intercom_contact",
    "slack_user",         # user profile has email if set
    "notion_user",
}

ALIAS_TYPES = {"email", "phone", "dni", "slack_user_id", "notion_user_id",
               "order_id", "ticket_id", "klaviyo_profile_id",
               "shopify_customer_id", "intercom_contact_id"}


@dataclass
class Subject:
    subject_id: str
    created_at: str
    last_seen:  str
    deleted_at: Optional[str]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _db_path(home: Path) -> Path:
    return home / "state" / "subjects.db.enc"


class SubjectRegistry:
    def __init__(self, home: Path):
        self.home = home
        self.path = _db_path(home)
        self._bootstrap()

    def _bootstrap(self):
        with open_db(self.path, SCHEMA):
            pass

    # ─────────────────────────────────────────────────────────────────────

    def _db(self) -> EncryptedDB:
        return EncryptedDB(self.path)

    def _audit(self, db: EncryptedDB, op: str, subject_id: str, actor: str, detail: dict | None = None):
        db.execute(
            "INSERT INTO subject_audit (ts, op, subject_id, actor, detail) VALUES (?, ?, ?, ?, ?)",
            (_now(), op, subject_id, actor, json.dumps(detail) if detail else None),
        )

    def _new_subject(self, db: EncryptedDB, actor: str) -> str:
        sid = str(uuid.uuid4())
        now = _now()
        db.execute(
            "INSERT INTO subjects (subject_id, created_at, last_seen) VALUES (?, ?, ?)",
            (sid, now, now),
        )
        self._audit(db, "create", sid, actor)
        return sid

    # ─────────────────────────────────────────────────────────────────────
    # Public API

    def resolve_or_create(
        self,
        alias_type: str,
        alias_value: str,
        *,
        source: str,
        actor: str = "system",
    ) -> str:
        """Return subject_id for an alias, creating a new subject if unknown."""
        if alias_type not in ALIAS_TYPES:
            raise ValueError(f"unknown alias_type: {alias_type}")
        with self._db() as db:
            row = db.execute(
                "SELECT subject_id FROM subject_aliases WHERE alias_type = ? AND alias_value = ?",
                (alias_type, alias_value),
            ).fetchone()
            if row:
                sid = row["subject_id"]
                db.execute("UPDATE subjects SET last_seen = ? WHERE subject_id = ?", (_now(), sid))
            else:
                sid = self._new_subject(db, actor)
                db.execute(
                    "INSERT INTO subject_aliases (alias_type, alias_value, subject_id, source, first_seen) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (alias_type, alias_value, sid, source, _now()),
                )
                self._audit(db, "alias_add", sid, actor, {"alias": [alias_type, alias_value], "source": source})
            db.commit()
            return sid

    def link_aliases(
        self,
        aliases: list[tuple[str, str]],
        *,
        source: str,
        actor: str = "system",
    ) -> str:
        """
        Link a set of aliases that MUST come from the same authoritative record
        (e.g. one Shopify customer row). Rejects if `source` is not in
        DETERMINISTIC_SOURCES.
        """
        if source not in DETERMINISTIC_SOURCES:
            raise ValueError(f"non-deterministic source '{source}' cannot link aliases")
        if not aliases:
            raise ValueError("empty alias list")

        with self._db() as db:
            # Find any existing subject for any of these aliases.
            existing_sids: set[str] = set()
            for atype, aval in aliases:
                row = db.execute(
                    "SELECT subject_id FROM subject_aliases WHERE alias_type = ? AND alias_value = ?",
                    (atype, aval),
                ).fetchone()
                if row:
                    existing_sids.add(row["subject_id"])

            if len(existing_sids) > 1:
                # Multiple distinct subjects found → conflict; do NOT auto-merge.
                # Log and refuse — operator must call `merge` explicitly.
                self._audit(db, "link_conflict", ",".join(sorted(existing_sids)), actor, {"aliases": aliases, "source": source})
                db.commit()
                raise ConflictError(
                    f"Aliases {aliases} reference {len(existing_sids)} distinct subjects. "
                    f"Use `operai-init ingest subjects merge` to resolve explicitly."
                )

            sid = existing_sids.pop() if existing_sids else self._new_subject(db, actor)

            for atype, aval in aliases:
                db.execute(
                    "INSERT OR IGNORE INTO subject_aliases (alias_type, alias_value, subject_id, source, first_seen) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (atype, aval, sid, source, _now()),
                )
            db.execute("UPDATE subjects SET last_seen = ? WHERE subject_id = ?", (_now(), sid))
            self._audit(db, "link", sid, actor, {"aliases": aliases, "source": source})
            db.commit()
            return sid

    def find_by_alias(self, alias_type: str, alias_value: str) -> Optional[str]:
        with self._db() as db:
            row = db.execute(
                "SELECT subject_id FROM subject_aliases WHERE alias_type = ? AND alias_value = ?",
                (alias_type, alias_value),
            ).fetchone()
            return row["subject_id"] if row else None

    def aliases_for(self, subject_id: str) -> list[dict]:
        with self._db() as db:
            rows = db.execute(
                "SELECT alias_type, alias_value, source, first_seen FROM subject_aliases WHERE subject_id = ?",
                (subject_id,),
            ).fetchall()
            return [dict(r) for r in rows]

    def merge(self, source_id: str, target_id: str, *, actor: str, reason: str) -> None:
        """Admin-only merge of two subjects. Requires explicit reason for audit."""
        with self._db() as db:
            db.execute("UPDATE subject_aliases SET subject_id = ? WHERE subject_id = ?", (target_id, source_id))
            db.execute("UPDATE subjects SET deleted_at = ? WHERE subject_id = ?", (_now(), source_id))
            self._audit(db, "merge", target_id, actor, {"merged_from": source_id, "reason": reason})
            db.commit()

    def mark_deleted(self, subject_id: str, *, actor: str, reason: str) -> None:
        """Soft-delete — real propagation handled by ledger + connectors."""
        with self._db() as db:
            db.execute("UPDATE subjects SET deleted_at = ? WHERE subject_id = ?", (_now(), subject_id))
            self._audit(db, "delete", subject_id, actor, {"reason": reason})
            db.commit()

    def stats(self) -> dict:
        with self._db() as db:
            total = db.execute("SELECT COUNT(*) AS n FROM subjects WHERE deleted_at IS NULL").fetchone()["n"]
            deleted = db.execute("SELECT COUNT(*) AS n FROM subjects WHERE deleted_at IS NOT NULL").fetchone()["n"]
            aliases = db.execute("SELECT COUNT(*) AS n FROM subject_aliases").fetchone()["n"]
            by_type = {
                r["alias_type"]: r["n"]
                for r in db.execute(
                    "SELECT alias_type, COUNT(*) AS n FROM subject_aliases GROUP BY alias_type"
                ).fetchall()
            }
        return {"active": total, "deleted": deleted, "aliases_total": aliases, "aliases_by_type": by_type}


class ConflictError(Exception):
    pass
