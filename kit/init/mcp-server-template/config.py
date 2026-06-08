"""Runtime config — resolves $OPERAI_HOME and brand slug."""
import os
from pathlib import Path

OPERAI_HOME = Path(os.environ.get("OPERAI_HOME", "/opt/operai"))


def _resolve_brand() -> str:
    env = os.environ.get("OPERAI_BRAND")
    if env:
        return env
    kb = OPERAI_HOME / "brain" / "knowledge"
    if kb.exists():
        reserved = {"platform", "personal", "projects"}
        for child in sorted(kb.iterdir()):
            if child.is_dir() and child.name not in reserved:
                return child.name
    return "unknown"


BRAND_SLUG = _resolve_brand()
BRAIN_ROOT = OPERAI_HOME / "brain"
KNOWLEDGE_ROOT = BRAIN_ROOT / "knowledge"
CRED_DIR = OPERAI_HOME / "credentials"
KEYS_FILE = CRED_DIR / "mcp-keys.json"
