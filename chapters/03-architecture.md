# Chapter 3: The Architecture — How a Multi-Agent System Actually Works

## Why One Agent Isn't Enough

The first mistake everyone makes: "I'll just set up one AI agent and have it do everything."

That's like hiring one person to do CS, accounting, marketing, inventory management, and wholesale sales. Even if they were brilliant, they'd be context-switching constantly and doing everything poorly.

The architecture that works is **specialized agents with a shared brain.**

## The Multi-Agent Architecture

```
                    ┌─────────────────────────────┐
                    │   🧠 STRATEGY AGENT (Central Hub)    │
                    │   Strategy + Orchestration    │
                    │   Cloud VPS (EU)       │
                    └───────────┬─────────────────┘
                                │ Tailscale Mesh
        ┌───────────┬───────────┼───────────┬───────────────┐
        │           │           │           │               │
   ┌────▼────┐ ┌────▼────┐ ┌────▼────┐ ┌────▼────┐ ┌───────▼───────┐
   │🦋CS Agent│ │📊Finance Agent│ │🏪 Retail Agent  │ │💻Donatel│ │🏖️ Merchandising Agent      │
   │   CS    │ │ Finance │ │ Retail  │ │Digital  │ │Merchandising  │
   │         │ │         │ │         │ │Marketing│ │& Wholesale    │
   └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘ └───────┬───────┘
        │           │           │           │               │
        └───────────┴───────────┴───────────┴───────────────┘
                         Mac Mini (secondary host)
                    ┌─────────────────────────────┐
                    │     SHARED BRAIN (3,007 files)   │
                    │   rsync ↔ every 30 minutes    │
                    │   + MCP Server (95 tools)     │
                    └─────────────────────────────┘
```

**The production topology:** Strategy Agent (hub/strategy) runs on a cloud VPS in the EU. The domain agents run on a dedicated secondary host. All connected through an encrypted private network. A shared brain syncs bidirectionally every 30 minutes. This is the reference deployment, not a requirement; the technical appendix shows the host-specific setup.

## Design Principles

### 1. Each Agent Has a Clear Domain

Every agent owns a specific area of the business. This means:
- **Clear responsibility:** If something goes wrong with inventory, you know which agent to look at
- **Focused context:** The CS agent doesn't need to know about wholesale pricing formulas
- **Independent scaling:** You can run the CS agent on a beefier model (Opus) while the reporting agent runs on a cheaper one (Sonnet/Flash)

### 2. Agents Communicate Through the Hub

In the ideal architecture, agents communicate through a central orchestrator — this prevents chaos and creates an audit trail. In practice, the coordination often flows through team messaging channels (Slack, WhatsApp) where both agents and humans participate. The key is that every cross-domain request is logged and traceable, whether it routes through the hub directly or through a shared channel.

Example flow:
1. **CS Agent** receives complaint: "My order hasn't arrived"
2. CS Agent checks Shopify order status → sees it's marked "fulfilled"
3. CS Agent escalates to **Ops Agent** via hub: "Order #4521 marked fulfilled but customer says not received"
4. **Ops Agent** checks 3PL tracking → finds package stuck in customs
5. Ops Agent responds to hub with status update
6. Hub routes back to **CS Agent** with full context
7. CS Agent drafts customer response with accurate tracking info and ETA

All of this happens in seconds. No human needed unless confidence is low.

### 3. Shared Knowledge, Separate Personalities

All agents share:
- **Catalog data** (products, descriptions, pricing, inventory, bundles, subscriptions, warranties)
- **Brand voice guidelines** (tone, vocabulary, do's and don'ts)
- **Customer history** (past orders, past issues, lifetime value)
- **Business rules** (return policy, shipping times, discount limits)

But each agent has its own:
- **SOUL.md** — personality, expertise, communication style
- **Tools** — only the integrations it needs
- **Decision thresholds** — when to act autonomously vs. escalate to human

### 4. Human-in-the-Loop by Default

This is critical. The system is designed with **graduated autonomy:**

| Confidence Level | Action |
|-----------------|--------|
| > 95% | Agent acts autonomously |
| 80-95% | Agent acts but flags for async human review |
| 60-80% | Agent drafts response, human must approve |
| < 60% | Agent escalates to human with full context |

Over time, as the system learns and you trust it more, you adjust these thresholds upward. In a typical deployment:
- Month 1: 40% autonomous
- Month 3: 65% autonomous
- Month 6: 82% autonomous
- Month 12: 91% autonomous (current)

The remaining 9% are genuinely complex cases that benefit from human judgment — legal issues, VIP customers, PR-sensitive situations.

### 5. Everything is Logged and Auditable

Every agent action is logged:
- What decision was made
- What data was used
- What confidence level was assigned
- Whether a human reviewed it
- What the outcome was

