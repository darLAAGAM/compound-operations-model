# Chapter 14: Team Onboarding — Connecting Humans to the Swarm

## The Last Mile Problem

You've built the agents. You've connected the APIs. You've deployed the MCP server. The system works beautifully — for the person or small team who built it.

But the rest of your team? They're still using Shopify admin panels, switching between 8 browser tabs, and asking you to "pull that number from somewhere." They don't know the agents exist. Or they think AI is something that writes blog posts.

This chapter solves that. In under 5 minutes per person, every employee on your team gets the same AI superpowers you have — without understanding a single thing about agents, MCP, or prompts.

## What Employees Get

When a team member connects to the swarm, they can:

- **Ask questions in natural language** and get real answers from real data ("How much did we sell yesterday?")
- **Read from the shared brain** — every policy, process, and decision the company has documented
- **Write to the shared brain** — contribute knowledge that makes everyone smarter
- **Talk to any agent** — ask Finance Agent about P&L, CS Agent about tickets, Retail Agent about store traffic
- **Access every business tool** — Shopify, Klaviyo, Google Workspace, Holded, Stockagile — without needing credentials on their machine
- **Create and edit Google Sheets, Docs, Calendar** — the full Google Workspace, through Claude

Zero API keys on employee machines. Zero training on business tools. Zero risk of credential leaks.

## Architecture

```
┌─────────────────────────────────────┐
│    Team Member's Claude Desktop     │
│    (just a chat window)             │
└──────────────┬──────────────────────┘
               │ HTTPS (encrypted)
               │
┌──────────────▼──────────────────────┐
│    Cloudflare Tunnel                │
│    mcp.yourdomain.com/sse           │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│    MCP Server (your VPS)            │
│    44 tools · role-based access     │
│    all credentials server-side      │
└──────────────┬──────────────────────┘
               │
    ┌──────────┼──────────┐
    ▼          ▼          ▼
 Shopify    Agents     Brain
 Klaviyo    (6 AI)     (400+ docs)
 Holded     Strategy Agent    Policies
 GA4        CS Agent    Processes
 Meta       Finance Agent    Decisions
 Slack      Retail Agent       Metrics
 GWorkspace Marketing Agent  Knowledge...        Merchandising Agent...
```

The critical design choice: **employees never touch the infrastructure layer.** They talk to Claude. Claude talks to the MCP server. The MCP server talks to everything else. If you change a tool, update an API, or add a new agent — nothing changes for the employee.

## Setup Per Employee (5 Minutes in the Reference Deployment)

### Prerequisites
- Claude Pro subscription (€20/month) — the company can cover this
- A computer (Mac or Windows)

### Step 1: Install Node.js

Node.js is required for the MCP bridge. It's a one-time install.

**Mac:**
```bash
curl -fsSL https://fnm.vercel.app/install | bash && source ~/.bashrc && fnm install --lts
```

**Windows:** Download from nodejs.org, install with defaults, restart.

### Step 2: Add MCP Configuration

**Mac** — Open Terminal, paste:
```bash
mkdir -p ~/Library/Application\ Support/Claude && cat > ~/Library/Application\ Support/Claude/claude_desktop_config.json << 'EOF'
{
  "mcpServers": {
    "your-brand": {
      "command": "npx",
      "args": ["mcp-remote", "https://mcp.yourdomain.com/sse"]
    }
  }
}
EOF
```

**Windows** — Create `%APPDATA%\Claude\claude_desktop_config.json` with:
```json
{
  "mcpServers": {
    "your-brand": {
      "command": "npx",
      "args": ["mcp-remote", "https://mcp.yourdomain.com/sse"]
    }
  }
}
```

### Step 3: Restart Claude Desktop

Quit completely, reopen. The tools icon should show 44 tools connected.

### Step 4: Test

Ask: "What were yesterday's sales?" — If Claude responds with real data, the employee is connected.

That's it. No API keys. No environment variables. No Docker. No terminal skills beyond copy-paste.

## Access Control

Not every employee should have the same access. The MCP server supports role-based permissions:

