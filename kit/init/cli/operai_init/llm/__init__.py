"""operai_init.llm — LLM provider abstraction.

Zero external dependencies. Each provider uses stdlib urllib.

Public API:
    from operai_init.llm import client as llm
    resp = llm.chat(system=..., user=..., json_mode=True, caller="cs-factory:triage")
    resp.text, resp.cost_usd, resp.provider, resp.model

Providers: anthropic, openai, gemini, qwen, minimax
"""
__version__ = "0.8.0"
