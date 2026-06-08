"""Ingest pipeline — orchestrates connector → DLP → subject registry → evidence + retrieval stores.

Every ingested doc lands in two places:
  1. Evidence store (encrypted, TTL, not indexed) — original canonical doc
  2. Retrieval store (sanitized markdown with ACL front-matter) — indexed by QMD

Retrieval store path structure:
    /opt/operai/brain/knowledge/<brand>/ingested/<acl_group>/<YYYY>/<MM>/<doc_id>.md

The <acl_group> folder is what makes ACL "at the index boundary": QMD's
per-collection config mirrors the acl-group folders, so an employee whose
keys only include `public` never has their query routed through the
`finance` index.
"""
from __future__ import annotations
import hashlib
import json
import os
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional

from operai_init.ingest.allowlist   import Allowlist
from operai_init.ingest.dlp         import sanitize, DLPResult
from operai_init.ingest.evidence    import EvidenceStore
from operai_init.ingest.ledger      import DeleteLedger
from operai_init.ingest.subjects    import SubjectRegistry


@dataclass
class CanonicalDoc:
    source:     str
    source_ref: str
    kind:       str
    title:      Optional[str]
    body_text:  str
    created_at: str
    updated_at: str
    native_acl: list[str] = field(default_factory=list)   # group names the doc came from
    source_meta: dict = field(default_factory=dict)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _stable_doc_id(source: str, source_ref: str) -> str:
    h = hashlib.sha256(f"{source}:{source_ref}".encode()).hexdigest()
    return f"{source}-{h[:16]}"


def _resolve_acl_group(native_acl: list[str]) -> str:
    """Pick a single primary ACL group for folder placement.

    Rule: most-restrictive wins. Known groups by priority (restrictive → open):
        finance, hr, wholesale, retail, marketing, product, ops, cs, general, public
    Unknown groups → 'general'.
    """
    priority = ["finance", "hr", "wholesale", "retail", "marketing",
                "product", "ops", "cs", "general", "public"]
    present = [g for g in priority if g in native_acl]
    return present[0] if present else "general"


@dataclass
class IngestResult:
    doc_id:   str
    source:   str
    stored:   bool             # went to retrieval store
    skipped:  Optional[str]    # reason if not stored
    subjects: list[str]        # subject_ids referenced


class Pipeline:
    def __init__(
        self,
        home: Path,
        *,
        brand: str,
        subjects: SubjectRegistry | None = None,
        ledger:   DeleteLedger | None = None,
        allowlist: Allowlist | None = None,
    ):
        self.home = home
        self.brand = brand
        self.subjects  = subjects  or SubjectRegistry(home)
        self.ledger    = ledger    or DeleteLedger(home)
        self.allowlist = allowlist or Allowlist(home)
        self.brain_root = home / "brain"

    # ─────────────────────────────────────────────────────────────────────
    def ingested_dir(self, acl_group: str, when: datetime) -> Path:
        return self.brain_root / "knowledge" / self.brand / "ingested" / acl_group / f"{when.year:04d}" / f"{when.month:02d}"

    def ingest(self, doc: CanonicalDoc) -> IngestResult:
        doc_id = _stable_doc_id(doc.source, doc.source_ref)

        # 1. DLP — Stage A + B
        resolver = lambda atype, aval: self.subjects.resolve_or_create(
            atype, aval, source=doc.source, actor="pipeline"
        )
        dlp = sanitize(doc.body_text, resolver=resolver)

        subject_ids = sorted({tok.split(":", 1)[1].rstrip(">") for (_, tok) in dlp.replacements})

        # 2. Evidence store — write original (even if DLP refused retrieval)
        evidence = EvidenceStore(self.home, doc.source)
        evidence.store(
            doc_id=doc_id,
            source_ref=doc.source_ref,
            kind=doc.kind,
            canonical=asdict(doc),
            subjects=subject_ids,
        )

        if not dlp.safe_for_retrieval:
            return IngestResult(doc_id=doc_id, source=doc.source, stored=False,
                                skipped=f"dlp_secret_detected:{','.join(dlp.found_secrets)}",
                                subjects=subject_ids)

        # 3. Retrieval store — sanitized markdown with ACL front-matter
        acl_group = _resolve_acl_group(doc.native_acl)
        when = datetime.now(timezone.utc)
        out_dir = self.ingested_dir(acl_group, when)
        out_dir.mkdir(parents=True, exist_ok=True)
        retention_until = (when + timedelta(days=90)).isoformat()

        front = {
            "source":     doc.source,
            "source_ref": doc.source_ref,
            "doc_id":     doc_id,
            "ingested_at": _now_iso(),
            "dlp_version": "0.4.0",
            "acl": {
                "group":              acl_group,
                "roles":              ["admin", "team"],
                "subjects_mentioned": subject_ids,
            },
            "retention_until": retention_until,
        }
        body = f"""---
{json.dumps(front, indent=2)}
---

# {doc.title or doc.source_ref}

{dlp.sanitized_text}
"""
        out_path = out_dir / f"{doc_id}.md"
        out_path.write_text(body)
        os.chmod(out_path, 0o640)

        return IngestResult(doc_id=doc_id, source=doc.source, stored=True,
                            skipped=None, subjects=subject_ids)

    # ─────────────────────────────────────────────────────────────────────
    def forget(self, subject_id: str, *, triggered_by: str, reason: str = "") -> int:
        """Propagate RTBF across all stores. Returns ledger deletion id."""
        ledger_id = self.ledger.record(subject_id, triggered_by=triggered_by, reason=reason)

        # Evidence stores — per source
        sources = [p.stem.removeprefix("evidence-").removesuffix(".db") for p in (self.home / "state").glob("evidence-*.db.enc")]
        total_deleted = 0
        for source in sources:
            name = source.split(".")[0]
            ev = EvidenceStore(self.home, name)
            total_deleted += ev.delete_by_subject(subject_id)
        self.ledger.mark_store_done(ledger_id, "evidence_done")

        # Retrieval store — grep through ingested/ for front-matter references
        deleted_retrieval = 0
        ingest_root = self.brain_root / "knowledge" / self.brand / "ingested"
        if ingest_root.exists():
            for md in ingest_root.rglob("*.md"):
                text = md.read_text(errors="replace")
                if subject_id in text:
                    md.unlink()
                    deleted_retrieval += 1
        self.ledger.mark_store_done(ledger_id, "retrieval_done")

        # Subject registry — soft delete
        self.subjects.mark_deleted(subject_id, actor=triggered_by, reason=reason)

        # QMD — next cron tick will reindex automatically. We don't block on it,
        # but mark the propagation step so the ledger can reach completed state.
        # (A dedicated qmd reindex job is triggered by install.sh cron).
        self.ledger.mark_store_done(ledger_id, "qmd_reindex_done")

        # Summaries / logs / backups / llm_provider are out of scope for synchronous
        # propagation. The daily maintenance job handles them.

        return ledger_id
