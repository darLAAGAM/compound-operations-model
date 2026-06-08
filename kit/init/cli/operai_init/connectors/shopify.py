"""Shopify connector — Custom App / Admin API access token flow.

Why not OAuth app? OperAI agents run server-side with long-lived access to one
specific Shopify store owned by the founder. The cleanest flow is:

  1. Founder creates a Custom App in their Shopify admin
  2. Founder grants Admin API scopes (orders, products, customers, etc.)
  3. Founder pastes the Admin API access token

This gives us a long-lived token scoped exactly to what the founder approved,
with no Partner app dependency on our side.
"""
from __future__ import annotations
import json
import urllib.error
import urllib.request
from pathlib import Path

from operai_init import common

DEFAULT_SCOPES = [
    "read_products", "read_orders", "read_customers", "read_inventory",
    "read_fulfillments", "read_shipping", "read_price_rules", "read_discounts",
    "read_draft_orders", "read_locations", "read_analytics",
]


def _test(shop: str, token: str) -> tuple[bool, str]:
    """Verify the token by hitting /admin/api/2024-01/shop.json."""
    url = f"https://{shop}.myshopify.com/admin/api/2024-01/shop.json"
    req = urllib.request.Request(url, headers={
        "X-Shopify-Access-Token": token,
        "Accept": "application/json",
    })
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            name = body.get("shop", {}).get("name", "?")
            return True, f"shop: {name}"
    except urllib.error.HTTPError as e:
        return False, f"HTTP {e.code}: {e.reason}"
    except Exception as e:
        return False, f"network error: {e}"


def connect(*, home: Path, brand: str) -> None:
    common.info("Shopify Custom App setup (5 min)")
    print("""
    1. In your Shopify admin, open Settings → Apps and sales channels → Develop apps
    2. Create a new app — name it "OperAI Swarm"
    3. Configure Admin API scopes. Recommended (read-only is fine for v0):
""")
    for s in DEFAULT_SCOPES:
        print(f"       - {s}")
    print("""
    4. Install the app to your store
    5. Copy the "Admin API access token" (starts with `shpat_`)
""")

    shop = common.prompt("Shopify store handle (e.g. 'acme' for acme.myshopify.com)").strip().rstrip(".myshopify.com").rstrip(".")
    if not shop:
        common.err("shop handle required")
        return

    token = common.read_secret("Admin API access token (paste, input hidden): ").strip()
    if not token.startswith("shpat_"):
        common.warn("Token does not start with 'shpat_' — continuing anyway, but verify.")

    common.info("verifying…")
    ok, detail = _test(shop, token)
    if not ok:
        common.err(f"Token rejected by Shopify ({detail})")
        if not common.confirm("Save anyway?", default=False):
            return
    else:
        common.ok(f"Shopify reachable ({detail})")

    path = common.save_credential(home, "shopify", {
        "shop":  shop,
        "token": token,
        "api_version": "2024-01",
        "scopes": DEFAULT_SCOPES,
    }, brand=brand)
    common.ok(f"credentials saved to {path}")