| Role | Can Read | Can Write | Example Employees |
|------|----------|-----------|-------------------|
| **Admin** | Everything | Everything (brain, files, shell) | Founder, CTO |
| **Team** | All APIs, brain, memory | Business APIs only | Finance, Marketing, Ops |

Each employee gets a unique API key (`lgm_{32-char-hex}`) stored server-side. The key determines their role. Keys can be revoked individually without affecting anyone else.

### What Team Members Cannot Do
- Execute shell commands on the server
- Write to the brain (read-only for now — can be unlocked per person)
- Access raw config files or credentials
- Modify agent behavior or prompts

## The Shared Brain

The most powerful feature isn't data access — it's the shared brain. Every agent and every connected human reads from and writes to the same knowledge base.

### Structure
```
brain/knowledge/
├── the-brand/          # Company knowledge
│   ├── finance/     # P&L rules, payment terms, tax info
│   ├── operations/  # Shipping, returns, warehouse processes
│   ├── product/     # Collections, sizing, materials
│   ├── retail/      # Store hours, staff, procedures
│   ├── marketing/   # Campaigns, segments, brand guidelines
│   └── team/        # Org chart, roles, contacts
├── platform/        # System documentation
└── projects/        # Active initiatives
```

### How Employees Interact with the Brain

**Reading** (everyone can do this):
- "What's our return policy?"
- "Search the brain for wholesale pricing"
- "What did we decide about the new store location?"

**Writing** (admin or unlocked):
- "Add to the brain that Wholesale Account X requires 50% deposit upfront"
- "Document that the flagship store closes at 20:00 on Saturdays"
- "Update the brain: WELCOME15 code only works on first purchase"

Every approved write makes the entire system smarter. When an employee documents a supplier quirk, every agent — and every other employee — can find that information from that moment forward.

### The Compound Effect

This is where the Compound Operations Model earns its name:

1. **Week 1:** Employee documents 3 supplier payment terms
2. **Week 2:** Finance agent uses those terms to flag a late payment automatically
3. **Week 3:** Another employee asks about the same supplier and gets an instant answer
4. **Month 2:** The brain has 50 new facts. Agents make better decisions. Employees get faster answers.
5. **Month 6:** The brain is the single source of truth for the entire company

No training needed. No wiki to maintain. No Notion pages to organize. The brain is just... there. And it gets better every day because the people who know the answers are writing them down in the same place the AI looks for answers.

## Google Workspace Integration

Through the MCP server, every connected employee can work with Google Workspace using natural language:

### Sheets
- "Create a spreadsheet with March sales by channel"
- "Add a row to the inventory tracker: Item A, M, 15 units"
- "Read the P&L sheet from the finance manager's Drive"

### Gmail
- "Show me unread emails from suppliers"
- "Draft a reply to the last email from Supplier X"

### Calendar
- "What's on my calendar tomorrow?"
- "Schedule a meeting with the finance manager for Thursday at 10am"

### Drive
- "Find the current season sourcing document"
- "Search Drive for the brand guidelines PDF"

All of this works because the MCP server uses Domain-Wide Delegation — a Google Workspace admin feature that lets the server act on behalf of any user in the organization. The employee doesn't configure anything. They just ask Claude, and Claude does it.

## Talking to Agents

Every employee can talk to any of the 6 agents through their Claude:

| Agent | What to ask | Example |
|-------|-------------|---------|
| **Strategy Agent** | General operations, company data | "Ask Strategy Agent for yesterday's revenue breakdown" |
| **CS Agent** | Customer service, tickets | "Tell CS Agent to check today's open tickets" |
| **Finance Agent** | Finance, P&L, invoices | "Ask Finance Agent for the Q1 P&L" |
| **Retail Agent** | Retail, store performance | "Ask Retail Agent how Store A did this week" |
| **Marketing Agent** | Digital marketing, ads, email | "Ask Marketing Agent for Meta Ads ROAS" |
| **Merchandising Agent** | Inventory, merchandising | "Ask Merchandising Agent about sell-through rates" |

