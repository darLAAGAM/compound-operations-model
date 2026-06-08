"""operai_init.ingest — Phase 1 (v0.4).

Ships structured-low-risk connectors (Shopify aggregated, Klaviyo metrics,
Ads stubs) plus the compliance infrastructure required before any connector
runs: allowlist, subject registry, delete ledger, evidence store, DLP,
ACL-aware retrieval store layout.

High-risk unstructured sources (Gmail, Slack, Notion, Drive, Richpanel) are
blocked in this phase. See Playbook Ch.11f for the v0.5 roadmap to unlock them.
"""
__version__ = "0.4.0"
