# Chapter 11e: Brand Bootstrap — From Zero to Swarm in One Command

> **Appendix · Technical depth.** This chapter is for operators or engineers deploying the brain themselves. It covers implementation details that aren't needed for understanding the conceptual architecture. Skip if you're reading for strategy.

## The Motivating Question

Every reader who makes it to this chapter has been wondering the same thing: *"OK, the architecture makes sense. The agents make sense. The compliance package makes sense. But what does it actually look like to deploy this for my brand?"*

For the first 12 months of Compai-inside-the-original-brand, the answer was: a 30-day activation path, a technical operator, and a lot of copy-paste. That path is documented end-to-end in the repo and it works — but it is not one command.

As of April 2026, it is.

```bash
curl -fsSL https://usecompai.com/init | bash
```

This chapter documents what that command does, what it does not do, and why the things it does not do are intentionally manual.

## What `curl | bash` does

On a fresh Ubuntu 24.04 VPS with 4GB RAM and 2 cores, the script runs for ~30 minutes unattended plus ~30 minutes of founder interaction. At the end, you have:

| Component | State after install |
|---|---|
| `/opt/operai/` directory tree | created, owned by the `Compai` system user |
| Python 3, Node LTS, Docker, QMD 2.0.1, cloudflared | installed |
| Brain with 6 QMD collections | seeded, first `qmd update` complete |
| Discovery interview | captured as `knowledge/<brand>/discovery-interview.md` |
| 7 agent SOUL templates | interpolated with the brand name |
| 8 systemd units | installed (7 agents + MCP server), **not started** |
| Compliance scaffold | pre-filled DPIA + AI System Register + Annex III review, awaiting signature |
| QMD indexing cron | scheduled every 5 minutes |

## The five phases of the bootstrap

### Phase 1 — System dependencies (automated, ~5 min)

The script installs Python 3, Node LTS, Docker, `cloudflared`, `qmd`, and system utilities. It detects Ubuntu/Debian and fails explicitly on anything else; v0.1 does not attempt to support other distros.

### Phase 2 — Filesystem layout (automated, <30 sec)

A non-privileged `Compai` system user owns `/opt/operai/`. The tree is:

```
/opt/operai/
├── agents/          (7 subfolders, one per agent)
├── brain/
│   ├── knowledge/
│   │   ├── <brand>/         (discovery + 10 domain folders)
│   │   ├── platform/        (infra docs)
│   │   ├── personal/        (founder personal context)
│   │   └── projects/        (active initiatives)
│   ├── memory/              (daily agent notes)
│   └──.qmd.json            (collection config)
├── services/
│   ├── mcp/                 (MCP server)
│   └── qmd/                 (indexer)
├── credentials/             (mode 700, outside prompts)
├── logs/
├── backups/
└── compliance/              (DPIA, AI System Register, Annex III)
```

### Phase 3 — Discovery interview (interactive, ~15 min)

This is the only part of the bootstrap where the founder types. The script asks 25 questions and writes the answers to `knowledge/<brand>/discovery-interview.md`. Example session:

```
── Discovery interview · nuvo ──

Legal name of the company (as it appears on invoices)
  > Nuvo Beauty SL

Public/marketing name of the brand
  > Nuvo

[...24 more questions...]

Biggest operational bottleneck right now (one sentence)
  > manual ticket triage eats 3h of a team member's day, every day
```

The interview has five sections: brand fundamentals, scale, stack, priorities + risk, data controller. The full question set is documented in `init/discovery.md` inside the repo. The rationale: we want the **minimum viable context** for the swarm to be useful on day one, and nothing more. Everything else is better filled in by real data ingestion than by typing.

Answers stay on the VPS. They never leave the server.

### Phase 4 — QMD bootstrap (automated, ~5 min)

Six collections get created:

| Collection | Path | Purpose |
|---|---|---|
| `workspace` | `/opt/operai/brain` | Everything — the catch-all |
| `memory` | `/opt/operai/brain/memory` | Daily agent notes |
| `<brand>` | `/opt/operai/brain/knowledge/<brand>` | Brand-scoped ground truth |
| `platform` | `/opt/operai/brain/knowledge/platform` | Infrastructure docs |
| `personal` | `/opt/operai/brain/knowledge/personal` | Founder personal context |
| `projects` | `/opt/operai/brain/knowledge/projects` | Active initiatives |

The initial `qmd update` pass indexes the ~12 seed docs in <1 minute. The `qmd embed` pass runs in the background and typically completes in ~30 minutes on a 2-core VPS (CPU-bound; no GPU required). A cron runs `qmd update` every 5 minutes after that, so any file you drop into the brain is searchable within 5 min — no restart, no rebuild.

### Phase 5 — Services installation (automated, <1 min)

Eight systemd units get installed but not enabled. Starting them is a deliberate founder action, not something the bootstrap does autonomously. Shadow mode first, always.

```bash
# After review:
systemctl enable --now operai-mcp
systemctl start operai-cs    # one agent at a time
tail -f /opt/operai/logs/cs.log
```

