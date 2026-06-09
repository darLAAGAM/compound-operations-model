# The Compound Operations Model
## An Open-Source AI Operations Playbook for Consumer SMEs

**By Compai** · Open-source educational portfolio · Built inside a profitable brand growing 100%+ annually · Repo: github.com/darLAAGAM/compound-operations-model

---

### What This Is

This is not a strategy deck. It's not a trend report. It's not thought leadership.

This is the operational blueprint built — and running — inside a profitable European consumer brand. Eight-figure revenue, healthy EBITDA, 100%+ annual growth, ~40-person team. Seven AI agents in production plus a founder command center — full system cost **€352/month**, verified value **€77K/year** in reclaimed labor hours. **18:1 ROI with every assumption on the table.** The source is published as an educational portfolio so other consumer SMEs can fork the repo, read the playbook, and adapt the patterns.

Everything in this playbook is real. The architectures are running. The configs are from production systems. The numbers are audited.

### The Thesis

For every dollar a brand spends on software, it spends six on services and headcount to operate that software. Shopify costs €2K/year. The people managing inventory, processing orders, answering tickets, and closing the books cost €200K+.

Most AI tools sell another dashboard. **This playbook documents the operating layer above the dashboards.**

Every improvement in AI models makes the system faster, cheaper, and easier for operators to adapt. We are not positioning this as a SaaS product or a paid repo. We are publishing the working architecture, the lessons, and the artifacts so consumer SMEs can fork the repo, inspect the assumptions, and build their own version.

### Who This Is For

Consumer SME operators — beauty, food & beverage, home, wellness, pet, outdoor, fashion, and retail — running on Shopify or a similar commerce stack with €2M–50M in revenue. You have a ~40-person team. Multiple channels. And operations that are creaking under growth.

If you've been told you need to hire 3 more people, this playbook shows you a different path.

### The Compound Operations Model™

We've organized this playbook around the open operating model used in the reference deployment:

1. **Integrate** — Connect your systems into a unified data layer
2. **Specialize** — Deploy purpose-built AI agents per operational domain
3. **Orchestrate** — Make agents coordinate across functions
4. **Compound** — Let the system get smarter every day

### Table of Contents

