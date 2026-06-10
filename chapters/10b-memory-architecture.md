# Chapter 10b: Memory Architecture — How Your Agents Remember Everything

## The Problem No One Talks About

Most "AI agent" demos show you a chatbot that answers one question, forgets everything, and starts from zero next time. That's not an operating system. That's a goldfish with a nice UI.

Real operations demand **institutional memory.** Your CS agent needs to remember that customer who complained three times last month. Your finance agent needs to remember the payment term negotiation from February. Your ops agent needs to remember the supplier lead time change from last quarter.

Without memory, your agents are perpetual interns — capable, but always asking questions they should already know the answers to.

## The Three-Layer Memory Stack

We run a three-layer architecture that mirrors how good organizations actually retain knowledge:

```
┌──────────────────────────────────────────────────┐
│          Layer 3: WORKING MEMORY                  │
│     memory/YYYY-MM-DD.md (daily session logs)     │
│     What happened today. Raw. Detailed.           │
├──────────────────────────────────────────────────┤
│          Layer 2: SEMANTIC MEMORY                  │
│     SuperMemory (cloud-native vector search)       │
│     Auto-indexed. Cross-session. Searchable.       │
├──────────────────────────────────────────────────┤
│          Layer 1: INSTITUTIONAL KNOWLEDGE          │
│     brain/knowledge/ (Context Tree)                │
│     Organized by domain. Curated. Authoritative.   │
└──────────────────────────────────────────────────┘
```

Each layer serves a different purpose:

| Layer | What It Stores | How It Gets There | Who Uses It |
|-------|---------------|-------------------|-------------|
| **Working Memory** | Today's sessions, decisions, conversations | Pre-compaction flush (automatic) | Any agent reviewing recent history |
| **Semantic Memory** | Key facts, preferences, patterns | Auto-indexed per session | Any agent needing contextual recall |
| **Institutional Knowledge** | Policies, APIs, team info, playbooks | Curated (manual + automated mining) | All agents, always |

## Layer 1: The Context Tree

This is the foundation. Instead of dumping 100+ files in a flat directory and hoping the agent finds the right one, we organize knowledge as a **domain hierarchy:**

```
brain/knowledge/
├── _index.md                    ← Root map (auto-generated)
│
├── the-brand/                      ← Business domain
│   ├── _index.md
│   ├── finance/                 ← Salaries, P&L, equity, invoices
│   │   ├── _index.md
│   │   └── [15 files]
│   ├── strategy/                ← BP, competitive, legal, buying
│   │   └── [9 files]
│   ├── operations/              ← Shopify, 3PL, inventory, CS
│   │   └── [10 files]
│   ├── team/                    ← Org chart, meetings
│   │   └── [10 files]
│   └── marketing/               ← Weekly reports, SEO, PR
│       └── [13 files]
│
├── platform/                    ← Technical/infra domain
│   ├── agents/                  ← Agent configs, comms, setup
│   ├── auth/                    ← Credentials, access
│   ├── setup/                   ← Browser, bots, troubleshooting
│   └── config/                  ← Rules, lessons, hygiene
│
├── personal/                    ← Founder/operator context
└── projects/                    ← Side projects, R&D
```

### Why This Matters

**Without it:** Agent gets a finance question → searches 100+ files → might find the right one, might hallucinate.

**With it:** Agent gets a finance question → knows to look in `the-brand/finance/` → finds authoritative answer in seconds.

The `_index.md` files are auto-generated summaries that propagate upward. Change a file in `finance/`, the `_index.md` for `finance/` and `the-brand/` update automatically. This means every agent always has an accurate map of what knowledge exists and where.

### Implementation

Every `_index.md` contains:
- Domain description
- File count
- File listing with first heading extracted
- Last update timestamp

```markdown
# Finance Knowledge
**Files:** 15 | **Domain:** the-brand/finance

| File | Topic |
|------|-------|
| salarios-2026.md | Salary structure and ranges |
| bonus-policy.md | Performance bonus framework |
| invoice-pipeline.md | AP/AR automation pipeline |...
```

## Layer 2: Semantic Memory (SuperMemory)