This isn't just good practice — it's a GDPR requirement if you're operating in Europe, and it's how the system learns and improves.

## The Technology Stack

At the core, the reference system runs on **OpenClaw** — an open-source AI agent framework that connects LLMs to real-world actions. You can fork the repo and swap this layer if another runtime fits your team better.

| Component | What We Use | Why |
|-----------|------------|-----|
| **Agent Runtime** | OpenClaw | Open source, local-first, 50+ integrations, active community |
| **Primary LLM** | Mixed: GPT-5.4 via ChatGPT OAuth (hub + 4 domain agents), Claude Sonnet 4 (CS + HR) | Best model per role with zero-incremental-cost routing where existing team subscriptions already exist |
| **Secondary LLMs** | GPT-5.4 / Codex / Gemini Flash | Cost-effective for simpler tasks, coding agents |
| **Hosting** | Dedicated server (Hetzner) | €40/mo, full control, EU data residency |
| **Agent-to-Agent** | ACP (Agent Communication Protocol) | Native cross-agent coordination |
| **Messaging** | WhatsApp, Slack, Email | Meet teams where they already work |
| **Memory** | Local files + structured knowledge base | No vendor lock-in, full data ownership |
| **Monitoring** | Built-in heartbeats + cron jobs | Self-healing, auto-restart |
| **ERP / Accounting** | Holded | Invoicing, payment reconciliation, ledger |
| **Expense Management** | Payhawk | Corporate cards, expense tracking, bank statements |
| **Knowledge Base** | Notion + Brain Context Tree | 3,007 docs organized by domain, auto-indexed |
| **Social Listening** | Agent-Reach + bird CLI | Twitter/X monitoring, multi-platform scanning |
| **Semantic Search** | Exa | Better than Google for competitive research |
| **Image Generation** | Krea AI | Product shots, creative assets |
| **Power-User Layer** | Claude Code + MCP | Founder's direct interface — 95 tools, slash commands, subagents |

**Total system cost:** €352/month all-in (infrastructure + LLM access + subscriptions). See Ch.12 for the complete cost breakdown.

Compare this to roughly €6,500/month in equivalent saved labor hours (62 hours/week × €21/h loaded operational labor, plus founder opportunity cost). That is a verifiable 18:1 ratio, calculated in Ch.12 with every assumption on the table.

## What You Need to Get Started

**Minimum viable setup (1 agent):**
- A Linux server or VPS (€20-40/month)
- An LLM API key (Anthropic, OpenAI, or similar)
- OpenClaw installed and configured
- One channel connection (Slack, WhatsApp, email, helpdesk, or team chat)
- 2-4 hours for initial setup

**Full deployment (8 agents):**
- VPS (€15/month) + Mac Mini as secondary compute (~€22/month amortized)
- ChatGPT OAuth seats for hub + non-customer agents, plus Anthropic API for CS/HR and fallbacks
- All channel connections configured
- Integrations with your existing tools (Shopify, Klaviyo, etc.)
- 2-4 weeks for full implementation and tuning
- A second compute node (Mac Mini, NUC, VPS, or equivalent) for agent isolation

> **A note on agent roles:** The production deployment documented in this playbook runs eight agents across eight domains: CS, Finance, Retail, Digital Marketing, Merchandising & Wholesale, and a central hub for strategy and orchestration. In practice, you'll adapt these to your org chart. Wholesale was absorbed into Merchandising because the same operational patterns apply (account management, order flow, pricing). Finance is now a standalone domain. The architecture is modular by design — start with the domains that hurt most, split or merge as you scale.

### 6. Confidence Scoring (New)

Every agent includes a standardized confidence framework that drives graduated autonomy:

| Confidence | Action | Example |
|-----------|--------|---------|
| > 95% | Act autonomously | Standard tracking query, stock check |
| 80-95% | Act + flag `[REVIEW]` | Return within policy, payment reminder |
| 60-80% | Draft for human approval | Complaint response, discount request |
| < 60% | Escalate with full context | Legal issue, VIP escalation |

Agents self-report confidence with every action: `[Confidence: 92%] Responding to tracking query`. This creates an auditable record and enables systematic threshold adjustment over time.

### 7. Audit Logging

Every agent action is logged to a structured JSONL audit trail:

```json
{"timestamp":"2026-03-28T21:21:14+00:00","agent":"cs_agent","action":"cs_ticket_response","confidence":"94%","data":"order_tracking","human_review":false}
```

Monthly rotation. GDPR-compliant. The audit log is the foundation for measuring autonomy rates and detecting quality regressions.

The next eight chapters walk through each agent in detail — what it does, how it's configured, and the specific results it delivers.

---

*Next: [Chapter 4 — Agent #1: Customer Service →](04-agent-cs.md)*
