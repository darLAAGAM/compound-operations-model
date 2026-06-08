"""Orchestrator — runs the full sub-agent chain sequentially (v0.9.0).

v0.9.0 keeps the simplest possible dispatch:
  1. Sort sub-agents by declared `order`
  2. Build a shared context dict starting from the event + any pre-loaded fields
  3. For each sub-agent:
       a. Extract declared `inputs` from context
       b. Execute
       c. Merge output back into context
  4. Decide final action based on escalation-scorer output (if present)
  5. Return full trace

Parallel dispatch respecting `max_parallel` ships in v0.9.1.
"""
from __future__ import annotations
import time
from dataclasses import dataclass, field
from typing import Any

from operai_init.factory_runtime.config import FactoryConfig
from operai_init.factory_runtime.executor import execute, SubAgentResult


@dataclass
class OrchestrationResult:
    domain:          str
    factory_version: str
    event:           dict
    context:         dict                       # final merged context
    sub_agent_trace: list[SubAgentResult] = field(default_factory=list)
    final_action:    str = "unknown"            # from escalation-scorer, or "unknown"
    final_rationale: str = ""
    draft_reply:     str = ""
    total_latency_ms: int = 0
    total_cost_usd:  float = 0.0
    ok:              bool = True
    errors:          list[str] = field(default_factory=list)


def _build_input(sub_agent, context: dict) -> dict:
    """Extract declared inputs from the context. Unknown keys pass through as None."""
    out = {}
    for key in sub_agent.inputs:
        out[key] = context.get(key)
    return out


def run_once(
    fc: FactoryConfig,
    event: dict,
    *,
    mock: bool = False,
    limit: int | None = None,
) -> OrchestrationResult:
    """Run the full factory chain on a single event. Returns the trace."""
    context = dict(event)   # shallow copy; sub-agents may add fields
    result = OrchestrationResult(
        domain=fc.domain,
        factory_version=fc.version,
        event=dict(event),
        context=context,
    )

    t_start = time.time()

    sub_agents = fc.sub_agents
    if limit is not None:
        sub_agents = sub_agents[:limit]

    for sa in sub_agents:
        input_dict = _build_input(sa, context)
        res = execute(sa, fc, input_dict, mock=mock)
        result.sub_agent_trace.append(res)
        result.total_latency_ms += res.latency_ms
        result.total_cost_usd   += res.cost_usd

        if not res.ok:
            result.errors.append(f"{sa.name}: {res.error}")
            # Continue execution — downstream sub-agents may tolerate missing fields.
            # Parent SOUL escalation is a v0.9.1 concern.
            continue

        # Merge outputs into context
        for k, v in res.output_dict.items():
            context[k] = v

    result.total_latency_ms = int((time.time() - t_start) * 1000) if not mock else result.total_latency_ms

    # Extract final action from escalation-scorer if present
    escalation = next((r for r in result.sub_agent_trace if r.name == "escalation-scorer" and r.ok), None)
    if escalation:
        result.final_action    = escalation.output_dict.get("action", "unknown")
        result.final_rationale = escalation.output_dict.get("rationale", "")
    drafter = next((r for r in result.sub_agent_trace if r.name == "drafter" and r.ok), None)
    if drafter:
        result.draft_reply = drafter.output_dict.get("draft_reply", "")

    result.ok = all(r.ok for r in result.sub_agent_trace)
    return result
