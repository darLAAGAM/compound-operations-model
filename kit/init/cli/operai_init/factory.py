"""factory — manage agent factories (parent + sub-agents).

Ships CS factory in v2.6 as reference. Other 6 domains roll out in v2.7+.

Commands:
  enable  --domain <cs>    Install factory templates into /opt/operai/agents/<domain>/
  disable --domain <cs>    Remove factory (monolithic SOUL remains unchanged)
  list                     Show available factory templates
  show    --domain <cs>    Show sub-agent details for one factory
  status                   Show which domains have factories enabled
"""
from __future__ import annotations
import argparse
import shutil
from pathlib import Path

from operai_init import common


AVAILABLE_FACTORIES = ["cs"]   # v2.6 — others roll out in v2.7-v2.9
PLANNED_FACTORIES   = ["finance", "ops", "marketing", "merch", "retail", "hr"]


def _templates_dir(home: Path) -> Path:
    return home / "services" / "init" / "agent-factory-templates"


def _factory_src(home: Path, domain: str) -> Path:
    return _templates_dir(home) / domain


def _factory_dst(home: Path, domain: str) -> Path:
    return home / "agents" / domain / "factory"


def cmd_enable(args, *, home: Path, brand: str):
    domain = args.domain
    if domain not in AVAILABLE_FACTORIES:
        if domain in PLANNED_FACTORIES:
            common.err(f"factory for '{domain}' is planned but not yet shipped (v2.7-v2.9)")
        else:
            common.err(f"unknown domain '{domain}'")
        return

    src = _factory_src(home, domain)
    if not src.exists():
        common.err(f"factory template not found at {src} — re-run install.sh")
        return

    dst = _factory_dst(home, domain)
    if dst.exists():
        common.warn(f"factory already enabled for '{domain}' at {dst}")
        if not common.confirm("Overwrite?", default=False):
            return
        shutil.rmtree(dst)

    common.banner(f"Enabling {domain} factory")
    shutil.copytree(src, dst)
    common.ok(f"factory copied to {dst}")

    # Count sub-agents
    sub_dir = dst / "sub-agents"
    n_subs = sum(1 for p in sub_dir.iterdir() if p.is_dir()) if sub_dir.exists() else 0
    common.ok(f"{n_subs} sub-agent SOULs installed")

    # Write a marker file so status can detect
    marker = dst / ".enabled"
    marker.write_text(f"enabled_at: {__import__('datetime').datetime.utcnow().isoformat()}Z\nbrand: {brand}\n")

    print(f"""
{common.BOLD}Next:{common.RESET}
  operai-init factory show --domain {domain}     # inspect sub-agents + contracts
  # Runtime LLM orchestration ships in v0.7 — for now the factory is a static artifact
  # parent agent-runner heartbeat continues to operate as before
""")


def cmd_disable(args, *, home: Path, brand: str):
    if not args.reason:
        common.err("--reason required (audit trail)")
        return
    dst = _factory_dst(home, args.domain)
    if not dst.exists():
        common.warn(f"no factory enabled for '{args.domain}'")
        return
    shutil.rmtree(dst)
    common.ok(f"factory disabled for {args.domain}")
    # Audit
    from datetime import datetime, timezone
    audit = home / "brain" / "audit" / "factory.log"
    audit.parent.mkdir(parents=True, exist_ok=True)
    with audit.open("a") as f:
        f.write(f"{datetime.now(timezone.utc).isoformat()}\tdisable\t{args.domain}\t{args.by or 'unknown'}\t{args.reason}\n")
    common.ok(f"audit: {audit}")


def cmd_list(args, *, home: Path, brand: str):
    print(f"\n  {common.BOLD}Factory templates{common.RESET}\n")
    for d in AVAILABLE_FACTORIES:
        src = _factory_src(home, d)
        dst = _factory_dst(home, d)
        avail = "available" if src.exists() else "missing"
        enabled = "ENABLED" if dst.exists() else "not enabled"
        print(f"  {d:<12} · {avail:<10} · {enabled}")
    for d in PLANNED_FACTORIES:
        print(f"  {d:<12} · {common.DIM}planned (v2.7-v2.9){common.RESET}")
    print()


def cmd_show(args, *, home: Path, brand: str):
    src = _factory_src(home, args.domain)
    if not src.exists():
        common.err(f"factory '{args.domain}' not available")
        return
    yml = src / "factory.yml"
    if yml.exists():
        print(f"\n  {common.BOLD}factory.yml{common.RESET} · {yml}\n")
        print(yml.read_text())
    sub_dir = src / "sub-agents"
    if sub_dir.exists():
        print(f"\n  {common.BOLD}Sub-agents{common.RESET}:\n")
        for p in sorted(sub_dir.iterdir()):
            if p.is_dir():
                soul = p / "SOUL.md"
                size = soul.stat().st_size if soul.exists() else 0
                print(f"    • {p.name} ({size} bytes)")
    print()


