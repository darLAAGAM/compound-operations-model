# Chapter 18: The LLM Provider Abstraction

> **Appendix · Technical depth.** This chapter is for operators or engineers deploying the brain themselves. It covers implementation details that aren't needed for understanding the conceptual architecture. Skip if you're reading for strategy.

## Why this chapter exists

Compai promised, in Chapter 15 (Pillar 5 — Dynamic Sourcing), that the swarm would **never lock a brand to a single LLM vendor**. repo v2.8 ships the surface that makes that promise real: a unified LLM client that speaks to five providers today and is designed to add more without changing a single line of agent code.

This matters for three reasons:

1. **Your LLM bill is yours.** Compai never touches your API keys. Each brand configures its own Anthropic / OpenAI / Gemini / Qwen / MiniMax account. The VPS stores those keys at mode 600. We sell software; you pay for inference.
2. **Vendor outage ≠ swarm outage.** Fallback chains let the runtime route around a 429 / 5xx automatically. If Anthropic goes down, the CS factory keeps answering tickets on OpenAI. This is the operational translation of McKinsey's "dynamic sourcing."
3. **Cost optimization at the sub-agent level.** Not every LLM call needs Claude Opus. Your triage sub-agent can run on GPT-4o-mini at $0.15/M tokens. Your drafter can run on Sonnet-4.5 for brand-voice quality. Your language-detect can run on Gemini 2.5 Flash's free tier. The savings compound.

## The five providers in v2.8