## What the bootstrap does NOT do (and why)

Three things require founder participation. The bootstrap refuses to automate them.

### 1. Integration tokens (`operai-init connect`)

Shopify, Klaviyo, Google Workspace, Slack — every integration requires the founder to generate a token in the platform's UI. There is no legal or technical shortcut. Post-install, the founder runs:

```bash
operai-init connect shopify            # Custom App + Admin API access token
operai-init connect klaviyo            # Private API key
operai-init connect google-workspace   # Service account JSON + domain-wide delegation
operai-init connect slack              # Bot User OAuth token
```

Each command:

- **Guides** the founder step-by-step through the platform's UI (where to click, which scopes to grant)
- **Reads the token** with hidden input (never echoed to terminal, never written to shell history)
- **Verifies** the token against a test API call before saving
- **Writes** to `/opt/operai/credentials/<service>.json` with mode 600, owned by the `Compai` user
- **Updates** `/opt/operai/credentials/index.json` so `operai-init status` can report connection health

Recommended scopes shipped with the repo are read-only where possible — e.g. Shopify gets `read_products`, `read_orders`, `read_customers`, `read_inventory` (no `write_` scopes until the founder explicitly enables writes for a specific agent). This keeps the blast radius minimal during the shadow-mode review period.

Each command takes 2-5 minutes including platform UI navigation. Tokens never appear in prompts, environment variables, or logs.

### 2. Compliance signatures

Under GDPR Article 4, the founder is the Data Controller. The DPIA and AI System Register (both required by the EU AI Act from August 2026) must be signed by the Data Controller personally. The bootstrap pre-fills the templates with the brand name, stack, and discovery answers — but the signature box stays blank until the founder completes it. Agents refuse to write to production systems before those signatures are on file.

### 3. Production activation

systemd units are installed, not started. The founder chooses when each agent goes live, and in what mode (shadow / review / autonomous). The default posture is: CS agent in shadow mode for 2 weeks, reviewing every draft against human replies before any draft ships to a real customer. Ditto for every other agent.

## The team onboarding layer

Once the swarm is running, every employee gets connected with one command too. After the founder has exposed the MCP server via Cloudflare Tunnel at `mcp.<brand>.com/sse`, each employee pastes this into their terminal (Mac) or PowerShell (Windows):

```bash
curl -fsSL 'https://usecompai.com/team-join?brand=<brand>&mcp=mcp.<brand>.com' | bash
```

That command:

- Detects the employee's OS (Mac / Linux / Windows-with-git-bash)
- Installs Node LTS via `fnm` if missing (no sudo required)
- Writes `claude_desktop_config.json` pointing at the brand's MCP endpoint
- Backs up any existing config
- Pre-caches `mcp-remote` on first run

The employee quits Claude Desktop, reopens it, and sees the brand's tools available. No API keys on their machine. No VPN. No training.

If you prefer not to use the hosted endpoint, `operai-init team-join --out team-join.sh` generates the same script locally on the VPS (with the MCP URL auto-detected from the tunnel config). You can then distribute that file through your own channel (Slack, email, internal wiki).



## Phase 6 — Operations CLI (`operai-init status` and friends)

Once the swarm is running, the `operai-init` CLI provides the ongoing operational surface:

| Command | What it does |
|---|---|
| `operai-init status` | Shows integration connection status, systemd state of all 8 services, brain doc count + QMD last index, tunnel config, compliance file presence. Use JSON mode (`--json`) for monitoring pipelines. |
| `operai-init connect <service>` | Re-auth an integration — same flow as install, but with `--force` to overwrite an expired token without prompting. |
| `operai-init tunnel <subdomain>` | Create the Cloudflare Tunnel + systemd unit + DNS route in one shot. Assumes `cloudflared tunnel login` was run once; idempotent if the tunnel already exists. |
| `operai-init team-join --out team-join.sh` | Regenerate the team onboarding script with the current MCP URL baked in. |
| `operai-init distil` | Planned v0.3 — auto-generate the 6 per-area contexts after 30 days of ingested data. |

The CLI is a standard Python package installed to `/usr/local/bin/operai-init` with its dependencies in `/opt/operai/services/init/cli/`. It has no external dependencies beyond the Python standard library — everything it talks to (Shopify, Klaviyo, Google, Slack, Cloudflare) goes through `urllib` or `subprocess` calls to platform CLIs.



## Phase 7 — The MCP server (what makes it usable)

The bootstrap installs a production-grade MCP server at `/opt/operai/services/mcp/` and exposes it through the Cloudflare Tunnel from Phase 6. Without this, the swarm is a directory tree. With this, the swarm is a running system that Claude Desktop (and any MCP client) can talk to.

### What's in the server

A ~500-line Python package (Starlette + SSE + the official `mcp` SDK) that exposes 11 tools:

