"""me.md tools — personal profiles per employee."""
from __future__ import annotations
import re
from pathlib import Path
from typing import Any

from config import KNOWLEDGE_ROOT, BRAND_SLUG

_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,40}$")


def _team_dir() -> Path:
    return KNOWLEDGE_ROOT / BRAND_SLUG / "team"


async def read(*, principal, name: str | None = None) -> Any:
    team = _team_dir()
    if not team.exists():
        return {"profiles": [], "warning": "team folder missing — no profiles yet"}

    if not name:
        names = []
        for p in sorted(team.glob("*me.md")) + sorted(team.glob("*/me.md")):
            # Look for files named me.md at any depth up to 2
            if p.is_file():
                slug = p.parent.name if p.name == "me.md" else p.stem.replace("-me", "")
                names.append(slug)
        return {"profiles": sorted(set(names))}

    if not _SLUG_RE.match(name):
        return {"error": f"invalid name '{name}' — use lowercase/digits/hyphens"}

    # Try <team>/<name>/me.md first, then <team>/<name>.md
    candidates = [team / name / "me.md", team / f"{name}.md"]
    for p in candidates:
        if p.exists():
            return {"name": name, "path": str(p), "content": p.read_text(errors="replace")}
    return {"error": f"no profile for '{name}'"}


async def write(*, principal, content: str, name: str | None = None) -> Any:
    target = name or principal.name
    if not _SLUG_RE.match(target):
        return {"error": f"invalid name '{target}'"}
    if target != principal.name and principal.role != "admin":
        return {"error": f"non-admin cannot write other people's me.md (you are {principal.name}, target {target})"}

    team = _team_dir()
    team.mkdir(parents=True, exist_ok=True)
    path = team / target / "me.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    return {"path": str(path), "name": target, "bytes": len(content)}