| Provider | Models shipped | Where to get a key |
|---|---|---|
| **Anthropic** | haiku-4.5 ($1/$5), sonnet-4.5 ($3/$15), opus-4.7 ($15/$75) | [console.anthropic.com/settings/keys](https://console.anthropic.com/settings/keys) |
| **OpenAI** | gpt-4o-mini ($0.15/$0.60), gpt-4o ($2.50/$10), gpt-5-mini ($0.50/$2), gpt-5 ($10/$30) | [platform.openai.com/api-keys](https://platform.openai.com/api-keys) |
| **Google Gemini** | gemini-2.5-flash ($0.075/$0.30), gemini-2.5-pro ($1.25/$5) | [aistudio.google.com/apikey](https://aistudio.google.com/apikey) |
| **Alibaba Qwen** | qwen-turbo ($0.05/$0.20), qwen-plus ($0.40/$1.20), qwen-max ($2/$6) | [dashscope.console.aliyun.com](https://dashscope.console.aliyun.com) |
| **MiniMax** | minimax-m2.5 ($0.30/$1.20), minimax-text01 ($0.20/$1.10) | [minimaxi.com](https://minimaxi.com) |

Prices are USD per 1M input / output tokens, reviewed 2026-04-21. They drift quarterly. `operai_init/llm/registry.py` is the single source of truth the swarm consults.

## Architecture

```
operai_init/llm/
├── registry.py          # 5 providers × 12 models × pricing + capability flags
├── config.py            # /opt/operai/credentials/llm-providers.json (mode 600)
├── client.py            # Unified dispatcher with fallback chains
├── usage.py             # SQLite of every call: tokens, cost, latency, caller
├── cli.py               # `operai-init llm configure|test|set-default|usage|...`
└── providers/
    ├── _http.py         # Shared urllib helper
    ├── anthropic.py     # x-api-key auth
    ├── openai.py        # Bearer auth, OpenAI-compatible
    ├── gemini.py        # x-goog-api-key, different request shape
    ├── qwen.py          # DashScope international, Alibaba-native shape
    └── minimax.py       # OpenAI-compatible v2 endpoint
```

**Zero external dependencies.** Every provider uses `urllib.request` from the stdlib. No `anthropic`, `openai`, `google-generativeai` packages. The repo stays small, supply-chain clean, and works in air-gapped deployments.

## The unified client

Every LLM call in the swarm — domain agents, factory sub-agents, meta-agents, Punta de Flecha deliberations — flows through one function:

```python
from operai_init.llm import client as llm

resp = llm.chat(
    system="You are the triage sub-agent. Classify tickets...",
    user=ticket_text,
    model="gpt-4o-mini",           # optional; uses default if omitted
    json_mode=True,
    caller="cs-factory:triage",    # for cost attribution
)

print(resp.text)           # parsed content
print(resp.cost_usd)       # computed from registry
print(resp.tokens_in)      # provider-reported
print(resp.latency_ms)     # wall-clock
print(resp.provider)       # which one actually served
print(resp.model)          # which model alias
```

Internally: resolve model → provider, call handler, record usage, return `LLMResponse`. On failure (401/429/5xx/timeout/network): fall through the configured chain, record the error, retry the next entry. If all fail: raise `LLMError` with the chain's last error.

## Founder setup (one time)

```bash
# Interactive — paste keys, test each provider
operai-init llm configure

# Or per-provider
operai-init llm configure anthropic
operai-init llm configure openai
operai-init llm configure gemini
# etc.

# Set brand-wide default (required before agents can run)
operai-init llm set-default --provider anthropic --model haiku-4.5

# Set fallback chain (optional but recommended)
operai-init llm fallback openai/gpt-4o-mini gemini/gemini-2.5-flash

# Verify
operai-init llm list
operai-init llm test anthropic
operai-init status       # now shows LLM section with configured providers + default
```

## Per-sub-agent overrides in factory.yml

repo v2.8 updates the CS factory's `factory.yml` to demonstrate how to route each sub-agent to the right model:

```yaml
default_llm:
  provider: anthropic
  model:    haiku-4.5

fallback_llm:
  - { provider: openai,  model: gpt-4o-mini }
  - { provider: gemini,  model: gemini-2.5-flash }

sub_agents:
  - name: triage
    llm: { provider: openai, model: gpt-4o-mini }        # fast classifier
    order: 1
  - name: language-detect
    llm: { provider: gemini, model: gemini-2.5-flash }   # free-tier coverage
    order: 4
  - name: drafter
    llm: { provider: anthropic, model: sonnet-4.5 }      # customer-facing copy
    order: 9
  - name: brand-voice-check
    llm: { provider: anthropic, model: sonnet-4.5 }      # quality gate
    order: 7
  # Other 6 sub-agents fall back to default_llm (haiku-4.5)
```

The effect: the CS factory's per-ticket cost shifts from ~€0.002 uniform Haiku to ~€0.0015 mixed. The cheap-and-fast sub-agents (triage, language-detect) offload to mini models; the quality-critical ones (drafter, brand-voice-check) use Sonnet.

## Cost visibility

Every call lands in `/opt/operai/state/llm-usage.db` (SQLite). Query via CLI:

```bash
operai-init llm usage --since 30
```

Output:

```
LLM usage — last 30 days

  PROVIDER     MODEL              CALLS     TOK_IN    TOK_OUT      USD
  ------------ -------------- ------- ---------- ---------- --------
  anthropic    sonnet-4.5         412    124,231     28,541  $0.7997
  openai       gpt-4o-mini      1,203    382,111     92,411  $0.1128
  gemini       gemini-2.5-f.      821    201,002     45,998  $0.0289
  Total: 2,436 calls, $0.9414
```

Errors surface separately:

```
Recent errors
  2026-04-21T10:14:02Z  anthropic/haiku-4.5  cs-factory:triage
    401 Unauthorized: invalid x-api-key
```

`--json` dumps machine-readable for dashboards.

## Pre-flight: agents refuse to start without LLM config

As decided in v2.8 planning, **there is no default provider**. Install.sh no longer picks Anthropic for you. `operai-init status` flags the missing config loudly:

```
LLM providers
  ✗ no providers configured — agents will refuse to start. Run: operai-init llm configure
```

Agent-runner (when the v0.7 runtime lands) will refuse to spawn if `llm-providers.json` is empty. This prevents silent fallback to the maintainer's keys (which don't exist in a brand's deployment) and forces the founder to make the explicit choice.

## Why not use the provider SDKs

Three reasons:

1. **Supply chain**: `pip install anthropic openai google-generativeai` pulls ~100MB of dependencies. Each with their own vulnerability surface. The repo's `urllib`-only approach is ~500 lines of HTTP that we own.
2. **Air-gap friendly**: SDKs often require outbound to vendor-managed telemetry endpoints. Raw HTTP doesn't.
3. **Uniform interface**: SDKs have incompatible APIs (Anthropic's `messages.create` vs OpenAI's `chat.completions.create` vs Gemini's `generateContent`). Abstracting once, well, is simpler than juggling three abstractions.

The tradeoff: we don't get SDK features like streaming, batch API, prompt caching out of the box. All three are on the roadmap as opt-in extensions to the client.

## What v2.8 does NOT ship

Honest scoping:

1. **No streaming support**. `chat()` is request/response only. Streaming adds to v2.9.
2. **No Anthropic batch API** (50% cheaper async batch submissions). Requires different client shape; v2.9.
3. **No prompt caching**. Anthropic's prompt-caching requires specific headers per call; v2.9.
4. **No local provider** (Ollama, LM Studio). the founder's v2.8 decision: 5 cloud providers only. Ollama lands when there's operator demand.
5. **No Bedrock / Azure OpenAI wrappers**. These require AWS/Azure auth flows; v2.9+.
6. **No runtime orchestrator for the factories**. The LLM client is ready; agent-runner still heartbeats. The factory runtime (which actually spawns sub-agent calls in parallel) ships in **v0.9**.

## Commercial framing

All of this is in the open-source repo. the founder's v2.5 rule held: dynamic sourcing is a differentiator, not an upsell. A team forking the repo gets:

- Seven domain agents (monolithic, SOULs)
- CS factory reference with 10 sub-agents (shipped v2.6)
- Meta-agent governance (critic + guardrail + compliance, v2.5)
- **Multi-LLM-provider abstraction for all of the above (v2.8)**
- Phase 1 structured-source ingestion (v2.4)

The "brand-owned" model now extends from hardware (self-hosted VPS), code (open repo), tokens (per-brand API keys), to vendor choice (any of 5 LLMs). Every axis of lock-in removed.

---

→ Back to [Ch.17 Agent Factory Pattern](17-agent-factory.md) · Forward to Ch.19 *(v2.9)*
