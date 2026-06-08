# OperAI Implementation Kit v3.1.1

This kit is the software-first deployment pack for building a multi-agent operating system inside a consumer brand.

It is not a prompt bundle. It is the asset layer that turns the free playbook into a real deployment.

## What This Kit Is For

- consumer, lifestyle, and retail brands
- teams with a technical operator
- staged rollout from documentation to production
- EU-based operators who need day-one AI Act compliance

## Start Here

**New brand deploying from scratch?** Run the one-command bootstrap instead:

```bash
curl -fsSL https://usecompai.com/init | bash
```

It does steps 1-6 below automatically. Jump to playbook Ch.11e for details.

**Existing brand or manual deploy?**

1. Read `deployment/prerequisites.md`
2. Read `deployment/reference-architecture.md`
3. Read `deployment/deployment-contract.md`
4. Read `knowledge-base/eu-ai-act-guardrails.md` **(new in v2.0 — read before wiring any agent to production data)**
5. Follow `deployment/activation-path.md`
6. Then execute `deployment/30-day-calendar.md`

## Core Contents (96 files)

- `templates/` — production templates for seven domain agents + OpenClaw launchd plists
- `scripts/` — operations, cron, and monitoring scripts
- `integrations/` — platform setup guides
- `deployment/` — rollout docs and activation path
- `patterns/` — reusable operational patterns
- `knowledge-base/` — security, compliance, and autonomy docs (8 files)
- `memory-architecture/` — shared brain scaffolding

## New in v2.8 (multi-LLM provider abstraction)

Zero vendor lock-in. Every LLM call in the swarm flows through one unified client that speaks to **5 providers** today with zero external dependencies (stdlib urllib only).

**Providers shipped:**
- Anthropic (haiku-4.5, sonnet-4.5, opus-4.7)
- OpenAI (gpt-4o-mini, gpt-4o, gpt-5-mini, gpt-5)
- Google Gemini (gemini-2.5-flash, gemini-2.5-pro)
- Alibaba Qwen (turbo, plus, max)
- MiniMax (m2.5, text01)

**Brand-owned keys:** OperAI never touches the brand's API keys. Each brand's keys live in `/opt/operai/credentials/llm-providers.json` (mode 600). The OperAI maintainer account is never used — every inference call bills the brand's own provider account.

**New CLI commands:**
```bash
operai-init llm configure                          # interactive setup for one/all providers
operai-init llm test anthropic                     # ping test with tiny prompt
operai-init llm set-default --provider anthropic --model haiku-4.5
operai-init llm fallback openai/gpt-4o-mini gemini/gemini-2.5-flash
operai-init llm usage --since 30                   # per-provider token + cost report
operai-init llm list                               # providers + configured status
operai-init llm remove anthropic                   # revoke credential
```

**Per-sub-agent routing** in `factory.yml`:
```yaml
default_llm:
  provider: anthropic
  model:    haiku-4.5
fallback_llm:
  - { provider: openai, model: gpt-4o-mini }
  - { provider: gemini, model: gemini-2.5-flash }
sub_agents:
  - name: triage
    llm: { provider: openai, model: gpt-4o-mini }    # fast + cheap
  - name: drafter
    llm: { provider: anthropic, model: sonnet-4.5 }  # quality customer copy
```

**Fallback chains:** if the primary provider returns 429 / 5xx / timeout, the runtime automatically tries the next entry. Brands get supply-chain resilience without writing retry logic.

**Pre-flight enforcement:** `operai-init status` now shows an LLM section. Without at least one configured provider + a default, agents refuse to start. No silent fallback, no using the maintainer's infra.

**Cost visibility:** every call is recorded in `/opt/operai/state/llm-usage.db` (SQLite). Per-provider, per-model, per-caller breakdowns via `operai-init llm usage`.

**Playbook Ch.18** documents the full design: architecture, five providers, per-sub-agent routing, cost model, pre-flight enforcement, roadmap.

## New in v2.7 (Agent Factory Pattern — CS reference)

*Moved from "new in v2.7" earlier — see playbook Ch.17 for details.*

## New in v2.6 (Phase 2 frozen + Custom Engagement tier)

