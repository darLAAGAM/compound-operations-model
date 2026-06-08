"""Google Gemini provider (Generative Language API).

Docs: https://ai.google.dev/api/rest
Auth: header `x-goog-api-key: AIza...`
Note: Gemini's API uses a different request shape than OpenAI-compatible.
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
    headers = {"x-goog-api-key": api_key}
    body: dict = {
        "system_instruction": {
            "parts": [{"text": system}],
        },
        "contents": [{
            "role": "user",
            "parts": [{"text": user}],
        }],
        "generationConfig": {
            "maxOutputTokens": max_tokens,
            "temperature": temperature,
        },
    }
    if json_mode:
        body["generationConfig"]["responseMimeType"] = "application/json"

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_id}:generateContent"
    resp = post_json(url, headers=headers, body=body, timeout=timeout)
    rb = resp["body"]

    text = ""
    candidates = rb.get("candidates", [])
    if candidates:
        parts = candidates[0].get("content", {}).get("parts", [])
        for p in parts:
            text += p.get("text", "")

    u = rb.get("usageMetadata", {})
    return {
        "text":       text.strip(),
        "tokens_in":  int(u.get("promptTokenCount", 0)),
        "tokens_out": int(u.get("candidatesTokenCount", 0)),
        "_raw":       rb,
    }