def cmd_status(args, *, home: Path, brand: str):
    print(f"\n  {common.BOLD}Factory status — {brand}{common.RESET}\n")
    enabled_count = 0
    for d in AVAILABLE_FACTORIES + PLANNED_FACTORIES:
        dst = _factory_dst(home, d)
        if dst.exists():
            marker = dst / ".enabled"
            ts = ""
            if marker.exists():
                try:
                    for line in marker.read_text().splitlines():
                        if line.startswith("enabled_at:"):
                            ts = line.split(":", 1)[1].strip()
                except Exception:
                    pass
            enabled_count += 1
            print(f"  {common.GREEN}✓{common.RESET} {d:<12} enabled  {common.DIM}{ts}{common.RESET}")
        elif d in AVAILABLE_FACTORIES:
            print(f"  {common.DIM}○{common.RESET} {d:<12} available but not enabled")
    print(f"\n  {enabled_count} factories enabled / {len(AVAILABLE_FACTORIES)} available / {len(PLANNED_FACTORIES)} planned\n")


def cmd_run_once(args, *, home: Path, brand: str):
    import json as _json
    from pathlib import Path as _Path
    from operai_init.factory_runtime import config as fc_cfg, orchestrator, trace as trace_mod

    dst = _factory_dst(home, args.domain)
    if not dst.exists():
        common.err(f"factory '{args.domain}' is not enabled. Run: operai-init factory enable --domain {args.domain}")
        return

    try:
        fc = fc_cfg.load(dst)
    except FileNotFoundError as e:
        common.err(str(e)); return
    issues = fc_cfg.validate(fc)
    if issues:
        common.warn("factory has issues:")
        for i in issues:
            print(f"   - {i}")

    input_path = _Path(args.input)
    if not input_path.exists():
        common.err(f"input not found: {input_path}"); return
    try:
        event = _json.loads(input_path.read_text())
    except _json.JSONDecodeError as e:
        common.err(f"input JSON parse error: {e}"); return

    common.banner(f"factory run-once · {args.domain} · {'MOCK' if args.mock_llm else 'LIVE'}")
    if not args.mock_llm:
        # Pre-flight: any providers configured?
        try:
            from operai_init.llm import config as llm_config
            configured = llm_config.list_configured(home)
            if not configured:
                common.err("no LLM providers configured. Run: operai-init llm configure  (or use --mock-llm)")
                return
        except ImportError:
            common.warn("llm module unavailable; falling back to mock")
            args.mock_llm = True

    result = orchestrator.run_once(fc, event, mock=args.mock_llm, limit=args.limit)

    if args.format == "json":
        body = trace_mod.to_json(result)
    else:
        body = trace_mod.to_markdown(result, event_label=input_path.stem)

    if args.output == "-":
        print(body)
    else:
        out_path = _Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(body)
        common.ok(f"trace written to {out_path}")

    # Summary to stderr so it shows even when output is piped
    import sys as _sys
    _sys.stderr.write(f"\n  {common.BOLD}Summary{common.RESET}: ok={result.ok} · sub-agents={len(result.sub_agent_trace)} · latency={result.total_latency_ms}ms · cost=${result.total_cost_usd:.6f} · action={result.final_action}\n")


def register(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("factory", help="Manage agent factories (parent + sub-agents)")
    inner = p.add_subparsers(dest="factory_action", required=True)

    sp = inner.add_parser("enable", help="Install a factory into /opt/operai/agents/<domain>/factory/")
    sp.add_argument("--domain", required=True, choices=AVAILABLE_FACTORIES + PLANNED_FACTORIES)
    sp.set_defaults(factory_func=cmd_enable)

    sp = inner.add_parser("disable", help="Remove a factory (audit-trailed)")
    sp.add_argument("--domain", required=True)
    sp.add_argument("--reason", required=True)
    sp.add_argument("--by")
    sp.set_defaults(factory_func=cmd_disable)

    sp = inner.add_parser("list", help="List available + planned factories")
    sp.set_defaults(factory_func=cmd_list)

    sp = inner.add_parser("show", help="Show factory config + sub-agent list")
    sp.add_argument("--domain", required=True)
    sp.set_defaults(factory_func=cmd_show)

    sp = inner.add_parser("status", help="Show enabled factories per brand")
    sp.set_defaults(factory_func=cmd_status)

    sp = inner.add_parser("run-once", help="Run the factory chain on a single event (v0.9.0 smoke test)")
    sp.add_argument("--domain", required=True, choices=AVAILABLE_FACTORIES)
    sp.add_argument("--input", required=True, help="Path to input event JSON")
    sp.add_argument("--output", default="-", help="Trace output path (default: stdout)")
    sp.add_argument("--format", choices=["markdown", "json"], default="markdown")
    sp.add_argument("--mock-llm", action="store_true", help="Use canned responses (no LLM calls)")
    sp.add_argument("--limit", type=int, help="Only run first N sub-agents (debugging)")
    sp.set_defaults(factory_func=cmd_run_once)
