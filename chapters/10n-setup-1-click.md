# Chapter 10n: Setup 1-click — connect any AI client in 2 minutes

## Setup friction kills adoption

The most common failure in company AI rollouts is not model quality. It is distribution.

A founder or engineer builds a useful brain, connects tools, writes the right prompt, and proves the system works on their own machine. Then the rollout stalls because every employee needs a slightly different setup: install Node, find the Claude Desktop config path, edit JSON without breaking existing MCP servers, restart the app, verify tools, paste the right prompt, and debug permissions.

That manual path looks small to a technical person. It is not small to a merchandiser, store manager, finance operator, or customer-service lead. Six setup steps and one JSON error are enough to turn an internal AI operating system into something only the builder uses.

In the reference implementation, setting up an MCP-aware Claude Desktop manually took roughly 6 steps and 30 minutes. It also created too many chances for configuration drift. One employee had Node missing. Another had `npx` in a different path. Another already had a different MCP server in `claude_desktop_config.json`. Another left Claude Desktop open while the config was being edited. Another copied malformed JSON.

Setup 1-click solves that operational problem. The employee runs one command. The script detects the OS and prerequisites, installs or validates Node, merges the Claude Desktop config without deleting other MCPs, adds the company MCP server, verifies the result, and exits cleanly.

This chapter is not about a clever install trick. It is about reducing the cost of distributing a company brain. If the brain is hard to connect, it will remain a founder toy. If every employee can connect in minutes, the brain becomes part of how the company works.

Be honest about the timeline. The setup script itself can be built quickly. The full rollout still takes time because it depends on MCP server stability, auth, master prompt governance, onboarding, and support. A consumer SME with one engineer should plan 6-8 weeks for the full Brain v2 operating layer, not because this script takes that long, but because the script is only one piece of the system.

## The happy path

The user experience should be one command per OS.

For macOS:

```bash
curl -fsSL https://your-mcp/setup.sh | bash
```

For Windows PowerShell:

```powershell
irm https://your-mcp/setup.ps1 | iex
```

In the reference deployment, the live commands pointed at the company's MCP domain:

```bash
curl -fsSL https://your-mcp.example/setup.sh | bash
```

```powershell
irm https://your-mcp.example/setup.ps1 | iex
```

For an open-source fork, replace the domain and server name. Do not copy company-specific endpoints or tokens. The pattern is portable; credentials are not.

The script should do six things:

1. Detect Node.js.
2. Install Node LTS if missing or unusable.
3. Close Claude Desktop before editing config.
4. Merge `claude_desktop_config.json` while preserving other MCP servers.
5. Add or update the company MCP entry.
6. Verify and print a clear success or failure message.

The output should be boring. The employee should not need to understand MCP, SSE, JSON, Node, or `npx`. They should see a short sequence of checks and a final `READY` or `LISTO`.

The reference script installs Node LTS v22 from the official package when missing, uses `mcp-remote@0.1.18`, and points Claude Desktop to an SSE endpoint. The generated config looked like this:

```json
{
  "mcpServers": {
    "company-brain": {
      "command": "/usr/local/bin/npx",
      "args": [
        "-y",
        "mcp-remote@0.1.18",
        "https://mcp.your-company.com/sse",
        "--transport",
        "sse-only"
      ]
    }
  }
}
```

If an employee already has other MCP servers, the script must preserve them:

```json
{
  "mcpServers": {
    "existing-server": {
      "command": "uvx",
      "args": ["some-existing-mcp"]
    },
    "company-brain": {
      "command": "/usr/local/bin/npx",
      "args": [
        "-y",
        "mcp-remote@0.1.18",
        "https://mcp.your-company.com/sse",
        "--transport",
        "sse-only"
      ]
    }
  }
}
```

Preserving existing MCPs is non-negotiable. Employees and technical operators may already use filesystem, browser, GitHub, or other MCPs. Your install script should be a good citizen.

## macOS script template

This is a sanitized template. Change `SERVER_NAME`, `MCP_URL`, and the Node installation policy for your environment. If your company uses an authenticated MCP with per-user tokens, do not bake shared secrets into the script. Prompt for them or use your own secure enrollment flow.

