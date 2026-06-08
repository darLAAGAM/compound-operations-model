#!/usr/bin/env python3
"""
operai-init — CLI dispatcher for OperAI brand bootstrap operations.

Installed at /usr/local/bin/operai-init by install.sh.

Subcommands:
    connect <service>      Wire an integration (shopify | klaviyo | google-workspace | slack)
    tunnel <subdomain>     Create + install a Cloudflare Tunnel for the MCP endpoint
    team-join [--out path] Generate team-join.sh for employee onboarding
    status                 Show health of integrations, services, and brain
    distil                 (v0.3 — placeholder) Auto-generate per-area contexts

All subcommands respect $OPERAI_HOME (default /opt/operai).
"""
from __future__ import annotations
import argparse
import json
import os
import sys
from pathlib import Path


# Make sibling packages importable when run from anywhere
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from operai_init import connect, tunnel, team_join, status, key as key_cmd, assess as assess_cmd, governance as gov_cmd, factory as factory_cmd  # noqa: E402
from operai_init.llm import cli as llm_cli  # noqa: E402
from operai_init import event as event_cli  # noqa: E402
from operai_init.webhook import cli as webhook_cli  # noqa: E402
from operai_init.webhook import digest_cli  # noqa: E402
from operai_init import onboarding as onboarding_cli  # noqa: E402
from operai_init import setup_brand as setup_brand_cli  # noqa: E402
from operai_init.ingest import cli as ingest_cli  # noqa: E402


GOLD = "\033[38;5;179m"
BOLD = "\033[1m"
DIM  = "\033[2m"
RESET = "\033[0m"
RED = "\033[31m"


def _home() -> Path:
    p = Path(os.environ.get("OPERAI_HOME", "/opt/operai"))
    if not p.exists():
        print(f"{RED}✗{RESET} {p} not found. Did you run install.sh?", file=sys.stderr)
        sys.exit(2)
    return p


def _brand(home: Path) -> str:
    """Resolve brand slug from /opt/operai/brain/knowledge/ layout."""
    kb = home / "brain" / "knowledge"
    if not kb.exists():
        return "unknown"
    reserved = {"platform", "personal", "projects"}
    for child in sorted(kb.iterdir()):
        if child.is_dir() and child.name not in reserved:
            return child.name
    return "unknown"


def cmd_connect(args):
    home = _home()
    brand = _brand(home)
    connect.run(args.service, home=home, brand=brand, force=args.force)


def cmd_tunnel(args):
    home = _home()
    brand = _brand(home)
    tunnel.run(args.subdomain, home=home, brand=brand, port=args.port)


def cmd_team_join(args):
    home = _home()
    brand = _brand(home)
    team_join.run(out=args.out, home=home, brand=brand, mcp_url=args.mcp_url)


def cmd_status(args):
    home = _home()
    brand = _brand(home)
    status.run(home=home, brand=brand, json_out=args.json)


def cmd_key(args):
    home = _home()
    if args.key_action == "create":
        key_cmd.create(home=home, name=args.name, role=args.role)
    elif args.key_action == "list":
        key_cmd.list_keys(home=home)
    elif args.key_action == "revoke":
        key_cmd.revoke(home=home, name=args.name)


def cmd_distil(args):
    print(f"{GOLD}{BOLD}operai-init distil{RESET} · v0.5 (not yet implemented)")
    print("This will auto-generate 6 per-area contexts after 30d of ingested data.")
    print("Tracking: knowledge/projects/operai/brand-bootstrap-v0.1.md")
    sys.exit(2)


def cmd_ingest(args):
    home = _home()
    brand = _brand(home)
    args.ingest_func(args, home=home, brand=brand)


def cmd_assess(args):
    home = _home()
    brand = _brand(home)
    assess_cmd.run(home=home, brand=brand, name=args.name, team=args.team)


def cmd_governance(args):
    home = _home()
    brand = _brand(home)
    args.gov_func(args, home=home, brand=brand)


def cmd_factory(args):
    home = _home()
    brand = _brand(home)
    args.factory_func(args, home=home, brand=brand)


def cmd_llm(args):
    home = _home()
    brand = _brand(home)
    args.llm_func(args, home=home, brand=brand)


def cmd_event(args):
    home = _home()
    brand = _brand(home)
    args.event_func(args, home=home, brand=brand)


def cmd_webhook(args):
    home = _home()
    brand = _brand(home)
    args.webhook_func(args, home=home, brand=brand)


def cmd_digest(args):
    home = _home()
    brand = _brand(home)
    args.digest_func(args, home=home, brand=brand)