The syntax is simple: "Ask [agent name] about [topic]" or "Tell [agent name] to [action]."

## Rollout Strategy

Don't roll out to 20 people at once. Use this sequence:

### Week 1: Power Users (2-3 people)
Pick the people who already use ChatGPT or Claude. They'll find bugs, figure out the best prompts, and become internal evangelists.

### Week 2: Department Leads (4-5 people)
Finance lead, CS lead, retail manager, marketing lead. These people will use it for real work and give feedback on what's missing.

### Week 3: Full Team
By now you have working examples, a list of "things to try," and 5 colleagues who can help troubleshoot. Send the setup guide and let people explore.

### Ongoing
- Share "prompt of the week" — real examples that worked
- Encourage brain writes — the more people contribute, the more valuable the system becomes
- Track usage — the MCP server logs every tool call

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| "No tools connected" | Check Node.js: `node -v`. If missing, reinstall. |
| "Connection error" | Server may be restarting. Wait 2 minutes. |
| First query is slow | Normal — first SSE connection takes 5-10 seconds. |
| "Tool not found" | Restart Claude Desktop completely (quit + reopen). |
| Wrong data | Check if the query is ambiguous. Be specific about dates and channels. |

For anything else: contact the founder or check `#ai-agents` in Slack.

## Security Model

- **Zero credentials on employee machines** — all API keys, tokens, and passwords stay on the MCP server
- **Encrypted in transit** — Cloudflare Tunnel provides HTTPS/TLS
- **Role-based access** — admins vs. team, individually revocable
- **Audit trail** — every tool call is logged with timestamp and user
- **No PII exposure** — employees access tools through the AI layer, never raw database connections

## Cost Per Employee

| Item | Cost | Notes |
|------|------|-------|
| Claude Pro subscription | €20/month | Can be covered by company |
| MCP server | €0 incremental | Already running for agents |
| Cloudflare Tunnel | €0 | Free tier |
| **Total per employee** | **€20/month** | |

For context: a single Shopify admin license costs €32/month, gives access to one system, and requires training. Claude + MCP gives access to everything and requires no training.

## What This Changes

Before:
- Employee needs X data → asks someone → waits → gets partial answer
- New policy decided → lives in someone's head → forgotten
- Tool credentials → scattered across 15 systems → security risk

After:
- Employee needs X data → asks Claude → gets answer in seconds
- New policy decided → written to brain → available to everyone forever
- Tool credentials → one server → zero on employee machines

The system is not just the agents anymore. It is the agents, the brain, and every human in the company — all connected, all learning, all getting smarter together.

---

*This chapter represents the final layer of the Compound Operations Model™. The technology is ready. The agents are running. The brain is growing. The only thing left is to connect the humans.*


## AI Adoption Framework (L0-L3)

Based on the approach that achieved 99.5% active adoption in a production deployment:

### L0 — Observer
- Uses generic AI chatbots occasionally
- Hasn't changed any workflow
- **Expectation:** exit L0 within first week. If no progress, manager conversation.

### L1 — Active User
- Connected to the shared brain via Claude Desktop / MCP
- Uses brain_search before asking questions about the brand
- Has completed the initialization prompt
- **Target:** entire team at L1 within 30 days of deployment

### L2 — Builder
- Has built something that automates part of their job
- Uses skills and tools autonomously
- Contributes by writing to the brain when they learn something new
- Shares what they build with the team
- **Target:** 25-30% of team at L2 within 60 days

### L3 — Multiplier
- Builds tools/workflows that benefit other teams
- Creates new skills or improves existing ones
- Teaches others how to use the system
- AI reference person in their department
- **Target:** 2-3 people at L3 within 6 months

### Measurement
- AI level reviewed in monthly check-ins
- Sustained L0 (>30 days without brain usage) → manager conversation
- L2+ achievements celebrated in All Hands
- New hires must demonstrate AI aptitude during selection process

