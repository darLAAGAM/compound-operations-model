#!/usr/bin/env python3
"""
OperAI Brain Bootstrap — brain-bootstrap.py
Version: 0.1.0

Called by install.sh after the system layout is ready. Does three things:

  1. Discovery interview (walks the founder through ~25 Qs)
  2. Brain skeleton creation (writes initial docs to /opt/operai/brain/knowledge/<brand>/)
  3. QMD collection init (creates 6 collections + first `qmd update` pass)

Design choices:
  - All interview answers go to ONE file: <brand>/discovery-interview.md
  - The distillation into 6 contexts (retail/marketing/finance/...) happens LATER,
    once the brand has ingested real data (Notion/Drive/Shopify). We just seed the
    structure here so QMD has something to index from day one.
  - QMD collections: workspace, memory, <brand>, platform, personal, projects
    (mirrors the the reference Second Brain v1 layout documented 2026-04-17)

Usage:
    python3 brain-bootstrap.py --brand acme --home /opt/operai --interactive
"""
from __future__ import annotations
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import textwrap
from datetime import date
from pathlib import Path


# ─────────────────────────────────────────────────────────────────────────────
# Discovery interview questions
# ─────────────────────────────────────────────────────────────────────────────

INTERVIEW = [
    # ── brand fundamentals ──
    ("brand_legal_name",     "Legal name of the company (as it appears on invoices)"),
    ("brand_display_name",   "Public/marketing name of the brand"),
    ("brand_website",        "Primary website URL"),
    ("brand_founded_year",   "Year founded"),
    ("brand_category",       "Primary category (fashion / beauty / home / food / wellness / outdoor / pet / other)"),
    ("brand_hq_country",     "HQ country (ISO code: ES, US, FR, DE, …)"),

    # ── scale ──
    ("revenue_band",         "Revenue band (<1M / 1-5M / 5-10M / 10-25M / 25-50M / 50M+)"),
    ("team_size",            "Team size (full-time headcount)"),
    ("channels",             "Active sales channels (comma-separated: DTC, retail, wholesale, marketplaces)"),
    ("physical_locations",   "Number of physical retail locations (0 if none)"),

    # ── stack ──
    ("ecom_platform",        "E-commerce platform (shopify / shopify-plus / woocommerce / other)"),
    ("erp",                  "ERP / finance system (holded / quickbooks / xero / sap / none / other)"),
    ("helpdesk",             "Helpdesk / CS tool (richpanel / zendesk / gorgias / freshdesk / none)"),
    ("email_platform",       "Email/lifecycle platform (klaviyo / mailchimp / sendgrid / other)"),
    ("inventory_system",     "Inventory / WMS (stockagile / cin7 / shopify-native / other)"),
    ("ads_platforms",        "Active ad platforms (comma: meta, google, pinterest, tiktok)"),
    ("analytics",            "Analytics stack (ga4 / shopify / other)"),
    ("comms",                "Internal comms (slack / teams / other)"),
    ("docs",                 "Docs system (google-workspace / notion / confluence / other)"),

    # ── pain + priorities ──
    ("biggest_op_bottleneck","Biggest operational bottleneck right now (one sentence)"),
    ("first_automation",     "If OperAI could automate ONE workflow first, what would it be?"),
    ("highest_risk_area",    "Area with most financial/legal risk if an AI made a mistake"),
    ("data_sensitivity",     "Does the brand handle special-category data? (health, biometric, minors) y/n"),

    # ── founder ──
    ("founder_name",         "Your name (founder / data controller)"),
    ("founder_email",        "Your email (for DPIA + compliance sign-off)"),
    ("founder_role",         "Your role (CEO, CTO, COO, …)"),
]


# ─────────────────────────────────────────────────────────────────────────────
# Pretty output
# ─────────────────────────────────────────────────────────────────────────────

