"""Slack daily digest — summarizes review queue + escalations + failed events.

Sends to a Slack webhook URL configured by the brand. Uses urllib only.

Cron-based, not daemon-based. Install via `operai-init digest schedule`
which appends to the operai user's crontab (08:00 UTC daily).
"""
from __future__ import annotations
import json
import os
import subprocess
import tempfile
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


# ─────────────────────────────────────────────────────────────────────────────
# Config — /opt/operai/credentials/digest.json
# ─────────────────────────────────────────────────────────────────────────────

def _config_path(home: Path) -> Path:
    return home / "credentials" / "digest.json"


def load_config(home: Path) -> dict:
    p = _config_path(home)
    if not p.exists():
        return {"slack_webhook": None, "channel": None, "schedule_cron": None, "enabled": False}
    try:
        return json.loads(p.read_text())
    except json.JSONDecodeError:
        return {"slack_webhook": None, "channel": None, "schedule_cron": None, "enabled": False}


def save_config(home: Path, data: dict) -> Path:
    p = _config_path(home)
    p.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(p.parent), prefix=".digest-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(data, f, indent=2, sort_keys=True)
        os.chmod(tmp, 0o600)
        os.replace(tmp, p)
    except Exception:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise
    return p


# ─────────────────────────────────────────────────────────────────────────────
# Digest content
# ─────────────────────────────────────────────────────────────────────────────

def _count_files(path: Path, pattern: str = "*.md", within_hours: int | None = None) -> int:
    if not path.exists():
        return 0
    if within_hours is None:
        return sum(1 for _ in path.rglob(pattern))
    import time
    cutoff = time.time() - within_hours * 3600
    return sum(1 for p in path.rglob(pattern) if p.stat().st_mtime >= cutoff)


def _recent_escalations(home: Path, limit: int = 5) -> list[dict]:
    base = home / "brain" / "review" / "escalated"
    if not base.exists():
        return []
    items = sorted(base.rglob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)[:limit]
    out = []
    for p in items:
        rel = p.relative_to(base)
        mtime = datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        # Try to extract the rationale line from the markdown
        rationale = ""
        try:
            for line in p.read_text(errors="replace").splitlines()[:30]:
                if line.startswith("- **Rationale:**"):
                    rationale = line.split("**Rationale:**", 1)[1].strip()
                    break
        except Exception:
            pass
        out.append({"event_id": p.stem, "domain": rel.parts[0] if rel.parts else "?", "queued_at": mtime, "rationale": rationale})
    return out


def build_digest(home: Path, brand: str) -> dict:
    """Build a structured digest payload. Returns dict with title, summary, blocks."""
    pending      = _count_files(home / "brain" / "review" / "pending")
    escalated    = _count_files(home / "brain" / "review" / "escalated")
    auto_sent_24 = _count_files(home / "brain" / "review" / "auto-sent", within_hours=24)
    failed_24    = _count_files(home / "events" / "failed", pattern="*.json", within_hours=24)
    completed_24 = _count_files(home / "events" / "completed", pattern="*.json", within_hours=24)

    escalations = _recent_escalations(home, limit=3)

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    summary = (
        f"*OperAI digest — {brand} — {ts}*\n\n"
        f"• {pending} tickets pending human review\n"
        f"• {escalated} escalations on record ({len([e for e in escalations])} most recent below)\n"
        f"• {auto_sent_24} auto-sent decisions in last 24h\n"
        f"• {completed_24} completed events in last 24h\n"
        f"• {failed_24} failed events in last 24h\n"
    )

    if escalations:
        summary += "\n*Recent escalations:*\n"
        for e in escalations:
            rationale = e["rationale"][:120] if e["rationale"] else "(no rationale)"
            summary += f"• `{e['event_id']}` ({e['domain']}) — {rationale}\n"

    return {
        "title":     f"OperAI digest — {brand}",
        "timestamp": ts,
        "summary":   summary,
        "counters":  {
            "pending":      pending,
            "escalated":    escalated,
            "auto_sent_24": auto_sent_24,
            "completed_24": completed_24,
            "failed_24":    failed_24,
        },
        "escalations": escalations,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Sender
# ─────────────────────────────────────────────────────────────────────────────

def send_to_slack(webhook_url: str, digest: dict, channel: str | None = None) -> tuple[bool, str]:
    if not webhook_url:
        return False, "no webhook URL configured"
    payload: dict = {
        "text": digest["summary"],
    }
    if channel:
        payload["channel"] = channel
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(webhook_url, data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return True, f"HTTP {resp.status}"
    except urllib.error.HTTPError as e:
        raw = e.read().decode(errors="replace") if hasattr(e, "read") else ""
        return False, f"HTTP {e.code}: {raw[:200]}"
    except Exception as e:  # noqa: BLE001
        return False, f"request error: {e}"


# ─────────────────────────────────────────────────────────────────────────────
# Cron scheduling
# ─────────────────────────────────────────────────────────────────────────────

def install_cron(home: Path, hour_utc: int = 8, minute: int = 0) -> tuple[bool, str]:
    """Append a daily cron line for the operai user. Idempotent."""
    line = f"{minute} {hour_utc} * * * /usr/local/bin/operai-init digest now >> {home}/logs/digest.log 2>&1"
    try:
        existing = subprocess.run(
            ["sudo", "-u", "operai", "crontab", "-l"],
            capture_output=True, text=True, timeout=10,
        )
        current = existing.stdout if existing.returncode == 0 else ""
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False, "crontab unavailable"

    if line in current:
        return True, "cron already installed"

    new = (current.rstrip() + "\n" + line + "\n") if current.strip() else (line + "\n")
    proc = subprocess.Popen(
        ["sudo", "-u", "operai", "crontab", "-"],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True,
    )
    _, err = proc.communicate(new, timeout=10)
    if proc.returncode != 0:
        return False, f"crontab install failed: {err[:200]}"
    return True, "cron installed"
