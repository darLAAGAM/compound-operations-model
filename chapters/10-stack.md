# Chapter 10: The Stack — What Runs in Production

> **Appendix · Technical depth.** This chapter is for operators or engineers deploying the brain themselves. It covers implementation details that aren't needed for understanding the conceptual architecture. Skip if you're reading for strategy.

## The Full Technology Stack

Every piece of technology in the deployment documented in this playbook, why it was chosen, and what it costs.

## Core Infrastructure

| Component | Choice | Why | Monthly Cost |
|---|---|---|---|
| **Agent Runtime** | OpenClaw | Open-source, local-first, 190K+ GitHub stars, 50+ integrations. Acquired by OpenAI in 2025. No vendor lock-in. | €0 (software) |
| **Primary VPS** | Hetzner Cloud (Germany, 8 vCPU / 16 GB) | Best price/performance in EU. Full data sovereignty. Hub agent + MCP server + crons. | €15 |
| **Secondary compute** | Mac Mini M4 (amortized over 36 months) | Apple Silicon idles at <10W. One-time €800 purchase. Runs 7 domain agents via LaunchDaemons. | €22 |
| **Mesh networking** | Tailscale Premium | Encrypted zero-config mesh between VPS, Mac Mini, and admin machines. | €17 |
| **Public ingress** | Cloudflare Tunnel | Permanent HTTPS tunnel for the MCP server at `mcp.<domain>`. No open ports on the VPS. | €0 |
| **Founder interface** | Claude Pro Max + MCP | Power-user command center. 95 tools, 5 subagents, 6 slash commands. | €185 |
| **Hub subscription** | ChatGPT Pro (GPT-5.4) | Primary model for the strategy hub agent. | €20 |
| **API usage (LLM)** | Anthropic API (Sonnet + Opus fallback + Haiku) | CS + HR primary, all fallbacks, Haiku for crons. | ~€93 |
| **Total** | | | **€631** |

**Annual: €7,572.** Full breakdown and ROI in Ch.12.

---

## The Model Matrix — What Runs Where

After testing expensive API-only routing, free-tier models, and paid low-cost alternatives, the system settled on a simple rule: use **GPT-5.4 via ChatGPT OAuth** wherever existing team subscriptions already cover the role, and keep **Claude Sonnet** for customer-facing and sensitive workflows.