After three adversarial design reviews, Phase 2 of the ingest layer (Gmail, Slack, Notion, Google Drive, Richpanel) is **frozen in the public Kit** and moved to a new commercial tier.

**What's technically enforced in v2.6:**

```bash
operai-init ingest allow --source notion ...
  → Error: source 'notion' is frozen in the public Kit (v2.6+).
    Available only via Custom Ingest Engagement.
    See playbook Ch.11f + Ch.13. Contact: founder@your-company.example
```

The 5 blocked sources — gmail, slack, notion, drive, richpanel — are refused at the allowlist layer with a clear pointer to the Custom Ingest Engagement tier.

**What's in the playbook:**

- **Ch.11f** — 100-line post-mortem documenting the three design reviews and why Phase 2 can't ship at Kit pricing. Honest about the 2-4 engineer-month gap between "defensible architecture" and "shippable compliance".
- **Ch.13 — new Path 3b** — "Custom Ingest Engagement" commercial tier:
  - Targets: brands €20M+ with DPO relationship
  - Price: €5-15K one-time + €500-1,500/month
  - Delivery: 4-8 weeks, source-by-source activation
  - Includes: webhook-based synchronous revocation, classifier validated against labelled corpus, Subject Registry behind service boundary, leak-surface verifier, per-source DPIA amendments co-signed with brand's counsel

**What still works in the public Kit:**

- Phase 1 structured-source ingestion (Shopify, Klaviyo, Ads) — shipped v2.4
- All manual brain writes via MCP (`brain_write`, `memory_write`, `me_write`)
- Discovery interview at install time
- Per-employee `me.md` profiles
- Direct .md edits under `knowledge/<brand>/` by admin-key holders

Structured sources cover 80%+ of a brand's numerical signal. Manual writes cover the tacit knowledge brands typically want agents to have. The 20% residual — automatic ingestion from corporate comms — is exactly where DPO-grade compliance becomes mandatory.

## New in v2.5 (agentic organization — McKinsey alignment)

Kit v2.5 maps OperAI onto McKinsey's September 2025 agentic-organization framework and ships the governance layer McKinsey prescribes.

**New playbook chapters:**
- **Ch.15 — The 5 Pillars Mapping**: maps each McKinsey pillar (business model / operating model / governance / workforce / tech+data) to a specific OperAI artifact. Sales argument: OperAI is the 1% network model, productized.
- **Ch.16 — Agentic Governance**: design + deployment of the 3 meta-agents McKinsey names explicitly (critic + guardrail + compliance).

**New playbook section in Ch.14 — Role profiles:**
- M-shaped Supervisor, T-shaped Specialist, AI-Empowered Frontline — McKinsey's 3 emerging talent profiles
- Mapped to OperAI's 7 agents
- New KPIs for the agentic era (agent orchestration ratio, profile progression, socioemotional time ratio)

**New CLI commands:**

```bash
operai-init assess <employee>            # 10-question interview → role profile + 90d training path
operai-init assess --team                # team distribution across the 3 profiles
operai-init governance enable            # installs 3 meta-agents (SOULs + systemd)
operai-init governance status            # service state + verdict counts
operai-init governance logs --agent critic
operai-init governance review            # pending compliance amendments
operai-init governance disable --reason "X" --by diego
```

**New meta-agents (McKinsey 5-pillar governance):**

| Meta-agent | What it does | Invocation |
|---|---|---|
| `critic` | Adversarial cross-model deliberation (Punta de Flecha: Opus + GPT-5 + Gemini) on high-stakes domain-agent outputs | Invoked when confidence < 0.85 OR impact > €500 OR customer-facing |
| `guardrail` | Enforces ACK, Article 50, Annex III, brand voice, financial thresholds, PII handling at write-time | Intercepts every policy-crossing tool call |
| `compliance` | Weekly scan of EUR-Lex, AEPD, EDPB, CNIL + LLM-provider changelogs; proposes DPIA/Register amendments | Monday 07:00 UTC cron |

**Economic model (add-on):**

| Meta-agent | Cost/month |
|---|---|
| Critic | €5-30 |
| Guardrail | €0-5 |
| Compliance | €2-5 |

Total fully-governed swarm: **€360-395/month** all-in (still inside the 18:1 ROI band).

