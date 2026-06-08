"""operai-init setup-brand — interactive happy-path wizard.

Runs the full founder-facing setup flow in ONE command after `install.sh`.
Each step is skippable. The wizard prints clear progress + a final summary.

Flow:
  1. LLM providers (at least 1 required)
  2. CS factory enable (skippable)
  3. Cloudflare tunnel setup (assisted, optional)
  4. Webhook receivers (optional, one per helpdesk)
  5. Slack digest (optional)
  6. Governance layer (optional)
  7. Onboarding pack install
  8. Generate founder admin key (if not already present)
  9. Summary + next actions
"""
from __future__ import annotations
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

from operai_init import common


def _yesno(question: str, default: bool = True) -> bool:
    return common.confirm(question, default=default)


def cmd_setup_brand(args, *, home: Path, brand: str):
    common.banner(f"OperAI Setup Wizard · {brand}")
    print(f"""
  This wizard runs the post-install configuration in order. Each step is
  skippable. You can re-run any step independently later via the sub-commands.

  Home: {home}
  Brand: {brand}
""")

    # Step 1 — LLM providers
    _step_header("LLM providers", "Required before any agent runs")
    if _yesno("Configure LLM providers now?", default=True):
        subprocess.run(["/usr/local/bin/operai-init", "llm", "configure"])
    else:
        common.warn("Skipped. Agents will refuse to start without at least one provider.")

    # Step 2 — CS factory
    _step_header("CS agent factory", "10 specialized sub-agents for customer service")
    if _yesno("Enable the CS factory?", default=True):
        subprocess.run(["/usr/local/bin/operai-init", "factory", "enable", "--domain", "cs"])

    # Step 3 — Cloudflare tunnel
    _step_header("Cloudflare Tunnel", "Exposes MCP server + webhook receiver publicly")
    print("""
  You'll need a Cloudflare account. If you haven't logged in yet:
    cloudflared tunnel login
""")
    if _yesno("Set up tunnel for mcp.<brand>.com now?", default=False):
        subdomain = common.prompt("Subdomain for the MCP endpoint (e.g. mcp.acme.com)")
        if subdomain:
            subprocess.run(["/usr/local/bin/operai-init", "tunnel", subdomain])

    # Step 4 — Webhook receivers
    _step_header("Webhook receivers", "Helpdesks POST to your brand for autonomous ticket processing")
    providers_to_configure = []
    if _yesno("Configure any webhook receiver (Richpanel/Gorgias/Zendesk/Intercom)?", default=False):
        for p in ("richpanel", "gorgias", "zendesk", "intercom"):
            if _yesno(f"  Configure {p}?", default=False):
                providers_to_configure.append(p)
        for p in providers_to_configure:
            subprocess.run(["/usr/local/bin/operai-init", "webhook", "configure", p])

        endpoint = common.prompt("Webhook endpoint base URL (e.g. https://webhook.acme.com) — leave blank to skip").strip()
        if endpoint:
            subprocess.run(["/usr/local/bin/operai-init", "webhook", "set-endpoint", endpoint])

    # Step 5 — Slack digest
    _step_header("Slack daily digest", "One daily post summarizing review queue + escalations")
    if _yesno("Configure Slack digest now?", default=False):
        subprocess.run(["/usr/local/bin/operai-init", "digest", "configure"])
        if _yesno("Schedule daily digest at 08:00 UTC?", default=True):
            subprocess.run(["/usr/local/bin/operai-init", "digest", "schedule", "--hour", "8"])

    # Step 6 — Governance
    _step_header("Agentic governance", "3 meta-agents: critic + guardrail + compliance")
    if _yesno("Enable the governance layer?", default=True):
        subprocess.run(["/usr/local/bin/operai-init", "governance", "enable"])

    # Step 7 — Onboarding pack
    _step_header("Onboarding pack", "Skills + custom instruction + Notion templates for employees")
    founder_name = common.prompt("Founder name for templates (e.g. Diego) — used in interpolation").strip() or "the founder"
    subprocess.run(["/usr/local/bin/operai-init", "onboarding-pack", "install", "--founder", founder_name])

    # Step 8 — Admin key summary
    _step_header("API keys", "Check founder admin key exists + offer to create one for the founder")
    keys_path = home / "credentials" / "mcp-keys.json"
    have_admin = False
    if keys_path.exists():
        try:
            keys = json.loads(keys_path.read_text())
            have_admin = any(
                m.get("role") == "admin" and not m.get("revoked")
                for m in keys.values()
            )
        except Exception:
            pass
    if have_admin:
        common.ok("At least one admin key exists (generated during install.sh or earlier).")
    else:
        common.warn("No admin key detected. Creating one now.")
        subprocess.run(["/usr/local/bin/operai-init", "key", "create", "founder", "--role", "admin"])

    # Summary
    _step_header("Summary", "Setup complete")
    print(f"""
  {common.BOLD}Next actions{common.RESET}:

    1. Start the core services:
       systemctl enable --now operai-mcp
       systemctl enable --now operai-factory-runtime
       systemctl enable --now operai-webhook   (if webhooks configured)

    2. Verify everything:
       operai-init status

    3. Onboard your first team member:
       operai-init team-onboard <name> --role team --groups cs

    4. Check the onboarding pack:
       ls /opt/operai/onboarding/

    5. If you set up webhooks, configure each helpdesk with the receiver URL:
       operai-init webhook list   (shows the URLs)

  Documentation: https://usecompai.com/playbook/
""")


def _step_header(title: str, subtitle: str = "") -> None:
    print("\n" + common.GOLD + common.BOLD + "┌─ " + title + common.RESET)
    if subtitle:
        print("  " + common.DIM + subtitle + common.RESET)
    print("")


def register(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("setup-brand", help="Interactive post-install wizard (LLM, factory, tunnel, webhooks, digest, governance, onboarding)")
    p.set_defaults(setup_func=cmd_setup_brand)
