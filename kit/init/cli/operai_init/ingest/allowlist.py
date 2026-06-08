"""Allowlist — explicit per-source scope control.

Required before any connector runs. No `walk workspace`, no crawl-by-default.

Allowlist entries carry the legal-basis justification and approver, because
the DPIA requires a proportionality/necessity test per scope.
"""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from operai_init.ingest.storage import open_db, EncryptedDB

SCHEMA = """
CREATE TABLE IF NOT EXISTS allowlist (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    source        TEXT NOT NULL,       -- shopify|klaviyo|ads_meta|ads_google|gmail|slack|notion|drive|richpanel
    unit_type     TEXT NOT NULL,       -- resource|account|mailbox|channel|folder|page
    unit_id       TEXT NOT NULL,
    reason        TEXT NOT NULL,       -- legal-basis / necessity justification
    approved_by   TEXT NOT NULL,       -- founder name or admin principal
    approved_at   TEXT NOT NULL,
    revoked_at    TEXT,
    UNIQUE (source, unit_type, unit_id)
);

CREATE INDEX IF NOT EXISTS idx_allowlist_source ON allowlist(source) WHERE revoked_at IS NULL;
"""

# Sources gated hard: require legal sign-off text before accepting.
HIGH_RISK_SOURCES = {"gmail", "slack", "notion", "drive", "richpanel"}

# Sources frozen in the public Kit (v2.6+) — available only via Custom Ingest Engagement.
# See playbook Ch.11f + Ch.13 for the decision trail.
FROZEN_IN_KIT = {"gmail", "slack", "notion", "drive", "richpanel"}

# Gmail: only shared mailboxes, never personal.
# Unit IDs look like "info@brand.com", "ops@brand.com". Reject if looks
# like a personal inbox.
def _validate_gmail_unit(unit_id: str) -> Optional[str]:
    if "@" not in unit_id:
        return "must be an email address"
    local = unit_id.split("@", 1)[0].lower()
    personal_smell = {"firstname", "lastname", "diego", "laura", "me", "personal"}
    if any(p in local for p in personal_smell):
        return "looks like a personal mailbox — only shared inboxes (info@, ops@, wholesale@, support@, hello@) are allowed"
    # Common safe shared-inbox prefixes
    safe_prefixes = {"info", "ops", "support", "hello", "wholesale", "press", "contact", "admin", "finance", "sales", "help", "team"}
    if local not in safe_prefixes:
        return f"'{local}@' doesn't match a known shared-inbox pattern ({sorted(safe_prefixes)}) — if this really is a shared inbox, add it via --force"
    return None


@dataclass
class AllowEntry:
    id: int
    source: str
    unit_type: str
    unit_id: str
    reason: str
    approved_by: str
    approved_at: str
    revoked_at: Optional[str]


def _db_path(home: Path) -> Path:
    return home / "state" / "allowlist.db.enc"


class Allowlist:
    def __init__(self, home: Path):
        self.home = home
        self.path = _db_path(home)
        with open_db(self.path, SCHEMA):
            pass

    def _db(self) -> EncryptedDB:
        return EncryptedDB(self.path)

    def allow(
        self,
        source: str,
        unit_type: str,
        unit_id: str,
        *,
        reason: str,
        approved_by: str,
        force: bool = False,
    ) -> int:
        if source == "gmail":
            if err := _validate_gmail_unit(unit_id):
                if not force:
                    raise ValueError(err)
        if source in FROZEN_IN_KIT:
            raise ValueError(
                f"source {source} is frozen in the public Kit (v2.6+). "
                f"Available only via Custom Ingest Engagement (see playbook Ch.11f + Ch.13). "
                f"Contact hello@usecompai.com with subject Custom Ingest Engagement."
            )
        if source in HIGH_RISK_SOURCES and len(reason.strip()) < 20:
            raise ValueError(
                f"'{source}' is a high-risk source; please provide a detailed legal-basis "
                f"justification (min 20 chars). Example: "
                f"'legítimo interés — comunicaciones con clientes B2B, necesario para CS ops, "
                f"retention 90d'."
            )
        now = datetime.now(timezone.utc).isoformat()
        with self._db() as db:
            cur = db.execute(
                "INSERT OR REPLACE INTO allowlist (source, unit_type, unit_id, reason, approved_by, approved_at, revoked_at) "
                "VALUES (?, ?, ?, ?, ?, ?, NULL)",
                (source, unit_type, unit_id, reason, approved_by, now),
            )
            db.commit()
            return cur.lastrowid

    def revoke(self, source: str, unit_type: str, unit_id: str) -> bool:
        now = datetime.now(timezone.utc).isoformat()
        with self._db() as db:
            cur = db.execute(
                "UPDATE allowlist SET revoked_at = ? WHERE source = ? AND unit_type = ? AND unit_id = ? AND revoked_at IS NULL",
                (now, source, unit_type, unit_id),
            )
            db.commit()
            return cur.rowcount > 0

    def list(self, source: Optional[str] = None, include_revoked: bool = False) -> list[AllowEntry]:
        with self._db() as db:
            sql = "SELECT * FROM allowlist"
            clauses = []
            args: list = []
            if source:
                clauses.append("source = ?")
                args.append(source)
            if not include_revoked:
                clauses.append("revoked_at IS NULL")
            if clauses:
                sql += " WHERE " + " AND ".join(clauses)
            sql += " ORDER BY approved_at DESC"
            rows = db.execute(sql, args).fetchall()
        return [AllowEntry(**dict(r)) for r in rows]

    def is_allowed(self, source: str, unit_type: str, unit_id: str) -> bool:
        with self._db() as db:
            row = db.execute(
                "SELECT 1 FROM allowlist WHERE source = ? AND unit_type = ? AND unit_id = ? AND revoked_at IS NULL",
                (source, unit_type, unit_id),
            ).fetchone()
        return row is not None

    def allowed_units(self, source: str) -> list[AllowEntry]:
        return [e for e in self.list(source=source) if e.revoked_at is None]
