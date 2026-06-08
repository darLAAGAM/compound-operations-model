"""operai-init digest — Slack digest CLI."""
from __future__ import annotations
import argparse
import json
from pathlib import Path

from operai_init import common
from operai_init.webhook import digest as dg


def cmd_configure(args, *, home: Path, brand: str):
    common.banner("Configure Slack digest")
    print(
        "\n  1. Go to Slack → your workspace → Settings → Manage apps → Incoming Webhooks"
        "\n  2. Add a new webhook, choose the channel (e.g. #operai-ops)"
        "\n  3. Copy the webhook URL (starts with https://hooks.slack.com/services/...)"
        "\n"
    )
    url = common.read_secret("Slack webhook URL (paste, hidden): ").strip()
    if not url.startswith("https://hooks.slack.com/"):
        common.warn("URL doesn't look like a Slack webhook — saving anyway")
    channel = common.prompt("Optional: Slack channel override (leave blank to use webhook default)").strip() or None
    cfg = dg.load_config(home)
    cfg.update({"slack_webhook": url, "channel": channel, "enabled": True})
    dg.save_config(home, cfg)
    common.ok("digest configured")
    if common.confirm("Send a test digest now?", default=True):
        cmd_now(args, home=home, brand=brand)


def cmd_now(args, *, home: Path, brand: str):
    cfg = dg.load_config(home)
    if not cfg.get("slack_webhook"):
        common.err("Slack webhook not configured. Run: operai-init digest configure")
        return
    digest = dg.build_digest(home, brand)
    if args.json:
        print(json.dumps(digest, indent=2))
        return
    print(digest["summary"])
    print()
    ok, detail = dg.send_to_slack(cfg["slack_webhook"], digest, channel=cfg.get("channel"))
    if ok:
        common.ok(f"sent to Slack · {detail}")
    else:
        common.err(f"send failed: {detail}")


def cmd_schedule(args, *, home: Path, brand: str):
    cfg = dg.load_config(home)
    if not cfg.get("slack_webhook"):
        common.err("configure a Slack webhook first: operai-init digest configure")
        return
    ok, detail = dg.install_cron(home, hour_utc=args.hour, minute=args.minute)
    cfg["schedule_cron"] = f"{args.minute} {args.hour} * * *"
    dg.save_config(home, cfg)
    if ok:
        common.ok(f"cron scheduled daily at {args.hour:02d}:{args.minute:02d} UTC · {detail}")
    else:
        common.err(f"could not install cron: {detail}")


def cmd_status(args, *, home: Path, brand: str):
    cfg = dg.load_config(home)
    print(f"\n  {common.BOLD}Digest status{common.RESET}\n")
    configured = bool(cfg.get("slack_webhook"))
    print(f"  Slack webhook: {'configured' if configured else common.RED + 'not configured' + common.RESET}")
    if cfg.get("channel"):
        print(f"  Override channel: {cfg['channel']}")
    if cfg.get("schedule_cron"):
        print(f"  Scheduled: {cfg['schedule_cron']} UTC (daily)")
    else:
        print(f"  Scheduled: {common.DIM}no cron installed — run: operai-init digest schedule{common.RESET}")
    print()
    # Preview current digest
    digest = dg.build_digest(home, brand)
    for k, v in digest["counters"].items():
        print(f"    {k:<14} {v}")
    print()


def register(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("digest", help="Daily Slack digest of factory activity")
    inner = p.add_subparsers(dest="digest_action", required=True)

    sp = inner.add_parser("configure", help="Configure the Slack webhook URL")
    sp.set_defaults(digest_func=cmd_configure)

    sp = inner.add_parser("now", help="Build + send a digest right now")
    sp.add_argument("--json", action="store_true")
    sp.set_defaults(digest_func=cmd_now)

    sp = inner.add_parser("schedule", help="Install a daily cron job")
    sp.add_argument("--hour",   type=int, default=8, help="UTC hour, 0-23 (default 8)")
    sp.add_argument("--minute", type=int, default=0)
    sp.set_defaults(digest_func=cmd_schedule)

    sp = inner.add_parser("status", help="Show config + current counters")
    sp.set_defaults(digest_func=cmd_status)
