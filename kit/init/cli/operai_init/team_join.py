"""team_join — generates team-join.sh for employee onboarding.

The generated script:
  1. Detects OS (Mac / Linux / Windows via git-bash)
  2. Installs Node LTS if missing (via fnm on Unix, manual note on Windows)
  3. Writes the Claude Desktop MCP config pointing to the brand's MCP URL
  4. Prints verification instructions

Every employee of the brand runs this ONE command:

    curl -fsSL https://usecompai.com/team-join?brand=<brand> | bash

(The server-side endpoint resolves the brand's MCP URL and materialises the
script. For founders who prefer to host it themselves, `operai-init team-join`
produces the same thing as a file they can distribute.)
"""
from __future__ import annotations
import json
import re
import shlex
import sys
from pathlib import Path

from operai_init import common


TEMPLATE = r"""#!/usr/bin/env bash
#
# OperAI Team Join — one-command onboarding for {brand} employees
# MCP endpoint: {mcp_url}
# Generated: {generated_at}
#
# Usage (from a fresh Mac/Linux/Windows-with-Git-Bash terminal):
#   curl -fsSL https://usecompai.com/team-join?brand={brand} | bash
# OR
#   ./team-join.sh
#
# What this does:
#   1. Verifies Node.js is available (installs via fnm if missing)
#   2. Writes your Claude Desktop MCP config
#   3. Prints next steps
#
# What it does NOT do:
#   - Share any credentials with your machine (all secrets stay on {brand}'s VPS)
#   - Install anything requiring sudo (except on Linux if fnm needs it)

set -euo pipefail

BRAND={brand_shell}
MCP_URL={mcp_url_shell}

GOLD=$'\033[38;5;179m'
BOLD=$'\033[1m'
RESET=$'\033[0m'
GREEN=$'\033[32m'
RED=$'\033[31m'

say()   {{ echo "${{GOLD}}${{BOLD}}[OperAI]${{RESET}} $*"; }}
ok()    {{ echo "  ${{GREEN}}✓${{RESET}} $*"; }}
fail()  {{ echo "  ${{RED}}✗${{RESET}} $*" >&2; exit 1; }}

# ── OS detection ─────────────────────────────────────────────────────
OS="unknown"
case "$(uname -s)" in
  Darwin*) OS="mac" ;;
  Linux*)  OS="linux" ;;
  MINGW*|MSYS*|CYGWIN*) OS="windows" ;;
esac
say "detected OS: $OS"

# ── Node.js ──────────────────────────────────────────────────────────
if ! command -v node >/dev/null 2>&1; then
  say "Node.js not found — installing via fnm"
  if [ "$OS" = "mac" ] || [ "$OS" = "linux" ]; then
    curl -fsSL https://fnm.vercel.app/install | bash >/dev/null
    export PATH="$HOME/.local/share/fnm:$PATH"
    eval "$(fnm env)"
    fnm install --lts >/dev/null
    ok "Node $(node -v) installed via fnm"
  else
    fail "Windows: please install Node LTS from nodejs.org, then re-run this script"
  fi
else
  ok "Node $(node -v) already installed"
fi

# ── Claude Desktop config ────────────────────────────────────────────
if [ "$OS" = "mac" ]; then
  CFG_DIR="$HOME/Library/Application Support/Claude"
elif [ "$OS" = "linux" ]; then
  CFG_DIR="$HOME/.config/Claude"
else
  CFG_DIR="$APPDATA/Claude"
fi

mkdir -p "$CFG_DIR"
CFG_FILE="$CFG_DIR/claude_desktop_config.json"

if [ -f "$CFG_FILE" ]; then
  BACKUP="$CFG_FILE.bak.$(date +%s)"
  cp "$CFG_FILE" "$BACKUP"
  ok "backed up existing config to $BACKUP"
fi

# ── API key prompt ───────────────────────────────────────────────────
# The founder gave each employee a key (from `operai-init key create`).
# Accept via env OPERAI_KEY or prompt interactively.
if [ -z "${{OPERAI_KEY:-}}" ]; then
  say "Paste the API key your founder sent you (starts with 'lgm_')"
  read -r -p "  > " OPERAI_KEY
fi
if [ -z "$OPERAI_KEY" ] || ! echo "$OPERAI_KEY" | grep -q "^lgm_"; then
  fail "Invalid key (must start with 'lgm_'). Ask your founder for a fresh one."
fi

cat > "$CFG_FILE" <<JSON
{{
  "mcpServers": {{
    "$BRAND": {{
      "command": "npx",
      "args": ["mcp-remote", "$MCP_URL", "--header", "Authorization:Bearer \\${{OPERAI_KEY}}"],
      "env": {{ "OPERAI_KEY": "$OPERAI_KEY" }}
    }}
  }}
}}
JSON
ok "Claude Desktop MCP config written to $CFG_FILE"

# ── First-run test ───────────────────────────────────────────────────
say "bootstrapping mcp-remote (first run caches the dependency)"
npx -y mcp-remote --help >/dev/null 2>&1 || true
ok "mcp-remote ready"

echo
echo "${{BOLD}}Done.${{RESET}}"
echo
echo "  Step 1 - Verify connection (2 min)"
echo "    * Quit Claude Desktop completely (Cmd-Q on Mac)"
echo "    * Reopen Claude Desktop"
echo "    * Click the tools icon - you should see $BRAND with ~11 tools connected"
echo ""
echo "  Step 2 - Paste the custom instruction (5 min)"
echo "    * Claude Desktop -> Settings -> Profile -> What should Claude know about you"
echo "    * Paste the block from: https://usecompai.com/onboarding/custom-instruction"
echo "    * This primes every chat with your brand operational contract"
echo ""
echo "  Step 3 - Create your me.md (15 min)"
echo "    * In a new Claude Desktop chat, type:"
echo "      Run the me-md-interview skill. My name is YOUR-NAME-LOWERCASE"
echo "    * Answer 6-8 conversational questions"
echo "    * Claude saves your personal profile to the brand brain"
echo ""
echo "  Step 4 - Full onboarding checklist"
echo "    * Day 1 / Week 1 / 30-60-90 plan:"
echo "      https://usecompai.com/onboarding/checklist"
echo ""
echo "  Troubleshooting"
echo "    * If $BRAND tools do not appear: check $CFG_FILE"
echo "    * Ask your founder for a new API key if yours is revoked"
echo "    * Support: hello@usecompai.com"
echo
"""


