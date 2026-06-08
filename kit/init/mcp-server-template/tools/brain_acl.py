"""ACL-aware brain tools — route query/read only through the principal's permitted collections.

Replaces the previous tools/brain.py behavior of reading globally. Now:

  brain_query → only searches collections the principal's acl_groups permit
  brain_read  → only returns docs whose on-disk path starts with a permitted group folder
  brain_list  → only shows folders the principal can enter

The acl_group name is derived from the doc's position in the ingested/ tree:
  brain/knowledge/<brand>/ingested/<acl_group>/YYYY/MM/doc.md

Legacy (non-ingested) docs under knowledge/<brand>/<area>/ inherit the
principal's role: team reads everything hand-curated; admin reads all.
"""
from __future__ import annotations
import asyncio
import json
import shutil
from pathlib import Path
from typing import Any

from config import BRAIN_ROOT, KNOWLEDGE_ROOT, BRAND_SLUG

_MAX_WRITE_BYTES = 256 * 1024


def _safe_resolve(user_path: str) -> Path:
    p = Path(user_path.strip().lstrip("/"))
    resolved = (BRAIN_ROOT / p).resolve()
    try:
        resolved.relative_to(BRAIN_ROOT.resolve())
    except ValueError:
        raise PermissionError(f"path '{user_path}' is outside the brain root")
    return resolved


def _principal_groups(principal) -> set[str]:
    # Defensive: always allow 'public' + 'general'. admin role gets all groups.
    groups = set(getattr(principal, "acl_groups", None) or []) | {"public", "general"}
    if principal.role == "admin":
        groups |= {"finance", "hr", "wholesale", "retail", "marketing", "product", "ops", "cs"}
    return groups


def _path_acl_group(abs_path: Path) -> str | None:
    """Return the acl_group folder name if path is inside ingested/<group>/..., else None."""
    try:
        rel = abs_path.relative_to(KNOWLEDGE_ROOT / BRAND_SLUG / "ingested")
    except ValueError:
        return None
    parts = rel.parts
    return parts[0] if parts else None


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
    """Hybrid search scoped to the principal's acl_groups.

    Previously this hit the 'workspace' collection blindly. Now it invokes
    one QMD call per permitted group collection and merges results.
    """
    qmd_bin = shutil.which("qmd")
    groups = _principal_groups(principal)

    if not qmd_bin:
        return await _grep_fallback(query, max_results, groups)

    # Build target collections: <brand>-<group> for each permitted group,
    # plus legacy 'workspace' if admin.
    target_cols: list[str] = [f"{BRAND_SLUG}-{g}" for g in sorted(groups)]
    if principal.role == "admin":
        target_cols.append("workspace")
    if collection:
        # Explicit collection requested — only honor if it's in target_cols
        if collection not in target_cols:
            return {"results": [], "warning": f"collection '{collection}' not permitted for principal"}
        target_cols = [collection]

    aggregated = []
    for col in target_cols:
        code, out, _ = await _run(
            [qmd_bin, "search", query, "--collection", col, "--limit", str(max_results), "--json"],
            cwd=BRAIN_ROOT,
        )
        if code == 0 and out.strip():
            try:
                parsed = json.loads(out)
                aggregated.extend(parsed if isinstance(parsed, list) else parsed.get("results", []))
            except json.JSONDecodeError:
                continue
    # De-dupe by path, preserve order
    seen, uniq = set(), []
    for r in aggregated:
        p = r.get("path")
        if p and p not in seen:
            seen.add(p); uniq.append(r)
    return {"results": uniq[:max_results], "scoped_to": sorted(groups)}


async def _grep_fallback(q: str, limit: int, groups: set[str]) -> dict:
    rg = shutil.which("rg") or shutil.which("grep")
    if not rg:
        return {"results": [], "warning": "qmd missing and no ripgrep/grep available"}
    # Build a list of folders to search — only permitted group folders + curated knowledge
    roots: list[Path] = []
    ing = KNOWLEDGE_ROOT / BRAND_SLUG / "ingested"
    if ing.exists():
        for g in groups:
            p = ing / g
            if p.exists():
                roots.append(p)
    # Curated (non-ingested) knowledge is always visible
    curated = KNOWLEDGE_ROOT / BRAND_SLUG
    if curated.exists():
        for p in curated.iterdir():
            if p.is_dir() and p.name != "ingested":
                roots.append(p)
    if not roots:
        return {"results": [], "warning": "no readable scopes for principal"}
    code, out, _ = await _run([rg, "-l", "-i", q] + [str(r) for r in roots])
    files = [l for l in out.strip().splitlines() if l][:limit]
    return {"results": [{"path": p} for p in files], "mode": "grep_fallback", "scoped_to": sorted(groups)}


async def read(*, principal, path: str) -> Any:
    resolved = _safe_resolve(path)
    if not resolved.exists():
        return {"error": f"not found: {path}"}
    if resolved.is_dir():
        return {"error": f"{path} is a directory — use brain_list"}

    acl_group = _path_acl_group(resolved)
    if acl_group and acl_group not in _principal_groups(principal):
        return {"error": f"access denied: doc belongs to '{acl_group}', your groups: {sorted(_principal_groups(principal))}"}
    try:
        text = resolved.read_text(errors="replace")
    except Exception as e:
        return {"error": str(e)}
    return {"path": str(resolved.relative_to(BRAIN_ROOT)), "size_bytes": len(text), "content": text}


async def write(*, principal, path: str, content: str) -> Any:
    if len(content.encode("utf-8")) > _MAX_WRITE_BYTES:
        return {"error": f"content exceeds {_MAX_WRITE_BYTES} bytes"}
    resolved = _safe_resolve(path)
    # Admins can write anywhere; team can only write in curated areas they own,
    # never into ingested/ (that is produced by the pipeline).
    acl_group = _path_acl_group(resolved)
    if acl_group is not None and principal.role != "admin":
        return {"error": "team role cannot write into ingested/ (pipeline-owned)"}
    resolved.parent.mkdir(parents=True, exist_ok=True)
    is_update = resolved.exists()
    resolved.write_text(content)
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
    acl_group = _path_acl_group(resolved)
    if acl_group and acl_group not in _principal_groups(principal):
        return {"error": f"access denied: folder is ACL-group '{acl_group}'"}
    groups = _principal_groups(principal)
    entries = []
    for child in sorted(resolved.iterdir()):
        # Hide ACL-group subfolders the principal can't enter
        child_group = _path_acl_group(child)
        if child_group and child_group not in groups:
            continue
        entries.append({
            "name": child.name,
            "type": "dir" if child.is_dir() else "file",
            "size": child.stat().st_size if child.is_file() else None,
        })
    return {"directory": str(resolved.relative_to(BRAIN_ROOT)) or ".", "entries": entries}
