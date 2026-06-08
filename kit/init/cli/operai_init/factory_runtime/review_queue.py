"""Review queue — markdown file per decision under brain/review/.

The daemon routes outputs:
  - auto_send   → v0.9.3 will send via helpdesk API (this version just logs)
  - human_review → writes markdown to brain/review/pending/<domain>/<event_id>.md
  - escalate_supervisor → writes to review/escalated/ + Slack DM (if configured)

Files are plain markdown so `operai-init ingest review` CLI (from Phase 1
ingest) can be extended later to cover factory decisions too.
"""
from __future__ import annotations
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from operai_init.factory_runtime.orchestrator import OrchestrationResult


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _review_dir(home: Path, bucket: str) -> Path:
    p = home / "brain" / "review" / bucket
    p.mkdir(parents=True, exist_ok=True)
    return p


def _render_review_md(event_id: str, result: "OrchestrationResult") -> str:
    from operai_init.factory_runtime.trace import to_markdown
    lines = [
        f"# Review required · {event_id}",
        "",
        f"*Queued: {_now_iso()}*",
        "",
        "## Decision summary",
        "",
        f"- **Action:** `{result.final_action}`",
        f"- **Rationale:** {result.final_rationale or '—'}",
        f"- **Total cost:** ${result.total_cost_usd:.6f}",
        f"- **Total latency:** {result.total_latency_ms} ms",
        "",
    ]
    if result.draft_reply:
        lines.append("## Proposed reply")
        lines.append("")
        lines.append("```")
        lines.append(result.draft_reply)
        lines.append("```")
        lines.append("")
    lines.append("## Full trace")
    lines.append("")
    lines.append(to_markdown(result, event_label=event_id))
    return "\n".join(lines) + "\n"


def route_decision(
    home: Path,
    event_id: str,
    domain: str,
    result: "OrchestrationResult",
) -> Path:
    """Write the result to the appropriate review bucket, return path written."""
    action = result.final_action or "unknown"
    bucket_map = {
        "auto_send":           "auto-sent",    # v0.9.3 will actually send; for now log
        "human_review":        "pending",
        "escalate_supervisor": "escalated",
        "unknown":             "unknown",
    }
    bucket = bucket_map.get(action, "unknown")
    domain_dir = _review_dir(home, f"{bucket}/{domain}")
    path = domain_dir / f"{event_id}.md"
    path.write_text(_render_review_md(event_id, result))
    os.chmod(path, 0o640)
    return path


def list_pending(home: Path, domain: str | None = None) -> list[dict]:
    base = home / "brain" / "review" / "pending"
    if not base.exists():
        return []
    out = []
    for md in sorted(base.rglob("*.md")):
        rel = md.relative_to(base)
        parts = rel.parts
        if domain and (not parts or parts[0] != domain):
            continue
        out.append({
            "event_id": md.stem,
            "domain":   parts[0] if parts else "?",
            "path":     str(md),
            "queued_at": datetime.fromtimestamp(md.stat().st_mtime, tz=timezone.utc).isoformat(),
            "size":     md.stat().st_size,
        })
    return out


def digest_summary(home: Path) -> str:
    """Human-readable one-line summary for Slack/email digests."""
    pending = list_pending(home)
    escalated = list_pending_in_bucket(home, "escalated")
    auto_sent = list_pending_in_bucket(home, "auto-sent")
    return (
        f"OperAI factory digest: "
        f"{len(pending)} pending review, "
        f"{len(escalated)} escalated, "
        f"{len(auto_sent)} auto-sent (24h)."
    )


def list_pending_in_bucket(home: Path, bucket: str, within_hours: int = 24) -> list[dict]:
    base = home / "brain" / "review" / bucket
    if not base.exists():
        return []
    import time
    cutoff = time.time() - within_hours * 3600
    return [
        {"event_id": p.stem, "path": str(p)}
        for p in base.rglob("*.md")
        if p.stat().st_mtime >= cutoff
    ]