## New in v2.4 (ingest layer — Phase 1)

The `operai-init ingest` surface adds structured data ingestion with compliance defaults. Designed under two rounds of adversarial review (Codex, 14 criticisms v1 + 9 criticisms v2). Every shipped line maps to a resolved criticism; deferred criticisms gate the Phase 2 sources.

**Phase 1 shipped (v0.4.0):**

```bash
operai-init ingest allow --source shopify --unit-type resource --unit-id products \
  --reason "legítimo interés — catalog sync for agents; retention 90d"
operai-init ingest run --source shopify --days 90
operai-init ingest stats
operai-init ingest forget --email alice@example.com --reason "RTBF 2026-04-18"
operai-init ingest forget --status
```

- **Allowlist-only**: no connector runs without an entry documenting legal basis
- **Subject Registry** (SQLCipher-encrypted) with deterministic-only linking, audit log, no name_literal column
- **Delete Ledger** tracking RTBF propagation across 7 stores with realistic per-store SLAs
- **DLP Stage A** (secret scanning: AWS, Stripe, Anthropic, GitHub, JWT, private keys) — hard refuse
- **DLP Stage B** (PII tokenization with validation: email, phone, DNI/NIE, IBAN, CC Luhn)
- **Evidence Store** per source (SQLCipher, TTL 30-365d, admin-only access)
- **Retrieval Store** partitioned by ACL group under `knowledge/<brand>/ingested/<group>/YYYY/MM/`
- **ACL at the index boundary**: per-group QMD collections, principal's key determines which collections their queries reach
- **Connectors**: Shopify (products + aggregated orders), Klaviyo (metrics + aggregated campaigns), Meta/Google Ads (account-level stubs)

**Key management now carries ACL groups:**

```bash
operai-init key create laura --role team --groups cs,retail
operai-init key create juan  --role team --groups finance
operai-init key create diego --role admin
```

**Phase 2 deferred** (Gmail/Slack/Notion/Drive/Richpanel) — 5 prerequisites documented in Playbook Ch.11f before unlock.

## New in v2.3 (MCP server + API keys)

The kit now ships a working MCP server. `curl | bash` leaves the brand with a production-grade swarm, not just a layout.

**What's live after install:**

- Python MCP server at `/opt/operai/services/mcp/server.py` (Starlette + SSE, 11 tools)
- Bearer-token auth with admin/team roles, enforced per tool
- API keys managed via `operai-init key create|list|revoke`
- Founder's admin key auto-generated by install.sh (one-time print to stdout)
- systemd unit `operai-mcp.service` (installed, enable with `systemctl enable --now operai-mcp`)

**The 11 tools:**

| Tool | Required role | Purpose |
|---|---|---|
| `brain_query` | team | Hybrid search (QMD vector + keyword + rerank) |
| `brain_read` | team | Read a brain doc by path |
| `brain_list` | team | List files/folders under a directory |
| `brain_write` | admin | Create/update a brain doc (audited) |
| `memory_write` | team | Append to today's memory note |
| `me_read` | team | Read a me.md personal profile |
| `me_write` | team | Write own me.md (admin can write any) |
| `status` | team | Health check |
| `shopify_query` | team | Shopify Admin API passthrough |
| `klaviyo_query` | team | Klaviyo API passthrough |
| `slack_send_message` | admin | Slack chat.postMessage |

**Team onboarding now carries auth:** the team-join script prompts each employee for their API key (given by the founder) and writes it into the Claude Desktop config as an env var referenced from a `--header Authorization:Bearer` arg to `mcp-remote`. No keys touch query strings or URLs.

## New in v2.2 (post-install CLI + team onboarding)

The `operai-init` CLI ships inside every new deploy and provides the post-bootstrap operations:

```bash
operai-init connect shopify                # Shopify Admin API custom app
operai-init connect klaviyo                # Klaviyo Private API key
operai-init connect google-workspace       # GWS service account + domain-wide delegation
operai-init connect slack                  # Slack Bot User OAuth token
operai-init tunnel mcp.acme.com            # Cloudflare Tunnel + systemd unit + DNS
operai-init team-join --out team-join.sh   # Generate employee onboarding script
operai-init status                         # Health check (integrations + services + brain + compliance)
```