```bash
#!/usr/bin/env bash
set -euo pipefail

SERVER_NAME="company-brain"
MCP_URL="https://mcp.your-company.com/sse"
MCP_REMOTE_VERSION="mcp-remote@0.1.18"
CONFIG_DIR="$HOME/Library/Application Support/Claude"
CONFIG_FILE="$CONFIG_DIR/claude_desktop_config.json"

log() { printf '%s\n' "$1"; }
fail() { printf 'ERROR: %s\n' "$1" >&2; exit 1; }

find_npx() {
  if command -v npx >/dev/null 2>&1; then
    command -v npx
    return 0
  fi
  if [ -x "/usr/local/bin/npx" ]; then
    printf '/usr/local/bin/npx\n'
    return 0
  fi
  if [ -x "/opt/homebrew/bin/npx" ]; then
    printf '/opt/homebrew/bin/npx\n'
    return 0
  fi
  return 1
}

install_node_if_missing() {
  if command -v node >/dev/null 2>&1 && command -v npx >/dev/null 2>&1; then
    log "Node detected: $(node --version)"
    return 0
  fi

  log "Node.js was not found. Installing Node LTS using the official macOS package."
  TMP_DIR="$(mktemp -d)"
  PKG="$TMP_DIR/node.pkg"
  NODE_PKG_URL="https://nodejs.org/dist/v22.11.0/node-v22.11.0.pkg"

  curl -fsSL "$NODE_PKG_URL" -o "$PKG"
  sudo installer -pkg "$PKG" -target /

  command -v node >/dev/null 2>&1 || fail "Node install finished but node is not on PATH"
  command -v npx >/dev/null 2>&1 || fail "Node install finished but npx is not on PATH"
  log "Node installed: $(node --version)"
}

close_claude() {
  if pgrep -x "Claude" >/dev/null 2>&1; then
    log "Closing Claude Desktop so the config can be updated."
    osascript -e 'tell application "Claude" to quit' || true
    sleep 2
  fi
}

merge_config() {
  mkdir -p "$CONFIG_DIR"
  NPX_PATH="$(find_npx)" || fail "npx not found after Node check"

  python3 - "$CONFIG_FILE" "$SERVER_NAME" "$NPX_PATH" "$MCP_REMOTE_VERSION" "$MCP_URL" <<'PY'
import json
import os
import sys

config_file, server_name, npx_path, remote_version, mcp_url = sys.argv[1:]

if os.path.exists(config_file):
    with open(config_file, 'r', encoding='utf-8') as f:
        raw = f.read().strip()
    config = json.loads(raw) if raw else {}
else:
    config = {}

if not isinstance(config, dict):
    raise SystemExit('Claude config must be a JSON object')

servers = config.setdefault('mcpServers', {})
if not isinstance(servers, dict):
    raise SystemExit('mcpServers must be a JSON object')

servers[server_name] = {
    'command': npx_path,
    'args': ['-y', remote_version, mcp_url, '--transport', 'sse-only']
}

tmp = config_file + '.tmp'
with open(tmp, 'w', encoding='utf-8') as f:
    json.dump(config, f, indent=2)
    f.write('\n')
os.replace(tmp, config_file)
PY
}

verify_config() {
  python3 - "$CONFIG_FILE" "$SERVER_NAME" <<'PY'
import json
import sys
config_file, server_name = sys.argv[1:]
with open(config_file, 'r', encoding='utf-8') as f:
    config = json.load(f)
server = config.get('mcpServers', {}).get(server_name)
if not server:
    raise SystemExit('server entry missing')
if 'command' not in server or 'args' not in server:
    raise SystemExit('server entry incomplete')
print('Verified Claude Desktop MCP config')
PY
}

install_node_if_missing
close_claude
merge_config
verify_config

log "READY: open Claude Desktop and check that company-brain tools are visible."
```

This script intentionally uses Python's JSON parser for the merge. Do not use string replacement for JSON config. A one-line shell append is how you break an employee's existing setup.

## Windows PowerShell template

This is a sanitized Windows template. It assumes a standard Claude Desktop config path and uses Node's official installer. You may prefer winget in controlled environments, but the script should still verify the resulting `node` and `npx` commands.

