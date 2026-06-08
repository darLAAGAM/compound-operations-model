"""Klaviyo connector — metrics + campaign aggregates only.

Scope:
  * metrics list       — names of tracked events
  * campaigns          — titles, sent_counts, open/click rates (aggregated)
  * lists              — list sizes (count only, no members)

Out of scope: individual profiles, individual events, segment members.
"""
from __future__ import annotations
import json
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from operai_init.ingest.pipeline import CanonicalDoc, Pipeline


def _load_cred(home: Path) -> dict | None:
    p = home / "credentials" / "klaviyo.json"
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text()).get("data", {})
    except json.JSONDecodeError:
        return None


def _http_get(url: str, api_key: str, revision: str) -> dict:
    req = urllib.request.Request(url, headers={
        "Authorization": f"Klaviyo-API-Key {api_key}",
        "revision": revision,
        "Accept": "application/json",
    })
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def run(*, home: Path, brand: str) -> dict:
    cred = _load_cred(home)
    if not cred:
        return {"error": "Klaviyo not connected — run `operai-init connect klaviyo` first"}
    api_key = cred["api_key"]
    revision = cred.get("revision", "2024-07-15")

    metrics   = _http_get("https://a.klaviyo.com/api/metrics", api_key, revision)
    lists     = _http_get("https://a.klaviyo.com/api/lists", api_key, revision)
    campaigns = _http_get("https://a.klaviyo.com/api/campaigns?filter=equals(messages.channel,'email')", api_key, revision)

    pipeline = Pipeline(home, brand=brand)

    summary = {
        "metrics": [{"id": m["id"], "name": m["attributes"].get("name")} for m in metrics.get("data", [])],
        "lists":   [{"id": l["id"], "name": l["attributes"].get("name"), "created": l["attributes"].get("created")} for l in lists.get("data", [])],
        "campaigns_count": len(campaigns.get("data", [])),
        "campaigns_sample": [
            {
                "id":   c["id"],
                "name": c["attributes"].get("name"),
                "status": c["attributes"].get("status"),
                "send_time": c["attributes"].get("send_time"),
            }
            for c in campaigns.get("data", [])[:20]
        ],
    }

    doc = CanonicalDoc(
        source="klaviyo",
        source_ref=f"snapshot-{datetime.now(timezone.utc).strftime('%Y%m%d')}",
        kind="marketing_snapshot",
        title=f"{brand} Klaviyo snapshot",
        body_text=json.dumps(summary, indent=2),
        created_at=datetime.now(timezone.utc).isoformat(),
        updated_at=datetime.now(timezone.utc).isoformat(),
        native_acl=["marketing", "general"],
        source_meta={"revision": revision},
    )
    result = pipeline.ingest(doc)
    return {"summary": summary, "result": result.__dict__}