### Day 1 Mandatory Setup
Every new hire completes on their first day:
1. Install Claude Desktop + connect to MCP (30 minutes with manager)
2. Run initialization prompt (1 hour of guided exploration)
3. Manager verifies: MCP connected, 44 tools visible, brain_search works
4. First real task using AI assigned (due by end of Week 1)
5. First task shared in #ai Slack channel (public commitment)

**The biggest surprise:** it wasn't who built the most. It was how many people had been waiting for permission to build at all.

---

## The Three Role Profiles (McKinsey 2025 + Production Evidence)

McKinsey's September 2025 agentic-organization paper identifies **three emerging talent profiles** that will replace traditional job descriptions as AI agents take over execution. The L0-L3 adoption framework above tells you how far along each employee is in the transition. This section tells you **where they are going** — the stable state after L3.

### Profile 1 — M-shaped Supervisor

> *"Broad generalists fluent in AI, orchestrating agents and the hybrid workforce across domains."* — McKinsey

**What they do:** own end-to-end outcomes that span 2-4 domains. They don't personally handle CS tickets, reconcile invoices, or write campaign copy — they steer the agents that do, set policy, catch patterns across domains, and intervene only on ambiguous or high-stakes cases.

**Required skills:**
- Higher cognitive: critical thinking, systems design, end-to-end problem solving
- AI fluency: can read an agent's output, spot failure modes, update a SOUL.md prompt
- Socioemotional: hires and upskills T-shaped and frontline roles
- Domain: at least 2 domains at expert level (e.g. CS + Finance, or Retail + Merchandising)

**Typical titles in a €10-50M consumer brand:**
- COO, Head of Operations, VP Commerce, Chief of Staff
- In smaller brands: the founder is the first M-shaped supervisor

**How many per brand:** 2-5. McKinsey: *"a human team of two to five people can already supervise an agent factory of 50 to 100 specialized agents."* In the reference deployment: 1 founder + 2 senior ops managers = 3 M-shaped, orchestrating 7 agents (+ 44 MCP tools + 167 skills) across the entire business.

**Typical training path (from L3):**
- 2-3 months of cross-domain rotations (CS ↔ Finance ↔ Marketing)
- Ownership of one SOUL.md end-to-end (writing, iterating, measuring outcomes)
- Exposure to the compliance layer (DPIA, AI Act, Annex III)
- Tool literacy across all 44 MCP tools

### Profile 2 — T-shaped Specialist

> *"Deep specialists who reimagine workflows, handle exceptions, and safeguard quality."* — McKinsey

**What they do:** own one domain at depth. They fine-tune the agent that serves that domain, handle edge cases the agent can't classify, and ensure quality. They are the humans "in the loop" for ambiguous decisions that the M-shaped supervisor doesn't have bandwidth for.

**Required skills:**
- Higher cognitive: deep expertise in their domain (CS policy, finance accounting principles, brand voice, retail operations)
- AI fluency: can tune prompts, review tool outputs, detect hallucinations, design new skills
- Domain: expert-level in exactly one area

**Typical titles:**
- CS Manager, Finance Controller, Merchandising Lead, Retail Operations Manager, Brand Director
- One per domain, sometimes two per domain in larger brands

**How many per brand:** 5-10. One per active domain (CS, Finance, Ops, Marketing, Merch, Retail, Wholesale, HR), sometimes with a deputy.

**Typical training path (from L2):**
- 3-month deep-dive into their domain agent (read every SOUL.md revision, every memory log, every lesson)
- Trained to write and revise their agent's SOUL.md themselves
- Authored at least 3 new MCP skills for their domain
- Authored at least 5 pattern entries for the cross-company library

### Profile 3 — AI-Empowered Frontline

> *"Employees in sales, service, HR, or operations who spend less time on systems and more time with humans."* — McKinsey

**What they do:** the socioemotional work. VIP customer handling, high-touch wholesale relationships, retail store conversion, creative direction, hiring interviews. The agent does the heavy data work; the human does the part where being human matters.

**Required skills:**
- Socioemotional: empathy, brand voice, negotiation, trust-building
- Basic AI fluency: can ask the brain, act on agent drafts, escalate when agent confidence is low
- Domain: working proficiency in their frontline role

