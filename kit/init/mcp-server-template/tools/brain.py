"""Brain tools — query, read, write, list.

Vector and hybrid search delegate to the `qmd` CLI that already runs on the VPS
and indexes the 6 collections every 5 min. Falls back to keyword grep if qmd is
not available (fresh install before the first cron tick).
"""
from __future__ import annotations
import asyncio
import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any

from config import BRAIN_ROOT, KNOWLEDGE_ROOT


_MAX_WRITE_BYTES = 256 * 1024  # 256KB


def _safe_resolve(user_path: str) -> Path:
    """Resolve path relative to BRAIN_ROOT, rejecting escapes and absolute paths."""
    p = Path(user_path.strip().lstrip("/"))
    resolved = (BRAIN_ROOT / p).resolve()
    # Prevent path traversal outside brain
    try:
        resolved.relative_to(BRAIN_ROOT.resolve())
    except ValueError:
        raise PermissionError(f"path '{user_path}' is outside the brain root")
    return resolved


async def _run(cmd: list[str], cwd: Path | None = None, timeout: float = 15) -> tuple[int, str, str]:
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=str(cwd) if cwd else None,
    )
    try:
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
    except asyncio.TimeoutError:
        proc.kill()
        return 124, "", "timeout"
    return proc.returncode or 0, stdout.decode(errors="replace"), stderr.decode(errors="replace")


async def query(*, principal, query: str, collection: str | None = None, max_results: int = 10) -> Any:
    """Hybrid search via qmd (vector + keyword + rerank). Fallback to ripgrep if qmd missing."""
    qmd_bin = shutil.which("qmd")
    collection = collection or "workspace"

    if qmd_bin and (BRAIN_ROOT / ".qmd.json").exists():
        cmd = [qmd_bin, "search", query, "--collection", collection, "--limit", str(max_results), "--json"]
        code, out, err = await _run(cmd, cwd=BRAIN_ROOT)
        if code == 0 and out.strip():
            try:
                return json.loads(out)
            except json.JSONDecodeError:
                return {"raw": out, "warning": "qmd returned non-JSON, returning raw"}
        # Fall through to grep fallback on qmd failure
    return await _grep_fallback(query, max_results)


async def _grep_fallback(q: str, limit: int) -> dict:
    rg = shutil.which("rg") or shutil.which("grep")
    if not rg:
        return {"results": [], "warning": "neither qmd nor ripgrep/grep available"}
    cmd = [rg, "-l", "-i", q, str(BRAIN_ROOT)] if "rg" in rg else [rg, "-rli", q, str(BRAIN_ROOT)]
    code, out, _ = await _run(cmd)
    files = [l for l in out.strip().splitlines() if l][:limit]
    return {"results": [{"path": p} for p in files], "mode": "grep_fallback"}


async def read(*, principal, path: str) -> Any:
    resolved = _safe_resolve(path)
    if not resolved.exists():
        return {"error": f"not found: {path}"}
    if resolved.is_dir():
        return {"error": f"{path} is a directory — use brain_list"}
    try:
        text = resolved.read_text(errors="replace")
    except Exception as e:
        return {"error": str(e)}
    return {"path": str(resolved.relative_to(BRAIN_ROOT)), "size_bytes": len(text), "content": text}


async def write(*, principal, path: str, content: str) -> Any:
    if len(content.encode("utf-8")) > _MAX_WRITE_BYTES:
        return {"error": f"content exceeds {_MAX_WRITE_BYTES} bytes"}
    resolved = _safe_resolve(path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    is_update = resolved.exists()
    resolved.write_text(content)
    # Audit trail — append one line to memory/brain-writes.log
    try:
        from datetime import datetime
        log_path = BRAIN_ROOT / "memory" / "brain-writes.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("a") as f:
            f.write(f"{datetime.utcnow().isoformat()}Z\t{principal.name}\t{'update' if is_update else 'create'}\t{path}\n")
    except Exception:
        pass
    return {"path": path, "action": "updated" if is_update else "created", "bytes": len(content)}


async def list_dir(*, principal, directory: str = "") -> Any:
    resolved = _safe_resolve(directory) if directory else BRAIN_ROOT
    if not resolved.exists():
        return {"error": f"not found: {directory}"}
    entries = []
    for child in sorted(resolved.iterdir()):
        entries.append({
            "name": child.name,
            "type": "dir" if child.is_dir() else "file",
            "size": child.stat().st_size if child.is_file() else None,
        })
    return {"directory": str(resolved.relative_to(BRAIN_ROOT)) or ".", "entries": entries}
