# Chapter 19: The Factory Runtime (v0.9.0 — Smoke Test)

> **Appendix · Technical depth.** This chapter is for operators or engineers deploying the brain themselves. It covers implementation details that aren't needed for understanding the conceptual architecture. Skip if you're reading for strategy.

## Why this chapter exists

Chapter 17 shipped the Agent Factory Pattern — 10 sub-agent SOULs plus `factory.yml` declaring their contracts. Chapter 18 shipped the LLM Provider Abstraction — 5 providers, brand-owned keys, per-sub-agent routing. Both were **static artifacts**: beautiful templates that didn't actually do anything.

Chapter 19 is the smallest viable runtime that **makes the factory execute**. One command. One input. One trace. You can see the 10 sub-agents run end-to-end against your configured LLMs.

```bash
operai-init factory run-once \
  --domain cs \
  --input sample-ticket.json \
  --output trace.md
```

That's it. No webhooks, no daemon, no event queue. Just: given a ticket, dispatch through the 10 sub-agents, merge their outputs, print a structured trace. Exactly enough to prove the factory works.

## The v0.9.0 scope (and what's next)

| Feature | v0.9.0 | v0.9.1 | v0.9.2 | v0.9.3 |
|---|---|---|---|---|
| Manual `run-once` CLI | ✅ | ✅ | ✅ | ✅ |
| Sequential sub-agent execution | ✅ | — | — | — |
| Parallel execution (`max_parallel`) | — | ✅ | ✅ | ✅ |
| Trace to markdown + JSON | ✅ | ✅ | ✅ | ✅ |
| Mock-LLM mode (offline) | ✅ | ✅ | ✅ | ✅ |
| Event-queue daemon | — | ✅ | ✅ | ✅ |
| Webhook receivers (Richpanel/Gorgias/Zendesk) | — | — | ✅ | ✅ |
| Action executor (send reply via helpdesk API) | — | — | — | ✅ |
| Retries + circuit breakers | — | — | — | ✅ |

Ship one, prove it, ship the next.

## The components shipped in v0.9.0

Four new modules in the repo under `operai_init/factory_runtime/`:

| Module | Lines | Role |
|---|---|---|
| `config.py` | ~230 | Parses `factory.yml` (minimal-YAML stdlib parser, no PyYAML dep) + validates SOULs exist + resolves `default_llm` with per-sub-agent overrides |
| `executor.py` | ~130 | `execute(sub_agent, factory_config, input_dict)` — reads SOUL, resolves LLM, calls `llm.chat()` with `json_mode=True`, validates output against declared schema, returns `SubAgentResult` |
| `orchestrator.py` | ~75 | `run_once(fc, event)` — sequential loop over sorted sub-agents, merges each output into shared context, extracts final action from `escalation-scorer` |
| `trace.py` | ~90 | Markdown + JSON writers for `OrchestrationResult` |

Plus CLI glue (`cmd_run_once` in `factory.py`) and 3 sample fixtures (`refund-request.json`, `complaint-angry.json`, `vip-product-question.json`).

**Zero external dependencies.** The YAML parser is custom (fit-for-purpose — it understands our `factory.yml` shape and nothing else). The LLM client is already stdlib-only from Ch.18.

## What the run-once flow does

Given a sample ticket:

```json
{
  "raw_ticket": "Hola, he recibido mi pedido hace 10 días...",
  "customer_email": "<email:subject_...>",
  "order_value_eur": 80.00,
  "order_age_days": 10,
  "brand_voice": "Warm, direct, customer-first..."
}
```

The orchestrator:

1. Loads `/opt/operai/agents/cs/factory/factory.yml`
2. Sorts sub-agents by declared `order`
3. Iterates:
   - Build input dict by extracting declared `inputs` keys from shared context
   - Call `llm.chat(system=SOUL, user=json.dumps(input), json_mode=True, provider/model=resolved_from_factory_yml)`
   - Parse JSON response + validate declared output keys present
   - Merge output into context
4. Reads `escalation-scorer.output` for the final `action`
5. Reads `drafter.output` for the `draft_reply`
6. Writes a full markdown (or JSON) trace

Total latency for CS factory mock run: ~1.5s (sequential). Real-LLM latency depends on provider; typically 5-10s for 10 sequential calls.

## Trace output format

Markdown trace per ticket looks like this (abbreviated):

```markdown
# Factory trace — refund-request

## Meta
- Domain: `cs`
- Sub-agents invoked: 10
- Total latency: 9,234 ms
- Total cost: $0.002871
- Overall OK: True

## Input event
```json
{...ticket...}
```

## Sub-agent execution

### [1] ✓ `triage`
- Model: `openai/gpt-4o-mini`
- Latency: 412 ms · Tokens: 320/45 · Cost: $0.000120

**Input:**
```json
{"raw_ticket": "..."}
```

**Output:**
```json
{"category": "refund", "priority": "P3", "sentiment": -0.4, "language": "es"}
```

### [2] ✓ `policy-lookup`...

## Summary
- **Final action:** `human_review`
- **Rationale:** Refund eligible with amount >€50 → policy requires human check.

**Draft reply:**
```
Hola María, gracias por tu mensaje. Hemos revisado...
```
```

