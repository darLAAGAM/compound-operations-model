"""Integration passthroughs — Shopify / Klaviyo / Slack.

All three load credentials from /opt/operai/credentials/<service>.json (written
by `operai-init connect`) and make outbound HTTP calls via stdlib `urllib`.

Errors are returned as structured dicts; raising is reserved for auth/permission
issues handled upstream in server.py.
"""
from __future__ import annotations
import json
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

from config import CRED_DIR


def _load_cred(service: str) -> dict | None:
    p = CRED_DIR / f"{service}.json"
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text()).get("data", {})
    except json.JSONDecodeError:
        return None


def _http(
    url: str,
    *,
    method: str = "GET",
    headers: dict | None = None,
    body: bytes | None = None,
    timeout: float = 15.0,
) -> dict:
    req = urllib.request.Request(url, method=method, headers=headers or {}, data=body)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            try:
                return {"status": resp.status, "body": json.loads(raw)}
            except json.JSONDecodeError:
                return {"status": resp.status, "body": raw[:10_000]}
    except urllib.error.HTTPError as e:
        return {"status": e.code, "error": e.reason, "body": e.read().decode(errors="replace")[:4_000]}
    except Exception as e:  # noqa: BLE001
        return {"status": 0, "error": str(e)}


# ─────────────────────────────────────────────────────────────────────────────

async def shopify_query(*, principal, resource: str) -> Any:
    cred = _load_cred("shopify")
    if not cred:
        return {"error": "Shopify not connected. Run: operai-init connect shopify"}
    shop = cred.get("shop")
    token = cred.get("token")
    api_version = cred.get("api_version", "2024-01")
    if not (shop and token):
        return {"error": "Shopify credentials malformed"}
    # Guardrail: only allow GET semantics (no mutation from this tool)
    if "?" in resource:
        path_part, _, _ = resource.partition("?")
    else:
        path_part = resource
    if not path_part.endswith(".json"):
        resource = resource + ".json" if "?" not in resource else resource.replace("?", ".json?", 1)
    url = f"https://{shop}.myshopify.com/admin/api/{api_version}/{resource.lstrip('/')}"
    return _http(url, headers={
        "X-Shopify-Access-Token": token,
        "Accept": "application/json",
    })


async def klaviyo_query(*, principal, endpoint: str, params: dict | None = None) -> Any:
    cred = _load_cred("klaviyo")
    if not cred:
        return {"error": "Klaviyo not connected. Run: operai-init connect klaviyo"}
    api_key = cred.get("api_key")
    revision = cred.get("revision", "2024-07-15")
    if not api_key:
        return {"error": "Klaviyo credentials malformed"}
    qs = "?" + urllib.parse.urlencode(params or {}, doseq=True) if params else ""
    url = f"https://a.klaviyo.com/api/{endpoint.lstrip('/')}{qs}"
    return _http(url, headers={
        "Authorization": f"Klaviyo-API-Key {api_key}",
        "revision": revision,
        "Accept": "application/json",
    })


async def slack_send_message(*, principal, channel: str, text: str) -> Any:
    cred = _load_cred("slack")
    if not cred:
        return {"error": "Slack not connected. Run: operai-init connect slack"}
    bot_token = cred.get("bot_token")
    if not bot_token:
        return {"error": "Slack credentials malformed"}
    payload = json.dumps({"channel": channel, "text": text}).encode("utf-8")
    return _http(
        "https://slack.com/api/chat.postMessage",
        method="POST",
        headers={
            "Authorization": f"Bearer {bot_token}",
            "Content-Type":  "application/json; charset=utf-8",
        },
        body=payload,
    )
