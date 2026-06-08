"""memory tools — append daily notes."""
from __future__ import annotations
from datetime import date, datetime
from typing import Any

from config import BRAIN_ROOT


async def write(*, principal, content: str) -> Any:
    """Append a note to today's memory file for the calling principal."""
    today = date.today().isoformat()
    mem_dir = BRAIN_ROOT / "memory"
    mem_dir.mkdir(parents=True, exist_ok=True)
    path = mem_dir / f"{today}-{principal.name}.md"

    is_new = not path.exists()
    header = f"# {today} — {principal.name}\n\n" if is_new else ""
    stamp = datetime.utcnow().isoformat() + "Z"
    entry = f"{header}## {stamp}\n\n{content}\n\n---\n"
    with path.open("a") as f:
        f.write(entry)

    return {"path": str(path.relative_to(BRAIN_ROOT)), "action": "appended", "bytes": len(entry)}
