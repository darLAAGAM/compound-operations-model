"""Factory config loader — parses factory.yml and validates SOULs exist.

We parse YAML with a minimal stdlib parser (no PyYAML dep) to keep the kit
zero-deps. Factory.yml uses a simple subset: scalars, lists of dicts, nested
dicts. Good enough for our shape.
"""
from __future__ import annotations
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


# ─────────────────────────────────────────────────────────────────────────────
# Minimal YAML subset parser — supports our factory.yml shape only.
# Not a full YAML implementation. We accept:
#   key: value
#   key:
#     sub: value
#   - name: x
#     inputs: [a, b]
#     llm: { provider: openai, model: gpt-4o-mini }
#   lists (flow + block)
# ─────────────────────────────────────────────────────────────────────────────

def _parse_yaml(text: str) -> dict:
    """Very small YAML parser for our factory.yml shape."""
    lines = []
    for raw in text.splitlines():
        # Strip trailing comments (# …) when not inside a string.
        # Simple: find '#' not preceded by '\' and not inside quotes.
        stripped = _strip_comment(raw)
        if stripped.strip() == "" and stripped != "":
            lines.append("")
        else:
            lines.append(stripped.rstrip())
    # Remove leading/trailing blank lines
    while lines and lines[0].strip() == "":
        lines.pop(0)
    while lines and lines[-1].strip() == "":
        lines.pop()

    idx = [0]
    result = _parse_block(lines, idx, 0)
    return result if isinstance(result, dict) else {}


def _strip_comment(line: str) -> str:
    # preserve lines inside quoted strings; our YAML has no quoted strings with # inside, so naive is ok
    out = []
    in_s = False
    in_d = False
    for ch in line:
        if ch == "'" and not in_d: in_s = not in_s
        elif ch == '"' and not in_s: in_d = not in_d
        elif ch == "#" and not in_s and not in_d:
            break
        out.append(ch)
    return "".join(out)


def _indent_of(line: str) -> int:
    n = 0
    for c in line:
        if c == " ":
            n += 1
        else:
            break
    return n


def _parse_block(lines: list[str], idx: list[int], base_indent: int):
    """Parse block starting at lines[idx[0]]. Returns dict or list."""
    result_dict: dict | None = None
    result_list: list | None = None

    while idx[0] < len(lines):
        line = lines[idx[0]]
        if line.strip() == "":
            idx[0] += 1
            continue
        indent = _indent_of(line)
        if indent < base_indent:
            break
        if indent > base_indent:
            # shouldn't happen at this level
            idx[0] += 1
            continue

        body = line[indent:]

        # List item?
        if body.startswith("- "):
            if result_list is None:
                result_list = []
            if result_dict is not None:
                break  # inconsistent, stop
            # Parse the list item body as a single dict starting from the "- " mark
            item_start = indent + 2
            inline_body = body[2:]
            # Check if the inline is a scalar or a key: value
            if ":" in inline_body:
                # key: val [...]
                item_dict: dict = {}
                k, v = inline_body.split(":", 1)
                k = k.strip()
                v = v.strip()
                if v:
                    item_dict[k] = _parse_scalar(v)
                # Consume following indented lines at item_start
                idx[0] += 1
                sub = _parse_block(lines, idx, item_start)
                if isinstance(sub, dict):
                    item_dict.update(sub)
                result_list.append(item_dict)
                continue
            else:
                # scalar list item
                result_list.append(_parse_scalar(inline_body))
                idx[0] += 1
                continue

        # Key: value
        if ":" in body:
            if result_dict is None:
                result_dict = {}
            if result_list is not None:
                break
            key, _, rest = body.partition(":")
            key = key.strip()
            rest = rest.strip()
            if rest:
                result_dict[key] = _parse_scalar(rest)
                idx[0] += 1
            else:
                idx[0] += 1
                # Next block at deeper indent
                # Peek next non-blank
                next_indent = None
                j = idx[0]
                while j < len(lines):
                    if lines[j].strip() == "":
                        j += 1
                        continue
                    next_indent = _indent_of(lines[j])
                    break
                if next_indent is None or next_indent <= indent:
                    result_dict[key] = None
                else:
                    result_dict[key] = _parse_block(lines, idx, next_indent)
            continue

        # unknown
        idx[0] += 1

    if result_list is not None:
        return result_list
    return result_dict or {}


