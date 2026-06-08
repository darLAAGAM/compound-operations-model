"""Brain auto-lookup — resolves context fields from the brain before dispatching.

Sub-agent SOULs assume they'll receive pre-loaded fields like `brand_voice`,
`applicable_policies`, and `customer_order_history`. v0.9.0 required the
caller to pre-load these into the event JSON. v0.9.1 resolves them
automatically from the brain so the daemon can process events that only
carry the raw ticket.

Resolution strategy (stdlib-only):
  - brand_voice → read knowledge/<brand>/marketing/brand-voice.md (first 2KB)
  - applicable_policies → grep-like scan of knowledge/<brand>/cs/policies/ for category
  - customer_order_history → shopify cred lookup if available (else None)

Pluggable: each brand can override these via workflow hooks (see workflows/).
"""
from __future__ import annotations
import json
import os
import re
from pathlib import Path
from typing import Any


def _brain_root() -> Path:
    return Path(os.environ.get("OPERAI_HOME", "/opt/operai")) / "brain"


def _knowledge_root(brand: str) -> Path:
    return _brain_root() / "knowledge" / brand


def _read_or_none(path: Path, max_bytes: int = 2048) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    try:
        text = path.read_text(errors="replace")
    except Exception:
        return None
    return text[:max_bytes] if max_bytes > 0 else text


def resolve_brand_voice(brand: str) -> str | None:
    """Look up the brand voice guide."""
    candidates = [
        _knowledge_root(brand) / "marketing" / "brand-voice.md",
        _knowledge_root(brand) / "marketing" / "tone-of-voice.md",
        _knowledge_root(brand) / "brand" / "voice.md",
    ]
    for p in candidates:
        text = _read_or_none(p)
        if text:
            return text
    return None


def resolve_applicable_policies(brand: str, category: str | None) -> list[dict] | None:
    """Walk cs/policies/ and return policies whose filename or title matches category."""
    policies_dir = _knowledge_root(brand) / "cs" / "policies"
    if not policies_dir.exists():
        return None
    category_lc = (category or "").lower()
    out: list[dict] = []
    for md in sorted(policies_dir.glob("*.md")):
        name = md.stem.lower()
        text = _read_or_none(md, max_bytes=0) or ""
        # Match by filename containing category OR by "category:" frontmatter
        matches = (
            category_lc and (category_lc in name or category_lc in text[:500].lower())
        )
        if matches or not category:
            # Extract first heading as title
            title = md.stem.replace("-", " ").title()
            m = re.search(r"^#\s+(.+)$", text, flags=re.MULTILINE)
            if m:
                title = m.group(1).strip()
            out.append({
                "policy_id":   md.stem,
                "title":       title,
                "excerpt":     text[:600],
                "source_path": f"brain/knowledge/{brand}/cs/policies/{md.name}",
            })
        if len(out) >= 5:
            break
    return out or None


def resolve_customer_history(brand: str, customer_email: str | None) -> dict | None:
    """Stub resolver — real implementation would query Shopify via connector creds.

    v0.9.1 returns None if customer_email is a subject token (`<email:subject_xxx>`)
    because the brain has the token, not the raw email. Real lookup happens in
    workflow hooks where the brand knows how to resolve their CRM.
    """
    if not customer_email:
        return None
    if customer_email.startswith("<") and customer_email.endswith(">"):
        # Tokenized PII — brand-specific CRM lookup via workflow hook
        return None
    # Placeholder: future v0.9.2 will add Shopify customer_search via connector
    return None


def enrich_event(brand: str, event: dict) -> dict:
    """Given a raw event, auto-resolve the standard brain-lookup fields in place.

    Does not overwrite fields the caller already provided. Safe to call multiple times.
    """
    enriched = dict(event)

    if "brand_voice" not in enriched or not enriched["brand_voice"]:
        bv = resolve_brand_voice(brand)
        if bv:
            enriched["brand_voice"] = bv

    # For applicable_policies we need a category — try triage output if already run,
    # else pre-resolve with None and let the policy-lookup sub-agent refine.
    if "applicable_policies" not in enriched or not enriched["applicable_policies"]:
        cat = enriched.get("category")
        pols = resolve_applicable_policies(brand, cat)
        if pols:
            enriched["applicable_policies"] = pols

    if "customer_order_history" not in enriched or not enriched["customer_order_history"]:
        ce = enriched.get("customer_email")
        hist = resolve_customer_history(brand, ce)
        if hist:
            enriched["customer_order_history"] = hist

    return enriched
