"""operai-init ingest — CLI subcommands.

Dispatched from operai_init_cli.py → ingest.run_cli(args).
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

from operai_init import common
from operai_init.ingest.allowlist import Allowlist
from operai_init.ingest.ledger    import DeleteLedger
from operai_init.ingest.pipeline  import Pipeline
from operai_init.ingest.subjects  import SubjectRegistry, ConflictError
from operai_init.ingest.connectors import shopify, klaviyo, ads


# ─────────────────────────────────────────────────────────────────────────────
# allow / revoke / list-allow
# ─────────────────────────────────────────────────────────────────────────────

def cmd_allow(args, *, home: Path, brand: str):
    al = Allowlist(home)
    try:
        al.allow(args.source, args.unit_type, args.unit_id,
                 reason=args.reason, approved_by=args.by or "founder",
                 force=args.force)
    except ValueError as e:
        common.err(str(e)); sys.exit(2)
    common.ok(f"allowlisted {args.source}/{args.unit_type}:{args.unit_id}")


def cmd_revoke(args, *, home: Path, brand: str):
    al = Allowlist(home)
    if al.revoke(args.source, args.unit_type, args.unit_id):
        common.ok("revoked")
    else:
        common.warn("no active entry matched")


def cmd_allowlist(args, *, home: Path, brand: str):
    al = Allowlist(home)
    entries = al.list(source=args.source, include_revoked=args.all)
    if not entries:
        common.info("empty allowlist — nothing will be ingested until you allow sources")
        return
    print(f"\n  {'SOURCE':<14} {'UNIT_TYPE':<12} {'UNIT_ID':<40} {'BY':<15} {'STATUS':<8}")
    print(f"  {'-'*14} {'-'*12} {'-'*40} {'-'*15} {'-'*8}")
    for e in entries:
        status = "revoked" if e.revoked_at else "active"
        print(f"  {e.source:<14} {e.unit_type:<12} {e.unit_id[:40]:<40} {e.approved_by:<15} {status:<8}")
    print()


# ─────────────────────────────────────────────────────────────────────────────
# run / sync
# ─────────────────────────────────────────────────────────────────────────────

CONNECTORS = {
    "shopify":    shopify.run,
    "klaviyo":    klaviyo.run,
    "meta_ads":   ads.run_meta,
    "google_ads": ads.run_google,
}


def cmd_run(args, *, home: Path, brand: str):
    sources = [args.source] if args.source else list(CONNECTORS.keys())
    for src in sources:
        handler = CONNECTORS.get(src)
        if not handler:
            common.err(f"unknown source: {src}")
            continue
        common.banner(f"ingest · {src}")
        try:
            kwargs = {"home": home, "brand": brand}
            if src == "shopify":
                kwargs["days"] = args.days
            result = handler(**kwargs)
        except Exception as exc:  # noqa: BLE001
            common.err(f"{src} failed: {exc}")
            continue
        if "error" in result:
            common.warn(result["error"])
        else:
            common.ok(f"{src}: ingested — {json.dumps(result)[:160]}…")


# ─────────────────────────────────────────────────────────────────────────────
# subjects
# ─────────────────────────────────────────────────────────────────────────────

def cmd_subjects(args, *, home: Path, brand: str):
    reg = SubjectRegistry(home)
    if args.subjects_action == "stats":
        print(json.dumps(reg.stats(), indent=2))
    elif args.subjects_action == "merge":
        try:
            reg.merge(args.source_id, args.target_id, actor=args.by or "founder", reason=args.reason)
            common.ok(f"merged {args.source_id} into {args.target_id}")
        except Exception as exc:
            common.err(str(exc)); sys.exit(2)
    elif args.subjects_action == "find":
        sid = reg.find_by_alias(args.alias_type, args.alias_value)
        if sid:
            print(json.dumps({"subject_id": sid, "aliases": reg.aliases_for(sid)}, indent=2))
        else:
            common.warn("not found")


# ─────────────────────────────────────────────────────────────────────────────
# forget / forget-status
# ─────────────────────────────────────────────────────────────────────────────

def cmd_forget(args, *, home: Path, brand: str):
    reg = SubjectRegistry(home)
    ledger = DeleteLedger(home)

    if args.status:
        pending = ledger.pending()
        if not pending:
            common.info("no pending deletions")
            return
        print(f"\n  {'ID':<6} {'SUBJECT':<40} {'REQUESTED':<22} {'STORES PENDING':<40}")
        for d in pending:
            pending_stores = [s for s, done in d.status.items() if not done]
            print(f"  {d.id:<6} {d.subject_id[:38]:<40} {d.requested_at[:19]:<22} {','.join(pending_stores)}")
        print()
        return

    subject_id = args.subject
    if not subject_id and args.email:
        subject_id = reg.find_by_alias("email", args.email)
        if not subject_id:
            common.err(f"no subject found for email {args.email}")
            sys.exit(2)
    if not subject_id:
        common.err("need --subject or --email")
        sys.exit(2)

    pipeline = Pipeline(home, brand=brand)
    deletion_id = pipeline.forget(subject_id, triggered_by=args.by or "founder", reason=args.reason or "")
    common.ok(f"RTBF queued · deletion id {deletion_id} · check with `operai-init ingest forget --status`")


# ─────────────────────────────────────────────────────────────────────────────
# stats
# ─────────────────────────────────────────────────────────────────────────────

def cmd_stats(args, *, home: Path, brand: str):
    reg = SubjectRegistry(home)
    ledger = DeleteLedger(home)
    al = Allowlist(home)
    ingest_root = home / "brain" / "knowledge" / brand / "ingested"
    total_docs = sum(1 for _ in ingest_root.rglob("*.md")) if ingest_root.exists() else 0
    by_group: dict[str, int] = {}
    if ingest_root.exists():
        for p in ingest_root.iterdir():
            if p.is_dir():
                by_group[p.name] = sum(1 for _ in p.rglob("*.md"))

    report = {
        "brand":         brand,
        "allowlist":     [e.__dict__ for e in al.list()],
        "subjects":      reg.stats(),
        "deletions":     ledger.stats(),
        "retrieval_docs_total": total_docs,
        "retrieval_docs_by_acl_group": by_group,
    }
    print(json.dumps(report, indent=2, default=str))


# ─────────────────────────────────────────────────────────────────────────────
# Argparse registration (called from operai_init_cli.py)
# ─────────────────────────────────────────────────────────────────────────────

def register(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("ingest", help="Ingest data from connected sources into the brain")
    inner = p.add_subparsers(dest="ingest_action", required=True)

    # allow
    sp = inner.add_parser("allow", help="Allowlist a scope for ingestion")
    sp.add_argument("--source", required=True, choices=["shopify", "klaviyo", "meta_ads", "google_ads",
                                                         "gmail", "slack", "notion", "drive", "richpanel"])
    sp.add_argument("--unit-type", required=True, help="resource|account|mailbox|channel|folder|page")
    sp.add_argument("--unit-id", required=True, help="source-specific identifier")
    sp.add_argument("--reason", required=True, help="legal-basis/necessity justification")
    sp.add_argument("--by", help="approver name (default: founder)")
    sp.add_argument("--force", action="store_true", help="bypass gmail shared-inbox heuristic (use carefully)")
    sp.set_defaults(ingest_func=cmd_allow)

    # revoke
    sp = inner.add_parser("revoke", help="Revoke an allowlist entry")
    sp.add_argument("--source", required=True)
    sp.add_argument("--unit-type", required=True)
    sp.add_argument("--unit-id", required=True)
    sp.set_defaults(ingest_func=cmd_revoke)

    # allowlist
    sp = inner.add_parser("allowlist", help="Show allowlist")
    sp.add_argument("--source", help="filter by source")
    sp.add_argument("--all", action="store_true", help="include revoked")
    sp.set_defaults(ingest_func=cmd_allowlist)

    # run
    sp = inner.add_parser("run", help="Run one or all connectors (Phase 1: shopify/klaviyo/ads only)")
    sp.add_argument("--source", choices=list(CONNECTORS.keys()))
    sp.add_argument("--days", type=int, default=90, help="window for aggregated data (default 90)")
    sp.set_defaults(ingest_func=cmd_run)

    # subjects
    sp = inner.add_parser("subjects", help="Subject Registry operations")
    ss = sp.add_subparsers(dest="subjects_action", required=True)
    ss.add_parser("stats")
    sm = ss.add_parser("merge"); sm.add_argument("source_id"); sm.add_argument("target_id")
    sm.add_argument("--reason", required=True); sm.add_argument("--by")
    sf = ss.add_parser("find"); sf.add_argument("alias_type"); sf.add_argument("alias_value")
    sp.set_defaults(ingest_func=cmd_subjects)

    # forget
    sp = inner.add_parser("forget", help="RTBF — purge a subject across all stores")
    sp.add_argument("--subject", help="subject_id (preferred)")
    sp.add_argument("--email", help="resolve via alias")
    sp.add_argument("--reason")
    sp.add_argument("--by")
    sp.add_argument("--status", action="store_true", help="show pending deletions")
    sp.set_defaults(ingest_func=cmd_forget)

    # stats
    sp = inner.add_parser("stats", help="Show ingest system stats as JSON")
    sp.set_defaults(ingest_func=cmd_stats)
