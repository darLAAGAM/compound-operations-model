"""Markdown trace writer — formats OrchestrationResult for humans + QMD indexing."""
from __future__ import annotations
import json
from datetime import datetime, timezone
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from operai_init.factory_runtime.orchestrator import OrchestrationResult


def to_markdown(result: "OrchestrationResult", *, event_label: str = "") -> str:
    lines: list[str] = []
    ts = datetime.now(timezone.utc).isoformat()
    label = event_label or f"{result.domain}-run-once"
    lines.append(f"# Factory trace — {label}")
    lines.append("")
    lines.append(f"*Generated: {ts}*")
    lines.append("")
    lines.append("## Meta")
    lines.append("")
    lines.append(f"- Domain: `{result.domain}`")
    lines.append(f"- Factory version: `{result.factory_version}`")
    lines.append(f"- Sub-agents invoked: {len(result.sub_agent_trace)}")
    lines.append(f"- Total latency: {result.total_latency_ms} ms")
    lines.append(f"- Total cost: ${result.total_cost_usd:.6f}")
    lines.append(f"- Overall OK: {result.ok}")
    if result.errors:
        lines.append(f"- Errors: {len(result.errors)}")
    lines.append("")

    # Event
    lines.append("## Input event")
    lines.append("")
    lines.append("```json")
    lines.append(json.dumps(result.event, indent=2, ensure_ascii=False))
    lines.append("```")
    lines.append("")

    # Sub-agent chain
    lines.append("## Sub-agent execution")
    lines.append("")
    for i, r in enumerate(result.sub_agent_trace, 1):
        mark = "✓" if r.ok else "✗"
        mock_tag = " [MOCK]" if r.mock else ""
        model_s = f"{r.provider}/{r.model}" if r.provider else "—"
        lines.append(f"### [{i}] {mark} `{r.name}`{mock_tag}")
        lines.append("")
        lines.append(f"- Model: `{model_s}`")
        lines.append(f"- Latency: {r.latency_ms} ms")
        lines.append(f"- Tokens: {r.tokens_in} in / {r.tokens_out} out")
        lines.append(f"- Cost: ${r.cost_usd:.6f}")
        if not r.ok:
            lines.append(f"- **Error:** `{r.error}`")
        lines.append("")
        lines.append("**Input:**")
        lines.append("")
        lines.append("```json")
        lines.append(json.dumps(r.input_dict, indent=2, ensure_ascii=False))
        lines.append("```")
        lines.append("")
        lines.append("**Output:**")
        lines.append("")
        lines.append("```json")
        lines.append(json.dumps(r.output_dict, indent=2, ensure_ascii=False) if r.output_dict else "(empty)")
        lines.append("```")
        lines.append("")

    # Summary
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Final action:** `{result.final_action}`")
    if result.final_rationale:
        lines.append(f"- **Rationale:** {result.final_rationale}")
    if result.draft_reply:
        lines.append("")
        lines.append("**Draft reply:**")
        lines.append("")
        lines.append("```")
        lines.append(result.draft_reply)
        lines.append("```")
    if result.errors:
        lines.append("")
        lines.append("**Errors:**")
        lines.append("")
        for e in result.errors:
            lines.append(f"- {e}")
    lines.append("")

    return "\n".join(lines) + "\n"


def to_json(result: "OrchestrationResult") -> str:
    payload = {
        "domain":           result.domain,
        "factory_version":  result.factory_version,
        "event":            result.event,
        "total_latency_ms": result.total_latency_ms,
        "total_cost_usd":   result.total_cost_usd,
        "ok":               result.ok,
        "errors":           result.errors,
        "final_action":     result.final_action,
        "final_rationale":  result.final_rationale,
        "draft_reply":      result.draft_reply,
        "sub_agents": [
            {
                "name":       r.name,
                "ok":         r.ok,
                "error":      r.error,
                "mock":       r.mock,
                "provider":   r.provider,
                "model":      r.model,
                "tokens_in":  r.tokens_in,
                "tokens_out": r.tokens_out,
                "cost_usd":   r.cost_usd,
                "latency_ms": r.latency_ms,
                "input":      r.input_dict,
                "output":     r.output_dict,
            }
            for r in result.sub_agent_trace
        ],
    }
    return json.dumps(payload, indent=2, ensure_ascii=False)