GOLD = "\033[38;5;179m"
BOLD = "\033[1m"
DIM  = "\033[2m"
RESET = "\033[0m"
GREEN = "\033[32m"
RED = "\033[31m"

def banner(msg):
    print("\n" + GOLD + BOLD + "── " + msg + " ──" + RESET + "\n")

def ok(msg):   print("  " + GREEN + "✓" + RESET + " " + msg)
def warn(msg): print("  " + GOLD  + "!" + RESET + " " + msg)
def err(msg):  print("  " + RED   + "✗" + RESET + " " + msg, file=sys.stderr)


# ─────────────────────────────────────────────────────────────────────────────
# Interview runner
# ─────────────────────────────────────────────────────────────────────────────

def run_interview(brand_slug):
    banner("Discovery interview · " + brand_slug)
    intro = (
        "The next ~25 questions shape the Brain that every agent will read from.\n"
        "You can leave an answer blank and fill it in later by editing\n"
        "/opt/operai/brain/knowledge/" + brand_slug + "/discovery-interview.md.\n\n"
        "Answers are stored locally on this VPS only. They never leave your server.\n"
    )
    print(intro)

    answers = {"brand_slug": brand_slug}
    for key, prompt in INTERVIEW:
        try:
            val = input(BOLD + prompt + RESET + "\n  > ").strip()
        except EOFError:
            val = ""
        answers[key] = val
    return answers


def render_discovery_md(answers):
    today = date.today().isoformat()
    brand = answers.get("brand_slug", "unknown")
    def a(key):
        return answers.get(key, "") or ""
    body = []
    body.append("# Discovery Interview — " + brand)
    body.append("")
    body.append("*Captured: " + today + " · Source: operai-init install.sh*")
    body.append("")
    body.append("This document is the ground-truth context for every agent in the swarm.")
    body.append("It is the first thing the MCP server hands to Claude when anyone asks")
    body.append("anything about the brand.")
    body.append("")
    body.append("---")
    body.append("")
    body.append("## Brand Fundamentals")
    body.append("")
    body.append("- **Legal name:** "    + a("brand_legal_name"))
    body.append("- **Display name:** "  + a("brand_display_name"))
    body.append("- **Website:** "       + a("brand_website"))
    body.append("- **Founded:** "       + a("brand_founded_year"))
    body.append("- **Category:** "      + a("brand_category"))
    body.append("- **HQ country:** "    + a("brand_hq_country"))
    body.append("")
    body.append("## Scale")
    body.append("")
    body.append("- **Revenue band:** "      + a("revenue_band"))
    body.append("- **Team size:** "         + a("team_size"))
    body.append("- **Channels:** "          + a("channels"))
    body.append("- **Physical locations:** "+ a("physical_locations"))
    body.append("")
    body.append("## Stack")
    body.append("")
    body.append("- **E-commerce:** "        + a("ecom_platform"))
    body.append("- **ERP / finance:** "     + a("erp"))
    body.append("- **Helpdesk:** "          + a("helpdesk"))
    body.append("- **Email / lifecycle:** " + a("email_platform"))
    body.append("- **Inventory / WMS:** "   + a("inventory_system"))
    body.append("- **Ads platforms:** "     + a("ads_platforms"))
    body.append("- **Analytics:** "         + a("analytics"))
    body.append("- **Internal comms:** "    + a("comms"))
    body.append("- **Docs:** "              + a("docs"))
    body.append("")
    body.append("## Priorities + Risk")
    body.append("")
    body.append("- **Biggest op bottleneck:** "    + a("biggest_op_bottleneck"))
    body.append("- **First workflow to automate:** " + a("first_automation"))
    body.append("- **Highest-risk area:** "        + a("highest_risk_area"))
    body.append("- **Special-category data:** "    + a("data_sensitivity"))
    body.append("")
    body.append("## Data Controller (GDPR Art. 4)")
    body.append("")
    body.append("- **Name:** "  + a("founder_name"))
    body.append("- **Email:** " + a("founder_email"))
    body.append("- **Role:** "  + a("founder_role"))
    body.append("")
    body.append("---")
    body.append("")
    body.append("## What happens next")
    body.append("")
    body.append("1. This file is indexed into the `" + brand + "` QMD collection within 5 min.")
    body.append("2. Agents read it on every session start via `brain_query(...)`.")
    body.append("3. When you connect integrations (Shopify, Klaviyo, GWS, Slack), ingest")
    body.append("   scripts write into sibling folders (product/, cs/, marketing/, etc.).")
    body.append("4. After 30 days of real data, run `operai-init distil` to generate the")
    body.append("   6 distilled contexts (retail, marketing, finance, product, cs, wholesale).")
    body.append("")
    body.append("## Editing this doc")
    body.append("")
    body.append("Edit freely. Every change is re-indexed on the next QMD cron (≤5 min).")
    body.append("If you want the change to propagate immediately: `qmd update`.")
    return "\n".join(body) + "\n"


