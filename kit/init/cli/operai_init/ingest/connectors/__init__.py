"""Ingest connectors — one module per source. Phase 1 ships structured-only:
Shopify (aggregated), Klaviyo (metrics), Meta/Google Ads (account-level).

High-risk unstructured sources (Gmail, Slack, Notion, Drive, Richpanel) are
deliberately out of scope until the v0.5 design pass addresses the 5 Codex
blockers (employee-scope exclusion, high-recall special-category, subject
registry hardening validation, ACL-at-index proof, evidence-encryption review).
"""