> **⚠️ Production Update (March 2026):** After 6 months in production, we **removed SuperMemory** from all agents. The reasons:
> - Memory pollution was severe despite nightly dedup (90+ duplicates/week/agent wasn't enough)
> - The vector search often surfaced irrelevant memories, degrading response quality
> - The Context Tree (Layer 1) + Working Memory (Layer 3) proved sufficient for operations
> - Cost/benefit didn't justify the maintenance overhead
>
> **Our recommendation:** Start without SuperMemory. Add it later only if you find agents lacking cross-session context that the Context Tree doesn't cover. Most operational tasks don't need it — they need structured, current knowledge, not fuzzy recall.

SuperMemory is a cloud-native vector store that automatically indexes important information from every session. When an agent starts a new conversation, it gets a contextual recall of relevant memories.

**What gets stored:**
- Key decisions ("We decided to use Amphora as our 3PL")
- User preferences ("the founder prefers Slack for async, WhatsApp for urgent")
- Entity facts ("The brand's gross margin is 67%")
- Patterns ("Returns spike on Mondays after weekend orders")

**How agents use it:**
- Every new session gets a `supermemory_profile` injection — what the system knows about this user
- Agents can `supermemory_search` for specific context ("what did we decide about the Canada pricing?")
- Old memories can be `supermemory_forget` when outdated

**Key advantage:** Works across all agents, all sessions, no local state. Agent on Server A can recall what Agent on Server B learned last week.

### Multi-Agent SuperMemory

Every agent in the ecosystem has SuperMemory installed:

```
Strategy Agent  → SuperMemory (Hetzner)       ✓
CS Agent  → SuperMemory (Mac Mini)      ✓
Finance Agent  → SuperMemory (Mac Mini)      ✓
Retail Agent     → SuperMemory (Mac Mini)      ✓
Marketing Agent → SuperMemory (Mac Mini)     ✓
Merchandising Agent   → SuperMemory (Mac Mini)      ✓
```

This means the CS agent remembers that a VIP customer had a bad experience, even if the original complaint was handled by the hub agent three weeks ago.



## Layer 2 (Replacement): ByteRover Native Memory Plugin

After removing SuperMemory, we evaluated several alternatives. [ByteRover](https://byterover.dev) is now **fully operational on all agents** — `brv` CLI v2.6.0, running as a ContextEngine slot-exclusive plugin with safeguard compaction mode. Heartbeat every 30 minutes confirms health across the fleet. It solved the exact problems SuperMemory had — without the noise.

### Why ByteRover Over SuperMemory

| Problem with SuperMemory | ByteRover Solution |
|--------------------------|-------------------|
| Vector store accumulates garbage | File-based Markdown hierarchy — human-readable, diffable, auditable |
| Dedup cron removed 90+/week but couldn't keep up | LLM-driven curation with UPSERT/MERGE operations — duplicates never enter |
| Semantic search surfaced irrelevant memories | 4-tier retrieval: Cache → MiniSearch → LLM search → Recursive LLM (92.2% accuracy) |
| Opaque embeddings, no auditability | Plain Markdown files organized in semantic hierarchy |
| Broke when models changed | Model-agnostic — works with any LLM provider |

### How It Works

ByteRover integrates **natively** into OpenClaw's context assembly pipeline (via PR #50848). Instead of injecting memories as a separate step, it becomes part of the agent's prompt construction:

```
Agent receives message
  → ByteRover retrieves relevant knowledge (4-tier retrieval)
  → Injects into system prompt via ContextEngine.assemble()
  → Agent responds with full context
  → ByteRover curates new knowledge from the session
```

### The Three Layers (ByteRover's Architecture)

ByteRover maintains three layers that map directly to our existing stack:

| ByteRover Layer | Our Equivalent | What It Stores |
|----------------|---------------|----------------|
| **Context Tree** | `brain/knowledge/` (3,007 docs) | Deep structured knowledge, organized by domain |
| **Workspace Memory** | `MEMORY.md` + `SOUL.md` | Core rules, preferences, business snapshot |
| **Daily Memory** | `memory/YYYY-MM-DD.md` | Session notes, operational logs |

**The key insight:** ByteRover didn't replace our architecture — it **automated and improved** what we were doing manually. Our Context Tree becomes ByteRover's Context Tree. Our MEMORY.md becomes Workspace Memory. Our daily logs become Daily Memory. Same structure, native integration.

### Curation Operations

Instead of our custom Knowledge Mining cron extracting patterns with regex fallback, ByteRover provides five atomic operations with per-operation feedback:

| Operation | What It Does | Example |
|-----------|-------------|---------|
| `ADD` | Create new knowledge entry | "DHL Express rates changed to €4.50/package" |
| `UPDATE` | Replace existing content | Update salary ranges for 2026 |
| `UPSERT` | Add if new, update if exists | Customer VIP threshold changed |
| `MERGE` | Intelligently combine entries | Combine two partial supplier records |
| `DELETE` | Remove stale entries | Remove last season's product catalog |

**Crash safety:** All writes use `writeFileAtomic()` — if the process crashes mid-write, no corruption.

**Feedback loop:** If an operation fails, the LLM gets the error and can retry with a different approach. Our custom Knowledge Mining script had no feedback — it wrote and hoped.

### 4-Tier Retrieval Pipeline

This is the biggest upgrade over both SuperMemory (probabilistic vector search) and our brain_search (single-tier QMD):

| Tier | Method | Speed | When Used |
|------|--------|-------|-----------|
| **0** | Cache lookup | <1ms | Repeated queries, recent context |
| **1** | MiniSearch full-text | <100ms | Keyword matches, exact terms |
| **2** | LLM-powered search | ~1-2s | Semantic understanding needed |
| **3** | Recursive LLM Search | ~3-5s | Complex, multi-hop questions |

**Result:** 92.2% retrieval accuracy on LoCoMo and LongMemEval benchmarks. Most queries resolve at Tier 0-2 (under 100ms).

**Out-of-domain detection:** When a query falls outside stored knowledge, ByteRover explicitly says "I don't have information about this" instead of hallucinating. Critical for financial and CS responses.

### Installation

Requires OpenClaw v2026.3.22+:

```bash
# Install globally
npm install -g @byterover/byterover

# Add to openclaw.json plugins
{
  "plugins": {
    "entries": {
      "@byterover/byterover": {
        "enabled": true,
        "config": {
          "ownsCompaction": false,
          "contextTree": {
            "basePath": "brain/knowledge",
            "enabled": true
          }
        }
      }
    }
  }
}

# Restart gateway
openclaw gateway run --force
```

**`ownsCompaction: false`** — delegates memory compaction to OpenClaw's native runtime. ByteRover handles curation; OpenClaw handles session management.

### Multi-Agent Deployment

We deployed ByteRover across all 6 agents:

| Agent | Host | ByteRover Status |
|-------|------|-----------------|
| Strategy Agent | Hetzner VPS | ✅ Fully operational |
| CS Agent | Mac Mini | ✅ Fully operational |
| Finance Agent | Mac Mini | ✅ Fully operational |
| Retail Agent | Mac Mini | ✅ Fully operational |
| Marketing Agent | Mac Mini | ✅ Fully operational |
| Merchandising Agent | Mac Mini | ✅ Fully operational |

All agents share the same Context Tree via brain-sync (rsync every 30 minutes). ByteRover curates locally; rsync propagates globally. This means knowledge learned by the CS agent (CS Agent) becomes available to the Finance agent (Finance Agent) within 30 minutes.

### What About Claude Code and Claude Desktop?

ByteRover is an **OpenClaw plugin** — it doesn't run inside Claude Code or Claude Desktop. But the improvement flows to all Claudes indirectly:

1. **Better brain = better MCP queries.** ByteRover curates the Context Tree that Claudes access via `brain_search`/`brain_read`. Higher quality knowledge → better answers.

2. **Smarter agents = smarter `agent_send`.** When you ask Finance Agent for a P&L via Claude Code, Finance Agent now has 4-tier retrieval backing its response.

3. **Knowledge Mining → brain → MCP → everyone.** The cycle: agents learn → ByteRover curates → brain-sync propagates → MCP serves → any Claude can query.

Claude Code has its own memory system (`CLAUDE.md`, conversation context) that serves the power-user interface well. ByteRover serves the always-on operational agents.

### Cost

**€0/month additional.** ByteRover is a free npm package. The only incremental cost is the LLM tokens for curation operations (~€0.05-0.10/day per agent for Tier 2-3 retrieval). At scale across 6 agents: ~€10-18/month — negligible compared to the accuracy improvement.

## Layer 3: Working Memory (Daily Logs)

Every session's work is captured in `memory/YYYY-MM-DD.md` files via pre-compaction flush. These are the raw operational logs:

```markdown
# Memory — 2026-03-11

## Session 1: CS Ticket Review (~08:00 UTC)
- Processed 14 tickets: 9 auto-resolved, 3 escalated to the CS lead, 2 flagged for quality
- New pattern: 3 complaints about recent collection sizing on "Product X" → logged for product team
- Updated shipping policy knowledge (new DHL Express rates)

## Session 2: Weekly P&L (~10:00 UTC)
- Revenue W10: +12% vs W09
- COGS anomaly: leather supplier invoice 15% above PO → escalated to the finance manager...
```

### The Compaction Cycle (Live in Production)

Every day at 06:00 UTC, the **Knowledge Mining** cron job (`/scripts/knowledge-mining.sh`):

1. Reads the latest `memory/YYYY-MM-DD.md` file
2. Sends content to Claude Sonnet for intelligent extraction (with regex fallback if API unavailable)
3. Extracts durable patterns — categorized by domain: `the-brand/finance/`, `the-brand/operations/`, `platform/agents/`, etc.
4. Routes each finding to the correct folder, creating or appending to files
5. At 06:10 UTC, `generate-index.sh` rebuilds all 61 `_index.md` files across the Context Tree

**Real output from first run:** 8 durable findings extracted from a single day's memory log.

**Before:** Session logs pile up. Knowledge stays trapped in chat history. Nobody reads old logs.

**After:** Every day's operational intelligence gets distilled into the institutional knowledge base. The Context Tree grows organically from real operations.

```
memory/2026-03-11.md
  → extracts: "DHL Express rates changed"
    → routes to: the-brand/operations/shipping-rates.md
  → extracts: "Product X sizing complaints (3x)"
    → routes to: the-brand/operations/quality-alerts.md
  → updates: the-brand/operations/_index.md
```

## The Shared Brain

In a multi-agent setup, you need all agents reading from the same knowledge base. We solve this with a **shared brain via symlinks:**

```
Server (Strategy Agent):
  /root/strategy_agent-v2/brain/knowledge/    ← Source of truth

Mac Mini (all other agents):
  /Users/Shared/shared-brain/knowledge/  ← Synced copy
  
  /Users/cs_agent/cs_agent/brain/ → /Users/Shared/shared-brain/
  /Users/finance_agent/finance_agent/brain/ → /Users/Shared/shared-brain/
  /Users/retail_agent/retail_agent/brain/ → /Users/Shared/shared-brain/...
```

**Sync mechanism:** Bidirectional `rsync` via `brain-sync.sh`, running every 30 minutes:
1. Pull from Mac Mini first (captures agent-written knowledge)
2. Push from Hetzner (Strategy Agent as source of truth)
3. `--update` flag: most recent file wins conflicts
4. Filters: only `.md/.json/.txt/.yaml` — excludes credentials and PDFs

**Health monitoring:** `brain-sync-health.sh` runs every 2 hours, checking:
- Mac Mini reachability via SSH
- Sync freshness (alert if >2h stale)
- Total doc count (currently 3,007 docs, 15MB)

**Result:** Update a policy on the hub agent → all agents see the change within minutes. No manual copying. No drift.

## MEMORY.md — The Executive Summary

Every agent has a `MEMORY.md` injected into every prompt. This is the distilled, always-current summary:

```markdown
# MEMORY.md — Distilled Knowledge
*Last updated: 11 Mar 2026*

## Business Snapshot
- Revenue trend: +51% YoY
- Growth target: +57% YoY
- Gross Margin: 67%
- Team: 20 people

## Knowledge Base
→ See brain/knowledge/_index.md for full map
- the-brand/finance/ — 15 files
- the-brand/operations/ — 10 files
- platform/agents/ — 8 files...

## Key Decisions (Last 30 Days)
- Migrated 3PL to Amphora (Feb 2026)
- Launched wholesale agent (Mar 2026)
- Changed CS model from Opus → Sonnet (cost optimization)
```

This ensures every agent, every session, starts with current context — not a blank slate.

## What Makes This Different

### vs. RAG (Retrieval-Augmented Generation)
Most AI tools use RAG: chunk documents, embed them, retrieve on query. That works for search. It doesn't work for operations.

Our Context Tree is **structured by domain,** not by embedding similarity. When the finance agent needs salary data, it doesn't search a vector store and hope the right chunk surfaces. It goes to `the-brand/finance/salarios-2026.md`. Deterministic, not probabilistic.

### vs. Fine-Tuning
Fine-tuning bakes knowledge into model weights. It's expensive, slow to update, and you lose it when you upgrade models. Our knowledge layer is model-agnostic — switch from Claude to GPT to Gemini and your institutional memory stays intact.

### vs. Chat History
Most tools "remember" by stuffing old chat messages into context. That works until the context window fills up (and it fills up fast with operational data). Our three-layer stack means agents always have the right amount of context: MEMORY.md for essentials, SuperMemory for recall, Context Tree for deep lookup.

### vs. ByteRover / Other Memory Tools
We evaluated ByteRover (popular on ClawHub) and took inspiration from its Context Tree concept. But we built it natively:
- No external daemon dependency
- Integrated with our multi-agent sync (shared brain)
- Domain-organized for business operations, not just code
- Knowledge Mining cron tailored to operational patterns

## Setup Guide

### Step 1: Create the Context Tree Structure

```bash
mkdir -p brain/knowledge/{your-brand}/{finance,operations,team,marketing,strategy}
mkdir -p brain/knowledge/platform/{agents,auth,setup,config}
```

### Step 2: Populate Core Knowledge

Start with these critical files:

| File | Content | Priority |
|------|---------|----------|
| `your-brand/operations/products.md` | Product catalog | Day 1 |
| `your-brand/operations/policies.md` | Returns, shipping, warranty | Day 1 |
| `your-brand/team/org-chart.md` | Who does what | Day 1 |
| `your-brand/operations/faq.md` | Top 30 customer questions | Day 2 |
| `your-brand/marketing/brand-voice.md` | Tone guidelines | Day 2 |
| `platform/agents/agents.md` | Agent roles and configs | Day 3 |
| `platform/config/rules.md` | Operational rules and guardrails | Day 3 |

### Step 3: Generate Index Files

```bash
# Auto-generate _index.md for every directory
for dir in $(find brain/knowledge -type d); do
  count=$(find "$dir" -maxdepth 1 -name "*.md" ! -name "_index.md" | wc -l)
  echo "# $(basename $dir)" > "$dir/_index.md"
  echo "**Files:** $count" >> "$dir/_index.md"
  echo "" >> "$dir/_index.md"
  for f in "$dir"/*.md; do
    [ "$(basename $f)" = "_index.md" ] && continue
    heading=$(head -1 "$f" | sed 's/^# //')
    echo "- [$(basename $f)]($(basename $f)) — $heading" >> "$dir/_index.md"
  done
done
```

### Step 4: Install SuperMemory

```bash
# On each agent
openclaw extensions install openclaw-supermemory
openclaw restart
```

### Step 5: Set Up Knowledge Mining Cron

Create a daily cron job that:
1. Reads the latest `memory/YYYY-MM-DD.md`
2. Extracts durable decisions, new info, changed processes
3. Creates or updates files in the appropriate domain folder
4. Regenerates affected `_index.md` files

### Step 6: Configure Shared Brain (Multi-Agent)

```bash
# On shared server
mkdir -p /shared/brain/knowledge
# Copy your Context Tree here

# On each agent's workspace
ln -s /shared/brain brain
```

Sync with: `rsync -avz --delete source/ shared/brain/knowledge/`

## Memory Hygiene: Automated Deduplication

Here's the dirty secret of AI memory: it accumulates garbage. Every agent, every session, generates memories. Many are duplicates. "the founder is the CEO" gets stored 15 times with slight variations. API access facts repeat across sessions. Troubleshooting states from months ago linger like digital cobwebs.

Left unchecked, memory pollution degrades agent performance:
- Irrelevant memories crowd out useful context
- Duplicate facts consume recall slots
- Stale operational state causes confusion

### The Automated Solution

We run a **nightly dedup cron** on every agent. It's dead simple:

```
Schedule: 03:45 UTC daily (staggered per agent)
Type: Isolated agent turn (no human interaction)
Task: Search SuperMemory for duplicate/redundant entries,
      delete noise, keep most informative version
```

**Cron job definition:**
```json
{
  "name": "SuperMemory Dedup",
  "schedule": { "kind": "cron", "expr": "45 3 * * *" },
  "sessionTarget": "isolated",
  "payload": {
    "kind": "agentTurn",
    "message": "Execute automated SuperMemory cleanup: Search for duplicate memories with high overlap. Focus on: multiple versions of same facts about people/roles/tools, temporal noise like troubleshooting states, redundant access permission statements. Delete duplicates keeping most informative version. Report stats briefly."
  },
  "delivery": { "mode": "none" }
}
```

### Fleet Deployment Pattern

For multi-agent setups, deploy the dedup cron to all agents:

```bash
# For each agent on the shared host
for AGENT in cs_agent retail_agent finance_agent marketing_agent merchandising_agent; do
  PORT=$(get_agent_port $AGENT)
  TOKEN=$(get_agent_token $AGENT)
  
  OPENCLAW_ALLOW_INSECURE_PRIVATE_WS=1 \
  OPENCLAW_GATEWAY_URL=ws://<host-ip>:$PORT \
  openclaw cron add \
    --name "SuperMemory Dedup" \
    --cron "45 3 * * *" \
    --session isolated \
    --message "Execute automated SuperMemory cleanup..." \
    --no-deliver \
    --token $TOKEN
done
```

**Key gotcha:** When deploying via SSH to agents on a shared host:
- Use `sudo -u <agent> bash -l -c '...'` to inherit the correct PATH
- Set `OPENCLAW_ALLOW_INSECURE_PRIVATE_WS=1` for private ws:// connections
- Agents bind to Tailnet IP, not localhost — use the correct IP:port

### Results in Production

After 2 weeks of automated dedup across 6 agents:
- **~90+ duplicate memories removed** per agent per week
- Common duplicates: identity facts (15+), API permissions (10+), troubleshooting logs (15+)
- Agent recall accuracy improved — less noise means better signal
- Zero human maintenance required

### Device Pairing for Fleet Deployment

When deploying cron jobs remotely, you may need to pair the CLI with each agent's gateway. The pairing protocol uses Ed25519 signatures:

1. Each agent has `identity/device.json` with a keypair
2. The gateway maintains `devices/paired.json` with authorized devices
3. The CLI authenticates by signing a challenge with its private key

**Critical detail:** The `publicKey` in `paired.json` must be the **raw 32-byte Ed25519 key** (base64url, no padding) — NOT the full DER/PEM encoding. To extract:

```python
import base64
# From PEM → DER → skip 12-byte SPKI header → raw key
der_bytes = base64.b64decode(pem_b64)
raw_key = der_bytes[-32:]
raw_b64url = base64.urlsafe_b64encode(raw_key).rstrip(b'=').decode()
```

This is a common gotcha — using the full DER key (44 bytes) instead of the raw key (32 bytes) causes "pairing required" errors even though the device appears paired.

## Cost

The entire memory architecture costs **€0/month in additional infrastructure.** It's files on disk, organized intelligently. SuperMemory is included with OpenClaw. The Knowledge Mining cron uses the same LLM you're already paying for (~€0.10/day in API tokens for the daily digest).

Compare that to:
- Pinecone: $70+/month
- Weaviate Cloud: $25+/month
- Custom RAG pipeline: Engineering time + vector DB costs

---

## Summary

| Component | Purpose | Cost | Setup Time |
|-----------|---------|------|------------|
| Context Tree | Structured institutional knowledge | €0 | 2-3 hours |
| ~~SuperMemory~~ | ~~Semantic cross-session recall~~ | ~~Deprecated~~ | — |
| ByteRover Native | 4-tier retrieval + LLM curation | €0 (npm package) | 10 minutes |
| Working Memory | Daily operational logs | €0 | Automatic |
| Knowledge Mining | Auto-distill logs → knowledge | ~€3/month | 30 minutes |
| Shared Brain | Multi-agent knowledge sync | €0 | 1 hour |
| MEMORY.md | Executive context injection | €0 | 30 minutes |

**Total: ~€3/month for a complete institutional memory system.**

The brands that build memory from day one will have an insurmountable advantage by month six. Their agents won't just be tools — they'll be the institutional memory of the organization, compounding every day.

---

*Next: [Chapter 11 — 30-Day Implementation Plan →](11-implementation.md)*
