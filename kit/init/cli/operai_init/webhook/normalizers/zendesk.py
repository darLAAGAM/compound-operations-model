"""Zendesk webhook payload → CanonicalTicket.

Zendesk webhooks are user-configurable via Triggers. We expect the trigger
to POST a payload of the form:

{
  "ticket": {
    "id": 42,
    "subject": "...",
    "description": "...",
    "priority": "urgent|high|normal|low",
    "via": {"channel": "email|web|chat|..."},
    "requester": {"email": "...", "name": "..."},
    "tags": [...],
    "created_at": "..."
  }
}

If the brand's trigger emits a different shape, they adjust this module or
add a workflow pre-hook.
"""
from __future__ import annotations


def source_ticket_id(payload: dict) -> str:
    return str(payload.get("ticket", {}).get("id", payload.get("id", "unknown")))


def normalize(payload: dict) -> dict:
    ticket = payload.get("ticket") or payload
    requester = ticket.get("requester", {}) or {}
    subject = ticket.get("subject", "") or ""
    description = ticket.get("description", "") or ""

    raw_ticket = f"{subject}\n\n{description}".strip() if subject else description

    priority_map = {"urgent": "P1", "high": "P2", "normal": "P3", "low": "P4"}
    priority = priority_map.get((ticket.get("priority") or "").lower(), "P3")

    via = ticket.get("via") or {}
    channel = (via.get("channel") or "email").lower()

    return {
        "raw_ticket":      raw_ticket,
        "ticket_summary":  subject or (description[:200] if description else ""),
        "customer_email":  requester.get("email"),
        "priority":        priority,
        "channel":         channel,
        "source_provider": "zendesk",
        "source_ticket_id": source_ticket_id(payload),
        "source_created_at": ticket.get("created_at"),
        "tags":            ticket.get("tags") or [],
    }
