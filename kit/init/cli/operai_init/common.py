"""Shared helpers for operai-init subcommands."""
from __future__ import annotations
import json
import os
import sys
import getpass
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

GOLD  = "\033[38;5;179m"
BOLD  = "\033[1m"
DIM   = "\033[2m"
RESET = "\033[0m"
GREEN = "\033[32m"
RED   = "\033[31m"
CYAN  = "\033[36m"


def banner(msg: str) -> None:
    print("\n" + GOLD + BOLD + "── " + msg + " ──" + RESET + "\n")


def ok(msg: str) -> None:
    print("  " + GREEN + "✓" + RESET + " " + msg)


def warn(msg: str) -> None:
    print("  " + GOLD + "!" + RESET + " " + msg)


def err(msg: str) -> None:
    print("  " + RED + "✗" + RESET + " " + msg, file=sys.stderr)


def info(msg: str) -> None:
    print("  " + CYAN + "•" + RESET + " " + msg)


def credential_path(home: Path, service: str) -> Path:
    p = home / "credentials" / f"{service}.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    try:
        os.chmod(p.parent, 0o700)
    except PermissionError:
        pass
    return p


def save_credential(
    home: Path,
    service: str,
    data: dict,
    *,
    brand: str = "unknown",
) -> Path:
    """Writes a credential file with mode 600 and updates the integrations index."""
    payload = {
        "service": service,
        "brand": brand,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "data": data,
    }
    path = credential_path(home, service)
    path.write_text(json.dumps(payload, indent=2))
    os.chmod(path, 0o600)
    _update_index(home, service, status="connected", path=path)
    return path


def load_credential(home: Path, service: str) -> Optional[dict]:
    p = credential_path(home, service)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text())
    except json.JSONDecodeError:
        return None


def _update_index(home: Path, service: str, *, status: str, path: Path) -> None:
    idx_path = home / "credentials" / "index.json"
    idx: dict[str, Any] = {}
    if idx_path.exists():
        try:
            idx = json.loads(idx_path.read_text())
        except json.JSONDecodeError:
            idx = {}
    idx[service] = {
        "status": status,
        "path": str(path),
        "updated_at": datetime.utcnow().isoformat() + "Z",
    }
    idx_path.write_text(json.dumps(idx, indent=2))
    os.chmod(idx_path, 0o600)


def read_secret(prompt: str) -> str:
    """Read a secret from stdin without echoing."""
    try:
        return getpass.getpass(prompt)
    except (EOFError, KeyboardInterrupt):
        err("aborted")
        sys.exit(130)


def prompt(prompt_str: str) -> str:
    try:
        return input(BOLD + prompt_str + RESET + "\n  > ").strip()
    except (EOFError, KeyboardInterrupt):
        err("aborted")
        sys.exit(130)


def confirm(prompt_str: str, default: bool = False) -> bool:
    hint = "Y/n" if default else "y/N"
    try:
        resp = input(f"{BOLD}{prompt_str}{RESET} [{hint}] ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        err("aborted")
        sys.exit(130)
    if not resp:
        return default
    return resp in ("y", "yes", "s", "si", "sí")


def existing_integration_check(home: Path, service: str, force: bool) -> None:
    existing = load_credential(home, service)
    if existing and not force:
        warn(f"{service} already connected (created {existing.get('created_at','?')})")
        if not confirm("Overwrite with new credentials?", default=False):
            info("Keeping existing credentials. Pass --force to overwrite without prompt.")
            sys.exit(0)