def _parse_scalar(s: str):
    """Parse a scalar value: int, float, bool, null, list (flow), dict (flow), or string."""
    s = s.strip()
    if not s:
        return ""
    # Flow list
    if s.startswith("[") and s.endswith("]"):
        inner = s[1:-1].strip()
        if not inner:
            return []
        # naive split on commas at depth 0
        return [_parse_scalar(x) for x in _split_top_level(inner)]
    # Flow dict
    if s.startswith("{") and s.endswith("}"):
        inner = s[1:-1].strip()
        if not inner:
            return {}
        d = {}
        for kv in _split_top_level(inner):
            if ":" in kv:
                k, v = kv.split(":", 1)
                d[k.strip()] = _parse_scalar(v.strip())
        return d
    # Quoted strings
    if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        return s[1:-1]
    # bool/null/numbers
    if s.lower() == "true":  return True
    if s.lower() == "false": return False
    if s.lower() in ("null", "~", "none"): return None
    try: return int(s)
    except ValueError: pass
    try: return float(s)
    except ValueError: pass
    return s


def _split_top_level(s: str) -> list[str]:
    """Split by commas at depth 0 (not inside [] or {})."""
    out = []
    depth = 0
    current = []
    for ch in s:
        if ch in "[{":
            depth += 1
        elif ch in "]}":
            depth -= 1
        if ch == "," and depth == 0:
            out.append("".join(current).strip())
            current = []
        else:
            current.append(ch)
    if current:
        out.append("".join(current).strip())
    return out


# ─────────────────────────────────────────────────────────────────────────────
# Typed config
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class SubAgentConfig:
    name:    str
    soul:    str
    inputs:  list[str]
    outputs: list[str]
    order:   int
    llm:     Optional[dict] = None   # {"provider": "...", "model": "..."} or None for default


@dataclass
class FactoryConfig:
    domain:         str
    parent_soul:    str
    version:        str
    default_llm:    dict                   # {"provider":..., "model":...}
    fallback_llm:   list[dict]             # list of provider/model
    sub_agents:     list[SubAgentConfig]
    orchestration:  dict = field(default_factory=dict)
    root:           Path = field(default=Path("."))


def load(factory_dir: Path) -> FactoryConfig:
    """Load factory.yml from an installed factory dir like /opt/operai/agents/cs/factory/."""
    yml = factory_dir / "factory.yml"
    if not yml.exists():
        raise FileNotFoundError(f"factory.yml not found at {yml}")
    parsed = _parse_yaml(yml.read_text())

    sub_agents_raw = parsed.get("sub_agents", []) or []
    sub_agents = []
    for s in sub_agents_raw:
        sub_agents.append(SubAgentConfig(
            name=s.get("name", ""),
            soul=s.get("soul", ""),
            inputs=s.get("inputs", []) or [],
            outputs=s.get("outputs", []) or [],
            order=int(s.get("order", 0)),
            llm=s.get("llm"),
        ))
    sub_agents.sort(key=lambda x: x.order)

    return FactoryConfig(
        domain=parsed.get("domain", ""),
        parent_soul=parsed.get("parent_soul", "SOUL.md"),
        version=str(parsed.get("version", "0.0.0")),
        default_llm=parsed.get("default_llm") or {},
        fallback_llm=parsed.get("fallback_llm", []) or [],
        sub_agents=sub_agents,
        orchestration=parsed.get("orchestration", {}) or {},
        root=factory_dir,
    )


def validate(fc: FactoryConfig) -> list[str]:
    """Returns a list of issues. Empty list = valid."""
    issues = []
    if not fc.default_llm.get("provider") or not fc.default_llm.get("model"):
        issues.append("default_llm missing provider or model")
    for s in fc.sub_agents:
        soul_path = fc.root / s.soul
        if not soul_path.exists():
            issues.append(f"sub-agent '{s.name}': SOUL not found at {soul_path}")
        if s.llm and (not s.llm.get("provider") or not s.llm.get("model")):
            issues.append(f"sub-agent '{s.name}': llm override malformed")
    return issues


def resolve_llm_for(fc: FactoryConfig, sub_agent: SubAgentConfig) -> dict:
    """Return the provider/model dict to use for this sub-agent."""
    if sub_agent.llm and sub_agent.llm.get("provider") and sub_agent.llm.get("model"):
        return {"provider": sub_agent.llm["provider"], "model": sub_agent.llm["model"]}
    return {"provider": fc.default_llm.get("provider"), "model": fc.default_llm.get("model")}


def soul_content(fc: FactoryConfig, sub_agent: SubAgentConfig) -> str:
    return (fc.root / sub_agent.soul).read_text()