| Ch. | Title | What You'll Learn |
|-----|-------|-------------------|
| 01 | [Introduction](01-introduction.md) | Who built this, why, and what makes it different |
| 02 | [The Problem](02-problem.md) | Why brands are stuck in operational quicksand |
| 03 | [Architecture](03-architecture.md) | The multi-agent operating system blueprint |
| | **— The Agents —** | |
| 04 | [Agent: Customer Intelligence](04-agent-cs.md) | CS triage, brand voice, pattern detection |
| 05 | [Agent: Inventory & Supply Chain](05-agent-ops.md) | Multi-location sync, 3PL, demand sensing |
| 06 | [Agent: Finance & Reporting](06-agent-finance.md) | Automated P&L, cash flow, anomaly detection |
| 07 | [Agent: Marketing & Lifecycle](07-agent-marketing.md) | Email optimization, segmentation, attribution |
| 08 | [Agent: Wholesale & B2B](08-agent-wholesale.md) | Account management, order ops, pipeline |
| 09a | [Agent: Retail & Physical](09-agent-retail.md) | Foot traffic, staffing, store performance |
| 09b | [Agent: Merchandising, Wholesale & Assortment](09b-agent-merchandising.md) | Sell-through, allocation, pricing, inventory health |
| | **— The Stack —** | |
| 09c | [Agent: HR & People Ops (HR Agent)](09c-agent-hr.md) | Onboarding, vacations, payroll prep, policies, expenses |
| 10a | [The Technology Stack](10-stack.md) | What runs under the hood — models, infra, Claude Code, Agent-Reach, 44 MCP tools |
| 10b | [Memory Architecture](10b-memory-architecture.md) | Context Tree, Knowledge Mining cron, shared brain sync (SuperMemory deprecated) |
| 10c | [The MCP Server](10c-mcp-server.md) | How your entire team gets AI superpowers — 44 tools, zero setup |
| 10d | [Advanced Operational Capabilities](10d-advanced-capabilities.md) | 15 specialized features that compound over time — AutoResearch, LLM Council, Pattern Library, and more |
| 10l | [Brain v2: Living Memory](10l-brain-v2-living-memory.md) | From wiki to operational memory with write-back, capture, tasks, outputs, and world model |
| 10m | [Capture Layer](10m-capture-layer.md) | Slack, Meet/Gemini, Gmail, and Drive capture with privacy hard-stops |
| 10n | [Setup 1-click](10n-setup-1-click.md) | Connect employee AI clients to the company Brain in one verified command |
| 10o | [Master Prompt](10o-master-prompt.md) | The operating contract that keeps every AI surface Brain-first and source-aware |
| 10p | [Tasks, Outputs, Decisions, Health](10p-tasks-outputs-health.md) | The lifecycle layer that prevents useful work from disappearing |
| 10q | [Public-by-default](10q-public-by-default.md) | Why agent work should be visible, searchable, and reusable by default |
| 10r | [Operational Compounding Loop](10r-operational-compounding-loop.md) | Health audits, shared memory, skillify, L3 queues, and workflow mining |
| | **— Implementation —** | |
| 11a | [Implementation Paths](11-implementation.md) | Read the playbook → fork the repo → run locally → adapt with human review → ask hello@usecompai.com for hands-on help |
| 11b | [Lessons from Production](11b-production-lessons.md) | 32 lessons: OAuth failures, memory cleanup, model routing, anti-injection hardening, OpenClaw vs systemd, and more |
| 11c | [OpenClaw Runtime Setup](11c-openclaw-setup.md) | Agent runtime framework — launchd plists, ChatGPT OAuth, cron scheduling |
| 11d | [EU AI Act Compliance](11d-eu-ai-act-compliance.md) | Full compliance package — DPIA, AI System Register, Annex III guardrails, Article 50 transparency |
| 11e | [Brand Bootstrap (1 cmd)](11e-brand-bootstrap.md) | From blank Ubuntu VPS to running swarm in one terminal command — `curl usecompai.com/init \| bash` |
| 11f | [Ingest Layer (Phase 1)](11f-ingest-layer.md) | Feeding the brain safely — allowlist + DLP + ACL at index boundary + RTBF. Structured sources only in v0.4 |
| 12 | [ROI Analysis](12-roi.md) | Real numbers from 6+ months in production |
| 14 | [Team Onboarding](14-team-onboarding.md) | Connect every employee to the swarm in 5 minutes — brain access, agents, Google Workspace, zero setup |
| | **— The Future —** | |
| 15 | [The 5 Pillars (McKinsey)](15-five-pillars.md) | The agentic organization framework mapped to Compai — the 1% network model, productized |
| 16 | [Agentic Governance](16-agentic-governance.md) | Three meta-agents (critic + guardrail + compliance) watching the seven domain agents |
| 17 | [Agent Factory Pattern](17-agent-factory.md) | McKinsey 2-5/50-100 ratio: 7 domain agents → factories of 10+ specialized sub-agents each. CS reference shipped v2.6 |
| 18 | [LLM Provider Abstraction](18-llm-providers.md) | 5-provider multi-LLM routing (Anthropic + OpenAI + Gemini + Qwen + MiniMax). Brand-owned API keys. Fallback chains. Per-sub-agent routing |
| 19 | [Factory Runtime v0.9.0](19-factory-runtime.md) | `operai-init factory run-once` — smoke test: 10 sub-agents dispatch end-to-end, full markdown trace, mock-LLM mode |
| 20 | [MVP Runtime](20-mvp-runtime.md) | Autonomous daemon: events → parallel dispatch → review queue. Workflow hook points for brand-specific extensions. Honest 70% of the reference swarm |
| 21 | [Webhooks + Slack Digest](21-webhooks-digest.md) | HMAC-verified receivers for 4 helpdesks + daily Slack digest. Autonomous end-to-end from customer email to review queue |
| 22 | [The Onboarding Experience](22-onboarding-experience.md) | Open onboarding pack (skills + custom instruction + templates) + setup wizard + team-onboard wrapper. 30 min per employee, same experience as the reference deployment |

### How to Read This

- **Founders/CEOs:** Read Ch. 1–3 and Ch. 12. That gives you the thesis, the architecture, and the business case.
- **Ops/Tech Leads:** Read everything. Ch. 4–9 are your implementation guides. Ch. 11b is the production war stories that will save you days of debugging.
- **Investors/Board:** Ch. 12 has the numbers you want. Ch. 3 has the architecture. Ch. 10c shows the team-wide impact.

---

*This playbook is a living document. The system it describes is in production and evolving daily. When we learn something new, we update the playbook.*

**Version 2.1** · 9 June 2026 — Adds the operational compounding loop from the latest Brain/Swarm work: weekly health audits, shared memory contract, inbox sweeper, skill evaluation harness, skillify loop, L3 action queues, and workflow mining. The public repo is now `github.com/darLAAGAM/compound-operations-model` and includes the full playbook plus public starter kit artifacts.

**Version 2.0** · 12 April 2026 — EU AI Act fully compliant (24/24 items, DPIA + AI System Register documented), honest 18:1 ROI with auditable math (€77K value / €4.2K cost), 32 production lessons, 15+ advanced capabilities (Punta de Flecha adversarial cross-model deliberation, AutoResearch, LLM Council, Pattern Library live), ChatGPT OAuth model strategy (5 agents at €0 incremental), anti-prompt-injection hardening across all SOULs, ACK rule fleet-wide, HR guardrails against Annex III high-risk uses, CS Article 50 transparency disclaimer deployed. Live at **usecompai.com** with public dashboard and free playbook, or contact **hello@usecompai.com** for hands-on implementation help.
