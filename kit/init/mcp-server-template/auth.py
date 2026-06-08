"""API key auth for the MCP server.

Keys are stored in /opt/operai/credentials/mcp-keys.json:

    {
      "lgm_<32 hex>": {
        "name":       "diego",
        "role":       "admin",
        "created_at": "2026-04-17T…",
        "last_seen":  null,
        "revoked":    false
      },
      ...
    }

Keys are generated and revoked via `operai-init key create|list|revoke`.

Every incoming request must carry:

    Authorization: Bearer lgm_<32 hex>

Anonymous access is rejected with 401.
"""
from __future__ import annotations
import json
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from config import KEYS_FILE


class AuthError(Exception):
    pass


@dataclass
class Principal:
    name:  str
    role:  str            # "admin" | "team"
    token: str
    acl_groups: list = None   # list[str] of group names; see key.py


def _load_keys() -> dict:
    if not KEYS_FILE.exists():
        return {}
    try:
        return json.loads(KEYS_FILE.read_text())
    except json.JSONDecodeError:
        return {}


def _touch_last_seen(token: str) -> None:
    try:
        keys = _load_keys()
        if token in keys:
            keys[token]["last_seen"] = datetime.utcnow().isoformat() + "Z"
            KEYS_FILE.write_text(json.dumps(keys, indent=2))
            os.chmod(KEYS_FILE, 0o600)
    except Exception:
        # Never break auth because last_seen write failed
        pass


def authenticate(request) -> Principal:
    header = request.headers.get("authorization") or request.headers.get("Authorization")
    if not header or not header.lower().startswith("bearer "):
        raise AuthError("missing Authorization: Bearer <key> header")
    token = header.split(None, 1)[1].strip()

    keys = _load_keys()
    entry = keys.get(token)
    if entry is None:
        raise AuthError("invalid API key")
    if entry.get("revoked"):
        raise AuthError("API key revoked")

    _touch_last_seen(token)

    return Principal(
        name=entry.get("name", "unknown"),
        role=entry.get("role", "team"),
        token=token,
        acl_groups=entry.get("acl_groups") or ["general"],
    )
