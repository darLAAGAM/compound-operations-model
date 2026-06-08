"""Provider config persistence — /opt/operai/credentials/llm-providers.json (mode 600).

Schema:
    {
      "default": {"provider": "anthropic", "model": "haiku-4.5"},
      "fallback": [{"provider": "openai", "model": "gpt-4o-mini"}],
      "providers": {
        "anthropic": {
          "api_key": "sk-ant-...",
          "configured_at": "...",
          "last_test_ok": "...",
          "last_test_error": null
        },
        ...
      }
    }

Writes are atomic (temp file + rename) and force mode 600.
"""
from __future__ import annotations
import json
import os
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _path(home: Path) -> Path:
    return home / "credentials" / "llm-providers.json"


def load(home: Path) -> dict:
    p = _path(home)
    if not p.exists():
        return {"default": None, "fallback": [], "providers": {}}
    try:
        return json.loads(p.read_text())
    except json.JSONDecodeError:
        return {"default": None, "fallback": [], "providers": {}}


def save(home: Path, data: dict) -> Path:
    p = _path(home)
    p.parent.mkdir(parents=True, exist_ok=True)
    os.chmod(p.parent, 0o700)
    # Atomic write
    fd, tmp = tempfile.mkstemp(dir=str(p.parent), prefix=".llm-", suffix=".tmp")
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


def set_provider(home: Path, provider: str, api_key: str) -> None:
    data = load(home)
    providers = data.setdefault("providers", {})
    providers[provider] = {
        "api_key":         api_key,
        "configured_at":   _now(),
        "last_test_ok":    None,
        "last_test_error": None,
    }
    save(home, data)


def get_api_key(home: Path, provider: str) -> Optional[str]:
    data = load(home)
    entry = data.get("providers", {}).get(provider)
    return entry.get("api_key") if entry else None


def mark_tested(home: Path, provider: str, ok: bool, error: str | None = None) -> None:
    data = load(home)
    providers = data.setdefault("providers", {})
    if provider not in providers:
        return
    if ok:
        providers[provider]["last_test_ok"] = _now()
        providers[provider]["last_test_error"] = None
    else:
        providers[provider]["last_test_error"] = error
    save(home, data)


def remove_provider(home: Path, provider: str) -> bool:
    data = load(home)
    providers = data.get("providers", {})
    if provider in providers:
        del providers[provider]
        # If default was this provider, clear it
        if data.get("default") and data["default"].get("provider") == provider:
            data["default"] = None
        save(home, data)
        return True
    return False


def set_default(home: Path, provider: str, model: str) -> None:
    data = load(home)
    data["default"] = {"provider": provider, "model": model}
    save(home, data)


def get_default(home: Path) -> Optional[dict]:
    return load(home).get("default")


def set_fallback_chain(home: Path, chain: list[dict]) -> None:
    data = load(home)
    data["fallback"] = chain
    save(home, data)


def list_configured(home: Path) -> list[str]:
    return list(load(home).get("providers", {}).keys())
