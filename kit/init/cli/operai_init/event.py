"""operai-init event — CLI for event submission + listing (pre-webhook MVP interface).

Usage:
    operai-init event submit --domain cs --input ticket.json [--id X]
    operai-init event list [--bucket pending|in-flight|completed|failed|escalations]
    operai-init event show --id <event_id>
    operai-init event replay --id <event_id>     # move from completed back to pending
"""
from __future__ import annotations
import argparse
import json
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path

from operai_init import common


def _events_root(home: Path) -> Path:
    p = home / "events"
    for b in ("pending", "completed", "failed", "in-flight", "escalations"):
        (p / b).mkdir(parents=True, exist_ok=True)
    return p


def cmd_submit(args, *, home: Path, brand: str):
    domain = args.domain
    input_path = Path(args.input)
    if not input_path.exists():
        common.err(f"input not found: {input_path}")
        return
    try:
        payload = json.loads(input_path.read_text())
    except json.JSONDecodeError as e:
        common.err(f"invalid JSON: {e}")
        return

    event_id = args.id or f"{domain}-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:8]}"
    target_dir = _events_root(home) / "pending" / domain
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / f"{event_id}.json"
    target.write_text(json.dumps(payload, indent=2, ensure_ascii=False))
    common.ok(f"event submitted: {event_id}")
    common.info(f"path: {target}")
    common.info(f"the daemon (if running) will pick it up within ~3s")


def cmd_list(args, *, home: Path, brand: str):
    root = _events_root(home)
    buckets = ["pending", "in-flight", "completed", "failed", "escalations"]
    if args.bucket:
        if args.bucket not in buckets:
            common.err(f"unknown bucket '{args.bucket}'")
            return
        buckets = [args.bucket]
    for b in buckets:
        base = root / b
        files = list(base.rglob("*.json")) if base.exists() else []
        print(f"\n  {common.BOLD}{b}{common.RESET} ({len(files)})")
        for f in sorted(files)[:20]:
            rel = f.relative_to(base)
            mtime = datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            print(f"    {mtime}  {rel}")
    print()


def cmd_show(args, *, home: Path, brand: str):
    root = _events_root(home)
    found = None
    for b in ("pending", "in-flight", "completed", "failed"):
        for f in (root / b).rglob(f"{args.id}.json"):
            found = f
            break
        if found:
            break
    if not found:
        common.err(f"event not found: {args.id}")
        return
    print(f"  {common.BOLD}{found}{common.RESET}")
    print(found.read_text())

    # Show trace if exists
    trace_path = home / "brain" / "memory"
    for md in trace_path.rglob(f"{args.id}.json"):
        print(f"\n  {common.BOLD}Trace JSON: {md}{common.RESET}")
        break


def cmd_replay(args, *, home: Path, brand: str):
    root = _events_root(home)
    completed = root / "completed"
    found = None
    for f in completed.rglob(f"{args.id}.json"):
        found = f
        break
    if not found:
        common.err(f"event not found in completed/: {args.id}")
        return
    domain = found.parent.name
    target = root / "pending" / domain / found.name
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(str(found), str(target))
    common.ok(f"event {args.id} replayed to pending/{domain}/")


def register(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("event", help="Submit / list / replay events for the factory runtime")
    inner = p.add_subparsers(dest="event_action", required=True)

    sp = inner.add_parser("submit", help="Submit an event JSON for daemon processing")
    sp.add_argument("--domain", required=True, help="e.g. cs")
    sp.add_argument("--input",  required=True, help="Path to event JSON")
    sp.add_argument("--id", help="Override event id (otherwise auto-generated)")
    sp.set_defaults(event_func=cmd_submit)

    sp = inner.add_parser("list", help="List events by bucket")
    sp.add_argument("--bucket", help="pending|in-flight|completed|failed|escalations")
    sp.set_defaults(event_func=cmd_list)

    sp = inner.add_parser("show", help="Show event + trace")
    sp.add_argument("--id", required=True)
    sp.set_defaults(event_func=cmd_show)

    sp = inner.add_parser("replay", help="Copy a completed event back to pending for re-run")
    sp.add_argument("--id", required=True)
    sp.set_defaults(event_func=cmd_replay)
