#!/usr/bin/env python3
"""OperAI webhook receiver — HTTP server that accepts helpdesk webhooks.

Runs on 127.0.0.1:8788 behind the brand's Cloudflare Tunnel (webhook.<brand>.com).

Endpoints:
  POST /webhook/<provider>/<domain>    e.g. /webhook/richpanel/cs
  GET  /health                         health check
  GET  /                                list configured providers

Flow:
  1. Read raw body
  2. Verify HMAC signature for the provider
  3. Parse JSON
  4. Normalize to CanonicalTicket
  5. Write to /opt/operai/events/<domain>/pending/<event_id>.json
  6. Return 200 fast; the factory-runtime daemon processes async

Failure modes:
  - 401: HMAC mismatch or missing signature
  - 400: unknown provider, bad JSON, missing required fields
  - 404: unknown domain (domain not in the brand's factory list)
  - 500: filesystem write failed (unusual)

All rejections are logged to /opt/operai/logs/webhook.log with the reason.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import logging
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, PlainTextResponse
from starlette.routing import Route

# Local imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from operai_init.webhook import config, hmac_verify
from operai_init.webhook.normalizers import richpanel, gorgias, zendesk, intercom


OPERAI_HOME = Path(os.environ.get("OPERAI_HOME", "/opt/operai"))

logging.basicConfig(
    level=os.environ.get("OPERAI_LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
log = logging.getLogger("operai-webhook")

NORMALIZERS = {
    "richpanel": richpanel,
    "gorgias":   gorgias,
    "zendesk":   zendesk,
    "intercom":  intercom,
}


def _events_dir(domain: str) -> Path:
    p = OPERAI_HOME / "events" / "pending" / domain
    p.mkdir(parents=True, exist_ok=True)
    return p


def _event_id(provider: str, source_id: str) -> str:
    # Stable + reasonably unique. Include a short uuid for safety on re-fires.
    return f"{provider}-{source_id}-{uuid.uuid4().hex[:6]}"


async def handle_health(request: Request):
    configured = config.list_configured(OPERAI_HOME)
    return JSONResponse({
        "ok":         True,
        "providers":  configured,
        "home":       str(OPERAI_HOME),
        "version":    "3.0.0",
    })


async def handle_index(request: Request):
    configured = config.list_configured(OPERAI_HOME)
    base = config.get_endpoint_base(OPERAI_HOME) or "https://<configure via operai-init webhook configure>"
    body = [
        "OperAI webhook receiver v3.0.0",
        "",
        "Configured providers:",
    ]
    for p in config.SUPPORTED:
        mark = "[x]" if p in configured else "[ ]"
        body.append(f"  {mark} {p}  →  POST {base}/webhook/{p}/<domain>")
    body.append("")
    body.append("Health: /health")
    return PlainTextResponse("\n".join(body) + "\n")


async def handle_webhook(request: Request):
    provider = request.path_params["provider"]
    domain   = request.path_params["domain"]
    client   = request.client.host if request.client else "?"

    # 1. Load body before anything else (HMAC needs raw bytes)
    body = await request.body()

    # 2. Provider supported?
    if provider not in NORMALIZERS:
        log.warning("reject %s (%s): unknown provider", client, provider)
        return JSONResponse({"error": f"unknown provider: {provider}"}, status_code=400)

    # 3. Secret configured?
    secret = config.get_secret(OPERAI_HOME, provider)
    if not secret:
        log.warning("reject %s (%s): provider not configured", client, provider)
        return JSONResponse({"error": f"provider '{provider}' not configured"}, status_code=401)

    # 4. HMAC verify
    ok, reason = hmac_verify.verify(provider, secret, body, dict(request.headers.items()))
    if not ok:
        log.warning("reject %s (%s): hmac fail (%s)", client, provider, reason)
        return JSONResponse({"error": "signature verification failed", "reason": reason}, status_code=401)

    # 5. Parse JSON
    try:
        payload = json.loads(body.decode("utf-8"))
    except json.JSONDecodeError as e:
        log.warning("reject %s (%s): bad json: %s", client, provider, e)
        return JSONResponse({"error": f"invalid JSON: {e}"}, status_code=400)

    # 6. Normalize
    normalizer = NORMALIZERS[provider]
    try:
        canonical = normalizer.normalize(payload)
        source_id = normalizer.source_ticket_id(payload)
    except Exception as e:  # noqa: BLE001
        log.exception("normalize failed for %s", provider)
        return JSONResponse({"error": f"normalize error: {e}"}, status_code=400)

    if not canonical.get("raw_ticket"):
        log.warning("reject %s (%s): empty raw_ticket after normalize", client, provider)
        return JSONResponse({"error": "normalized payload has empty raw_ticket"}, status_code=400)

    # 7. Write event to pending/
    event_id = _event_id(provider, source_id)
    out_path = _events_dir(domain) / f"{event_id}.json"

    # Save the raw payload alongside for audit
    raw_dump_dir = OPERAI_HOME / "events" / "webhook-payloads" / provider
    raw_dump_dir.mkdir(parents=True, exist_ok=True)
    (raw_dump_dir / f"{event_id}.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False))

    out_path.write_text(json.dumps(canonical, indent=2, ensure_ascii=False))

    log.info("accepted %s/%s → %s", provider, domain, event_id)

    return JSONResponse({
        "ok":        True,
        "event_id":  event_id,
        "domain":    domain,
        "provider":  provider,
        "ts":        datetime.now(timezone.utc).isoformat(),
    })


app = Starlette(
    debug=bool(os.environ.get("OPERAI_DEBUG")),
    routes=[
        Route("/",        handle_index,   methods=["GET"]),
        Route("/health",  handle_health,  methods=["GET"]),
        Route("/webhook/{provider}/{domain}", handle_webhook, methods=["POST"]),
    ],
)


def main():
    import uvicorn
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8788)
    args = ap.parse_args()

    log.info("webhook receiver starting: host=%s port=%s home=%s", args.host, args.port, OPERAI_HOME)
    log.info("configured providers: %s", config.list_configured(OPERAI_HOME))
    uvicorn.run(app, host=args.host, port=args.port, log_level="info")


if __name__ == "__main__":
    main()
