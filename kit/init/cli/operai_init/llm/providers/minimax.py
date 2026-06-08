"""MiniMax provider (Text Generation API).

Docs: https://intl.minimaxi.com/document/ChatCompletion
Auth: `Authorization: Bearer <MINIMAX_API_KEY>`
Endpoint: https://api.minimaxi.chat/v1/text/chatcompletion_v2
OpenAI-compatible body shape (MiniMax's v2 endpoint).
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
    headers = {"Authorization": f"Bearer {api_key}"}
    body: dict = {
        "model": model_id,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user",   "content": user},
        ],
        "max_tokens":  max_tokens,
        "temperature": temperature,
    }
    if json_mode:
        body["response_format"] = {"type": "json_object"}

    resp = post_json("https://api.minimaxi.chat/v1/text/chatcompletion_v2",
                     headers=headers, body=body, timeout=timeout)
    rb = resp["body"]

    text = ""
    choices = rb.get("choices", [])
    if choices:
        text = choices[0].get("message", {}).get("content", "") or ""

    u = rb.get("usage", {})
    return {
        "text":       text.strip(),
        "tokens_in":  int(u.get("prompt_tokens", 0)),
        "tokens_out": int(u.get("completion_tokens", 0)),
        "_raw":       rb,
    }
