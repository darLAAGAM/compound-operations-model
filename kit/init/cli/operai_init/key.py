"""key — manage MCP API keys.

Stored at /opt/operai/credentials/mcp-keys.json (mode 600).

Schema:
    {
      "lgm_<32 hex>": {
        "name":       "diego",
        "role":       "admin",
        "created_at": "...",
        "last_seen":  null,
        "revoked":    false
      }
    }
"""
from __future__ import annotations
import json
import os
import re
import secrets
from datetime import datetime
from pathlib import Path
from typing import Any

from operai_init import common

_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,40}$")


def _keys_path(home: Path) -> Path:
    cdir = home / "credentials"
    cdir.mkdir(parents=True, exist_ok=True)
    try:
        os.chmod(cdir, 0o700)
    except PermissionError:
        pass
    return cdir / "mcp-keys.json"


def _load(home: Path) -> dict:
    p = _keys_path(home)
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text())
    except json.JSONDecodeError:
        return {}


def _save(home: Path, keys: dict) -> None:
    p = _keys_path(home)
    p.write_text(json.dumps(keys, indent=2))
    os.chmod(p, 0o600)


def _gen_token() -> str:
    return "lgm_" + secrets.token_hex(16)  # 32 hex chars


def create(*, home: Path, name: str, role: str, groups: list[str] | None = None) -> None:
    if not _SLUG_RE.match(name):
        common.err(f"invalid name '{name}' — use lowercase/digits/hyphens, max 41 chars")
        raise SystemExit(2)
    if role not in ("admin", "team"):
        common.err(f"invalid role '{role}' — use admin or team")
        raise SystemExit(2)

    keys = _load(home)
    # Warn if a key already exists for this name (not blocking — you can have multiple)
    existing = [t for t, meta in keys.items() if meta.get("name") == name and not meta.get("revoked")]
    if existing:
        common.warn(f"{len(existing)} active key(s) already exist for '{name}'")

    token = _gen_token()
    keys[token] = {
        "name":       name,
        "role":       role,
        "acl_groups": groups or (["general"] if role == "team" else ["general","cs","ops","finance","marketing","product","retail","wholesale","hr"]),
        "created_at": datetime.utcnow().isoformat() + "Z",
        "last_seen":  None,
        "revoked":    False,
    }
    _save(home, keys)

    common.banner(f"API key created · {name} · {role}")
    print(f"  {common.BOLD}{token}{common.RESET}\n")
    print(f"  {common.DIM}⚠ Copy this now — it is not shown again.{common.RESET}")
    print(f"  {common.DIM}Stored at {_keys_path(home)}{common.RESET}\n")


def list_keys(*, home: Path) -> None:
    keys = _load(home)
    if not keys:
        common.info("no keys yet — create one with: operai-init key create <name> --role admin")
        return

    common.banner("API keys")
    print(f"  {'NAME':<20} {'ROLE':<8} {'CREATED':<22} {'LAST SEEN':<22} {'STATUS':<10}")
    print(f"  {'-'*20} {'-'*8} {'-'*22} {'-'*22} {'-'*10}")
    for token, meta in sorted(keys.items(), key=lambda kv: kv[1].get("name","")):
        status = "revoked" if meta.get("revoked") else "active"
        masked = token[:7] + "…" + token[-4:]
        print(f"  {meta.get('name','?'):<20} {meta.get('role','?'):<8} {meta.get('created_at','?')[:19]:<22} {(meta.get('last_seen') or '—')[:19]:<22} {status:<10} {common.DIM}({masked}){common.RESET}")
    print()


def revoke(*, home: Path, name: str) -> None:
    keys = _load(home)
    changed = 0
    for token, meta in keys.items():
        if meta.get("name") == name and not meta.get("revoked"):
            meta["revoked"] = True
            meta["revoked_at"] = datetime.utcnow().isoformat() + "Z"
            changed += 1
    _save(home, keys)
    if changed:
        common.ok(f"revoked {changed} key(s) for '{name}'")
    else:
        common.warn(f"no active keys found for '{name}'")
