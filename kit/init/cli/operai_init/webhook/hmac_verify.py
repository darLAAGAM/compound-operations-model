"""HMAC signature verification per helpdesk provider.

Each provider has a slightly different contract:

  Richpanel — X-Richpanel-Signature: sha256=<hex>   (HMAC-SHA256 over raw body)
  Gorgias   — X-Gorgias-Hmac-SHA256: <base64>       (HMAC-SHA256, base64)
  Zendesk   — X-Zendesk-Webhook-Signature + X-Zendesk-Webhook-Signature-Timestamp
              signature = base64( HMAC-SHA256(secret, timestamp + body) )
  Intercom  — X-Hub-Signature-256: sha256=<hex>     (HMAC-SHA256 over raw body)

Fail-closed: any verification failure returns False. The receiver rejects
unverified requests with 401.
"""
from __future__ import annotations
import base64
import hashlib
import hmac
from typing import Optional


def _hex_digest(secret: str, body: bytes) -> str:
    return hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()


def _b64_digest(secret: str, body: bytes) -> str:
    return base64.b64encode(hmac.new(secret.encode(), body, hashlib.sha256).digest()).decode()


def verify_richpanel(secret: str, body: bytes, header_value: str) -> bool:
    if not header_value or not secret:
        return False
    # Header: "sha256=<hex>"
    if header_value.startswith("sha256="):
        expected = header_value[len("sha256="):]
    else:
        expected = header_value
    actual = _hex_digest(secret, body)
    return hmac.compare_digest(expected.lower().strip(), actual.lower())


def verify_gorgias(secret: str, body: bytes, header_value: str) -> bool:
    if not header_value or not secret:
        return False
    actual = _b64_digest(secret, body)
    return hmac.compare_digest(header_value.strip(), actual)


def verify_zendesk(secret: str, body: bytes, signature: str, timestamp: str) -> bool:
    if not signature or not timestamp or not secret:
        return False
    payload = timestamp.encode() + body
    expected = base64.b64encode(hmac.new(secret.encode(), payload, hashlib.sha256).digest()).decode()
    return hmac.compare_digest(expected, signature.strip())


def verify_intercom(secret: str, body: bytes, header_value: str) -> bool:
    if not header_value or not secret:
        return False
    if header_value.startswith("sha256="):
        expected = header_value[len("sha256="):]
    else:
        expected = header_value
    actual = _hex_digest(secret, body)
    return hmac.compare_digest(expected.lower().strip(), actual.lower())


def verify(
    provider: str,
    secret: str,
    body: bytes,
    headers: dict,
) -> tuple[bool, str]:
    """Return (ok, reason). All comparisons are constant-time."""
    # Normalize headers to lowercase for lookup
    h = {k.lower(): v for k, v in headers.items()}
    if provider == "richpanel":
        sig = h.get("x-richpanel-signature", "")
        return (verify_richpanel(secret, body, sig), "richpanel-sig" if sig else "missing-header")
    if provider == "gorgias":
        sig = h.get("x-gorgias-hmac-sha256", "")
        return (verify_gorgias(secret, body, sig), "gorgias-sig" if sig else "missing-header")
    if provider == "zendesk":
        sig = h.get("x-zendesk-webhook-signature", "")
        ts  = h.get("x-zendesk-webhook-signature-timestamp", "")
        if not sig or not ts:
            return (False, "missing-headers")
        return (verify_zendesk(secret, body, sig, ts), "zendesk-sig")
    if provider == "intercom":
        sig = h.get("x-hub-signature-256", h.get("x-hub-signature", ""))
        return (verify_intercom(secret, body, sig), "intercom-sig" if sig else "missing-header")
    return (False, f"unknown-provider:{provider}")
