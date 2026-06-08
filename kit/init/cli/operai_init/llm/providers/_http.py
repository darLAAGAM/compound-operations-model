"""Shared HTTP helper for provider modules (stdlib urllib)."""
from __future__ import annotations
import json
import urllib.error
import urllib.request
from typing import Optional


def post_json(
    url: str,
    *,
    headers: dict,
    body: dict,
    timeout: float = 60.0,
) -> dict:
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    for k, v in headers.items():
        req.add_header(k, v)
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            return {"status": resp.status, "body": json.loads(raw) if raw else {}}
    except urllib.error.HTTPError as e:
        raw = e.read().decode(errors="replace") if hasattr(e, "read") else ""
        try:
            body_err = json.loads(raw)
        except json.JSONDecodeError:
            body_err = {"raw": raw[:2000]}
        raise ProviderHTTPError(f"{e.code} {e.reason}", status=e.code, body=body_err) from e


class ProviderHTTPError(Exception):
    def __init__(self, msg: str, status: int, body: dict):
        super().__init__(f"{msg}: {json.dumps(body)[:300]}")
        self.status = status
        self.body = body