| Tool | Role | What it does |
|---|---|---|
| `brain_query` | team | Hybrid search over the 6 QMD collections |
| `brain_read` | team | Read a specific doc from the brain |
| `brain_list` | team | List files/folders at a path |
| `brain_write` | admin | Create/update a brain doc (audited to `brain/memory/brain-writes.log`) |
| `memory_write` | team | Append a note to today's memory file |
| `me_read` | team | Read a me.md personal profile (or list all) |
| `me_write` | team | Write your own me.md; admins can write anyone's |
| `status` | team | Health check — integrations, services, brain, tunnel, compliance |
| `shopify_query` | team | Shopify Admin API passthrough (read scopes only by default) |
| `klaviyo_query` | team | Klaviyo API passthrough |
| `slack_send_message` | admin | Post to Slack (admin-gated to prevent accidental mass-send) |

Each tool declares a minimum role (`team` or `admin`). The server enforces the role check before dispatching the tool handler.

### Auth model

Every request to `/sse` must carry:

```
Authorization: Bearer lgm_<32 hex>
```

Keys live in `/opt/operai/credentials/mcp-keys.json` (mode 600), managed by:

```bash
operai-init key create <name> --role admin|team   # generates lgm_<32 hex>, prints once
operai-init key list                              # shows name + role + last seen (tokens masked)
operai-init key revoke <name>                     # soft-revoke (audit trail preserved)
```

The first admin key is **auto-generated by install.sh** during bootstrap — the founder copies it from the install log. That key is the one used for their own Claude Desktop config. Additional keys (one per employee) are created afterwards with `operai-init key create <name> --role team`.

### What the team-join script does with the key

The v0.3 team-join script (generated by `operai-init team-join` or fetched from `usecompai.com/team-join?brand=X&mcp=Y`) prompts the employee for their key and writes a Claude Desktop config like:

```json
{
  "mcpServers": {
    "<brand>": {
      "command": "npx",
      "args": ["mcp-remote", "https://mcp.<brand>.com/sse",
               "--header", "Authorization:Bearer ${OPERAI_KEY}"],
      "env": { "OPERAI_KEY": "lgm_..." }
    }
  }
}
```

The key never appears in a URL, never in shell history (`read -r`, not `curl ?key=`), and stays scoped to one employee — revokable individually without affecting anyone else.

### What the server does NOT do (v0.3)

- No rate limiting per key (add nginx or Cloudflare Workers for production traffic)
- No tool-level audit log beyond the brain_write trail (planned v0.4)
- No websocket or Streamable HTTP transport (SSE only; `mcp-remote` handles translation for Claude Desktop)
- No secret-rotation automation (operators rotate by `revoke` + `create`)


## What changes on day 30

The bootstrap seeds the brain skeleton. Real data fills it in over the following weeks, from three sources:

- **Ingest scripts** pull historical data: Shopify catalog, Klaviyo subscribers, Notion workspace export, Google Drive shared folders, Slack public channels (last 90 days)
- **Agent memory writes** accumulate daily: every agent writes short notes to `brain/memory/YYYY-MM-DD-<agent>.md` summarising what it did, what it flagged, what it escalated
- **Human edits** — the founder and team members add docs directly to the brain when they realise the agents need context (policies, decisions, answers to FAQs)

After 30 days, run:

```bash
operai-init distil
```

This fires six parallel subagents that read the brand's collection and produce distilled 15-20KB context documents per area (retail, marketing, finance, product, CS, wholesale). Those become the new top of the context hierarchy — any new agent session starts there and drills down.

The pattern mirrors how the original brand did it: at 968 docs in the brain, reading everything was no longer practical. The distilled contexts give new agents 80% of the operational context in 30 minutes of reading, regardless of how deep the underlying corpus has grown.

## Versioning and what's next

| Version | Status | Notes |
|---|---|---|
| 0.1.0 | ✅ Shipped | Core bootstrap, 7 SOULs, 6 QMD collections, compliance scaffold |
| 0.2.0 | ✅ Shipped | `operai-init connect` (Shopify / Klaviyo / GWS / Slack), `tunnel`, `team-join`, `status` |
| 0.3.0 | ✅ Shipped | Production MCP server with 11 tools + API key auth + role-based access + `operai-init key` |
| 0.4.0 | Planned | `operai-init ingest` for historical data pulls (Notion export, Drive, Slack 90d) |
| 0.5.0 | Planned | `operai-init distil` for auto-generating 6 per-area contexts after 30d |

The end state: a founder with no prior swarm experience can go from purchase to their first working agent in a single afternoon. The 30-day activation path documented earlier in this repo remains the reference implementation; `Compai init` is the compressed, opinionated path for brands that want the defaults we learned the hard way.

## Where to look next

- The repo's `init/` directory has the full source: `install.sh`, `brain-bootstrap.py`, the SOUL templates, the systemd units, and the compliance scaffold
- The discovery interview question set and rationale: `init/discovery.md`
- The brain architecture this bootstraps: Chapter 10b (Memory Architecture) + Chapter 10c (MCP Server)
- The compliance package that ships pre-filled: Chapter 11d (EU AI Act Compliance)

---

→ Next: [Chapter 12 — ROI Analysis](12-roi.md)
