"""governance — install + manage the three meta-agents (critic, guardrail, compliance).

Scope (v0.5):
  enable   — install SOULs + systemd units, create config scaffold
  status   — show meta-agent service states + recent verdict counts
  logs     — tail one of the three logs
  review   — list pending compliance amendments
  disable  — stop + disable all three (with audit trail)
"""
from __future__ import annotations
import argparse
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from operai_init import common


META_AGENTS = ["critic", "guardrail", "compliance"]


def _soul_src(home: Path) -> Path:
    return home / "services" / "init" / "governance" / "soul-templates"


def _systemd_src(home: Path) -> Path:
    return home / "services" / "init" / "governance" / "systemd-templates"


def _interpolate(text: str, brand: str, home: Path) -> str:
    return (text
            .replace("@BRAND@", brand)
            .replace("@BRAND_DISPLAY@", brand.title())
            .replace("@HOME@", str(home))
            .replace("@USER@", "operai")
            .replace("@THRESHOLD@", "500"))


def cmd_enable(args, *, home: Path, brand: str):
    soul_src = _soul_src(home)
    sys_src  = _systemd_src(home)
    if not soul_src.exists():
        common.err(f"governance templates not found at {soul_src} — re-run install.sh")
        return

    common.banner("Enabling agentic governance (3 meta-agents)")

    # 1. Generate SOULs per agent
    for slug in META_AGENTS:
        src = soul_src / f"{slug}-agent.SOUL.md.tmpl"
        dst_dir = home / "agents" / slug
        dst_dir.mkdir(parents=True, exist_ok=True)
        dst = dst_dir / "SOUL.md"
        dst.write_text(_interpolate(src.read_text(), brand, home))
        common.ok(f"SOUL written: {dst}")

    # 2. Install systemd units
    for slug in META_AGENTS:
        src = sys_src / f"operai-{slug}.service.tmpl"
        unit_dst = Path(f"/etc/systemd/system/operai-{slug}.service")
        try:
            unit_dst.write_text(_interpolate(src.read_text(), brand, home))
        except PermissionError:
            common.err(f"need root to write {unit_dst} — run with sudo")
            return
        common.ok(f"systemd unit: {unit_dst}")

    # 3. Reload systemd
    try:
        subprocess.run(["systemctl", "daemon-reload"], check=True)
        common.ok("systemctl daemon-reload")
    except (FileNotFoundError, subprocess.CalledProcessError) as e:
        common.warn(f"systemctl reload skipped: {e}")

    # 4. Create memory folders
    for slug in META_AGENTS:
        (home / "brain" / "memory" / slug).mkdir(parents=True, exist_ok=True)
    common.ok("memory folders ready")

    # 5. Compliance sources default
    sources_path = home / "brain" / "knowledge" / brand / "compliance" / "sources.yml"
    sources_path.parent.mkdir(parents=True, exist_ok=True)
    if not sources_path.exists():
        sources_path.write_text(_DEFAULT_SOURCES)
        common.ok(f"compliance sources seeded: {sources_path}")

    print(f"""
{common.BOLD}Next:{common.RESET}
  systemctl enable --now operai-critic
  systemctl enable --now operai-guardrail
  systemctl enable --now operai-compliance

  # Then:
  operai-init governance status
""")


def cmd_status(args, *, home: Path, brand: str):
    print(f"\n  {common.BOLD}Governance — {brand}{common.RESET}\n")
    for slug in META_AGENTS:
        state = _service_state(f"operai-{slug}")
        log = home / "logs" / f"{slug}.log"
        last = "—"
        if log.exists():
            try:
                mtime = datetime.fromtimestamp(log.stat().st_mtime, tz=timezone.utc)
                last = mtime.strftime("%Y-%m-%d %H:%M")
            except Exception:
                pass
        print(f"  {slug:<12} state={state:<12} last-activity={last}")

    # Recent verdict counts
    mem = home / "brain" / "memory"
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    for slug in META_AGENTS:
        log_today = mem / slug / f"{today}.log"
        if log_today.exists():
            n = sum(1 for _ in log_today.read_text(errors="replace").splitlines() if _.strip())
            print(f"  {slug} verdicts today: {n}")
    print()


