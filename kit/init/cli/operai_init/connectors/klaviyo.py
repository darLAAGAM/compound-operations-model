"""Klaviyo connector — Private API key flow.

Klaviyo exposes Private API keys per account. For OperAI agents, a read/write
key scoped to Lists + Campaigns + Metrics + Profiles is sufficient.
"""
from __future__ import annotations
import json
import urllib.error
import urllib.request
from pathlib import Path

from operai_init import common


def _test(key: str) -> tuple[bool, str]:
    """Verify by hitting /api/accounts/."""
    req = urllib.request.Request(
        "https://a.klaviyo.com/api/accounts/",
        headers={
            "Authorization": f"Klaviyo-API-Key {key}",
            "revision": "2024-07-15",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            accounts = body.get("data", [])
            if accounts:
                attrs = accounts[0].get("attributes", {})
                return True, f"account: {attrs.get('contact_information', {}).get('organization_name', '?')}"
            return True, "reachable"
    except urllib.error.HTTPError as e:
        return False, f"HTTP {e.code}: {e.reason}"
    except Exception as e:
        return False, f"network error: {e}"


def connect(*, home: Path, brand: str) -> None:
    common.info("Klaviyo Private API key setup (2 min)")
    print("""
    1. In Klaviyo: Account → Settings → API keys
    2. Create Private API key — name it "OperAI Swarm"
    3. Grant scopes: Accounts (read), Campaigns (r/w), Lists (r/w),
       Metrics (read), Profiles (r/w), Events (read), Flows (read)
    4. Copy the key (starts with `pk_`)
""")

    key = common.read_secret("Klaviyo Private API key (paste, input hidden): ").strip()
    if not key.startswith("pk_"):
        common.warn("Key does not start with 'pk_' — continuing anyway, but verify.")

    common.info("verifying…")
    ok, detail = _test(key)
    if not ok:
        common.err(f"Key rejected by Klaviyo ({detail})")
        if not common.confirm("Save anyway?", default=False):
            return
    else:
        common.ok(f"Klaviyo reachable ({detail})")

    path = common.save_credential(home, "klaviyo", {
        "api_key":  key,
        "revision": "2024-07-15",
    }, brand=brand)
    common.ok(f"credentials saved to {path}")
