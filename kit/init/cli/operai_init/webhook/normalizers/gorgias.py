"""Gorgias webhook payload → CanonicalTicket.

Gorgias ticket webhook shape:
{
  "id": 123,
  "subject": "...",
  "priority": "low|normal|high|urgent",
  "channel": "email|chat|contact-form|...",
  "status": "open|pending|closed|...",
  "customer": {"email": "...", "name": "...", "phone": "..."},
  "messages": [{"body_text": "...", "sender": {"email": ...}, "from_agent": false, "created_datetime": "..."}],
  "tags": [{"name": "..."}],
  "created_datetime": "..."
}
"""
from __future__ import annotations


def source_ticket_id(payload: dict) -> str:
    return str(payload.get("id", "unknown"))


def normalize(payload: dict) -> dict:
    customer = payload.get("customer", {}) or {}
    messages = payload.get("messages") or []
    first_customer_msg = next((m for m in messages if not m.get("from_agent")), messages[0] if messages else {})
    body = first_customer_msg.get("body_text") or first_customer_msg.get("body_html") or ""
    subject = payload.get("subject", "") or ""

    raw_ticket = f"{subject}\n\n{body}".strip() if subject else body

    priority_map = {"urgent": "P1", "high": "P2", "normal": "P3", "low": "P4"}
    priority = priority_map.get((payload.get("priority") or "").lower(), "P3")

    tags = [t.get("name") for t in (payload.get("tags") or []) if isinstance(t, dict) and t.get("name")]

    return {
        "raw_ticket":      raw_ticket,
        "ticket_summary":  subject or (body[:200] if body else ""),
        "customer_email":  customer.get("email"),
        "priority":        priority,
        "channel":         (payload.get("channel") or "email").lower(),
        "source_provider": "gorgias",
        "source_ticket_id": source_ticket_id(payload),
        "source_created_at": payload.get("created_datetime"),
        "tags":            tags,
    }
