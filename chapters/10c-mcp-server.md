# Chapter 10c: The MCP Server — Giving Your Entire Team AI Superpowers

## The Problem: Agents Are Powerful, But Only the Builder Can Use Them

You've deployed seven agents. They can query Shopify, check inventory, pull financial data, search your knowledge base, and send messages across channels. Amazing.

But only you — the person who set it up — can talk to them. Your finance manager can't ask the system a question. Your CS lead can't query customer history. Your retail manager can't pull foot traffic data. The AI is locked inside a terminal that nobody else knows how to use.

**The MCP Server solves this.** It turns your entire agent swarm into a set of tools that anyone on the team can access from Claude Desktop, Cursor, or any MCP-compatible client — with zero technical setup on their end.

## What MCP Is

MCP (Model Context Protocol) is an open standard that lets AI applications connect to external data sources and tools. Think of it as a universal adapter: your agent swarm speaks MCP, and any AI client that speaks MCP can use it.

In practice: your finance manager opens Claude Desktop, and it already knows how to query Holded, pull Shopify orders, check Payhawk expenses, and search the company knowledge base. No API keys on their machine. No SSH. No terminal.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                  TEAM MEMBERS                        │
│  Claude Desktop / Cursor / Any MCP Client            │
│  (Mac, Windows, Linux — zero config)                 │
└───────────────────┬─────────────────────────────────┘
                    │ SSE (Server-Sent Events)
                    │ https://mcp.yourdomain.com/sse
                    │
┌───────────────────▼─────────────────────────────────┐
│              MCP SERVER (Python / FastMCP)            │
│              Internal port                    │
│              Cloudflare Tunnel → mcp.yourdomain.com       │
│                                                       │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐             │
│  │  Brain   │ │  Swarm   │ │  APIs    │             │
│  │  Tools   │ │  Control │ │  Direct  │             │
│  │ 5 tools  │ │ 2 tools  │ │ 20 tools │             │
│  └──────────┘ └──────────┘ └──────────┘             │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐             │
│  │  Files   │ │  Memory  │ │  Infra   │             │
│  │ 3 tools  │ │ 3 tools  │ │ 8 tools  │             │
│  └──────────┘ └──────────┘ └──────────┘             │
│  ┌──────────┐                                        │
│  │  Skills  │                                        │
│  │ 3 tools  │ → access to 352 skills                 │
│  └──────────┘                                        │
└─────────────────────────────────────────────────────┘
                    │
    ┌───────────────┼───────────────────┐
    │               │                   │
