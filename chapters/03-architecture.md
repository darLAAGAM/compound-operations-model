# Chapter 3: The Architecture — How a Multi-Agent System Actually Works

## Why One Agent Isn't Enough

The first mistake everyone makes: "I'll just set up one AI agent and have it do everything."

That's like hiring one person to do CS, accounting, marketing, inventory management, and wholesale sales. Even if they were brilliant, they'd be context-switching constantly and doing everything poorly.

The architecture that works is **specialized agents with a shared brain.**

## The Multi-Agent Architecture

```
                    ┌─────────────────────────────┐
                    │      CENTRAL HUB            │
                    │   Orchestration + Memory +  │
                    │   Cross-agent Intelligence  │
                    └───────────┬─────────────────┘
                                │
        ┌───────────┬───────────┼───────────┬───────────┬───────────┐
        │           │           │           │           │           │
   ┌────▼────┐ ┌────▼────┐ ┌────▼────┐ ┌────▼────┐ ┌────▼────┐ ┌────▼────┐
   │   CS    │ │  Ops /  │ │ Finance │ │Marketing│ │Wholesale│ │ Retail  │
   │  Agent  │ │Inventory│ │  Agent  │ │  Agent  │ │  Agent  │ │  Agent  │
   └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘
        │           │           │           │           │           │
   ┌────▼────┐ ┌────▼────┐ ┌────▼────┐ ┌────▼────┐ ┌────▼────┐ ┌────▼────┐
   │Your CS  │ │Shopify  │ │ Finance │ │ Klaviyo │ │  Email  │ │  POS    │
   │Platform │ │3PL APIs │ │ Tools   │ │Meta Ads │ │  B2B    │ │Analytics│
   │Gorgias/ │ │Inventory│ │ Google  │ │   GSC   │ │Linesheet│ │TC Store │
   │Richpanel│ │Systems  │ │ Sheets  │ │         │ │         │ │         │
   └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘
```

## Design Principles

### 1. Each Agent Has a Clear Domain

Every agent owns a specific area of the business. This means:
- **Clear responsibility:** If something goes wrong with inventory, you know which agent to look at
- **Focused context:** The CS agent doesn't need to know about wholesale pricing formulas
- **Independent scaling:** You can run the CS agent on a beefier model (Opus) while the reporting agent runs on a cheaper one (Sonnet/Flash)

### 2. Agents Communicate Through the Hub

Agents don't talk to each other directly. They communicate through a central orchestrator. This prevents chaos and creates an audit trail.

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
- **Product catalog** (descriptions, pricing, inventory levels)
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

Over time, as the system learns and you trust it more, you adjust these thresholds upward. In our deployment:
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

At the core, the system runs on **OpenClaw** — an open-source AI agent framework that connects LLMs to real-world actions.

| Component | What We Use | Why |
|-----------|------------|-----|
| **Agent Runtime** | OpenClaw | Open source, local-first, 50+ integrations, active community |
| **Primary LLM** | Claude Opus/Sonnet | Best reasoning for complex business decisions |
| **Secondary LLM** | GPT-5.4 / Gemini Flash | Cost-effective for simpler tasks |
| **Hosting** | Dedicated server (Hetzner) | €40/mo, full control, EU data residency |
| **Agent-to-Agent** | ACP (Agent Communication Protocol) | Native cross-agent coordination |
| **Messaging** | WhatsApp, Slack, Email | Meet teams where they already work |
| **Memory** | Local files + structured knowledge base | No vendor lock-in, full data ownership |
| **Monitoring** | Built-in heartbeats + cron jobs | Self-healing, auto-restart |

**Total infrastructure cost:** ~€400-800/month depending on LLM usage

Compare this to the €12,000-15,000/month equivalent in human operational costs.

## What You Need to Get Started

**Minimum viable setup (1 agent):**
- A Linux server or VPS (€20-40/month)
- An LLM API key (Anthropic, OpenAI, or similar)
- OpenClaw installed and configured
- One channel connection (Slack, WhatsApp, or email)
- 2-4 hours for initial setup

**Full deployment (6 agents):**
- Dedicated server with good specs (€40-80/month)
- Multiple LLM API keys for redundancy
- All channel connections configured
- Integrations with your existing tools (Shopify, Klaviyo, etc.)
- 2-4 weeks for full implementation and tuning

The next chapters in the implementation kit walk through each agent in detail — what it does, how it's configured, and the specific results it delivers.

---

*Continue reading in [the Complete Implementation Kit](https://operai-six.vercel.app) →*