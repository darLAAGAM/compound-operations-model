"""Provider + model registry with pricing.

All prices are USD per 1M tokens. Consumers convert to EUR via the latest
fx rate at usage-summary time (stdlib-only, no network dependency at
call time).

Model aliases (short names) map to provider-specific IDs so factory.yml
can reference `haiku-4.5` or `gpt-4o-mini` without tying to a specific
dated revision.

Last reviewed: 2026-04-21.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ModelSpec:
    alias:           str
    provider_id:     str           # what the provider API expects
    input_per_mtok:  float         # USD per 1M input tokens
    output_per_mtok: float         # USD per 1M output tokens
    context_window:  int
    supports_json:   bool = True


@dataclass(frozen=True)
class ProviderSpec:
    name:           str
    api_base:       str
    env_var:        str            # where the SDK expects the key
    auth_header:    str            # e.g. "Authorization: Bearer X" or "x-api-key: X"
    models:         dict[str, ModelSpec]
    default_model:  str
    test_model:     str            # small/cheap model for `llm test`


REGISTRY: dict[str, ProviderSpec] = {
    # ─── Anthropic ──────────────────────────────────────────────────
    "anthropic": ProviderSpec(
        name="anthropic",
        api_base="https://api.anthropic.com",
        env_var="ANTHROPIC_API_KEY",
        auth_header="x-api-key",
        default_model="haiku-4.5",
        test_model="haiku-4.5",
        models={
            "haiku-4.5":  ModelSpec("haiku-4.5",  "claude-haiku-4-5-20251025",   1.0,  5.0,  200_000, True),
            "sonnet-4.5": ModelSpec("sonnet-4.5", "claude-sonnet-4-5-20250929",  3.0, 15.0,  200_000, True),
            "opus-4.7":   ModelSpec("opus-4.7",   "claude-opus-4-7-20260215",   15.0, 75.0,  200_000, True),
        },
    ),

    # ─── OpenAI ──────────────────────────────────────────────────────
    "openai": ProviderSpec(
        name="openai",
        api_base="https://api.openai.com/v1",
        env_var="OPENAI_API_KEY",
        auth_header="Authorization",       # value is "Bearer ${KEY}"
        default_model="gpt-4o-mini",
        test_model="gpt-4o-mini",
        models={
            "gpt-4o-mini": ModelSpec("gpt-4o-mini", "gpt-4o-mini", 0.15, 0.60, 128_000, True),
            "gpt-4o":      ModelSpec("gpt-4o",      "gpt-4o",      2.50, 10.0, 128_000, True),
            "gpt-5":       ModelSpec("gpt-5",       "gpt-5",       10.0, 30.0, 200_000, True),
            "gpt-5-mini":  ModelSpec("gpt-5-mini",  "gpt-5-mini",  0.50, 2.00, 200_000, True),
        },
    ),

    # ─── Google Gemini ──────────────────────────────────────────────
    "gemini": ProviderSpec(
        name="gemini",
        api_base="https://generativelanguage.googleapis.com/v1beta",
        env_var="GEMINI_API_KEY",
        auth_header="x-goog-api-key",
        default_model="gemini-2.5-flash",
        test_model="gemini-2.5-flash",
        models={
            "gemini-2.5-flash": ModelSpec("gemini-2.5-flash", "gemini-2.5-flash", 0.075, 0.30, 1_000_000, True),
            "gemini-2.5-pro":   ModelSpec("gemini-2.5-pro",   "gemini-2.5-pro",   1.25,  5.00, 2_000_000, True),
        },
    ),

    # ─── Qwen (Alibaba DashScope, international endpoint) ───────────
    "qwen": ProviderSpec(
        name="qwen",
        api_base="https://dashscope-intl.aliyuncs.com/api/v1",
        env_var="DASHSCOPE_API_KEY",
        auth_header="Authorization",
        default_model="qwen-plus",
        test_model="qwen-turbo",
        models={
            "qwen-turbo":  ModelSpec("qwen-turbo",  "qwen-turbo",  0.05, 0.20,  128_000, True),
            "qwen-plus":   ModelSpec("qwen-plus",   "qwen-plus",   0.40, 1.20,  128_000, True),
            "qwen-max":    ModelSpec("qwen-max",    "qwen-max",    2.00, 6.00,  128_000, True),
        },
    ),

    # ─── MiniMax ─────────────────────────────────────────────────────
    "minimax": ProviderSpec(
        name="minimax",
        api_base="https://api.minimaxi.chat/v1",
        env_var="MINIMAX_API_KEY",
        auth_header="Authorization",
        default_model="minimax-m2.5",
        test_model="minimax-m2.5",
        models={
            "minimax-m2.5":   ModelSpec("minimax-m2.5",   "MiniMax-M2.5",     0.30, 1.20, 1_000_000, True),
            "minimax-text01": ModelSpec("minimax-text01", "MiniMax-Text-01",  0.20, 1.10, 1_000_000, True),
        },
    ),
}

ALL_PROVIDERS = list(REGISTRY.keys())


def resolve_model(provider: str, model: str) -> Optional[ModelSpec]:
    """Resolve provider + alias → ModelSpec, returning None if unknown."""
    p = REGISTRY.get(provider)
    if not p:
        return None
    return p.models.get(model)


def cost_usd(provider: str, model: str, tokens_in: int, tokens_out: int) -> float:
    spec = resolve_model(provider, model)
    if not spec:
        return 0.0
    return (tokens_in / 1_000_000) * spec.input_per_mtok + (tokens_out / 1_000_000) * spec.output_per_mtok


def list_models(provider: str | None = None) -> list[tuple[str, str, float, float]]:
    """Return (provider, alias, input_per_mtok, output_per_mtok) tuples."""
    out: list[tuple[str, str, float, float]] = []
    providers = [provider] if provider else ALL_PROVIDERS
    for p in providers:
        spec = REGISTRY.get(p)
        if not spec:
            continue
        for m in spec.models.values():
            out.append((p, m.alias, m.input_per_mtok, m.output_per_mtok))
    return out