┌───▼───┐     ┌─────▼─────┐     ┌──────▼──────┐
│Shopify│     │  Holded   │     │  7 Agents   │
│Klaviyo│     │  Payhawk  │     │  (via HTTP)  │
│Meta   │     │  Amphora  │     │             │
│...  │     │...     │     │             │
└───────┘     └───────────┘     └─────────────┘
```

## The Tool Inventory

The MCP server exposes 95 tools organized by domain:

### Knowledge & Memory
| Tool | What It Does |
|------|-------------|
| `brain_search` | Semantic search across 3,007+ knowledge docs |
| `brain_read` | Read a specific knowledge document |
| `brain_write` | Create or update knowledge docs |
| `brain_list` | Browse the knowledge tree |
| `read_megadoc` | Load the complete company reference doc |
| `memory_read` | Read daily operational logs |
| `memory_write` | Append to daily logs |
| `memory_list_recent` | List recent log files |

### Swarm Control
| Tool | What It Does |
|------|-------------|
| `agent_status` | Health check all 7 agents (online/offline, model, uptime) |
| `agent_send` | Send a message to any agent and get a response |

### Business APIs (Full Read/Write)
| Tool | What It Does |
|------|-------------|
| `shopify_query` | Orders, products, inventory, customers, POS |
| `stockagile_query` | Multi-warehouse stock, transfers, purchase orders |
| `klaviyo_query` | Email campaigns, flows, segments, profiles |
| `holded_query` | Invoices, contacts, treasury, accounting |
| `meta_ads_query` | Campaign performance, spend, ROAS |
| `payhawk_query` | Expenses, corporate cards, bank statements |
| `amphora_query` | 3PL orders, returns, inventory, inbounds |
| `richpanel_query` | CS tickets, customer history |
| `notion_query` | Pages, databases, blocks — full Notion API |
| `google_workspace` | Gmail, Calendar, Drive, Sheets, Docs |
| `holded_leaves` | Team absences (custom microservice) |
| `ga4_query` | Google Analytics — sessions, revenue, conversions |
| `tc_analytics_query` | Physical store foot traffic |

### Slack
| Tool | What It Does |
|------|-------------|
| `slack_search` | Full-text search across all messages |
| `slack_list_channels` | List channels with IDs |
| `slack_read_channel` | Read recent messages from a channel |
| `slack_read_thread` | Read thread replies |
| `slack_send_message` | Post to channels or threads |
| `slack_user_info` | Look up users |

### Infrastructure
| Tool | What It Does |
|------|-------------|
| `file_read` / `file_write` / `file_list` | Full workspace filesystem access |
| `shell_exec` | Execute any shell command on the VPS |
| `exa_search` | Semantic web search (better than Google for research) |
| `vercel_query` | Deployment management |
| `krea_generate` / `krea_status` | AI image generation |
| `upstash_redis` | Key-value store operations |

### Skills Library
| Tool | What It Does |
|------|-------------|
| `skills_list` | Browse 167+ categorized skills across 12 domains (marketing, seo, cro, analytics, etc.) |
| `skill_read` | Read a skill's full methodology and prompts |
| `skill_search` | Search across all skills by keyword |

## How the Team Uses It

### Setup (2 minutes per person)

Every team member gets the same config. Add this to Claude Desktop's config file:

```json
{
  "mcpServers": {
    "your-brand": {
      "command": "npx",
      "args": ["mcp-remote", "https://mcp.yourdomain.com/sse"]
    }
  }
}
```

Restart Claude Desktop. Done. All 95 tools are available.

### Real Usage Examples

**Finance manager** asks Claude Desktop:
> "What were our total sales yesterday across all channels?"

Claude calls `shopify_query("orders.json?status=any&created_at_min=2026-03-25&limit=250")`, aggregates, and returns a summary. No dashboards to build. No reports to run.

**CS lead** asks:
> "Show me all open tickets from VIP customers this week"

Claude calls `richpanel_query("tickets", params="status=OPEN")`, cross-references with Klaviyo segments, and surfaces the priority tickets.

**Retail manager** asks:
> "Compare foot traffic between Store A and Store B last week"

Claude calls `tc_analytics_query("store_b", "2026-03-17", "2026-03-23")` and `tc_analytics_query("store_a", "2026-03-17", "2026-03-23")`, then produces a comparison table with conversion rates.

**The CEO** asks:
> "Send a message to Marketing Agent asking for this week's Meta Ads ROAS by campaign"

Claude calls `agent_send("marketing_agent", "Pull this week's Meta Ads ROAS broken down by campaign")` and returns Marketing Agent's analysis.

## Security Model

### Two-Tier Access

| Role | Can Read | Can Write |
|------|----------|-----------|
| **Admin** (founder, finance) | Everything | Everything (brain, files, shell, APIs) |
| **Team** | All APIs, brain, memory | APIs only (Shopify, Klaviyo, etc.) — no brain_write, file_write, shell_exec |

### API Key Authentication (Optional)

Each team member gets a unique token (`lgm_{hex}`). When activated:
- Every tool call is logged with who made it
- Write permissions are per-role
- Keys can be revoked individually
- Usage tracking per employee

### Network Security

- Server runs on Tailscale mesh network (encrypted, private)
- HTTPS via Tailscale Funnel (public URL with TLS)
- No API keys stored on employee machines
- All credentials stay server-side

## Implementation

### The Server

The MCP server is a single Python file (~400 lines) using FastMCP:

```python
from mcp.server.fastmcp import FastMCP
mcp = FastMCP("Your Brand AI")

@mcp.tool()
def shopify_query(endpoint: str, method: str = "GET", body: str = "") -> str:
    """Query Shopify Admin API. Full read/write access."""
    return _http(f"{SHOPIFY_BASE}/{endpoint}", method=method, 
                 headers={"X-Shopify-Access-Token": SHOPIFY_TOKEN}, body=body)
```

Each tool is a decorated function that wraps an API call. The pattern is identical for every integration: validate input → call API → return truncated result.

### Deployment

```bash
# Install
pip install mcp

# Run (stdio mode for SSH, SSE mode for network)
python server.py sse    # Network mode (for team)
python server.py stdio  # SSH mode (for single user)

