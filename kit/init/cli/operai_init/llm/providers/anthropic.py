"""Anthropic provider (Messages API).

Docs: https://docs.anthropic.com/en/api/messages
Auth: header `x-api-key: sk-ant-...` + `anthropic-version: 2023-06-01`
"""
from __future__ import annotations

from operai_init.llm.providers._http import post_json


def call(
    *,
    api_key: str,
    model_id: str,
    system: str,
    user: str,
    max_tokens: int,
    temperature: float,
    json_mode: bool,
    timeout: float,
) -> dict:
    headers = {
        "x-api-key":         api_key,
        "anthropic-version": "2023-06-01",
    }
    body: dict = {
        "model":       model_id,
        "max_tokens":  max_tokens,
        "temperature": temperature,
        "system":      system,
        "messages":    [{"role": "user", "content": user}],
    }
    if json_mode:
        # Anthropic doesn't have a hard json_mode flag; we steer via system + response format guidance.
        body["system"] = system + "\n\nRespond with a single JSON object and nothing else. Do not wrap in code fences."

    resp = post_json("https://api.anthropic.com/v1/messages",
                     headers=headers, body=body, timeout=timeout)
    rb = resp["body"]
    text = ""
    if rb.get("content"):
        for block in rb["content"]:
            if block.get("type") == "text":
                text += block.get("text", "")
    usage_block = rb.get("usage", {})
    return {
        "text":       text.strip(),
        "tokens_in":  int(usage_block.get("input_tokens", 0)),
        "tokens_out": int(usage_block.get("output_tokens", 0)),
        "_raw":       rb,
    }
