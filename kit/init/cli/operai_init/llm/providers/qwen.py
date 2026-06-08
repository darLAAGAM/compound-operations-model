"""Alibaba Qwen (DashScope international) provider.

Docs: https://www.alibabacloud.com/help/en/model-studio/developer-reference/
Auth: `Authorization: Bearer <DASHSCOPE_API_KEY>`
Endpoint: https://dashscope-intl.aliyuncs.com/api/v1/services/aigc/text-generation/generation
Body shape is different from OpenAI — Alibaba-native schema.
"""
from __future__ import annotations
import json

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
        "Authorization": f"Bearer {api_key}",
        "X-DashScope-SSE": "disable",
    }
    # DashScope expects `input.messages` + `parameters`
    if json_mode:
        system = system + "\n\nRespond with a single JSON object and nothing else."
    body: dict = {
        "model": model_id,
        "input": {
            "messages": [
                {"role": "system", "content": system},
                {"role": "user",   "content": user},
            ],
        },
        "parameters": {
            "max_tokens":  max_tokens,
            "temperature": temperature,
            "result_format": "message",
        },
    }
    url = "https://dashscope-intl.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
    resp = post_json(url, headers=headers, body=body, timeout=timeout)
    rb = resp["body"]

    text = ""
    output = rb.get("output", {})
    choices = output.get("choices", [])
    if choices:
        text = choices[0].get("message", {}).get("content", "") or ""

    u = rb.get("usage", {})
    return {
        "text":       text.strip(),
        "tokens_in":  int(u.get("input_tokens", 0)),
        "tokens_out": int(u.get("output_tokens", 0)),
        "_raw":       rb,
    }
