"""Shopify connector — low-risk only (products + aggregated orders/customers).

Scope:
  * products        — full catalog snapshot (PII-free)
  * orders_agg      — daily aggregates (revenue, units, top SKUs), no PII
  * customers_agg   — counts + segment sizes, no individual records

Out of scope in Phase 1: individual orders, individual customers, abandoned
carts, drafts. These would carry PII; revisit in Phase 2 with subject-level
consent and purpose-limitation guarantees.

Every ingested doc is structured JSON → auto-accept (no review queue).
"""
from __future__ import annotations
import json
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Iterator

from operai_init.ingest.pipeline import CanonicalDoc, Pipeline
from operai_init import common


def _load_cred(home: Path) -> dict | None:
    p = home / "credentials" / "shopify.json"
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text()).get("data", {})
    except json.JSONDecodeError:
        return None


def _http_json(url: str, token: str) -> dict:
    req = urllib.request.Request(url, headers={
        "X-Shopify-Access-Token": token,
        "Accept": "application/json",
    })
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _products(shop: str, token: str, api_version: str) -> Iterator[dict]:
    # Paginate via page_info (Shopify cursor-based)
    url = f"https://{shop}.myshopify.com/admin/api/{api_version}/products.json?limit=250"
    while url:
        # NOTE: production needs Link-header parsing for page_info. MVP: single page.
        data = _http_json(url, token)
        for p in data.get("products", []):
            yield p
        url = None  # TODO: parse Link: rel=next from response headers


def _orders_aggregate(shop: str, token: str, api_version: str, days: int = 90) -> dict:
    since = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")
    url = (f"https://{shop}.myshopify.com/admin/api/{api_version}/orders.json"
           f"?status=any&created_at_min={urllib.parse.quote(since)}"
           f"&fields=id,created_at,total_price,currency,line_items&limit=250")
    data = _http_json(url, token)
    orders = data.get("orders", [])

    by_day: dict[str, dict] = defaultdict(lambda: {"revenue": 0.0, "count": 0, "units": 0})
    top_sku: dict[str, dict] = defaultdict(lambda: {"units": 0, "revenue": 0.0})
    for o in orders:
        day = o["created_at"][:10]
        total = float(o.get("total_price") or 0)
        by_day[day]["revenue"] += total
        by_day[day]["count"] += 1
        for li in o.get("line_items", []):
            by_day[day]["units"] += int(li.get("quantity") or 0)
            sku = li.get("sku") or li.get("title") or "unknown"
            top_sku[sku]["units"] += int(li.get("quantity") or 0)
            top_sku[sku]["revenue"] += float(li.get("price") or 0) * int(li.get("quantity") or 0)

    # Strip anything that could be PII (order ids, customer refs) — keep only aggregates.
    return {
        "window_days": days,
        "since":       since,
        "total_orders": sum(d["count"] for d in by_day.values()),
        "total_revenue": round(sum(d["revenue"] for d in by_day.values()), 2),
        "currency":     orders[0].get("currency") if orders else None,
        "by_day":       {k: {"revenue": round(v["revenue"], 2), "count": v["count"], "units": v["units"]} for k, v in sorted(by_day.items())},
        "top_skus":     [{"sku": k, **{kk: round(vv, 2) if isinstance(vv, float) else vv for kk, vv in v.items()}}
                         for k, v in sorted(top_sku.items(), key=lambda kv: -kv[1]["revenue"])[:20]],
    }


def run(*, home: Path, brand: str, days: int = 90) -> dict:
    cred = _load_cred(home)
    if not cred:
        return {"error": "Shopify not connected — run `operai-init connect shopify` first"}
    shop = cred["shop"]
    token = cred["token"]
    api_version = cred.get("api_version", "2024-01")

    pipeline = Pipeline(home, brand=brand)

    # Products snapshot (one doc summarising the catalog)
    products = list(_products(shop, token, api_version))
    products_doc = CanonicalDoc(
        source="shopify",
        source_ref=f"products-snapshot-{datetime.now(timezone.utc).strftime('%Y%m%d')}",
        kind="product_catalog",
        title=f"{brand} product catalog snapshot",
        body_text=json.dumps({
            "total_products": len(products),
            "products": [{
                "id":    p.get("id"),
                "title": p.get("title"),
                "type":  p.get("product_type"),
                "vendor": p.get("vendor"),
                "tags":  p.get("tags"),
                "status": p.get("status"),
                "variants": [{"sku": v.get("sku"), "price": v.get("price"), "inventory": v.get("inventory_quantity")}
                             for v in p.get("variants", [])],
            } for p in products],
        }, indent=2),
        created_at=datetime.now(timezone.utc).isoformat(),
        updated_at=datetime.now(timezone.utc).isoformat(),
        native_acl=["product", "general"],
        source_meta={"shop": shop, "api_version": api_version},
    )
    pr = pipeline.ingest(products_doc)

    # Orders aggregated (one doc per run)
    orders_agg = _orders_aggregate(shop, token, api_version, days=days)
    orders_doc = CanonicalDoc(
        source="shopify",
        source_ref=f"orders-agg-{datetime.now(timezone.utc).strftime('%Y%m%d')}",
        kind="orders_aggregate",
        title=f"{brand} orders — last {days}d aggregate",
        body_text=json.dumps(orders_agg, indent=2),
        created_at=datetime.now(timezone.utc).isoformat(),
        updated_at=datetime.now(timezone.utc).isoformat(),
        native_acl=["finance", "general"],
        source_meta={"shop": shop, "days": days},
    )
    or_ = pipeline.ingest(orders_doc)

    return {
        "shop":       shop,
        "products":   {"count": len(products), "result": pr.__dict__},
        "orders_agg": {"window_days": days, "result": or_.__dict__},
    }
