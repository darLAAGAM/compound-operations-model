# Discovery Interview — The Founder Script

*Version: 0.1.0 · Used by `brain-bootstrap.py --interactive`*

This is the conversational script that seeds every new OperAI deployment. It is intentionally short — 25 answers, ~15 minutes. Everything here gets written to `/opt/operai/brain/knowledge/<brand>/discovery-interview.md` and becomes the first thing every agent reads on boot.

## Why these 25 questions (and not more)

We want the **minimum viable context** for the swarm to start being useful on day 1. Anything beyond this is better filled in by real data ingestion (Shopify, Klaviyo, Notion, Drive, Slack) than by asking the founder to type it.

The questions map onto three concerns:

| Concern | Count | Purpose |
|---|---|---|
| **Who are you** | 6 | brand identity for brand-voice decisions |
| **What is your scale** | 4 | calibrates thresholds (€100 refund is huge for 1M, noise for 50M) |
| **What runs your stack** | 9 | tells the MCP server which integrations to wire |
| **Where does it hurt** | 4 | picks the first automation + risk posture |
| **Who are you (legal)** | 3 | DPIA signatory + AI System Register owner |

## How the interview runs

The founder sees one question at a time, in bold, with a caret prompt. Blank answers are allowed — the field stays empty in the output doc and can be filled later by editing the file directly (QMD re-indexes on the next 5-min cron).

```
What is the biggest operational bottleneck right now? (one sentence)
  > manual ticket triage is eating 3h of Laura's day
```

## The full question set

See `brain-bootstrap.py` → `INTERVIEW` list. Each entry is `(key, prompt)`:

- `brand_legal_name` — Legal name (for invoices)
- `brand_display_name` — Public/marketing name
- `brand_website` — Primary URL
- `brand_founded_year` — Year founded
- `brand_category` — fashion / beauty / home / food / wellness / outdoor / pet / other
- `brand_hq_country` — ISO code
- `revenue_band` — <1M / 1-5M / 5-10M / 10-25M / 25-50M / 50M+
- `team_size` — Full-time headcount
- `channels` — DTC, retail, wholesale, marketplaces
- `physical_locations` — Count (0 if none)
- `ecom_platform` — shopify / shopify-plus / woocommerce / other
- `erp` — holded / quickbooks / xero / sap / none / other
- `helpdesk` — richpanel / zendesk / gorgias / freshdesk / none
- `email_platform` — klaviyo / mailchimp / sendgrid / other
- `inventory_system` — stockagile / cin7 / shopify-native / other
- `ads_platforms` — meta, google, pinterest, tiktok (comma-separated)
- `analytics` — ga4 / shopify / other
- `comms` — slack / teams / other
- `docs` — google-workspace / notion / confluence / other
- `biggest_op_bottleneck` — one sentence
- `first_automation` — one workflow
- `highest_risk_area` — area most sensitive to AI mistake
- `data_sensitivity` — special-category data? y/n
- `founder_name` — name
- `founder_email` — email
- `founder_role` — CEO / CTO / COO / …

## What the output looks like

See `brain-bootstrap.py → render_discovery_md()`. The doc has 5 sections:

1. Brand Fundamentals
2. Scale
3. Stack
4. Priorities + Risk
5. Data Controller (GDPR Art. 4)

## How this doc is used by the swarm

Every agent reads this doc through `brain_query("brand fundamentals")` or `brain_read("knowledge/<brand>/discovery-interview.md")` on session start. It is the first and most important input. Every other doc in the brain is contextualised against this one.

## Editing after the fact

The file is just markdown. Edit it, save it, wait ≤5 min for QMD to re-index. Everything downstream picks up the change automatically — no agents need to be restarted.

## When to re-run

Re-run `brain-bootstrap.py --interactive` (overwriting the previous file) when:

- The brand does a major pivot (new category, new geography)
- Revenue band changes (thresholds recalibrate)
- Stack swaps (ERP migration, new helpdesk)
- Ownership changes (new DPIA signatory)

Otherwise, edit in-place.
