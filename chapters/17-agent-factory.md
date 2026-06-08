# Chapter 17: The Agent Factory Pattern

> **Appendix · Technical depth.** This chapter is for operators or engineers deploying the brain themselves. It covers implementation details that aren't needed for understanding the conceptual architecture. Skip if you're reading for strategy.

## Why this chapter exists

McKinsey's September 2025 framework (mapped in Ch.15) makes one quantitative claim that matters more than any other:

> *"A human team of two to five people can already supervise an agent factory of 50 to 100 specialized agents running an end-to-end process."*

In repo v2.5 and earlier, Compai shipped **7 monolithic domain agents**: one CS agent, one Finance agent, one Ops agent, etc. That architecture works for a 8-figure brand — the reference deployment ran 12+ months this way. But it leaves unexploited the ratio McKinsey identifies as the agentic organization's defining advantage: **1 human to 10-20 specialized agents per domain**.

repo v2.6 refactors each domain agent into a **factory** of 5-12 specialized sub-agents. This chapter documents the pattern, the contract model, and the reference implementation (CS agent factory, 10 sub-agents) that ships in v2.6.

## The pattern

A domain **agent factory** consists of:

1. **Parent SOUL.md** at `agents/<domain>/SOUL.md` — the orchestrator role, steering + dispatch logic, escalation rules
2. **Sub-agent SOULs** at `agents/<domain>/sub-agents/<name>/SOUL.md` — each with a tight single-responsibility contract
3. **Factory config** at `agents/<domain>/factory.yml` — declares the sub-agent list, their invocation order, and their input/output schemas
4. **Shared memory** at `brain/memory/<domain>/` — the parent and all sub-agents write to the same domain-scoped log

At runtime, the parent is invoked by an event (ticket arrives, daily cron fires, order placed). It dispatches to sub-agents in order, passing structured outputs between them. Humans supervise the parent's decisions, not the sub-agents — the ratio compresses.

## The sub-agent contract

Every sub-agent has:

- **One input schema** (what it receives from the parent)
- **One output schema** (what it returns)
- **One SOUL.md** (50-150 lines — focused, not sprawling)
- **Zero tool access by default** (pure LLM function; escalates to parent for I/O)

Sub-agents never call other sub-agents directly. The parent is the only dispatcher. This keeps the blast radius of any prompt injection or hallucination bounded to one atomic step.

Sample contract (`factory.yml` fragment for CS domain):

```yaml
domain: cs
parent_soul: SOUL.md
sub_agents:
  - name: triage
    soul: sub-agents/triage/SOUL.md
    inputs:  [raw_ticket]
    outputs: [category, priority, sentiment, language]
    order:   1
  - name: policy-lookup
    soul: sub-agents/policy-lookup/SOUL.md
    inputs:  [category, ticket_summary]
    outputs: [applicable_policies, policy_confidence]
    order:   2
  - name: drafter
    soul: sub-agents/drafter/SOUL.md
    inputs:  [ticket, applicable_policies, brand_voice]
    outputs: [draft_reply, action_recommended]
    order:   3
  #... 7 more sub-agents
```

## The reference CS factory (10 sub-agents)

Shipped in repo v2.6 under `repo/init/agent-factory-templates/cs/`:

| # | Sub-agent | Role | Typical tokens/call |
|---|---|---|---|
| 1 | **triage** | Classify ticket into [shipping / refund / product / complaint / other], assign P1-P4 priority, detect sentiment (-1..1), identify language (ES/EN/FR/DE) | 300 |
| 2 | **policy-lookup** | Given category + ticket summary, retrieve applicable policies from `brain/knowledge/<brand>/cs/policies/` via brain_query | 500 |
| 3 | **vip-detector** | Cross-reference customer against VIP list (Pattern Library entry), flag special handling required | 150 |
| 4 | **language-detect** | Deep language + dialect check (ES-ES vs ES-LATAM, EN-UK vs EN-US) for brand-voice calibration | 100 |
| 5 | **sentiment-deep** | Detect escalation risk: anger, threat to churn, legal/press signals. Returns 0-10 escalation score | 400 |
| 6 | **refund-calc** | Given policy + order value, compute refund amount per brand's tiered rules | 200 |
| 7 | **brand-voice-check** | Validate draft text against brand style guide at `brain/knowledge/<brand>/marketing/brand-voice.md` | 400 |
| 8 | **escalation-scorer** | Decide: auto-send / human-review / escalate-to-supervisor, with rationale | 250 |
| 9 | **drafter** | Compose the customer-facing reply given policies + brand voice + refund (if any) + sentiment guidance | 800 |
| 10 | **follow-up-scheduler** | Determine when to follow up if no customer response (default: 48h, 7d, 14d), schedule via cron | 150 |

**Total per ticket:** ~3,250 tokens input, ~700 output. At Haiku 4.5 batch pricing ($0.50/M input, $2.50/M output): **~€0.002 per ticket**. For a brand processing 500 tickets/week: **€4/month**.

Against the old monolithic CS agent (one big SOUL, one big LLM call per ticket, ~€0.015 per ticket): factories are **~7× cheaper per ticket** because each sub-agent uses a smaller prompt and shorter output schema. Quality also improves because each sub-agent's context window is focused.