The trace is designed to be **pasted into a code review or PR**. A T-shaped CS specialist can read the chain in under 30 seconds and approve or escalate.

## Mock mode for offline smoke tests

```bash
operai-init factory run-once --domain cs --input sample.json --mock-llm
```

The `--mock-llm` flag skips the LLM entirely and uses canned responses keyed by sub-agent name. Useful for:

- CI tests (no API key needed)
- First-time founders testing the install before configuring providers
- Demos where you want deterministic output

Mock responses live in `operai_init/factory_runtime/executor.py` → `_MOCK_RESPONSES`. They're representative but obviously not real inference.

## Pre-flight enforcement

Without `--mock-llm`, `run-once` checks that `operai-init llm configure` has been completed. If no providers are configured, it refuses with a clear pointer:

```
✗ no LLM providers configured. Run: operai-init llm configure  (or use --mock-llm)
```

This is the same pre-flight `operai-init status` shows — consistent across the surface.

## What you can actually do with v0.9.0

Concrete workflows unblocked today:

1. **Smoke-test your install end-to-end.** Run the mock. If you see 10 sub-agents complete and a draft reply generated, the repo is wired correctly.
2. **Tune a SOUL and validate.** Edit `agents/cs/factory/sub-agents/drafter/SOUL.md`, re-run, compare the new draft against the old. No systemctl reload, no redeploy.
3. **Compare LLM providers per sub-agent.** Edit `factory.yml` to swap `triage` from `openai/gpt-4o-mini` to `gemini/gemini-2.5-flash`. Run both. Compare output quality and cost.
4. **Debug a specific sub-agent.** Use `--limit 3` to only run the first 3 sub-agents. Fast iteration while you tune the early steps.
5. **Generate regression fixtures.** Run on canonical tickets, capture traces, commit to git. Future SOUL changes can be diffed against known-good outputs.

These five are enough to replace what a T-shaped CS specialist would otherwise do with ad-hoc LLM playgrounds (ChatGPT tab, Anthropic Console, Gemini AI Studio), because the factory runtime routes to their configured providers, applies the full SOUL chain, and produces auditable traces.

## What v0.9.0 does NOT do (deliberately)

- **No webhooks**: Richpanel/Gorgias/Zendesk don't POST here yet. v0.9.2.
- **No daemon**: the runtime is not a long-running process. Manual `run-once` only. v0.9.1.
- **No action execution**: we print the recommendation. We don't send the reply. The founder reviews the trace, decides, and acts via the helpdesk UI. v0.9.3.
- **No parallel dispatch**: sub-agents run strictly in declared `order`. v0.9.1 adds `max_parallel` respect.
- **No retries**: failed sub-agents log the error and the chain continues with a partial context. Robust retry logic + circuit breakers land in v0.9.3.
- **No brain auto-lookup**: the input JSON must include pre-loaded fields like `brand_voice`, `applicable_policies`, `customer_order_history`. Automatic brain lookups (via `brain_query`) come in v0.9.1.
- **No cost budget enforcement**: `factory.yml` declares `cost_budget_per_ticket_eur` but v0.9.0 doesn't check it. v0.9.3.

Each limitation is a known-scope carry-over, not a bug. If the founder wants any of these today, the honest answer is Custom Engagement (Ch.13 Path 3b).

## The commercial framing

Runtime v2.9 now delivers a real, demonstrable system end-to-end. A founder buying the open-source repo can, in the same afternoon:

1. `curl usecompai.com/init | bash` → swarm infrastructure
2. `operai-init llm configure` → wire their providers
3. `operai-init factory enable --domain cs` → deploy the factory templates
4. `operai-init factory run-once --domain cs --input demo.json` → **see 10 sub-agents execute against their LLMs, produce a draft reply, emit a trace**

The story is complete on day one. What ships across v0.9.1–v0.9.3 is the "lights-out" automation layer — valuable, but not the part that makes the product demonstrable.

## Roadmap pointer

- **v0.9.0** (this chapter): `run-once` smoke test
- **v0.9.1**: parallel dispatch + event queue daemon + brain auto-lookup
- **v0.9.2**: webhook receivers for 4 helpdesks
- **v0.9.3**: action executor via Guardrail meta-agent + retries + cost budget enforcement

At that point, a deployed Compai processes real tickets end-to-end at €0.002 each, with M-shaped supervisors reviewing ~20% of outputs, and 7-domain-agent parity with the McKinsey "50-100 specialized agents" benchmark.

---

→ Back to [Ch.18 LLM Provider Abstraction](18-llm-providers.md)