def _resolve_mcp_url(home: Path) -> str | None:
    meta_path = home / "services" / "tunnel.json"
    if not meta_path.exists():
        return None
    try:
        meta = json.loads(meta_path.read_text())
        sub = meta.get("subdomain")
        if sub:
            return f"https://{sub}/sse"
    except json.JSONDecodeError:
        pass
    return None


def _validate_brand(brand: str) -> str:
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{1,30}", brand):
        common.err("Invalid brand. Use lowercase letters, digits, and hyphens, 2-31 chars.")
        raise SystemExit(2)
    return brand


def _validate_mcp_url(mcp_url: str) -> str:
    from urllib.parse import urlparse

    parsed = urlparse(mcp_url if "://" in mcp_url else f"https://{mcp_url}")
    if parsed.scheme != "https":
        common.err("Invalid MCP URL. HTTPS is required.")
        raise SystemExit(2)
    if not re.fullmatch(r"[A-Za-z0-9.-]+", parsed.hostname or "") or "." not in (parsed.hostname or ""):
        common.err("Invalid MCP URL hostname.")
        raise SystemExit(2)
    if parsed.username or parsed.password or parsed.port or parsed.query or parsed.fragment:
        common.err("Invalid MCP URL. Userinfo, ports, query strings, and fragments are not allowed.")
        raise SystemExit(2)
    if parsed.path not in ("", "/", "/sse"):
        common.err("Invalid MCP URL path. Use the host or /sse only.")
        raise SystemExit(2)
    return f"https://{parsed.hostname}/sse"


def render(brand: str, mcp_url: str) -> str:
    from datetime import datetime

    brand = _validate_brand(brand)
    mcp_url = _validate_mcp_url(mcp_url)
    return TEMPLATE.format(
        brand=brand,
        brand_shell=shlex.quote(brand),
        mcp_url=mcp_url,
        mcp_url_shell=shlex.quote(mcp_url),
        generated_at=datetime.utcnow().isoformat() + "Z",
    )


def run(*, out: str, home: Path, brand: str, mcp_url: str | None) -> None:
    url = mcp_url or _resolve_mcp_url(home)
    if not url:
        common.err("MCP URL not known. Run `operai-init tunnel <subdomain>` first, or pass --mcp-url.")
        raise SystemExit(2)

    body = render(brand, url)

    if out == "-":
        sys.stdout.write(body)
        return

    p = Path(out)
    p.write_text(body)
    p.chmod(0o755)
    common.ok(f"team-join.sh written to {p} ({len(body)} bytes)")
    common.info(f"MCP URL embedded: {url}")
    common.info(f"Share with each employee:  bash {p}")
