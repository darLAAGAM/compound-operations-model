"""status — health check for a deployed swarm.

Reports:
  - integrations connected (from /opt/operai/credentials/index.json)
  - systemd units state (systemctl is-active <unit>)
  - brain stats (doc count, last QMD index, last memory note)
  - tunnel (if configured)
"""
from __future__ import annotations
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from operai_init import common


AGENT_UNITS = [
    "operai-mcp",
    "operai-cs", "operai-finance", "operai-ops", "operai-marketing",
    "operai-merch", "operai-retail", "operai-hr",
    "operai-tunnel",
]


def _integrations(home: Path) -> dict:
    idx = home / "credentials" / "index.json"
    if not idx.exists():
        return {}
    try:
        return json.loads(idx.read_text())
    except json.JSONDecodeError:
        return {}


def _service_state(unit: str) -> str:
    try:
        out = subprocess.run(
            ["systemctl", "is-active", unit],
            capture_output=True, text=True, timeout=5,
        )
        return out.stdout.strip() or "unknown"
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return "unreachable"


def _brain_stats(home: Path) -> dict:
    brain = home / "brain"
    if not brain.exists():
        return {"doc_count": 0, "qmd_config": False}
    docs = sum(1 for _ in brain.rglob("*.md"))
    qmd_cfg = brain / ".qmd.json"
    return {
        "doc_count":   docs,
        "qmd_config":  qmd_cfg.exists(),
        "memory_notes": sum(1 for _ in (brain / "memory").glob("*.md")) if (brain / "memory").exists() else 0,
    }


def _tunnel(home: Path) -> dict | None:
    p = home / "services" / "tunnel.json"
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text())
    except json.JSONDecodeError:
        return None


def _last_qmd_run(home: Path) -> str:
    log = home / "logs" / "qmd.log"
    if not log.exists():
        return "never"
    try:
        mtime = datetime.fromtimestamp(log.stat().st_mtime, tz=timezone.utc)
        return mtime.isoformat()
    except OSError:
        return "unknown"


def _compliance(home: Path) -> dict:
    cdir = home / "compliance"
    if not cdir.exists():
        return {"present": False}
    return {
        "present":   True,
        "dpia":      (cdir / "dpia.md").exists(),
        "register":  (cdir / "ai-system-register.md").exists(),
        "annex_iii": (cdir / "annex-iii-review.md").exists(),
    }




def _llm_config(home: Path) -> dict:
    try:
        from operai_init.llm import config as llm_config
        providers = llm_config.list_configured(home)
        default = llm_config.get_default(home)
        return {
            "configured_providers": providers,
            "default": default,
            "ready": bool(providers and default),
        }
    except Exception as e:
        return {"error": str(e), "ready": False}

def build_report(home: Path, brand: str) -> dict:
    integrations = _integrations(home)
    return {
        "brand":        brand,
        "home":         str(home),
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "integrations": {
            svc: {"status": meta.get("status", "unknown"), "updated_at": meta.get("updated_at")}
            for svc, meta in integrations.items()
        },
        "services": {unit: _service_state(unit) for unit in AGENT_UNITS},
        "brain":        _brain_stats(home),
        "tunnel":       _tunnel(home),
        "qmd_last_run": _last_qmd_run(home),
        "llm":          _llm_config(home),
        "compliance":   _compliance(home),
    }


def _pretty(report: dict) -> None:
    print(f"\n{common.BOLD}OperAI status — {report['brand']}{common.RESET}")
    print(f"  {common.DIM}generated {report['generated_at']}{common.RESET}")
    print(f"  {common.DIM}home {report['home']}{common.RESET}")

    print(f"\n{common.BOLD}Integrations{common.RESET}")
    if not report["integrations"]:
        print(f"  {common.DIM}none connected yet — run `operai-init connect <service>`{common.RESET}")
    else:
        for svc, meta in report["integrations"].items():
            symbol = common.GREEN + "✓" if meta["status"] == "connected" else common.GOLD + "!"
            print(f"  {symbol}{common.RESET} {svc:<20} {common.DIM}{meta.get('updated_at','')}{common.RESET}")

    print(f"\n{common.BOLD}Services (systemd){common.RESET}")
    for unit, state in report["services"].items():
        if state == "active":
            color = common.GREEN + "✓"
        elif state in ("inactive", "dead"):
            color = common.DIM + "○"
        elif state == "failed":
            color = common.RED + "✗"
        else:
            color = common.GOLD + "?"
        print(f"  {color}{common.RESET} {unit:<22} {common.DIM}{state}{common.RESET}")

    print(f"\n{common.BOLD}Brain{common.RESET}")
    b = report["brain"]
    qmd = "yes" if b["qmd_config"] else "no"
    print(f"  docs indexed: {b['doc_count']} · memory notes: {b.get('memory_notes',0)} · QMD config: {qmd}")
    print(f"  QMD last run: {report['qmd_last_run']}")

    # LLM section
    print(f"\n{common.BOLD}LLM providers{common.RESET}")
    l = report.get("llm") or {}
    if l.get("error"):
        print(f"  {common.RED}✗{common.RESET} error: {l.get("error")}")
    elif not l.get("configured_providers"):
        print(f"  {common.RED}✗{common.RESET} no providers configured — agents will refuse to start. Run: {common.BOLD}operai-init llm configure{common.RESET}")
    else:
        provs = ",".join(l["configured_providers"])
        dft = l.get("default")
        dft_s = (dft.get("provider", "?") + "/" + dft.get("model", "?")) if dft else (common.RED + "NOT SET" + common.RESET)
        print(f"  configured: {provs}")
        print(f"  default:    {dft_s}")

    t = report["tunnel"]
    print(f"\n{common.BOLD}Tunnel{common.RESET}")
    if t:
        print(f"  {t['subdomain']} → 127.0.0.1:{t['port']} (tunnel {t['tunnel_name']})")
    else:
        print(f"  {common.DIM}not configured — run `operai-init tunnel <subdomain>`{common.RESET}")

    print(f"\n{common.BOLD}Compliance{common.RESET}")
    c = report["compliance"]
    if not c.get("present"):
        print(f"  {common.RED}✗{common.RESET} compliance folder missing")
    else:
        for key, label in [("dpia", "DPIA"), ("register", "AI System Register"), ("annex_iii", "Annex III review")]:
            mark = common.GREEN + "✓" if c.get(key) else common.RED + "✗"
            print(f"  {mark}{common.RESET} {label}")
    print()


def run(*, home: Path, brand: str, json_out: bool = False) -> None:
    report = build_report(home, brand)
    if json_out:
        print(json.dumps(report, indent=2))
    else:
        _pretty(report)
