# Codex (OpenAI GPT-5.4) — Integration Guide

> Connect OpenAI's Codex agent to your MCP brain alongside Claude.
> Same brain, same tools, different model — enables cross-model deliberation.

---

## What This Enables

- **GPT-5.4 with full brain access** — same 44+ tools as Claude Desktop
- **Cross-model deliberation** — Claude and GPT-5.4 analyzing the same data
- **Punta de Flecha** — adversarial convergence between Anthropic and OpenAI
- **Model diversity** — different strengths for different tasks

## Requirements

- ChatGPT Plus ($20/mo) or Pro ($200/mo) subscription
- Your MCP server running with SSE transport
- Node.js installed (the setup scripts handle this)

## Setup

### 1. Install Codex CLI

**Mac:**
```bash
brew install codex
```

**Windows:**
```powershell
winget install OpenAI.Codex
```

### 2. Authenticate

```bash
codex login
```

Browser opens → login with ChatGPT account → authorize.

Verify: `codex login status` → "Logged in using ChatGPT"

### 3. Connect to MCP Brain

Edit `~/.codex/config.toml`:

```toml
[mcp_servers.your_brand]
command = "npx"
args = ["mcp-remote", "https://YOUR-MCP-URL/sse"]
```

### 4. Verify

```bash
codex
> Use brain_search to find "company name"
```

If it returns brain results, it's connected.

## Configuration

### Recommended config.toml settings

```toml
model = "gpt-5.4"
approval_policy = "never"
sandbox_policy = "danger-full-access"

[mcp_servers.your_brand]
command = "npx"
args = ["mcp-remote", "https://YOUR-MCP-URL/sse"]
```

### For ChatGPT Pro users

Pro gives access to `gpt-5.4-pro` (more powerful, more compute):

```toml
model = "gpt-5.4-pro"
```

## Agent OAuth for Swarm Integration

If your swarm agents (running on OpenClaw or similar) need to use GPT-5.4 via ChatGPT OAuth:

1. Each agent needs its own `~/.codex/auth.json` with OAuth tokens
2. Use `codex login --device-auth` for headless servers
3. Or: employee runs `codex login` on their Mac, copies `~/.codex/auth.json` to the agent's home directory
4. Multiple agents can share one ChatGPT account (rate limits apply — Pro recommended for 2+ agents)

## Gotchas

| Issue | Detail |
|-------|--------|
| **Node 25.x EPIPE errors** | Codex CLI may fail with Node 25+. Use Node 22 LTS wrapper |
| **Rate limits (Plus)** | ChatGPT Plus has lower rate limits. 2 agents sharing = may saturate. Upgrade to Pro. |
| **Token refresh** | Codex CLI auto-refreshes tokens. If expired, re-run `codex login` |
| **device-auth 429** | OpenAI rate-limits device-auth from the same IP. Space out requests or use browser auth |

## Cross-Model Deliberation

With both Claude and Codex connected to the same brain:

```python
# In your MCP server, the punta_de_flecha tool runs:
# Round 1: Claude analyzes → sends to GPT-5.4
# Round 2: GPT-5.4 challenges → sends back to Claude
# ... up to 7 rounds until convergence
# Result: consensus analysis from both models
```

Use for: high-stakes decisions, strategy, anything where single-model bias is risky.
