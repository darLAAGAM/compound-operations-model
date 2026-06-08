# OperAI MCP Server — v0.3

Minimal reference Model Context Protocol server for a brand-new OperAI deployment.

- **Transport:** Server-Sent Events at `/sse`
- **Auth:** Bearer token (per employee), managed by `operai-init key …`
- **Tools:** 11 — brain_* (4), memory_write, me_* (2), status, shopify_query, klaviyo_query, slack_send_message
- **Lines of code:** ~500 across `server.py` + `auth.py` + `config.py` + `tools/`

## Structure

```
mcp-server-template/
├── server.py         # entry point — Starlette app with SSE + auth middleware
├── auth.py           # bearer token validation + Principal dataclass
├── config.py         # resolves OPERAI_HOME + brand slug from layout
├── requirements.txt  # mcp + starlette + uvicorn
└── tools/
    ├── __init__.py
    ├── brain.py       # query / read / write / list (wraps QMD)
    ├── memory.py      # memory_write (appends to today's note)
    ├── me.py          # me_read / me_write (personal profiles)
    ├── status.py      # proxies to operai_init.status
    └── integrations.py # Shopify / Klaviyo / Slack passthroughs
```

## Role model

Each API key carries a role. Tools declare the minimum role they require.

| Tool | Required role | Rationale |
|---|---|---|
| brain_query, brain_read, brain_list | team | Read-only access |
| brain_write | admin | Prevents accidental overwrites; audited |
| memory_write | team | Everyone can write their own daily notes |
| me_read | team | Everyone can read anyone's profile |
| me_write | team | Everyone can write their own; admin can write any |
| status | team | Health check is non-sensitive |
| shopify_query, klaviyo_query | team | Read-only platform queries |
| slack_send_message | admin | Prevents accidental mass-send |

## Local dev

```bash
pip install -r requirements.txt
OPERAI_HOME=/opt/operai python3 server.py --host 127.0.0.1 --port 8787
```

Health check: `curl http://127.0.0.1:8787/health`

## Production

Installed by `install.sh` at `/opt/operai/services/mcp/`, started by the
`operai-mcp.service` systemd unit, and exposed publicly via the
`operai-tunnel.service` Cloudflare Tunnel.

## Key management

```bash
operai-init key create <name> --role admin|team   # generates lgm_<32 hex>
operai-init key list                              # shows names + roles + last_seen
operai-init key revoke <name>                     # soft-revokes (keeps audit)
```

Keys live in `/opt/operai/credentials/mcp-keys.json` with mode 600.

## Extending

Each tool is a coroutine taking `principal=Principal` plus the args declared in
its input_schema. Register new tools in the `TOOLS` dict at the top of
`server.py`. No other glue required.

## What this does NOT do (yet, v0.3)

- No rate limiting per key — add nginx/caddy in front for production
- No tool-level audit log beyond the brain_write trail
- No websocket transport — SSE only
- No Streamable HTTP — SSE only for now (mcp-remote handles the translation for
  Claude Desktop clients)
