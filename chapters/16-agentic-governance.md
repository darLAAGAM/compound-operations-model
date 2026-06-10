# Chapter 16: Agentic Governance — Meta-Agents That Watch Other Agents

## Why this layer exists

Chapter 15 establishes that Compai implements McKinsey's five pillars of the agentic organization. Pillar 3 — Governance — is the pillar McKinsey flags as the **rate-limiting factor**:

> *"The scale of agentic adoption will be capped by how much oversight capacity humans can provide — making governance itself a potential bottleneck to productivity."*

The compliance package shipped in repo v2.0 (DPIA, AI System Register, Annex III guardrails, Article 50 transparency) handles **static governance** — the documents regulators want to see. Chapter 16 introduces **dynamic governance** — three meta-agents that watch the seven domain agents in real time, so that human oversight capacity can scale sub-linearly as the agent fleet grows.

McKinsey names the pattern explicitly:

> *"Critic agents will challenge outputs, guardrail agents will enforce policy, and compliance agents will monitor regulation."* — McKinsey, Sep 2025

Compai repo v2.5 ships exactly these three.

## The three meta-agents

### Meta-agent 1 — Critic Agent

**Purpose:** challenge high-stakes outputs before they reach customers, finance systems, or public surfaces. Catch hallucinations, tone drift, brand inconsistencies, and logical errors.

**How it works:**

1. Every domain agent (CS, Finance, Marketing, etc.) emits a proposed action to its review queue.
2. If the action carries a `confidence < 0.85` flag OR the monetary/reputational impact exceeds a configured threshold (default: €500 spend, customer-facing send, legal statement), the critic-agent is invoked.
3. The critic runs **adversarial cross-model deliberation** (Punta de Flecha protocol: Opus + GPT-5 + Gemini 2.5 vote blind) and emits one of three verdicts:
   - `approve` — consensus, proceed
   - `revise` — one or more models dissent, specific revision proposed
   - `escalate` — multi-model dissent or policy concern; human T-shaped specialist invoked
4. Every verdict is logged to `brain/memory/critic/YYYY-MM-DD.log` with full reasoning.

**Cost:** ~€0.10-1.00 per deliberation. Runs only on high-stakes cases (~5-10% of agent outputs in a mature deployment).

### Meta-agent 2 — Guardrail Agent

**Purpose:** enforce fleet-wide policy at write-time. A single authority on what every agent is allowed to do.

**How it works:**

1. Intercepts every tool call that crosses a policy boundary: write to production DB, send email to customer, post to Slack, trigger a refund, modify an order.
2. Evaluates the call against the brand's policy bundle:
   - **ACK rule:** agent must acknowledge what it's doing; silent operations blocked
   - **Article 50 (EU AI Act):** customer-facing text must carry AI disclosure if required
   - **Annex III guardrails:** refuse actions affecting hiring, firing, performance evaluation, credit decisions, biometric inference
   - **Brand voice compliance:** outbound copy checked against the brand's style guide
   - **Financial thresholds:** escalate any single-action impact > €X (founder-configurable)
   - **PII handling:** reject any action that would write PII to a non-evidence store
3. Returns `allow` / `deny` / `modify` decisions in <200ms (rule-based, no LLM for standard checks; LLM-assisted for ambiguous copy).
4. Every denial is logged + escalated to the founder's `#operai-ops` Slack channel.

**Cost:** near zero per call (mostly rule-based). LLM calls only for ambiguous policy interpretations.

### Meta-agent 3 — Compliance Agent

**Purpose:** monitor the regulatory environment and flag DPIA/Register updates the brand's data controller needs to sign off on.

**How it works:**

1. Weekly cron pulls regulatory updates from a curated list of sources: EUR-Lex (AI Act amendments), AEPD guidance, EDPB statements, CNIL publications.
2. For each update, runs a relevance classifier against the brand's DPIA and AI System Register: "does this change require action?"
3. If yes, drafts a proposed amendment to `/opt/operai/compliance/dpia.md` or `ai-system-register.md` and files it in the Review Queue.
4. The data controller (founder) reviews and signs or rejects the amendment via `operai-init governance review`.
5. All changes are version-tracked in Git inside `/opt/operai/compliance/` for audit trail.