```powershell
$ErrorActionPreference = "Stop"

$ServerName = "company-brain"
$McpUrl = "https://mcp.your-company.com/sse"
$McpRemoteVersion = "mcp-remote@0.1.18"
$ConfigDir = Join-Path $env:APPDATA "Claude"
$ConfigFile = Join-Path $ConfigDir "claude_desktop_config.json"

function Fail($Message) {
  Write-Error $Message
  exit 1
}

function Test-Command($Name) {
  $null -ne (Get-Command $Name -ErrorAction SilentlyContinue)
}

function Install-NodeIfMissing {
  if ((Test-Command "node") -and (Test-Command "npx")) {
    Write-Host "Node detected: $(node --version)"
    return
  }

  Write-Host "Node.js was not found. Installing Node LTS."
  $Temp = New-Item -ItemType Directory -Path ([System.IO.Path]::GetTempPath()) -Name ("node-" + [guid]::NewGuid())
  $Msi = Join-Path $Temp.FullName "node.msi"
  $NodeUrl = "https://nodejs.org/dist/v22.11.0/node-v22.11.0-x64.msi"

  Invoke-WebRequest -Uri $NodeUrl -OutFile $Msi
  Start-Process msiexec.exe -Wait -ArgumentList "/i `"$Msi`" /qn"

  $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
  if (-not (Test-Command "node")) { Fail "Node install finished but node is not on PATH" }
  if (-not (Test-Command "npx")) { Fail "Node install finished but npx is not on PATH" }
  Write-Host "Node installed: $(node --version)"
}

function Close-Claude {
  $proc = Get-Process "Claude" -ErrorAction SilentlyContinue
  if ($proc) {
    Write-Host "Closing Claude Desktop so the config can be updated."
    $proc | Stop-Process -Force
    Start-Sleep -Seconds 2
  }
}

function Merge-Config {
  New-Item -ItemType Directory -Force -Path $ConfigDir | Out-Null
  $NpxPath = (Get-Command "npx" -ErrorAction Stop).Source

  if (Test-Path $ConfigFile) {
    $Raw = Get-Content $ConfigFile -Raw
    if ($Raw.Trim().Length -gt 0) {
      $Config = $Raw | ConvertFrom-Json -AsHashtable
    } else {
      $Config = @{}
    }
  } else {
    $Config = @{}
  }

  if (-not $Config.ContainsKey("mcpServers")) {
    $Config["mcpServers"] = @{}
  }

  $Config["mcpServers"][$ServerName] = @{
    command = $NpxPath
    args = @("-y", $McpRemoteVersion, $McpUrl, "--transport", "sse-only")
  }

  $Json = $Config | ConvertTo-Json -Depth 20
  Set-Content -Path $ConfigFile -Value $Json -Encoding UTF8
}

function Verify-Config {
  $Config = Get-Content $ConfigFile -Raw | ConvertFrom-Json -AsHashtable
  if (-not $Config["mcpServers"].ContainsKey($ServerName)) {
    Fail "server entry missing"
  }
  Write-Host "Verified Claude Desktop MCP config"
}

Install-NodeIfMissing
Close-Claude
Merge-Config
Verify-Config

Write-Host "READY: open Claude Desktop and check that company-brain tools are visible."
```

For Windows, test PowerShell versions explicitly. `ConvertFrom-Json -AsHashtable` is not available in every old environment. If your employee base includes older Windows machines, either enforce a supported PowerShell version or ship a fallback.

## Hosting the setup scripts

The reference setup scripts live under the MCP service repo, at a path equivalent to:

```text
/opt/company-ai/services/mcp/setup.sh
/opt/company-ai/services/mcp/setup.ps1
```

They are served by the MCP service's Starlette/uvicorn app on port `18820` and exposed through a Cloudflare Tunnel on the public MCP domain. The setup handlers have a rate limit of 60 requests per minute per IP.

A portable host can be simpler. You need:

| Requirement | Why |
|---|---|
| HTTPS endpoint | Employees will pipe the script into a shell |
| Stable domain | The command should not change every week |
| Versioned source file | You need to audit what employees ran |
| Rate limit | Prevent accidental or malicious hammering |
| Short response | The script should download quickly |
| No secrets in script | Public setup URLs should not reveal credentials |

A minimal Starlette route looks like this:

```python
from pathlib import Path
from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
from starlette.routing import Route

ROOT = Path(__file__).parent

async def setup_sh(request):
    return PlainTextResponse((ROOT / "setup.sh").read_text(), media_type="text/x-shellscript")

async def setup_ps1(request):
    return PlainTextResponse((ROOT / "setup.ps1").read_text(), media_type="text/plain")