def cmd_logs(args, *, home: Path, brand: str):
    log = home / "logs" / f"{args.agent}.log"
    if not log.exists():
        common.warn(f"no log yet at {log}")
        return
    text = log.read_text(errors="replace")
    print(text[-4000:] if len(text) > 4000 else text)


def cmd_review(args, *, home: Path, brand: str):
    pending_dir = home / "compliance" / "pending"
    if not pending_dir.exists() or not any(pending_dir.iterdir()):
        common.info("no pending compliance amendments")
        return
    for p in sorted(pending_dir.iterdir()):
        if p.is_file() and p.suffix == ".md":
            print(f"\n  {common.BOLD}{p.name}{common.RESET}")
            print(f"  {p.stat().st_size} bytes · {datetime.fromtimestamp(p.stat().st_mtime).isoformat()}")


def cmd_disable(args, *, home: Path, brand: str):
    if not args.reason:
        common.err("--reason required for audit trail")
        return
    common.banner("Disabling governance")
    for slug in META_AGENTS:
        try:
            subprocess.run(["systemctl", "disable", "--now", f"operai-{slug}"], check=False, timeout=10)
            common.ok(f"disabled operai-{slug}")
        except Exception as e:
            common.warn(f"could not disable operai-{slug}: {e}")
    audit = home / "brain" / "audit" / "governance.log"
    audit.parent.mkdir(parents=True, exist_ok=True)
    with audit.open("a") as f:
        f.write(f"{datetime.now(timezone.utc).isoformat()}\tdisable\t{args.by or 'unknown'}\t{args.reason}\n")
    common.ok(f"audit trail: {audit}")


def _service_state(unit: str) -> str:
    try:
        out = subprocess.run(["systemctl", "is-active", unit], capture_output=True, text=True, timeout=5)
        return out.stdout.strip() or "unknown"
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return "unavailable"


_DEFAULT_SOURCES = """# Compliance Agent source list
# Weekly Monday 07:00 UTC scan. Edit freely.

sources:
  - id: eur-lex-ai-act
    name: EUR-Lex — AI Act (Reg. 2024/1689)
    url: https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32024R1689
    scope: [ai-act]
  - id: aepd
    name: AEPD — Agencia Española de Protección de Datos
    url: https://www.aepd.es/informes-y-resoluciones
    scope: [gdpr, ai-agentic]
  - id: edpb
    name: EDPB — European Data Protection Board
    url: https://www.edpb.europa.eu/news/news_en
    scope: [gdpr]
  - id: cnil
    name: CNIL — France
    url: https://www.cnil.fr/en/news
    scope: [gdpr, ai]
  - id: anthropic-changelog
    name: Anthropic — Model + Policy Changes
    url: https://www.anthropic.com/news
    scope: [llm-provider]
  - id: shopify-privacy
    name: Shopify — Privacy & Trust
    url: https://www.shopify.com/legal/privacy
    scope: [data-processor]
"""


def register(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("governance", help="Manage the 3 meta-agents (critic, guardrail, compliance)")
    inner = p.add_subparsers(dest="gov_action", required=True)

    sp = inner.add_parser("enable", help="Install SOULs + systemd units + config scaffold")
    sp.set_defaults(gov_func=cmd_enable)

    sp = inner.add_parser("status", help="Service state + verdict counts")
    sp.set_defaults(gov_func=cmd_status)

    sp = inner.add_parser("logs", help="Tail one meta-agent's log")
    sp.add_argument("--agent", choices=META_AGENTS, default="critic")
    sp.set_defaults(gov_func=cmd_logs)

    sp = inner.add_parser("review", help="List pending compliance amendments")
    sp.set_defaults(gov_func=cmd_review)

    sp = inner.add_parser("disable", help="Disable all 3 meta-agents (audit trail required)")
    sp.add_argument("--reason", required=True)
    sp.add_argument("--by")
    sp.set_defaults(gov_func=cmd_disable)
