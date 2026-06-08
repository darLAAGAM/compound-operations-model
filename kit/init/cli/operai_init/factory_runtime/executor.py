"""Sub-agent executor — one SOUL + one input dict → one parsed output dict.

The LLM is called via the unified llm client (provider-agnostic).
In mock mode, we use canned responses based on sub-agent name for offline
smoke tests.
"""
from __future__ import annotations
import json
import time
from dataclasses import dataclass, field
from typing import Any

from operai_init.factory_runtime.config import FactoryConfig, SubAgentConfig, resolve_llm_for, soul_content


@dataclass
class SubAgentResult:
    name:        str
    input_dict:  dict
    output_dict: dict
    raw_text:    str
    tokens_in:   int = 0
    tokens_out:  int = 0
    cost_usd:    float = 0.0
    latency_ms:  int = 0
    provider:    str = ""
    model:       str = ""
    ok:          bool = True
    error:       str = ""
    mock:        bool = False


# ─────────────────────────────────────────────────────────────────────────────
# Mock responses — canned outputs keyed by sub-agent name.
# For offline smoke tests without real API keys.
# ─────────────────────────────────────────────────────────────────────────────

_MOCK_RESPONSES = {
    "triage": {
        "category": "refund",
        "priority": "P3",
        "sentiment": -0.4,
        "language": "es",
        "confidence": 0.87,
    },
    "policy-lookup": {
        "applicable_policies": [
            {"policy_id": "pol-refund-14d", "title": "14-day refund window",
             "excerpt": "Customers are entitled to a full refund within 14 days of purchase.",
             "source_path": "brain/knowledge/acme/cs/policies/refund-policy.md"},
        ],
        "policy_confidence": 0.82,
    },
    "vip-detector": {
        "is_vip": False,
        "vip_tier": "none",
        "special_handling_notes": "",
    },
    "language-detect": {
        "language": "es",
        "dialect": "ES-ES",
        "confidence": 0.95,
    },
    "sentiment-deep": {
        "escalation_score": 3,
        "escalation_signals": [],
    },
    "refund-calc": {
        "refund_eligible": True,
        "refund_amount_eur": 80.00,
        "refund_rationale": "Order placed 10 days ago; within 14-day full-refund window.",
    },
    "brand-voice-check": {
        "voice_score": 8,
        "suggested_revisions": [],
    },
    "escalation-scorer": {
        "action": "human_review",
        "rationale": "Refund eligible with amount >€50; standard brand policy requires human check.",
    },
    "drafter": {
        "draft_reply": (
            "Hola María,\n\nGracias por tu mensaje. Hemos revisado tu pedido y "
            "confirmamos que está dentro del periodo de reembolso completo. "
            "Procederemos con la devolución de 80,00 € en las próximas 24-48 horas.\n\n"
            "Un saludo,\nEl equipo de Acme"
        ),
        "action_recommended": "hold_for_review",
    },
    "follow-up-scheduler": {
        "follow_up_schedule": ["2026-04-23T10:00:00Z", "2026-04-28T10:00:00Z"],
    },
}


def execute(
    sub_agent: SubAgentConfig,
    factory_config: FactoryConfig,
    input_dict: dict,
    *,
    mock: bool = False,
) -> SubAgentResult:
    """Execute one sub-agent. Returns a SubAgentResult."""
    resolved = resolve_llm_for(factory_config, sub_agent)
    provider = resolved.get("provider", "")
    model    = resolved.get("model", "")

    t0 = time.time()

    if mock:
        out = dict(_MOCK_RESPONSES.get(sub_agent.name, {}))
        latency = int((time.time() - t0) * 1000) + 150  # simulate some latency
        return SubAgentResult(
            name=sub_agent.name,
            input_dict=input_dict,
            output_dict=out,
            raw_text=json.dumps(out),
            provider=provider,
            model=model,
            latency_ms=latency,
            ok=True,
            mock=True,
        )

    # Real LLM path
    try:
        from operai_init.llm import client as llm
    except ImportError as e:
        return SubAgentResult(
            name=sub_agent.name, input_dict=input_dict, output_dict={},
            raw_text="", provider=provider, model=model,
            ok=False, error=f"llm client import failed: {e}",
        )

    soul = soul_content(factory_config, sub_agent)
    user_prompt = json.dumps(input_dict, indent=2, ensure_ascii=False)

    try:
        resp = llm.chat(
            system=soul,
            user=user_prompt,
            provider=provider,
            model=model,
            json_mode=True,
            max_tokens=1024,
            temperature=0.3,
            caller=f"factory:{factory_config.domain}:{sub_agent.name}",
        )
    except Exception as e:  # noqa: BLE001
        latency = int((time.time() - t0) * 1000)
        return SubAgentResult(
            name=sub_agent.name, input_dict=input_dict, output_dict={},
            raw_text="", provider=provider, model=model,
            latency_ms=latency, ok=False, error=str(e),
        )

    # Parse JSON
    parsed: dict
    try:
        # Some models wrap in ```json ... ``` fences; strip if present
        txt = resp.text.strip()
        if txt.startswith("```"):
            # find first \n and last ```
            lines = txt.splitlines()
            if lines[0].startswith("```"): lines = lines[1:]
            if lines and lines[-1].startswith("```"): lines = lines[:-1]
            txt = "\n".join(lines).strip()
        parsed = json.loads(txt)
    except json.JSONDecodeError as e:
        return SubAgentResult(
            name=sub_agent.name, input_dict=input_dict, output_dict={},
            raw_text=resp.text, provider=provider, model=model,
            latency_ms=resp.latency_ms, ok=False,
            error=f"JSON parse error: {e}",
        )

    # Basic schema validation — check declared outputs are present
    missing = [k for k in sub_agent.outputs if k not in parsed]
    if missing:
        return SubAgentResult(
            name=sub_agent.name, input_dict=input_dict, output_dict=parsed,
            raw_text=resp.text, provider=provider, model=model,
            tokens_in=resp.tokens_in, tokens_out=resp.tokens_out,
            cost_usd=resp.cost_usd, latency_ms=resp.latency_ms,
            ok=False, error=f"missing required output fields: {missing}",
        )

    return SubAgentResult(
        name=sub_agent.name,
        input_dict=input_dict,
        output_dict=parsed,
        raw_text=resp.text,
        tokens_in=resp.tokens_in,
        tokens_out=resp.tokens_out,
        cost_usd=resp.cost_usd,
        latency_ms=resp.latency_ms,
        provider=resp.provider,
        model=resp.model,
        ok=True,
    )
