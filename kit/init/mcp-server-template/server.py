#!/usr/bin/env python3
"""
OperAI MCP Server — minimal reference implementation.

Runs at 127.0.0.1:8787 behind a Cloudflare Tunnel, speaks the Model Context
Protocol over Server-Sent Events, and exposes the swarm's 11 core tools:

  Brain:         brain_query, brain_read, brain_write, brain_list
  Memory:        memory_write
  Personal:      me_read, me_write
  Swarm:         status
  Integrations:  shopify_query, klaviyo_query, slack_send_message

Auth: bearer token per employee, stored in /opt/operai/credentials/mcp-keys.json,
created by `operai-init key create <name> --role team|admin`.

Roles:
  admin  — full access (read + write brain, integrations, memory, me_write_any)
  team   — read brain + me_read + write own memory/me + integration reads

The server is intentionally small (~500 lines total across server.py + tools/)
and relies on the Python stdlib + three deps: mcp, starlette, uvicorn.
"""
from __future__ import annotations
import json
import logging
import os
import sys
from pathlib import Path

from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.types import TextContent, Tool
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Mount, Route

# Local imports
sys.path.insert(0, str(Path(__file__).parent))
from auth import authenticate, AuthError, Principal
from config import OPERAI_HOME, BRAND_SLUG
from tools import brain_acl as brain, memory as mem_tools, me as me_tools, status as status_tool, integrations

logging.basicConfig(
    level=os.environ.get("OPERAI_LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
log = logging.getLogger("operai-mcp")


# ─────────────────────────────────────────────────────────────────────────────
# Tool registry — (name, input_schema, handler, required_role)
# ─────────────────────────────────────────────────────────────────────────────

TOOLS: dict[str, dict] = {
    "brain_query": {
        "description": "Hybrid search across the brain (vector + keyword + rerank). Default choice.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query":       {"type": "string"},
                "collection":  {"type": "string", "description": "Collection name (workspace|memory|<brand>|platform|personal|projects). Omit for workspace."},
                "max_results": {"type": "integer", "default": 10},
            },
            "required": ["query"],
        },
        "handler":       brain.query,
        "required_role": "team",
    },
    "brain_read": {
        "description": "Read a single doc from the brain by path (relative to brain root).",
        "input_schema": {
            "type": "object",
            "properties": {"path": {"type": "string"}},
            "required": ["path"],
        },
        "handler":       brain.read,
        "required_role": "team",
    },
    "brain_write": {
        "description": "Create or update a doc in the brain. Admin only.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path":    {"type": "string"},
                "content": {"type": "string"},
            },
            "required": ["path", "content"],
        },
        "handler":       brain.write,
        "required_role": "admin",
    },
    "brain_list": {
        "description": "List files and folders under a directory (relative to brain root).",
        "input_schema": {
            "type": "object",
            "properties": {"directory": {"type": "string", "default": ""}},
        },
        "handler":       brain.list_dir,
        "required_role": "team",
    },
    "memory_write": {
        "description": "Append a note to today's memory file for the calling employee.",
        "input_schema": {
            "type": "object",
            "properties": {"content": {"type": "string"}},
            "required": ["content"],
        },
        "handler":       mem_tools.write,
        "required_role": "team",
    },
    "me_read": {
        "description": "Read a me.md personal profile. If name omitted, lists all profiles.",
        "input_schema": {
            "type": "object",
            "properties": {"name": {"type": "string"}},
        },
        "handler":       me_tools.read,
        "required_role": "team",
    },
    "me_write": {
        "description": "Write your own me.md personal profile (or any employee's if admin).",
        "input_schema": {
            "type": "object",
            "properties": {
                "name":    {"type": "string"},
                "content": {"type": "string"},
            },
            "required": ["content"],
        },
        "handler":       me_tools.write,
        "required_role": "team",
    },
    "status": {
        "description": "Health check — returns integrations, services, brain stats, tunnel.",
        "input_schema": {"type": "object", "properties": {}},
        "handler":       status_tool.run,
        "required_role": "team",
    },
    "shopify_query": {
        "description": "Shopify Admin API GET call. Pass resource like 'orders.json?status=any&limit=5'.",
        "input_schema": {
            "type": "object",
            "properties": {"resource": {"type": "string"}},
            "required": ["resource"],
        },
        "handler":       integrations.shopify_query,
        "required_role": "team",
    },
    "klaviyo_query": {
        "description": "Klaviyo API GET call. Pass endpoint like 'campaigns' or 'metrics'.",
        "input_schema": {
            "type": "object",
            "properties": {
                "endpoint": {"type": "string"},
                "params":   {"type": "object", "default": {}},
            },
            "required": ["endpoint"],
        },
        "handler":       integrations.klaviyo_query,
        "required_role": "team",
    },
    "slack_send_message": {
        "description": "Post a message to a Slack channel. Admin only (prevents accidental mass-send).",
        "input_schema": {
            "type": "object",
            "properties": {
                "channel": {"type": "string"},
                "text":    {"type": "string"},
            },
            "required": ["channel", "text"],
        },
        "handler":       integrations.slack_send_message,
        "required_role": "admin",
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# MCP server setup
# ─────────────────────────────────────────────────────────────────────────────

mcp_server = Server(name=f"operai-{BRAND_SLUG}")


@mcp_server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name=name,
            description=meta["description"],
            inputSchema=meta["input_schema"],
        )
        for name, meta in TOOLS.items()
    ]


