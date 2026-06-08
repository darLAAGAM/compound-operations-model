"""Slack connector — User/Bot OAuth token flow.

For v0.2 we accept a manually-created Slack app token. The founder:
  1. Creates a Slack app at api.slack.com/apps
  2. Grants OAuth scopes (channels:read, chat:write, users:read, etc.)
  3. Installs to workspace → copies the Bot User OAuth token (xoxb-…)
"""
from __future__ import annotations
import json
import urllib.error
import urllib.request
from pathlib import Path

from operai_init import common


BOT_SCOPES = [
    "channels:read", "channels:history", "groups:read", "groups:history",
    "chat:write", "chat:write.public",
    "users:read", "users:read.email",
    "files:read", "reactions:read", "reactions:write",
    "search:read",
]


def _test(token: str) -> tuple[bool, str]:
    req = urllib.request.Request(
        "https://slack.com/api/auth.test",
        headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            if body.get("ok"):
                return True, f"team: {body.get('team','?')} · bot: {body.get('user','?')}"
            return False, body.get("error", "unknown")
    except urllib.error.HTTPError as e:
        return False, f"HTTP {e.code}: {e.reason}"
    except Exception as e:
        return False, f"network error: {e}"


def connect(*, home: Path, brand: str) -> None:
    common.info("Slack app setup (5 min)")
    print("""
    1. Go to https://api.slack.com/apps → Create New App → From scratch
       Name: "OperAI Swarm" · Workspace: your workspace
    2. OAuth & Permissions → Bot Token Scopes — add:
""")
    for s in BOT_SCOPES:
        print(f"       {s}")
    print("""
    3. Install to Workspace → authorize
    4. Copy "Bot User OAuth Token" (starts with `xoxb-`)
    5. Optional: Add the bot to your #operai-ops channel (create it if missing)
""")

    token = common.read_secret("Slack Bot User OAuth Token (paste, input hidden): ").strip()
    if not token.startswith("xoxb-"):
        common.warn("Token does not start with 'xoxb-' — continuing, but verify.")

    common.info("verifying…")
    ok, detail = _test(token)
    if not ok:
        common.err(f"Slack rejected token ({detail})")
        if not common.confirm("Save anyway?", default=False):
            return
    else:
        common.ok(f"Slack reachable ({detail})")

    channel = common.prompt("Primary ops channel (e.g. 'operai-ops') — leave blank to skip").strip().lstrip("#")

    path = common.save_credential(home, "slack", {
        "bot_token": token,
        "scopes":    BOT_SCOPES,
        "ops_channel": channel or None,
    }, brand=brand)
    common.ok(f"credentials saved to {path}")
