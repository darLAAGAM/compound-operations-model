"""Intercom webhook payload → CanonicalTicket.

Intercom emits conversation-level webhooks. The interesting topic for CS is
`conversation.user.created` and `conversation.user.replied`.

Shape (simplified):
{
  "type": "notification_event",
  "topic": "conversation.user.created",
  "data": {
    "item": {
      "id": "abc123",
      "type": "conversation",
      "source": {
        "subject": "...",
        "body": "<p>...</p>",
        "author": {"email": "...", "name": "...", "type": "user"}
      },
      "contacts": {"contacts": [{"email": "...", "name": "..."}]},
      "tags": {"tags": [{"name": "..."}]},
      "priority": "priority|not_priority",
      "created_at": 1712345678
    }
  }
}
"""
from __future__ import annotations
import re
from datetime import datetime, timezone


def source_ticket_id(payload: dict) -> str:
    return str(payload.get("data", {}).get("item", {}).get("id", "unknown"))


def _strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text or "").strip()


def normalize(payload: dict) -> dict:
    item = payload.get("data", {}).get("item", {}) or {}
    source = item.get("source", {}) or {}
    author = source.get("author", {}) or {}

    subject = source.get("subject", "") or ""
    body = _strip_html(source.get("body", "") or "")
    raw_ticket = f"{subject}\n\n{body}".strip() if subject else body

    # Intercom priority is binary; map to P2 if prioritized else P3
    priority = "P2" if (item.get("priority") == "priority") else "P3"

    tags = []
    tags_block = item.get("tags", {}).get("tags") or []
    for t in tags_block:
        if isinstance(t, dict) and t.get("name"):
            tags.append(t["name"])

    created_ts = item.get("created_at")
    created_iso = None
    if created_ts:
        try:
            created_iso = datetime.fromtimestamp(int(created_ts), tz=timezone.utc).isoformat()
        except (ValueError, TypeError):
            created_iso = None

    return {
        "raw_ticket":      raw_ticket,
        "ticket_summary":  subject or (body[:200] if body else ""),
        "customer_email":  author.get("email"),
        "priority":        priority,
        "channel":         "intercom",
        "source_provider": "intercom",
        "source_ticket_id": source_ticket_id(payload),
        "source_created_at": created_iso,
        "tags":            tags,
    }