app = Starlette(routes=[
    Route("/setup.sh", setup_sh),
    Route("/setup.ps1", setup_ps1),
])
```

In production, add rate limiting, logging, and checksums. For a public script, it is reasonable to publish the script contents in the repo as well. Employees and technical buyers should be able to inspect what they are about to run.

## Verification matrix

Test the script before company rollout. Do not use your own machine as the only proof.

The reference verification matrix included:

| Case | Expected result |
|---|---|
| Clean Mac without Node | Installs Node LTS and writes config |
| Mac with Node already installed | Skips Node install and writes config |
| Mac with other MCP servers | Preserves existing `mcpServers` entries |
| Bash shell | Runs without shell-specific syntax failures |
| zsh shell | Runs through `bash` command cleanly |
| Endpoint check | `curl -I https://your-mcp/setup.sh` returns 200 |

Add Windows cases:

| Case | Expected result |
|---|---|
| Windows without Node | Installs Node LTS and writes config |
| Windows with Node | Skips install and writes config |
| Existing config file | Preserves other MCP servers |
| Locked Claude process | Stops Claude or prints clear instruction |
| Restricted permissions | Fails clearly before corrupting config |

Also test idempotency. Running the script twice should update the same server entry, not duplicate it. Running it after changing the endpoint should replace the endpoint. Running it with malformed existing JSON should fail clearly and leave a backup if you choose to implement backups.

## Failure modes

Most setup failures are predictable.

Node version mismatch is common. Some machines have old Node versions installed through Homebrew, fnm, nvm, Volta, or a system package. Decide your minimum version and enforce it. If Node exists but `npx` fails, treat the install as incomplete.

Permissions can break installation. macOS package installs may need `sudo`. Windows MSI installs may require admin rights. If your employees do not have admin rights, coordinate with IT or use a user-level Node installation strategy.

Claude Desktop can cache config or hold files open. The script should close the app before editing and instruct the employee to reopen it. If the app is managed by MDM or locked down, the script should fail clearly.

Malformed JSON in an existing config is another common issue. Do not overwrite it blindly. Print the path and the parse error. A more mature script can copy the broken file to `claude_desktop_config.json.bak` and write a clean config, but that is a policy decision because it may temporarily remove other MCPs.

Corporate proxies can block downloads from Node or your MCP domain. The script should distinguish between network failure and config failure.

Architecture matters. Apple Silicon and Intel Macs can both run Node, but paths may differ. Windows ARM may need separate handling. Linux is not part of Claude Desktop's mainstream desktop flow today, but if your team uses compatible clients, ship a separate path.

Finally, auth should not be an afterthought. The reference setup used a public MCP endpoint with auth observe during a transition. A portable deployment should decide whether employees use per-user API keys, OAuth, mTLS, VPN, or another access control. Do not put a shared bearer token in a public setup script.

## The governance around setup

Setup 1-click is useful only if it connects employees to the right behavior. The technical config must pair with a master prompt and onboarding process.

A good employee flow is:

1. Run the setup command.
2. Open Claude Desktop.
3. Confirm the company MCP tools are visible.
4. Paste or apply the canonical master prompt.
5. Run a first `brain_search` or equivalent.
6. Complete a real task in the first week.
7. Share a useful example in the public AI channel.

The reference onboarding required day-one setup, manager verification before lunch, a first real AI task in week one, and a day-30 maturity check. The levels were L0 Observador, L1 Usuario activo, L2 Constructor, and L3 Multiplicador. The exact labels can change, but the idea should not: setup is the beginning of adoption, not the adoption itself.

## For Compai readers

Clone the script, change the endpoint, change the server name, test the matrix, and ship. Keep it boring.

A good first fork replaces:

```text
SERVER_NAME="company-brain"
MCP_URL="https://mcp.your-company.com/sse"
```

with your own values and keeps the rest idempotent. If your MCP server requires auth, add a secure enrollment step rather than embedding credentials. If your company uses a different AI client, keep the same principle: one command, preserve existing config, verify, and exit clean.

Do not promise that setup equals transformation. It removes distribution friction. The real operating memory still needs capture, write-back, task/output lifecycle, health, privacy, and a master prompt. For a consumer SME with one engineer, the full system is a 6-8 week build. This chapter is the two-minute front door.

## Operational ownership

Assign an owner for the setup script. It is easy to treat it as a one-time onboarding asset and forget that it touches every employee's AI client. The owner should review it whenever Claude Desktop changes config behavior, Node LTS changes, the MCP endpoint changes, or the company changes auth policy. Keep a short changelog beside the scripts and record production issues as gotchas.

Also decide what support means. A setup script should print the config path, the server name, the MCP URL, and the exact next step. When it fails, it should leave the machine in a known state. A non-technical employee should be able to paste the final error into the public AI channel or IT channel and receive help without explaining what MCP is.

If you want help, hello@usecompai.com. Most don't.