**Typical titles:**
- Retail Sales Associate, VIP CS Representative, Sales Development Rep, Account Executive, Creative Director, Buyer, Designer

**How many per brand:** the majority of the headcount. 70-80% of a deploying brand's team will be AI-empowered frontline.

**Typical training path (from L1):**
- 1-week onboarding on Claude Desktop + brand's MCP tools
- Scripted workflows for their role (pre-built prompts the agent understands)
- Clear escalation rules: when to bring the agent in, when to bypass, when to flag the M-shaped supervisor

## Matching Profiles to Compai's Seven Agents

Each of the 7 domain agents has a natural pairing with T-shaped specialists:

| Agent | Primary T-shaped owner | Frontline beneficiaries |
|---|---|---|
| CS Agent | CS Manager | VIP rep, retail support |
| Finance Agent | Controller / Finance Director | Bookkeeper, founder |
| Ops Agent | Operations Manager | Warehouse lead, logistics coord. |
| Marketing Agent | Brand / Growth Director | Content creator, designer |
| Merchandising Agent | Head of Merch | Buyer, planner |
| Retail Agent | Retail Operations Manager | Store manager, sales associate |
| HR Agent (HR Agent) | People Ops Lead | Every employee |

The M-shaped supervisor orchestrates across all seven. In a 8-figure brand, this is frequently the founder themselves. In a €30-50M brand, it's the COO + 1-2 Chiefs of Staff.

## The New `operai-init assess` Command

The repo can include an optional assessment helper:

```bash
operai-init assess <employee-name>
```

This runs a short conversational interview (8-10 questions) that classifies the employee into one of the three profiles and outputs a **personalized training path** with concrete milestones. The assessment writes to `knowledge/<brand>/team/<employee>/role-profile.md` alongside their `me.md` — the brain now knows each person's current profile, target profile, and next steps.

**Typical output:**

```
Role profile for: laura
Current: AI-Empowered Frontline (L1 adoption)
Target:  T-shaped Specialist — CS Domain
Next 90 days:
  - Month 1: pair with CS Agent (CS Agent) on 20% of tickets; review every draft
  - Month 2: write 2 new CS skills (refund policy variants, VIP detection rules)
  - Month 3: author first SOUL.md revision proposal
Training budget: €500 (internal review time)
```

The founder sees the full org's profile distribution via `operai-init assess --team`.

## Measuring the Shift

The agentic organization replaces linear career ladders with **role profile progressions**. Traditional KPIs (tickets closed, reports generated) stop mattering because the agent owns them. New KPIs:

| Metric | Measures | Target |
|---|---|---|
| Agent orchestration ratio | % of work done by agent vs human | 60%+ at Month 12 |
| Human interventions per domain | Count of decisions the agent escalated | Declining curve |
| Profile progression | L1 → T-shaped conversions over time | 25% of L1/L2 → T-shaped by Month 12 |
| SOUL.md revision velocity | Iterations per agent per quarter | 1-2 minor / 0.25 major |
| Cross-domain pattern contributions | Skills or patterns authored by T-shaped specialists | 1-2 per specialist per quarter |
| Socioemotional time ratio | % of frontline time with humans (vs systems) | 70%+ for frontline roles |

The last metric is the one McKinsey explicitly flags as the competitive advantage: *"employees in sales, service, HR, or operations who spend less time on systems and more time with humans."* The claim from the reference deployment is that a brand adopting the pattern — and measuring this ratio — can move from ~30% (typical pre-deploy) toward 70%+ within 12 months.

## What Doesn't Change

Three things remain anchored in humans regardless of profile:

1. **Final decision authority** on customer-facing actions (Article 50, Annex III)
2. **Culture and ethics** (the M-shaped supervisor is the ethical compass for their squad)
3. **Hiring new humans** (HR agent assists, never decides)

The point of the three-profile framework isn't to replace people. It's to give every person in a consumer brand a clear, measurable path from "L0 observer" to a stable role profile where their time compounds instead of drains.
