# OperAI Brand Bootstrap (`init/`)

*Version: 0.1.0 · Part of the OperAI Implementation Kit · usecompai.com*

This is the `operai init` component of the kit. It is the one-command path from a blank Ubuntu VPS to a running OperAI swarm for a brand-new consumer brand.

## What this does

One command on a fresh Ubuntu 24.04 VPS:

```bash
curl -fsSL https://usecompai.com/init | bash
```

Produces, in ~30 minutes (automated) + ~30 minutes (founder clicks):

- `/opt/operai/` directory tree (brain, agents, services, logs, compliance)
- Python 3 + Node LTS + Docker + QMD 2.0.1 + cloudflared installed
- Brain seeded with **6 QMD collections** (workspace, memory, `<brand>`, platform, personal, projects)
- **Discovery interview** captured as the first brain doc
- **7 SOUL templates** interpolated with the brand name
- **8 systemd units** installed (7 agents + MCP server) — not started
- Compliance scaffold (DPIA + AI System Register + Annex III review) ready for founder signature
- QMD indexing cron every 5 min

## Files in this directory

| File | Role |
|---|---|
| `install.sh` | Main orchestrator — runs on the fresh VPS |
| `brain-bootstrap.py` | Discovery interview + brain skeleton + QMD init |
| `discovery.md` | Documentation of the interview question set |
| `soul-templates/*.SOUL.md.tmpl` | 7 agent SOULs (cs, finance, ops, marketing, merch, retail, hr) |
| `systemd-templates/*.service.tmpl` | 8 systemd units (7 agents + MCP server) |
| `compliance-scaffold/*.md` | DPIA + AI System Register + Annex III review, pre-filled with `@BRAND@` placeholder |
| `brain-skeleton/` | Reserved for future knowledge templates (playbooks, SOPs) |
| `mcp-server-template/` | Reserved for the lightweight MCP server shipped with v0.2 |

## What it does NOT do (by design)

These require founder participation — we don't pretend otherwise:

1. **OAuth handoffs** — Shopify, Klaviyo, Google Workspace, Slack all require the founder to click "Authorize". No workaround.
2. **Compliance signatures** — DPIA and AI System Register must be signed by the Data Controller (the founder) in person.
3. **Production activation** — Agents are installed but not started. Shadow mode review comes first.

## Stack assumptions (v0.1)

- **OS:** Ubuntu 24.04 LTS (Debian 12 probably works, untested)
- **Host:** Any VPS with 4GB+ RAM, 40GB+ disk, 2+ CPU (Hetzner CX22 or equivalent is fine)
- **Runtime:** systemd for agents (Linux-native; macOS launchd is a v1+ nice-to-have)
- **Network:** Cloudflare Tunnel for the MCP endpoint (no inbound ports required)

## The sequence

```
┌──────────────────────────────────────────────┐
│ 1. Founder spins up Ubuntu VPS (Hetzner,      │
│    Hetzner Cloud, DigitalOcean, etc.)        │
└─────────────┬────────────────────────────────┘
              ▼
┌──────────────────────────────────────────────┐
│ 2. Founder runs:                              │
│    curl -fsSL usecompai.com/init | bash       │
└─────────────┬────────────────────────────────┘
              ▼
┌──────────────────────────────────────────────┐
│ 3. install.sh:                                │
│    - installs deps                            │
│    - creates /opt/operai/                     │
│    - runs brain-bootstrap.py (interview)      │
│    - installs 8 systemd units                 │
│    - scaffolds compliance docs                │
└─────────────┬────────────────────────────────┘
              ▼
┌──────────────────────────────────────────────┐
│ 4. Founder completes (manual but guided):     │
│    - OAuth for each integration               │
│    - Cloudflare Tunnel setup                  │
│    - Signs DPIA + Register                    │
│    - Starts agents in shadow mode             │
└─────────────┬────────────────────────────────┘
              ▼
┌──────────────────────────────────────────────┐
│ 5. Team onboarding (1 copy-paste per human)   │
│    Generated team-join.sh from the VPS        │
└──────────────────────────────────────────────┘
```

## Extending the discovery interview

Edit `brain-bootstrap.py → INTERVIEW` list. Each entry is `(field_name, prompt)`. The renderer in `render_discovery_md()` automatically includes any new fields in the output under the appropriate section — add a section heading if you introduce a new concern area.

## Versioning

| Version | Date | Notes |
|---|---|---|
| 0.1.0 | 2026-04-17 | First cut — core bootstrap, 7 SOULs, 6 QMD collections, compliance scaffold |
| 0.2.0 | *planned* | OAuth connect flows (Shopify/Klaviyo/GWS/Slack) as `operai-init connect <name>` |
| 0.3.0 | *planned* | `operai-init distil` — auto-generate the 6 per-area contexts from 30 days of ingested data |
| 0.4.0 | *planned* | `operai-init tunnel` — automated Cloudflare Tunnel + DNS |

## Support

- Playbook: https://usecompai.com/playbook/
- Story: https://usecompai.com/story.html
- Live dashboard (reference brand): https://usecompai.com/live.html
- Contact: hello@usecompai.com