Each `connect` command:
- Instructs the founder where to generate the token in the platform's UI
- Accepts the token via hidden input (never echoed)
- Verifies against the platform's API before saving
- Writes to `/opt/operai/credentials/<service>.json` with mode 600

`tunnel` creates a named Cloudflare Tunnel (`<brand>-mcp`), writes the config to `/opt/operai/services/cloudflared.yml`, routes DNS, and installs the `operai-tunnel.service` systemd unit.

`team-join` generates a signed employee onboarding script with the brand's MCP URL baked in. Every employee runs it once and has the full swarm tooling in Claude Desktop.

### Team onboarding — one command per employee

Once the tunnel is live, each team member runs (on their Mac / Linux / Windows git-bash):

```bash
curl -fsSL 'https://usecompai.com/team-join?brand=<brand>&mcp=mcp.<brand>.com' | bash
```

The script detects OS, installs Node LTS via fnm if missing, writes `claude_desktop_config.json`, and points Claude Desktop at the brand's MCP endpoint. No credentials touch employee machines — all tokens stay on the brand's VPS.

## New in v2.1 (brand bootstrap)

**One-command deploy for a brand-new company:**

```bash
curl -fsSL https://usecompai.com/init | bash
```

From a fresh Ubuntu 24.04 VPS to a running OperAI swarm in ~30 min (automated) + ~30 min (founder clicks).

- `init/install.sh` — main orchestrator, installs deps + runs bootstrap
- `init/brain-bootstrap.py` — interactive discovery interview + 6 QMD collections + brain skeleton
- `init/discovery.md` — documentation of the 25-question interview
- `init/soul-templates/*.SOUL.md.tmpl` — 7 agent SOULs, interpolated with brand name
- `init/systemd-templates/*.service.tmpl` — 8 systemd units (7 agents + MCP server)
- `init/compliance-scaffold/*.md` — DPIA + AI System Register + Annex III review pre-filled with @BRAND@

See playbook Chapter 11e for the full walk-through.

## New in v2.0

**Compliance package** (ready for your legal counsel):
- `knowledge-base/eu-ai-act-guardrails.md` — Annex III prohibited uses, Article 50 transparency, Article 14 human oversight
- `knowledge-base/dpia-template.md` — Data Protection Impact Assessment (anonymized, GDPR Art. 35)
- `knowledge-base/ai-system-register-template.md` — full inventory of agents, models, data flows, retention

**Operational additions:**
- `knowledge-base/punta-de-flecha.md` — adversarial cross-model deliberation protocol (Opus + GPT-5 + Gemini 2.5)
- `knowledge-base/ads-audit-heuristics.md` — 27 heuristics for auditing paid-media accounts pre-deploy
- `knowledge-base/ai-onboarding-framework.md` — L0-L3 maturity model for rolling out AI to a 40+ person team

**Runtime assets:**
- `templates/configs/openclaw-reference.json` — canonical agent runtime config
- `templates/launch-daemons/ai.openclaw.AGENT.plist` — macOS launchd template for always-on agents

## MCP Default

Use Streamable HTTP as the default MCP transport for new deployments. Keep SSE only as a temporary fallback during migration windows.

## Compliance Default

Every new deployment MUST complete, in order:

1. DPIA (copy `knowledge-base/dpia-template.md` → fill → sign)
2. AI System Register (copy `knowledge-base/ai-system-register-template.md` → fill → store)
3. Annex III review — confirm no automated hiring, firing, evaluation, credit scoring, or biometric inference
4. Article 50 disclosure — wire the CS agent disclaimer template before going live with end-user traffic
5. Anti-injection hardening — apply `knowledge-base/anti-injection-template.md` patterns to every agent SOUL

If you skip any of these, you are shipping a system that cannot pass an EU AI Act audit. Do not skip.

## Support

- Playbook: https://usecompai.com/playbook/
- Story: https://usecompai.com/story.html
- Live dashboard: https://usecompai.com/live.html
- Contact: founder@your-company.example

## Operating Rule

Do not promise autonomy before the review loop works.

And do not ship an agent to production before the compliance package is on file.

---

**Version 3.1.1** · April 2026 · 144 files · EU AI Act ready · honest 18:1 ROI