# Systemd service (auto-start, auto-restart)
systemctl enable --now your-brand-mcp
```

### Exposing to the Team

The MCP server runs behind a **permanent Cloudflare Tunnel** for public HTTPS access without opening any ports on the VPS:

```bash
# One-time setup
cloudflared tunnel create your-brand-mcp
cloudflared tunnel route dns your-brand-mcp mcp.yourdomain.com

# Config file: /etc/cloudflared/config.yml
tunnel: your-brand-mcp
credentials-file: /root/.cloudflared/<tunnel-id>.json
ingress:
  - hostname: mcp.yourdomain.com
    service: http://localhost:18820
  - service: http_status:404

# Run as systemd service
systemctl enable --now cloudflared
```

**Result:** `https://mcp.yourdomain.com/sse` is live, TLS-terminated by Cloudflare, served from your VPS over an encrypted outbound tunnel. No inbound ports. No DNS headaches. Zero monthly cost.

**Alternative:** Tailscale Funnel still works and requires no dedicated domain. Cloudflare Tunnel is preferred for production because it uses your own domain and doesn't require team members to have Tailscale installed.

## Cost

**€0/month additional.** The MCP server is a Python process (~400 lines) running on the same server as your agents. The Cloudflare Tunnel is free tier. No new infrastructure. No SaaS subscription. The only cost is the LLM tokens your team members use in Claude Desktop — and that's their own Claude Pro subscription.

### Claude Code Integration

For power users (founders, tech leads), Claude Code provides an even deeper interface:

```bash
# In ~/.claude/CLAUDE.md — all 95 tools + slash commands + subagents
# In ~/.claude/mcp.json — MCP server connection
# In ~/.claude/agents/ — 5 domain-specific subagents
# In ~/.claude/commands/ — 6 operational slash commands
```

Claude Code users get everything Claude Desktop users get, plus:
- **Slash commands:** `/deploy`, `/weekly-report`, `/stock-check`, `/swarm-status`, `/customer-lookup`, `/brain-update`
- **Subagents:** Launch parallel research across domains
- **File system access:** Read/write directly to the brain
- **Shell execution:** Run scripts, deploy code, manage infrastructure

This is the "operator cockpit" — one interface for the entire business.

## QMD — Quoted Markdown Search

On top of the 95 tools, the MCP server runs **QMD (Quoted Markdown) v2.0.1** — a lightweight semantic index over the brain:

- **Hourly cron** rebuilds the vector store from the latest brain state
- **3,007 files indexed** across all knowledge domains
- **128+ embedded vectors** covering the highest-traffic lookups
- **4-tier retrieval** (cache → full-text → LLM search → recursive LLM) matches ByteRover's retrieval quality

QMD is invisible to end users — it powers the `brain_search` tool under the hood. Queries that previously returned 10+ irrelevant matches now return 3-5 highly relevant files. Response latency on typical brain queries dropped from ~2s to ~200ms.

**Cost:** €0/month additional. QMD is a local binary that runs on the VPS alongside the MCP server.

## Security Hardening

The MCP server is the primary entry point for the entire team's AI access. Security matters.

### Plugin Permissions

OpenClaw's security layer blocks world-writable plugin paths. Never `chmod -R 777` — fix ownership with `chown`, not permissions with `chmod`. Run `openclaw security-scan` after any plugin install to verify baseline scores (VPS: 100/100, Mac Mini: 85/100 with DM channels open).

### Secret Rotation

Every API key in the MCP server environment is rotated quarterly. The rotation script pulls new values from a secret manager, writes them to `/etc/default/your-brand-mcp`, and restarts the systemd unit. Downtime: <5 seconds.

### Audit Logging

Every tool call is logged with:
- Timestamp
- Caller (resolved from bearer token when team auth is enabled)
- Tool name and arguments
- Response size + status

Logs rotate daily, compressed, retained for 90 days. GDPR-compliant retention policy.

### Brain Write Protection

`brain_write` is the only tool that modifies persistent knowledge. It's restricted to admin tokens by default and logged with the full before/after diff. Every brain mutation is reversible from the git history of the brain repo.

## Why This Matters

The MCP server transforms your AI operations system from a single-operator tool into a **team-wide intelligence layer.** Every person in the company can ask questions across all your systems simultaneously — something that previously required switching between 12 different dashboards, or asking the ops lead to pull data manually.

It's the difference between "the founder has an AI system" and "the company runs on AI."

---

*Next: [Chapter 11 — Implementation →](11-implementation.md)*
