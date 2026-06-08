"""Unified LLM dispatcher with fallback chains + usage tracking.

Usage:
    from operai_init.llm import client as llm
    resp = llm.chat(
        system="You are ...",
        user="Classify this ticket: ...",
        model="haiku-4.5",          # or omit → uses default from config
        json_mode=True,
    )
    print(resp.text, resp.cost_eur, resp.provider, resp.model)

Automatic behavior:
  - Resolves `model` → (provider, provider_id) via the registry
  - Falls back through the configured chain on network / 429 / 5xx errors
  - Records each call in the usage DB (operai_init.llm.usage)
  - Refuses to run if no providers are configured
"""
from __future__ import annotations
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from operai_init.llm import config, registry, usage
from operai_init.llm.providers import anthropic as prov_anthropic
from operai_init.llm.providers import openai as prov_openai
from operai_init.llm.providers import gemini as prov_gemini
from operai_init.llm.providers import qwen as prov_qwen
from operai_init.llm.providers import minimax as prov_minimax

PROVIDER_HANDLERS = {
    "anthropic": prov_anthropic.call,
    "openai":    prov_openai.call,
    "gemini":    prov_gemini.call,
    "qwen":      prov_qwen.call,
    "minimax":   prov_minimax.call,
}


@dataclass
class LLMResponse:
    text:        str
    tokens_in:   int
    tokens_out:  int
    provider:    str
    model:       str
    cost_usd:    float
    latency_ms:  int
    raw:         dict


class LLMError(Exception):
    pass


class NoProvidersConfiguredError(LLMError):
    pass


def _home() -> Path:
    return Path(os.environ.get("OPERAI_HOME", "/opt/operai"))


def _find_provider_for_model(model_alias: str) -> Optional[str]:
    """If a factory.yml references model by alias only, figure out which provider owns it."""
    for p, spec in registry.REGISTRY.items():
        if model_alias in spec.models:
            return p
    return None


def _resolve_call_plan(
    model: str | None,
    provider: str | None,
) -> list[tuple[str, str]]:
    """Return ordered list of (provider, model) to try."""
    home = _home()
    configured = set(config.list_configured(home))
    if not configured:
        raise NoProvidersConfiguredError(
            "No LLM providers configured. Run: operai-init llm configure"
        )

    # Explicit choice wins
    if provider and model:
        return [(provider, model)]
    if model and not provider:
        p = _find_provider_for_model(model)
        if p:
            return [(p, model)]

    # Default + fallback chain from config
    data = config.load(home)
    default = data.get("default")
    plan: list[tuple[str, str]] = []
    if default:
        plan.append((default["provider"], default["model"]))
    for fb in data.get("fallback", []):
        plan.append((fb["provider"], fb["model"]))

    if not plan:
        # No default set; pick any configured provider with its default model
        for p in configured:
            spec = registry.REGISTRY.get(p)
            if spec:
                plan.append((p, spec.default_model))
                break

    # Filter plan to only configured providers
    plan = [(p, m) for (p, m) in plan if p in configured]
    if not plan:
        raise NoProvidersConfiguredError(
            "No provider in the call plan is configured. Run: operai-init llm configure"
        )
    return plan


def chat(
    *,
    system: str,
    user: str,
    model: str | None = None,
    provider: str | None = None,
    max_tokens: int = 1024,
    temperature: float = 0.7,
    json_mode: bool = False,
    timeout: float = 60.0,
    caller: str = "unknown",      # e.g. "cs-factory:triage"
) -> LLMResponse:
    home = _home()
    plan = _resolve_call_plan(model, provider)

    last_error: Exception | None = None
    for (p, m) in plan:
        spec = registry.resolve_model(p, m)
        if not spec:
            last_error = LLMError(f"unknown model {p}/{m}")
            continue
        api_key = config.get_api_key(home, p)
        if not api_key:
            last_error = LLMError(f"provider {p} not configured")
            continue
        handler = PROVIDER_HANDLERS.get(p)
        if not handler:
            last_error = LLMError(f"no handler for provider {p}")
            continue

        t0 = time.time()
        try:
            raw = handler(
                api_key=api_key,
                model_id=spec.provider_id,
                system=system,
                user=user,
                max_tokens=max_tokens,
                temperature=temperature,
                json_mode=json_mode and spec.supports_json,
                timeout=timeout,
            )
        except Exception as e:
            last_error = e
            # Log failure + fall through to next in plan
            usage.record(
                home=home, provider=p, model=m,
                tokens_in=0, tokens_out=0, cost_usd=0.0,
                latency_ms=int((time.time() - t0) * 1000),
                caller=caller, ok=False, error=str(e),
            )
            continue

        latency_ms = int((time.time() - t0) * 1000)
        cost = registry.cost_usd(p, m, raw["tokens_in"], raw["tokens_out"])
        usage.record(
            home=home, provider=p, model=m,
            tokens_in=raw["tokens_in"], tokens_out=raw["tokens_out"], cost_usd=cost,
            latency_ms=latency_ms, caller=caller, ok=True,
        )
        return LLMResponse(
            text=raw["text"],
            tokens_in=raw["tokens_in"],
            tokens_out=raw["tokens_out"],
            provider=p,
            model=m,
            cost_usd=cost,
            latency_ms=latency_ms,
            raw=raw.get("_raw", {}),
        )

    raise LLMError(f"All providers in plan failed. Last error: {last_error}")