| Agent | Primary | Auth Method | Fallback | Why |
|---|---|---|---|---|
| **Strategy Hub** | GPT-5.4 | ChatGPT OAuth (founder's sub) | Opus 4.6 (Anthropic) | Best reasoning + 1M context. €0 incremental — reuses existing ChatGPT Plus. |
| **CS Agent** | Claude Sonnet 4 | Anthropic API key | Opus 4.6 | Customer-facing tone matters. Sonnet replaced Opus as primary (Lesson 24) — quality is identical for CS, 5× cheaper. |
| **Finance Agent** | GPT-5.4 | ChatGPT OAuth (employee sub) | Opus 4.6 | €0 incremental. Piggybacks on finance manager's ChatGPT. |
| **Retail Agent** | GPT-5.4 | ChatGPT OAuth (employee sub) | Opus 4.6 | €0 incremental. Piggybacks on ecommerce lead's ChatGPT. |
| **Marketing Agent** | GPT-5.4 | ChatGPT OAuth (employee sub) | Opus 4.6 | €0 incremental. Same ecommerce lead's ChatGPT subscription. |
| **Merchandising Agent** | GPT-5.4 | ChatGPT OAuth (employee sub) | Opus 4.6 | €0 incremental. Same finance manager's ChatGPT subscription. |
| **HR Agent** | Claude Sonnet 4 | Anthropic API key | Opus 4.6 | HR data is sensitive — Anthropic's audit trail preferred. ~€10/mo. |
| **Founder interface** | Claude Opus 4.6 | Claude Pro Max subscription | — | Power-user interface with 95 MCP tools. Bundled with Pro Max. |

### The Model Cost Evolution (Three Pivots in 6 Months)

The cost optimization journey went through three distinct phases:

> **Phase 1 (Month 1-3):** All agents on Opus 4.6 / Sonnet. API costs climbing to ~€500/month.  
> **Phase 2 (historical):** Free-tier and low-cost routing looked attractive, but rate limits and operational fragility made it a poor default.  
> **Phase 3 (current):** **ChatGPT OAuth** lets agents piggyback on employee ChatGPT Plus/Pro subscriptions at **zero incremental cost**. 5 of 7 agents now run GPT-5.4 this way, while CS and HR stay on Claude Sonnet because tone quality and sensitive workflows matter more than squeezing the last euro out of the bill.

**The final architecture:**
- 5 agents on GPT-5.4 via ChatGPT OAuth = €0 incremental (subscriptions were already being paid)
- 2 agents on Claude Sonnet 4 via API keys = ~€93/month including fallbacks and Haiku crons
- Fallback for all: Opus 4.6 (Anthropic) for edge cases

**The rule:** before buying API tokens, audit what subscriptions your team already has. The cheapest token is the one you are already paying for.

---

## Per-Agent Configuration

### CS Agent
```
Model:         Claude Sonnet 4 primary, Opus 4.6 fallback
Host:          Mac Mini (LaunchAgent for GUI session)
Channels:      WhatsApp + Email + Richpanel
Integrations:  Shopify Admin API, Richpanel, Klaviyo (read-only)
Knowledge:     Product catalog, FAQ, returns policy, brand voice
Hardening:     Anti-prompt-injection (standard + CS-specific extra)
Autonomy:      Graduated rollout (week 1 shadow → week 5+ full on proven categories)
```

### Strategy Hub
```
Model:         GPT-5.4 primary, Opus 4.6 fallback
Host:          VPS (cron @reboot, not systemd — see Lesson 25)
Channels:      Slack (primary) + WhatsApp (urgent) + MCP relay
Integrations:  All 95 MCP tools + brain_search/brain_write + Knowledge Mining cron
Role:          Cross-domain orchestration, morning briefings, competitive scans
```

### Finance Agent
```
Model:         GPT-5.4 via ChatGPT OAuth (employee sub)
Host:          Mac Mini (LaunchDaemon)
Channels:      Email + Slack
Integrations:  Holded (ERP), Revolut, Payhawk, Shopify, GSheets, GDrive
Knowledge:     Chart of accounts, revenue recognition rules, variance thresholds
```

### Marketing Agent
```
Model:         GPT-5.4 via ChatGPT OAuth (employee sub)
Host:          Mac Mini (LaunchDaemon)
Channels:      Slack
Integrations:  Klaviyo, Meta Ads, GA4, GSC, Pinterest Ads
Knowledge:     Brand guidelines, campaign calendar, KPI targets, copy patterns
```

### Retail Agent
```
Model:         GPT-5.4 via ChatGPT OAuth (employee sub)
Host:          Mac Mini (LaunchDaemon)
Channels:      Slack
Integrations:  TC Analytics (foot traffic), Shopify POS, Stockagile
Knowledge:     Store KPIs, staff schedules, location metadata
```

### Merchandising Agent
```
Model:         GPT-5.4 via ChatGPT OAuth (employee sub)
Host:          Mac Mini (LaunchDaemon)
Channels:      Slack
Integrations:  Shopify Admin API, Stockagile, Amphora (3PL)
Knowledge:     Sell-through targets, inventory distributions by variant, category hierarchy, wholesale accounts
```

### HR Agent
```
Model:         Claude Sonnet 4 via Anthropic API
Host:          Mac Mini (LaunchDaemon)
Channels:      Slack
Integrations:  Notion, Holded (via custom Leaves microservice), Payhawk
Knowledge:     Policies, onboarding templates, vacation balances, payroll rules
```

---

## Business Systems Integrated

Beyond agent-specific tools, the system connects to the full operational stack:

| System | Category | What Agents Do With It |
|---|---|---|
| **Holded** | ERP / Accounting | Invoice management, payment reconciliation, revenue tracking, payroll prep |
| **Revolut** | Business Banking | Multi-currency ops across 6 currencies, bank feed reconciliation |
| **Payhawk** | Corporate Cards | Expense monitoring, card management, team spending limits |
| **Shopify** | E-commerce | Orders, products, inventory, customer data, POS across all stores |
| **Stockagile** | Inventory Management | Multi-warehouse stock, transfers, purchase orders, wholesale B2B |
| **Amphora** | 3PL / Fulfillment | Shipping, returns, warehouse operations |
| **Klaviyo** | Email Marketing | Campaigns, flows, segmentation, customer profiles |
| **Meta Ads** | Paid Advertising | Campaign performance, spend tracking, ROAS monitoring |
| **Pinterest Ads** | Paid Advertising | Reach campaigns, pin-level performance |
| **Richpanel** | Customer Service | Ticket management, customer history |
| **Google Workspace** | Productivity | Gmail, Calendar, Drive, Sheets, Docs (Domain-Wide Delegation to the swarm) |
| **Notion** | Knowledge Base | Supplier notes, meeting records, operational wikis |
| **TC Analytics** | Retail Foot Traffic | Store visits, conversion rates, hourly patterns (scraper via Playwright) |
| **Exa** | Semantic Web Search | Competitive research, trend monitoring |
| **Krea AI** | Image Generation | Product imagery, marketing assets |
| **Upstash Redis** | Key-Value Store | Caching, state management between agents |
| **Holded Leaves API** | HR / Absences | Custom microservice — scrapes the Holded web UI because the official API doesn't expose leave data |

**Key principle:** agents don't replace these systems — they **orchestrate** them. Each system remains the source of truth for its domain. Agents read, analyze, cross-reference, and act across all of them simultaneously. No human can check 16 systems in parallel before answering a question.

---

## Infrastructure Hardening

Running 7 agents on always-on hosts with API keys, brain access, and live business systems requires production-grade hardening. Lessons learned the hard way (see Ch.11b for the full stories).

### 3 LaunchDaemons per Agent (Mac Mini)

Every agent on the secondary host runs **three persistent services**:

1. **Gateway** — the OpenClaw agent itself (`com.Compai.openclaw-gateway.<agent>.plist`)
2. **Watchdog** — monitors gateway health, auto-restarts on failure (every 5 minutes)
3. **Port forwarder** — asyncio TCP proxy from Tailscale IP → loopback (`127.0.0.1:<port>`)

All three have `KeepAlive: true` and `RunAtLoad: true`, so they survive reboots and auto-recover from crashes.

### Loopback Binding + Asyncio Port Forwarder

All OpenClaw gateways bind to **`127.0.0.1`** only. No direct external access to agent ports, even on the Tailscale mesh. Remote access is routed through a 30-line Python asyncio TCP proxy that runs as its own LaunchDaemon per agent.

**Why:** loopback binding is the correct security default. A bug in the gateway that exposes arbitrary command execution can't be reached from the network. The port forwarder provides controlled, logged, restartable remote access.

### openclaw-ops Toolrepo

The production stack includes four scripts maintained as a toolrepo:

| Script | Purpose | Runs |
|---|---|---|
| `heal.sh` | Detect unhealthy agents, restart them | Manual + watchdog |
| `watchdog.sh` | Continuous health monitoring of all agents | Every 5 min (LaunchDaemon + systemd timer) |
| `security-scan.sh` | Audit plugin paths, permissions, exposed ports | After any config change |
| `skill-audit.sh` | Validate that all skills are loadable and parseable | Weekly cron |

**Baseline scores:**
- VPS: 100/100 (fully locked down)
- Mac Mini: 85/100 (DM channels open is deliberate — needed for GUI agents)

### Gateway Binding Rules

| Host | Method | Never use |
|---|---|---|
| Linux VPS | `cron @reboot` | systemd `Type=simple` (see Lesson 25 — causes restart loop because OpenClaw forks a child and exits) |
| macOS Mac Mini | LaunchDaemon (headless) or LaunchAgent (GUI session) | `nohup` with `sudo -u` — doesn't survive reboots and doesn't set HOME correctly |

---

## Why OpenClaw Over Alternatives

| Alternative | Why Not |
|---|---|
| **Custom-built agents** | 10× development time. Why reinvent the wheel? |
| **LangChain / CrewAI** | Framework, not a runtime. No built-in messaging, memory, or integrations. |
| **Enterprise platforms** (Salesforce AI, ServiceNow) | €5K+/month. Overkill for brands under €50M. |
| **SaaS agents** (Sierra, Siena, Artisan) | Single-purpose. No full-stack ops. No customization. |
| **n8n / Make.com** | Good for simple automations, not for reasoning-heavy agent work. |

**OpenClaw's killer features for this use case:**

1. **Local-first** — your data never leaves your server
2. **Channel-native** — built-in WhatsApp, Slack, Email, Telegram support
3. **Skill system** — modular capabilities you can add/remove (352 skills in this deployment)
4. **Memory** — persistent context across conversations and sessions
5. **Cron & heartbeat** — self-healing, scheduled tasks, autonomous operation
6. **Agent-to-agent (ACP)** — agents coordinate without human intervention
7. **Cost** — the software is free. You only pay for LLMs and hosting.

---

## Security Considerations

Running AI agents with access to business systems requires serious security:

1. **Principle of least privilege** — each agent only has API keys for its own domain
2. **Read vs. write** — start with read-only access, add write access per-capability
3. **Audit logging** — every agent action logged to structured JSONL with timestamp + confidence + data source
4. **Key rotation** — API keys rotated quarterly
5. **Network isolation** — agents can't access systems outside their scope
6. **Human escalation** — all financial transactions require human approval
7. **EU hosting** — server in Germany, data stays in EU
8. **No training** — API usage only, never consumer products; data is never used to train LLMs
9. **Anti-prompt-injection** — every SOUL.md includes a hardened anti-injection section; the CS agent has an additional block because it processes customer messages
10. **Gateway loopback binding** — no direct external access to agent ports
11. **Port forwarding via asyncio proxy** — controlled remote access through proxies, not direct binding
12. **openclaw-ops toolrepo** — continuous health monitoring and security scanning
13. **Graduated autonomy** — new capabilities start in shadow mode, then 60-80% (human review), then 80-95% (act + flag), then >95% (autonomous)

---

## Cost Breakdown — Final

| Item | €/month |
|---|---|
| VPS hosting (Hetzner) | 15 |
| Mac Mini amortized | 22 |
| Tailscale Premium | 17 |
| Anthropic API (CS Sonnet + HR Sonnet + fallbacks + Haiku crons) | 80 |
| ChatGPT OAuth (5 agents on employee subs) | 0 |
| ChatGPT Pro (hub) | 20 |
| Claude Pro Max (founder interface) | 185 |
| Cloudflare Tunnel + Vercel | 0 |
| **Total** | **€631** |

**Annual: €7,572.** Value created: €77,584 (see Ch.12). **ROI: 10:1.**

---

*Next: [Chapter 10b — Memory Architecture →](10b-memory-architecture.md)*