# ─────────────────────────────────────────────────────────────────────────────
# Brain skeleton
# ─────────────────────────────────────────────────────────────────────────────

def seed_brain_skeleton(brand_slug, home, answers):
    banner("Seeding brain skeleton")
    brain = home / "brain"
    kb    = brain / "knowledge"
    bdir  = kb / brand_slug

    readme = []
    readme.append("# " + brand_slug + " Brain")
    readme.append("")
    readme.append("This is the shared knowledge base for every AI agent in the swarm.")
    readme.append("Auto-indexed by QMD 2.0.1 every 5 minutes into 6 collections:")
    readme.append("")
    readme.append("- `workspace` (this root)")
    readme.append("- `memory` (" + str(brain / "memory") + ")")
    readme.append("- `" + brand_slug + "` (" + str(bdir) + ")")
    readme.append("- `platform` (" + str(kb / "platform") + ")")
    readme.append("- `personal` (" + str(kb / "personal") + ")")
    readme.append("- `projects` (" + str(kb / "projects") + ")")
    readme.append("")
    readme.append("## Access")
    readme.append("- Agents: filesystem direct (they run on this VPS)")
    readme.append("- Claude (Desktop / Code): MCP server at mcp." + brand_slug + ".com")
    readme.append("- Humans: edit .md files directly — QMD will re-index")
    readme.append("")
    readme.append("## Rules")
    readme.append("1. Read before you write (use `brain_query`)")
    readme.append("2. Write in the correct folder")
    readme.append("3. Update, don't duplicate")
    readme.append("4. Document learnings via `/learn` skill")
    readme.append("")
    readme.append("Source: OperAI Brand Bootstrap v0.1.0 · usecompai.com")
    (brain / "README.md").write_text("\n".join(readme) + "\n")
    ok("brain/README.md")

    # Brand-scoped folders get a short index each
    folders = [
        ("context",   "Strategic context distilled per area (auto-generated after 30d)"),
        ("team",      "People: org chart, me.md profiles per employee"),
        ("product",   "Catalog, sizing, collections, materials"),
        ("ops",       "Shipping, returns, warehouse, 3PL"),
        ("retail",    "Physical stores, traffic, staffing"),
        ("marketing", "Campaigns, segments, SEO, ads"),
        ("finance",   "P&L rules, payment terms, tax posture"),
        ("cs",        "Tickets, policies, escalation paths"),
        ("wholesale", "B2B partners, corners, tradeshows"),
        ("strategy",  "Plans, expansion, pivots"),
    ]
    for folder, purpose in folders:
        p = bdir / folder / "_index.md"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("# " + brand_slug + " · " + folder + "\n\n*" + purpose + "*\n\nThis folder is empty until integrations are connected or the founder adds docs.\n")

    (bdir / "discovery-interview.md").write_text(render_discovery_md(answers))
    ok("knowledge/" + brand_slug + "/discovery-interview.md")

    (brain / "memory").mkdir(parents=True, exist_ok=True)
    (kb / "platform").mkdir(parents=True, exist_ok=True)
    (kb / "personal").mkdir(parents=True, exist_ok=True)
    (kb / "projects").mkdir(parents=True, exist_ok=True)

    (brain / "memory" / "_index.md").write_text(
        "# Memory — " + brand_slug + "\n\nDaily notes from agents live here. Auto-indexed.\n"
    )
    boot_note = []
    boot_note.append("# " + date.today().isoformat() + " — Brand bootstrap")
    boot_note.append("")
    boot_note.append("OperAI install.sh ran today for brand `" + brand_slug + "`.")
    boot_note.append("Founder: " + (answers.get("founder_name") or "unknown"))
    boot_note.append("First workflow to automate: " + (answers.get("first_automation") or "—"))
    boot_note.append("Biggest bottleneck: " + (answers.get("biggest_op_bottleneck") or "—"))
    (brain / "memory" / (date.today().isoformat() + "-bootstrap.md")).write_text("\n".join(boot_note) + "\n")
    ok("memory seeded")