@mcp_server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    # Principal is attached to the ContextVar by the SSE transport layer below
    principal = _CURRENT_PRINCIPAL.get()
    if principal is None:
        raise PermissionError("unauthenticated")

    meta = TOOLS.get(name)
    if meta is None:
        raise ValueError(f"unknown tool: {name}")

    required = meta["required_role"]
    if required == "admin" and principal.role != "admin":
        raise PermissionError(f"{name} requires admin role (you are {principal.role})")

    handler = meta["handler"]
    try:
        result = await handler(principal=principal, **arguments)
    except Exception as exc:  # noqa: BLE001
        log.exception("tool %s failed", name)
        return [TextContent(type="text", text=f"error: {exc}")]

    if isinstance(result, str):
        return [TextContent(type="text", text=result)]
    return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]


# ─────────────────────────────────────────────────────────────────────────────
# Starlette transport layer — SSE + auth middleware
# ─────────────────────────────────────────────────────────────────────────────

from contextvars import ContextVar

_CURRENT_PRINCIPAL: ContextVar[Principal | None] = ContextVar("current_principal", default=None)

sse_transport = SseServerTransport("/messages/")


async def handle_sse(request: Request):
    try:
        principal = authenticate(request)
    except AuthError as e:
        return JSONResponse({"error": str(e)}, status_code=401)

    token = _CURRENT_PRINCIPAL.set(principal)
    try:
        async with sse_transport.connect_sse(
            request.scope, request.receive, request._send
        ) as streams:
            await mcp_server.run(
                streams[0], streams[1], mcp_server.create_initialization_options()
            )
    finally:
        _CURRENT_PRINCIPAL.reset(token)
    # SseServerTransport already wrote the response; return a sentinel so Starlette
    # doesn't try to send again. Empty body + 200 is the safe default.
    return Response(status_code=200)


async def health(request: Request):
    return JSONResponse({
        "ok": True,
        "brand": BRAND_SLUG,
        "home": str(OPERAI_HOME),
        "tools": sorted(TOOLS.keys()),
    })


app = Starlette(
    debug=bool(os.environ.get("OPERAI_DEBUG")),
    routes=[
        Route("/", endpoint=health),
        Route("/health", endpoint=health),
        Route("/sse", endpoint=handle_sse),
        Mount("/messages/", app=sse_transport.handle_post_message),
    ],
)


def main():
    import argparse
    import uvicorn

    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8787)
    ap.add_argument("--reload", action="store_true")
    args = ap.parse_args()

    log.info("OperAI MCP server starting — brand=%s home=%s", BRAND_SLUG, OPERAI_HOME)
    log.info("tools registered: %d", len(TOOLS))
    uvicorn.run(app, host=args.host, port=args.port, reload=args.reload, log_level="info")


if __name__ == "__main__":
    main()
