# Chapter 20: The Runtime v3.0-beta MVP — From Template to Autonomous System

> **Appendix · Technical depth.** This chapter is for operators or engineers deploying the brain themselves. It covers implementation details that aren't needed for understanding the conceptual architecture. Skip if you're reading for strategy.

## What changed in v3.0-β

Runtime v2.9 shipped the factory runtime's smoke test (`factory run-once` — manual invocation per ticket). Runtime v3.0-beta makes the same runtime **autonomous**: a daemon watches the event queue, processes whatever lands there, writes decisions to a review queue. No human in the dispatch loop.

The gap between v2.9 and v3.0-β is five new components:

| Component | Lines | Role |
|---|---|---|
| `factory_runtime/daemon.py` | ~220 | Filesystem watcher + event pickup + routing + signal-safe shutdown |
| `factory_runtime/parallel.py` | ~120 | Asyncio dispatcher respecting `max_parallel` with a dependency-aware wave scheduler |
| `factory_runtime/brain_lookup.py` | ~100 | Auto-enrichment: reads `brand_voice.md`, scans `cs/policies/`, resolves customer history stubs |
| `factory_runtime/review_queue.py` | ~100 | Writes markdown per decision to `brain/review/<bucket>/<domain>/<event_id>.md` |
| `operai_init/event.py` | ~110 | `operai-init event submit/list/show/replay` CLI |

Plus: one new systemd unit (`operai-factory-runtime.service`), workflow hook scaffolding (`/opt/operai/workflows/`), and updated `install.sh` to provision all of it.

## The autonomous flow

```
┌──────────────────────────────────────────────────────────────────┐
│ 1. Event arrives at /opt/operai/events/<domain>/pending/X.json   │
│    Source: operai-init event submit (MVP) OR webhook (v0.9.2)    │
└───────────────────────────────┬──────────────────────────────────┘
                                ▼
┌──────────────────────────────────────────────────────────────────┐
│ 2. Daemon polls pending/ every 3s (configurable), picks up file  │
│    Moves to /in-flight/ atomically (prevents double-processing)  │
└───────────────────────────────┬──────────────────────────────────┘
                                ▼
┌──────────────────────────────────────────────────────────────────┐
│ 3. Brain auto-lookup enriches event:                              │
│    • brand_voice from knowledge/<brand>/marketing/brand-voice.md │
│    • applicable_policies from knowledge/<brand>/cs/policies/     │
│    • customer_order_history via workflow hook (brand-specific)   │
└───────────────────────────────┬──────────────────────────────────┘
                                ▼
┌──────────────────────────────────────────────────────────────────┐
│ 4. PRE-HOOK: brand's custom Python at                             │
│    /opt/operai/workflows/<domain>/pre_process.py                 │
│    Modifies event before factory dispatch                         │
└───────────────────────────────┬──────────────────────────────────┘
                                ▼
┌──────────────────────────────────────────────────────────────────┐
│ 5. Parallel dispatch:                                             │
│    • Wave scheduler finds runnable sub-agents (inputs available) │
│    • Dispatches up to max_parallel concurrently (asyncio + sem)  │
│    • On wave completion, merges outputs and evaluates next wave  │
│    • Each sub-agent calls llm.chat(system=SOUL, user=inputs, …) │
└───────────────────────────────┬──────────────────────────────────┘
                                ▼
┌──────────────────────────────────────────────────────────────────┐
│ 6. POST-HOOK: brand's custom Python at                            │
│    /opt/operai/workflows/<domain>/post_process.py                │
│    Inspect / modify / side-effect on the OrchestrationResult     │
└───────────────────────────────┬──────────────────────────────────┘
                                ▼
┌──────────────────────────────────────────────────────────────────┐
│ 7. Review queue routing by escalation-scorer output:              │
│    • auto_send        → brain/review/auto-sent/<domain>/ (v0.9.3 │
│                          will actually send via helpdesk API)     │
│    • human_review    → brain/review/pending/<domain>/            │
│    • escalate_super. → brain/review/escalated/<domain>/          │
│                         + Slack DM marker for founder            │
└───────────────────────────────┬──────────────────────────────────┘
                                ▼
┌──────────────────────────────────────────────────────────────────┐
│ 8. Trace JSON to brain/memory/<domain>/traces/<event_id>.json    │
│    QMD indexes it → brain_query("refund decisions") finds it     │
└───────────────────────────────┬──────────────────────────────────┘
                                ▼
┌──────────────────────────────────────────────────────────────────┐
│ 9. Event moves to /opt/operai/events/<domain>/completed/          │
└──────────────────────────────────────────────────────────────────┘
```

## What this unblocks for the buyer

A team forking the repo today can, same afternoon:

```bash
curl usecompai.com/init | bash            # swarm up
operai-init llm configure                  # paste provider keys
operai-init factory enable --domain cs     # 10 sub-agents deployed
systemctl enable --now operai-factory-runtime   # daemon running
```

From that moment, anything that drops a JSON file in `/opt/operai/events/cs/pending/` gets processed autonomously. Concretely:

- A cron hitting a helpdesk API every 5 min and dumping new tickets as JSON → the daemon picks them up. Brand's own cron, brand's own helpdesk.
- A webhook receiver (to be shipped in v0.9.2, or the brand writes one in 30 min with Starlette) that drops JSONs → processed.
- `operai-init event submit` from the command line → processed. Useful for manual testing + ad-hoc runs.