# ─────────────────────────────────────────────────────────────────────────────
# QMD collections
# ─────────────────────────────────────────────────────────────────────────────

def init_qmd_collections(brand_slug, home):
    banner("Initialising QMD collections")
    brain = home / "brain"

    qmd_bin = shutil.which("qmd")
    if not qmd_bin:
        warn("qmd binary not found — skipping index init (install.sh should have installed it)")
        return

    collections = [
        ("workspace",    brain),
        ("memory",       brain / "memory"),
        (brand_slug,     brain / "knowledge" / brand_slug),
        ("platform",     brain / "knowledge" / "platform"),
        ("personal",     brain / "knowledge" / "personal"),
        ("projects",     brain / "knowledge" / "projects"),
    ]

    cfg = {
        "version": "2.0.1",
        "brand": brand_slug,
        "collections": [
            {"name": name, "path": str(path), "embeddings": True}
            for name, path in collections
        ],
        "index_interval_seconds": 300,
    }
    cfg_path = brain / ".qmd.json"
    cfg_path.write_text(json.dumps(cfg, indent=2))
    ok(".qmd.json written (" + str(len(collections)) + " collections)")

    try:
        subprocess.run(
            [qmd_bin, "update", "--config", str(cfg_path)],
            cwd=str(brain),
            check=False, timeout=120,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        ok("qmd update — initial index pass complete")
    except Exception as e:
        warn("qmd update failed: " + str(e) + " (will retry via cron)")


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--brand", required=True, help="Brand slug (lowercase)")
    ap.add_argument("--home",  default="/opt/operai", help="Install home")
    ap.add_argument("--interactive", action="store_true")
    ap.add_argument("--answers-file", help="JSON file with pre-filled answers (skip interview)")
    args = ap.parse_args()

    brand = args.brand
    home  = Path(args.home)

    if not re.match(r"^[a-z0-9][a-z0-9-]{1,30}$", brand):
        err("Invalid brand slug. Use lowercase, digits, hyphens (2-31 chars).")
        sys.exit(2)

    if not home.exists():
        err(str(home) + " does not exist. Run install.sh first.")
        sys.exit(2)

    if args.answers_file:
        answers = json.loads(Path(args.answers_file).read_text())
        answers.setdefault("brand_slug", brand)
    elif args.interactive:
        answers = run_interview(brand)
    else:
        answers = {"brand_slug": brand}

    seed_brain_skeleton(brand, home, answers)
    init_qmd_collections(brand, home)

    banner("Brain bootstrap complete")
    print("  Brain root: " + str(home / "brain"))
    print("  Discovery:  " + str(home / "brain" / "knowledge" / brand / "discovery-interview.md"))
    print("  Collections: 6 (workspace, memory, " + brand + ", platform, personal, projects)")
    print()


if __name__ == "__main__":
    main()
