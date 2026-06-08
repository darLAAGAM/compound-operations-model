"""Richpanel webhook payload → CanonicalTicket.

Richpanel ticket.created webhook shape (as of 2026-04):
{
  "event": "ticket.created",
  "data": {
    "id": "...",
    "subject": "...",
    "priority": "LOW|NORMAL|HIGH|URGENT",
    "status": "OPEN|PENDING|RESOLVED|CLOSED",
    "customer": {"email": "...", "name": "...", "phone": "..."},
    "messages": [{"body": "...", "direction": "INBOUND|OUTBOUND", "created_at": "..."}],
    "channel": "email|chat|form|...",
    "tags": [...],
    "created_at": "..."
  }
}
"""
from __future__ import annotations


def source_ticket_id(payload: dict) -> str:
    return str(payload.get("data", {}).get("id", "unknown"))


def normalize(payload: dict) -> dict:
    data = payload.get("data", {}) or {}
    customer = data.get("customer", {}) or {}
    messages = data.get("messages") or []
    first_inbound = next((m for m in messages if m.get("direction", "").upper() == "INBOUND"), messages[0] if messages else {})
    body = first_inbound.get("body", "") or ""
    subject = data.get("subject", "") or ""

    raw_ticket = f"{subject}\n\n{body}".strip() if subject else body

    priority_map = {"URGENT": "P1", "HIGH": "P2", "NORMAL": "P3", "LOW": "P4"}
    priority = priority_map.get((data.get("priority") or "").upper(), "P3")

    return {
        "raw_ticket":      raw_ticket,
        "ticket_summary":  subject or (body[:200] if body else ""),
        "customer_email":  customer.get("email"),     # raw; DLP tokenizes if ingested
        "priority":        priority,
        "channel":         (data.get("channel") or "email").lower(),
        "source_provider": "richpanel",
        "source_ticket_id": source_ticket_id(payload),
        "source_created_at": data.get("created_at"),
        "tags":            data.get("tags") or [],
    }
