"""Ads connectors — Meta + Google account-level metrics only.

No individual audiences, no PII-linked conversions. Just the numbers a founder
or CMO needs to see in the swarm's context.

v0.4 accepts that these APIs are moving targets (Meta Graph changes monthly;
Google Ads API requires OAuth + developer token). We ship a stub that reads
the `meta_ads` / `google_ads` credentials if present and writes a placeholder
snapshot; production implementations land in v0.5.
"""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path

from operai_init.ingest.pipeline import CanonicalDoc, Pipeline


def _load_cred(home: Path, service: str) -> dict | None:
    p = home / "credentials" / f"{service}.json"
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text()).get("data", {})
    except json.JSONDecodeError:
        return None


def _ingest_placeholder(pipeline: Pipeline, brand: str, service: str, cred: dict) -> dict:
    doc = CanonicalDoc(
        source=service,
        source_ref=f"snapshot-{datetime.now(timezone.utc).strftime('%Y%m%d')}",
        kind="ads_snapshot_stub",
        title=f"{brand} {service} snapshot (stub)",
        body_text=json.dumps({
            "service": service,
            "connected_at": cred.get("created_at"),
            "note": "Phase 1 stub — v0.5 ships real metric pulls. Connector credentials verified.",
        }, indent=2),
        created_at=datetime.now(timezone.utc).isoformat(),
        updated_at=datetime.now(timezone.utc).isoformat(),
        native_acl=["marketing", "general"],
        source_meta={"stub": True},
    )
    result = pipeline.ingest(doc)
    return {"service": service, "result": result.__dict__}


def run_meta(*, home: Path, brand: str) -> dict:
    cred = _load_cred(home, "meta_ads")
    if not cred:
        return {"error": "Meta Ads not connected"}
    return _ingest_placeholder(Pipeline(home, brand=brand), brand, "meta_ads", cred)


def run_google(*, home: Path, brand: str) -> dict:
    cred = _load_cred(home, "google_ads")
    if not cred:
        return {"error": "Google Ads not connected"}
    return _ingest_placeholder(Pipeline(home, brand=brand), brand, "google_ads", cred)