## Workflow hooks — where the brand extends

The MVP is **deliberately generic**. Every brand has specific logic that doesn't belong in a generic repo:

- "A VIP is LTV > €3,000, not the repo's default of €1,000."
- "Our customers are B2B — skip the consumer-language policy lookup."
- "We use Stockagile for inventory; look up stock status before drafting refund replies."
- "Our Spanish dialect is specifically Canarias — override the dialect detector."

`/opt/operai/workflows/<domain>/pre_process.py` and `post_process.py` are where the brand puts this code. The daemon loads them via `importlib.util` per event, so edits take effect on the next event — no daemon restart needed.

Sample `pre_process.py` that ships in Runtime v3.0-beta:

```python
def run(event: dict, meta: dict) -> dict:
    """Pre-process: normalize priority for wholesale channel."""
    if event.get("channel") == "wholesale" and event.get("priority"):
        event.setdefault("_meta", {})["priority_boosted"] = True
    # Example — brand adds their CRM lookup here:
    # from my_brand.crm import get_customer_ltv
    # if event.get("customer_email_raw"):
    #     event["customer_order_history"] = {"lifetime_value_eur": get_customer_ltv(...)}
    return event
```

The repo does **not** ship the brand's CRM integration, Stockagile wrapper, TC Analytics scraper, etc. Those are the brand's work. The repo ships the hook points + the dispatcher; the brand ships the domain-specific code.

## The honest scope of "autonomous"

What the MVP does autonomously:

1. **Watches for events** — yes, filesystem polling every 3s
2. **Enriches with brain context** — yes, brand voice + policies read at dispatch
3. **Runs the full sub-agent chain** — yes, parallel up to `max_parallel`
4. **Decides an action** — yes, via escalation-scorer sub-agent
5. **Writes a reviewable artifact** — yes, markdown per decision

What the MVP does **not** do autonomously (yet):

1. **Receive tickets from helpdesks** — v0.9.2. Today the brand wires their own event source (cron + helpdesk API + drop JSON).
2. **Send replies automatically** — v0.9.3. Today auto-send decisions are logged to `review/auto-sent/` but not actually transmitted. A human (or a brand-side workflow hook) does the send.
3. **Retry on transient failures** — v0.9.3. Today failures move to `events/failed/` with an `.error` file; the founder replays manually with `operai-init event replay`.
4. **Enforce cost budget** — v0.9.3. Today `factory.yml` declares `cost_budget_per_ticket_eur` but the runtime doesn't check it.

If the buyer needs all four, they either: (a) wait for v0.9.3, (b) implement them via workflow hooks, or (c) buy into the Managed Operations tier (Ch.13 Path 3a).

## Operational surface

New CLI in v3.0-β:

```bash
# Submit an event (pre-webhook MVP path)
operai-init event submit --domain cs --input ticket.json

# Inspect event buckets
operai-init event list                  # all buckets
operai-init event list --bucket pending
operai-init event list --bucket failed

# Detailed view of one event + trace
operai-init event show --id smoke-test-001

# Re-run an event (copy completed → pending)
operai-init event replay --id smoke-test-001

# Daemon lifecycle
systemctl enable --now operai-factory-runtime
systemctl status operai-factory-runtime
tail -f /opt/operai/logs/factory-runtime.log
```

## Runtime v3.0-beta vs repo v3.0 (the roadmap)

v3.0-β is an **MVP release**. It is stable enough for brands with technical operators who understand the gaps and fill them with workflow hooks and their own event sources. It is **not** a "plug-and-play SaaS experience."

For that, the roadmap continues:

| Version | Scope | Status |
|---|---|---|
| v3.0-β (this chapter) | Daemon + parallel + brain lookup + review queue + hook points | **SHIPPED** |
| v3.0 | + Webhook receivers (Richpanel/Gorgias/Zendesk/Intercom) + Slack digest integration | Next |
| v3.1 | + Action executor (reply via helpdesk API) + Guardrail meta-agent integration + retries + cost budget | Planned |
| v3.2 | + Live dashboard template + port finance+ops factories | Planned |
| v3.3 | + port marketing+merch+retail+hr factories | Planned |
| v3.4 | + extended connector library (WooCommerce, Gorgias, Zendesk, Cin7, etc.) | Planned |

A brand that wants v3.4 functionality today buys Managed Operations (Ch.13 Path 3a, €5K-15K/month).

## Commercial framing

Runtime v3.0-beta remains in the open-source repo. The hooks architecture makes "brand-specific customization" explicit and scoped: **free if the brand does it in-house** (Python programming skill required), or **€5-15K one-time engagement** if they want Compai to build their integrations (Ch.13 Custom Engagement).

The honest positioning:

- **The repo is 70% of the reference swarm, productized.** The infrastructure, the patterns, the runtime, the compliance package.
- **The remaining 30% — brand-specific workflows, bespoke integrations, accumulated operational patterns — is not transferable.** It's the founder's work to build.
- **If you don't want to do that work, Managed Operations.**

No founder reading this chapter should be surprised by what they get for the open-source repo vs what they get for a Managed Operations engagement.

---

→ Back to [Ch.19 Factory Runtime v0.9.0](19-factory-runtime.md) · Forward to Ch.21 *(v0.9.2 webhooks — coming)*