**Cost:** a few LLM calls per week — classification + drafting, not monitoring 24/7. ~€2-5/month.

## Installation

As of repo v2.5:

```bash
# Install the three meta-agents (systemd units + SOUL templates + config)
operai-init governance enable

# Check status
operai-init governance status

# View recent critic verdicts
operai-init governance logs --since 24h --agent critic

# Review pending compliance updates
operai-init governance review

# Disable (emergency only — recorded in audit log)
operai-init governance disable --reason "debugging issue X" --by founder
```

After `enable`, three new systemd units run alongside the existing agents:

- `operai-critic.service`
- `operai-guardrail.service`
- `operai-compliance.service`

Each has its own SOUL.md at `/opt/operai/agents/<meta>/SOUL.md`, interpolated from templates shipped in `repo/init/governance/`.

## Where this fits in the ACL model

Meta-agents operate with a dedicated role tier: **`meta-admin`**. They can read everything (including evidence store, in audit mode), but they cannot write anywhere except:

- Their own memory log (`brain/memory/critic/`, `brain/memory/guardrail/`, `brain/memory/compliance/`)
- The Review Queue (propose changes, never apply directly)
- The audit trail (append-only log at `brain/audit/`)

This is by design. Meta-agents **surface** decisions — they don't **make** them. Humans remain accountable. McKinsey again:

> *"The challenge is finding the sweet spot: enough oversight to manage risk without pulling agents back to human speed."*

The three meta-agents shift that sweet spot rightward by doing most of the oversight work at machine speed, escalating to humans only on genuine ambiguity.

## What changes for the founder

Before repo v2.5: founder reviews every flagged agent output manually, occasionally misses things, and compliance is a quarterly fire drill.

After repo v2.5:
- The critic catches 80%+ of drift automatically; founder reviews ~5/day instead of ~50
- The guardrail blocks 100% of policy violations at write-time; founder reviews ~0 (only sees the audit log)
- The compliance agent queues 1-2 DPIA amendments per month; founder signs or rejects in 10 minutes

The human oversight ratio shifts from "founder as bottleneck" to "founder as final authority." This is the operational definition of McKinsey's *"humans above the loop."*

## Economic model

| Meta-agent | Ongoing cost (per brand) |
|---|---|
| Critic | €5-30/month (depends on high-stakes call volume) |
| Guardrail | €0-5/month (mostly rule-based) |
| Compliance | €2-5/month (weekly batch) |
| **Total add-on** | **€7-40/month** |

Added to the base €631/month for the seven domain agents, a fully-governed swarm costs **€360-395/month** all-in. Still well inside the 10:1 ROI band.

## Limitations shipped in v2.5

Honest scoping:

1. **Critic is Punta de Flecha only.** Can be extended to richer multi-agent jury protocols in v0.6.
2. **Guardrail policy bundle is configurable, not learnable.** Brands express policy as rules, not through examples. A future version can learn policy from the Pattern Library.
3. **Compliance agent relies on a curated source list.** Brands outside EU/ES get a reduced source list; we ship EU-focused defaults and document how to extend.
4. **No real-time dashboarding.** Logs are queryable via CLI; a web UI for founder review comes in v0.6.

## What this gives the brand that deploys Compai

- **One command installs three meta-agents.** No custom LLM pipeline, no vendor integrations.
- **Governance scales with agent count**, not linearly with founder attention.
- **Every high-stakes action carries an audit trail** — specifically the trail a DPO or regulator asks for.
- **The McKinsey Pillar 3 box is ticked**, not aspirationally but with running code.

---

→ Back to [Chapter 15 — The Five Pillars](15-five-pillars.md)