def cmd_onboarding(args):
    home = _home()
    brand = _brand(home)
    args.onboarding_func(args, home=home, brand=brand)


def cmd_setup_brand(args):
    home = _home()
    brand = _brand(home)
    args.setup_func(args, home=home, brand=brand)


def main():
    ap = argparse.ArgumentParser(prog="operai-init", description=__doc__)
    sub = ap.add_subparsers(dest="command", required=True)

    # connect
    sp = sub.add_parser("connect", help="Wire an integration")
    sp.add_argument("service", choices=["shopify", "klaviyo", "google-workspace", "slack"])
    sp.add_argument("--force", action="store_true", help="Overwrite existing credentials")
    sp.set_defaults(func=cmd_connect)

    # tunnel
    sp = sub.add_parser("tunnel", help="Create Cloudflare Tunnel for MCP endpoint")
    sp.add_argument("subdomain", help="Full subdomain, e.g. mcp.acme.com")
    sp.add_argument("--port", type=int, default=8787, help="Local MCP port (default 8787)")
    sp.set_defaults(func=cmd_tunnel)

    # team-join
    sp = sub.add_parser("team-join", help="Generate team-join.sh for employees")
    sp.add_argument("--out", default="-", help="Output path or '-' for stdout (default)")
    sp.add_argument("--mcp-url", default=None, help="Override MCP URL (else auto-detected)")
    sp.set_defaults(func=cmd_team_join)

    # status
    sp = sub.add_parser("status", help="Health check of the swarm")
    sp.add_argument("--json", action="store_true", help="Emit JSON instead of pretty output")
    sp.set_defaults(func=cmd_status)

    # key
    sp = sub.add_parser("key", help="Manage MCP API keys (create / list / revoke)")
    key_sub = sp.add_subparsers(dest="key_action", required=True)
    kc = key_sub.add_parser("create", help="Generate a new API key")
    kc.add_argument("name", help="Employee name/slug (e.g. diego, laura)")
    kc.add_argument("--role", choices=["admin", "team"], default="team")
    key_sub.add_parser("list", help="List all keys (tokens masked)")
    kr = key_sub.add_parser("revoke", help="Revoke all active keys for a name")
    kr.add_argument("name")
    sp.set_defaults(func=cmd_key)

    # ingest (Phase 1 — structured low-risk)
    ingest_cli.register(sub)
    if "ingest" in sub.choices:
        sub.choices["ingest"].set_defaults(func=cmd_ingest)

    # governance
    gov_cmd.register(sub)
    if "governance" in sub.choices:
        sub.choices["governance"].set_defaults(func=cmd_governance)

    # factory
    factory_cmd.register(sub)
    if "factory" in sub.choices:
        sub.choices["factory"].set_defaults(func=cmd_factory)

    # llm
    llm_cli.register(sub)
    if "llm" in sub.choices:
        sub.choices["llm"].set_defaults(func=cmd_llm)

    # event (v0.9.1 MVP — manual event submission before webhooks)
    event_cli.register(sub)
    if "event" in sub.choices:
        sub.choices["event"].set_defaults(func=cmd_event)

    # webhook (v3.0 — helpdesk HTTP receivers)
    webhook_cli.register(sub)
    if "webhook" in sub.choices:
        sub.choices["webhook"].set_defaults(func=cmd_webhook)

    # digest (v3.0 — Slack daily digest)
    digest_cli.register(sub)
    if "digest" in sub.choices:
        sub.choices["digest"].set_defaults(func=cmd_digest)

    # onboarding (v3.1 — team-onboard + onboarding-pack)
    onboarding_cli.register(sub)
    for name in ("team-onboard", "onboarding-pack"):
        if name in sub.choices:
            sub.choices[name].set_defaults(func=cmd_onboarding)

    # setup-brand (v3.1 — interactive happy-path wizard)
    setup_brand_cli.register(sub)
    if "setup-brand" in sub.choices:
        sub.choices["setup-brand"].set_defaults(func=cmd_setup_brand)

    # assess
    sp = sub.add_parser("assess", help="Classify employee into M-shaped/T-shaped/frontline + training path")
    sp.add_argument("name", nargs="?", help="Employee slug (or omit with --team for distribution)")
    sp.add_argument("--team", action="store_true", help="Show team profile distribution")
    sp.set_defaults(func=cmd_assess)

    # distil
    sp = sub.add_parser("distil", help="(v0.5) Auto-generate 6 per-area contexts")
    sp.set_defaults(func=cmd_distil)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
