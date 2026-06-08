"""Webhook config — /opt/operai/credentials/webhooks.json (mode 600).

Schema:
{
  "providers": {
    "richpanel": {"secret": "whsec_...", "configured_at": "..."},
    "gorgias":   {"secret": "...", "configured_at": "..."},
    ...
  },
  "routing": {
    "default_domain": "cs"   # all webhooks land in cs/ for now
  },
  "endpoint_base": "https://webhook.acme.com"   # where the brand exposed this via tunnel
}
"""
from __future__ import annotations
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path


SUPPORTED = ["richpanel", "gorgias", "zendesk", "intercom"]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _path(home: Path) -> Path:
    return home / "credentials" / "webhooks.json"


def load(home: Path) -> dict:
    p = _path(home)
    if not p.exists():
        return {"providers": {}, "routing": {"default_domain": "cs"}, "endpoint_base": None}
    try:
        return json.loads(p.read_text())
    except json.JSONDecodeError:
        return {"providers": {}, "routing": {"default_domain": "cs"}, "endpoint_base": None}


def save(home: Path, data: dict) -> Path:
    p = _path(home)
    p.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(p.parent), prefix=".wh-", suffix=".tmp")
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


def set_provider(home: Path, provider: str, secret: str) -> None:
    if provider not in SUPPORTED:
        raise ValueError(f"unknown provider '{provider}' (supported: {SUPPORTED})")
    data = load(home)
    data.setdefault("providers", {})[provider] = {
        "secret":         secret,
        "configured_at":  _now(),
    }
    save(home, data)


def remove_provider(home: Path, provider: str) -> bool:
    data = load(home)
    if provider in data.get("providers", {}):
        del data["providers"][provider]
        save(home, data)
        return True
    return False


def get_secret(home: Path, provider: str) -> str | None:
    return load(home).get("providers", {}).get(provider, {}).get("secret")


def list_configured(home: Path) -> list[str]:
    return list(load(home).get("providers", {}).keys())


def set_endpoint_base(home: Path, url: str) -> None:
    data = load(home)
    data["endpoint_base"] = url.rstrip("/")
    save(home, data)


def get_endpoint_base(home: Path) -> str | None:
    return load(home).get("endpoint_base")