## Human supervision model

The M-shaped supervisor (Ch.14) reviews the **parent's aggregated decision**, not each sub-agent's output. The parent SOUL is explicitly written to:

1. Summarize the sub-agent chain's outputs in one paragraph
2. Flag confidence < 0.85 or internal disagreement for human review
3. Log the full trace to `brain/memory/cs/YYYY-MM-DD.log`
4. Escalate to the **critic meta-agent** (Ch.16) for high-stakes cases

The supervisor's review surface is one ticket summary per flagged case, not ten sub-agent outputs. Ratio compresses from "10 agents per human per day" to "10 decisions per human per day" — same order of magnitude as monolithic agents, but with each decision backed by 10x more specialized processing.

## Why this changes the economics

Three shifts compound:

1. **Cheaper per-task cost** (sub-agents use smaller prompts)
2. **Higher quality** (each sub-agent specialized, fewer tokens wasted on irrelevant context)
3. **Easier to iterate** (tune one sub-agent without touching others — small SOUL files, clear contracts)

The result is the McKinsey ratio in practice. A CS team of 1 T-shaped specialist + 1 M-shaped supervisor can now orchestrate a CS factory of 10 sub-agents handling 500+ tickets/week at €4/month LLM cost.

## Rolling out factories

repo v2.6 ships the CS factory as the reference. The other 6 domain agents can be refactored to factories using the same pattern:

| Domain | Planned factory size | Most valuable sub-agents |
|---|---|---|
| CS | 10 (shipped) | (this chapter) |
| Finance | 8 | P&L-drafter, AR-chaser, reconciliation-worker, anomaly-detector, invoice-parser, COGS-computer, VAT-validator, closing-checker |
| Ops | 9 | inventory-reconciler, 3PL-coord, demand-forecaster, stockout-predictor, reorder-calculator, lead-time-tracker, location-balancer, returns-processor, carrier-selector |
| Marketing | 12 | campaign-brief, audience-segmenter, copy-drafter, subject-line-tester, send-time-optimizer, list-hygiene, flow-builder, attribution-modeler, GEO-monitor, ads-audit, creative-brief, brand-voice-check |
| Merchandising | 10 | sell-through-analyzer, size-curve-optimizer, reorder-recommender, markdown-sequencer, allocation-planner, vendor-performance, colorway-proposer, category-rebalancer, end-of-season-clearance, stock-health-scorer |
| Retail | 7 | traffic-parser, conversion-investigator, staffing-optimizer, till-reconciler, ticket-per-transaction-analyzer, store-comparison, manager-briefer |
| HR (HR Agent) | 6 | onboarding-checklist, vacation-balancer, payroll-prep, policy-lookup, expense-categorizer, team-mood-monitor |

Total after full rollout: **~62 sub-agents** across 7 factories. Squarely inside McKinsey's "50-100 specialized agents" prediction.

**Roadmap:**
- v2.6 (shipped): CS factory — 10 sub-agents, reference implementation
- v2.7: Finance + Ops factories (high-value, low-risk)
- v2.8: Marketing + Merch factories (highest complexity, most valuable)
- v2.9: Retail + HR factories (last, smallest brand value relative to cost)

## What the founder deploys in v2.6

```bash
# Installs the CS factory alongside the existing monolithic SOULs:
operai-init factory enable --domain cs

# Lists available factories
operai-init factory list

# Shows sub-agent details for one factory
operai-init factory show --domain cs

# Disables (rolls back to monolithic SOUL)
operai-init factory disable --domain cs --reason "rollback for debugging"
```

The monolithic SOULs remain in place until the factory is explicitly enabled, so there's no disruption to existing deployments. Founders upgrading from v2.5 → v2.6 see no behavioural change unless they opt in.

## What this does NOT do in v2.6

Honest scoping:

1. **No real LLM orchestration runtime** — the factory config + sub-agent SOULs ship, but agent-runner still runs a heartbeat (see Ch.11e). The full runtime — spawning Claude API calls per sub-agent, passing outputs, aggregating — lands in **v0.7**. Ch.17 documents the pattern and ships the templates; v0.7 makes it live.
2. **Only CS factory as reference** — 6 other domains will port over as we validate the pattern in production.
3. **No cross-factory coordination** — for now, each factory is self-contained. A CS ticket never invokes the Finance factory. Cross-domain workflows are v0.8+.

## Commercial framing

Agent Factory remains in the repo (no separate tier). the founder's decision on v2.5 held: the McKinsey framework and its implementation are differentiators, not upsells. A team forking the open-source repo today gets:

- Seven monolithic agents (still the default)
- CS factory reference in v2.6 (opt-in via `operai-init factory enable`)
- Full factory rollout as v2.7-v2.9 ship

This doubles the agent density per human without doubling the repo price. The competitive moat widens.

---

→ Back to [Ch.16 Agentic Governance](16-agentic-governance.md) · Forward to [Ch.18 Sharing The Load](18-sharing-the-load.md) *(coming in v2.7)*
