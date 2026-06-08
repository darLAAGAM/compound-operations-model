"""operai-init webhook — CLI for webhook receiver configuration + testing."""
from __future__ import annotations
import argparse
import base64
import hashlib
import hmac
import json
import secrets as _secrets
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path

from operai_init import common
from operai_init.webhook import config as wh_config


def cmd_configure(args, *, home: Path, brand: str):
    provider = args.provider
    if provider not in wh_config.SUPPORTED:
        common.err(f"unknown provider '{provider}' — supported: {wh_config.SUPPORTED}")
        return

    common.banner(f"Configure webhook: {provider}")
    print(_provider_setup_guide(provider))

    existing = wh_config.get_secret(home, provider)
    if existing:
        if not common.confirm(f"{provider} already configured. Replace?", default=False):
            return

    if args.generate:
        secret = "whsec_" + _secrets.token_urlsafe(32)
        common.info(f"generated signing secret: {secret}")
        common.info(f"paste this into the {provider} webhook settings")
    else:
        secret = common.read_secret(f"{provider} signing secret (paste, hidden): ").strip()
        if not secret:
            common.err("no secret provided")
            return

    wh_config.set_provider(home, provider, secret)
    common.ok(f"{provider} configured")


def cmd_list(args, *, home: Path, brand: str):
    configured = set(wh_config.list_configured(home))
    base = wh_config.get_endpoint_base(home) or "<not configured — run: operai-init webhook set-endpoint>"

    print(f"\n  {common.BOLD}Webhook receivers{common.RESET}\n")
    print(f"  Endpoint base: {base}\n")
    print(f"  {'PROVIDER':<12} {'STATUS':<14} {'RECEIVER URL':<}")
    print(f"  {'-'*12} {'-'*14} {'-'*40}")
    for p in wh_config.SUPPORTED:
        is_conf = p in configured
        color = common.GREEN if is_conf else common.DIM
        status = "configured" if is_conf else "not configured"
        url = f"{base}/webhook/{p}/cs" if is_conf else "—"
        print(f"  {color}{p:<12}{common.RESET} {status:<14} {common.DIM}{url}{common.RESET}")
    print()


def cmd_remove(args, *, home: Path, brand: str):
    if wh_config.remove_provider(home, args.provider):
        common.ok(f"removed {args.provider}")
    else:
        common.warn(f"{args.provider} was not configured")


def cmd_set_endpoint(args, *, home: Path, brand: str):
    if not args.url.startswith("https://"):
        common.warn("endpoint URL should start with https:// for production")
    wh_config.set_endpoint_base(home, args.url)
    common.ok(f"endpoint base set to {args.url}")


def cmd_test(args, *, home: Path, brand: str):
    """Send a test webhook to the local receiver (assumes systemctl start operai-webhook)."""
    provider = args.provider
    if provider not in wh_config.SUPPORTED:
        common.err(f"unknown provider '{provider}'")
        return

    secret = wh_config.get_secret(home, provider)
    if not secret:
        common.err(f"{provider} not configured. Run: operai-init webhook configure {provider}")
        return

    sample = _sample_payload(provider)
    body = json.dumps(sample).encode("utf-8")

    # Build provider-specific header
    headers = {"Content-Type": "application/json"}
    if provider == "richpanel":
        sig = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
        headers["X-Richpanel-Signature"] = f"sha256={sig}"
    elif provider == "gorgias":
        sig = base64.b64encode(hmac.new(secret.encode(), body, hashlib.sha256).digest()).decode()
        headers["X-Gorgias-Hmac-SHA256"] = sig
    elif provider == "zendesk":
        ts = str(int(time.time() * 1000))
        sig = base64.b64encode(hmac.new(secret.encode(), ts.encode() + body, hashlib.sha256).digest()).decode()
        headers["X-Zendesk-Webhook-Signature"] = sig
        headers["X-Zendesk-Webhook-Signature-Timestamp"] = ts
    elif provider == "intercom":
        sig = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
        headers["X-Hub-Signature-256"] = f"sha256={sig}"

    url = f"http://{args.host}:{args.port}/webhook/{provider}/{args.domain}"
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    common.info(f"POST {url}")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            txt = resp.read().decode()
            common.ok(f"HTTP {resp.status}")
            print(f"  {txt}")
    except urllib.error.HTTPError as e:
        txt = e.read().decode() if hasattr(e, "read") else ""
        common.err(f"HTTP {e.code}: {txt[:200]}")
    except Exception as e:  # noqa: BLE001
        common.err(f"request failed: {e}")


def cmd_status(args, *, home: Path, brand: str):
    # Check if systemd unit active
    state = "unknown"
    try:
        out = subprocess.run(["systemctl", "is-active", "operai-webhook"], capture_output=True, text=True, timeout=5)
        state = out.stdout.strip() or "unknown"
    except (FileNotFoundError, subprocess.TimeoutExpired):
        state = "systemctl-unavailable"

    print(f"\n  {common.BOLD}Webhook receiver status{common.RESET}\n")
    print(f"  Service: operai-webhook  →  {state}")
    print(f"  Listening on: 127.0.0.1:8788")
    print(f"  Configured providers: {', '.join(wh_config.list_configured(home)) or '(none)'}")
    base = wh_config.get_endpoint_base(home)
    if base:
        print(f"  Public endpoint base: {base}")
    else:
        print(f"  Public endpoint base: {common.GOLD}not set{common.RESET} — run: operai-init webhook set-endpoint <url>")

    # Recent webhook activity — tail log
    log_path = home / "logs" / "webhook.log"
    if log_path.exists():
        lines = log_path.read_text(errors="replace").splitlines()[-5:]
        if lines:
            print(f"\n  {common.BOLD}Recent activity{common.RESET}")
            for line in lines:
                print(f"  {common.DIM}{line[:150]}{common.RESET}")
    print()


# ─────────────────────────────────────────────────────────────────────────────
# Provider setup guides
# ─────────────────────────────────────────────────────────────────────────────

def _provider_setup_guide(provider: str) -> str:
    guides = {
        "richpanel": """
    Richpanel setup:
    1. Go to Richpanel → Settings → Developer → Webhooks
    2. Click "Create Webhook"
    3. Event: ticket.created
    4. URL: <your endpoint base>/webhook/richpanel/cs
    5. Copy the "Signing Secret" shown
    6. Paste it below
    """,
        "gorgias": """
    Gorgias setup:
    1. Settings → Integrations → HTTP Integrations → Create
    2. Method: POST, URL: <endpoint base>/webhook/gorgias/cs
    3. Trigger: "Ticket created"
    4. Under Headers: Gorgias will include X-Gorgias-Hmac-SHA256 automatically
    5. Copy the "Secret key" from the integration detail page
    6. Paste it below
    """,
        "zendesk": """
    Zendesk setup:
    1. Admin Center → Apps and integrations → Webhooks → Add webhook
    2. Authentication: Bearer OR basic (we use HMAC per Zendesk security)
    3. Under Advanced settings → Signing Secret → Generate
    4. URL: <endpoint base>/webhook/zendesk/cs
    5. Create a Trigger (Admin → Triggers) firing on "Ticket is Created"
    6. Copy the signing secret shown once
    7. Paste it below
    """,
        "intercom": """
    Intercom setup:
    1. Developer Hub → your app → Webhooks
    2. Topics to subscribe: conversation.user.created, conversation.user.replied
    3. URL: <endpoint base>/webhook/intercom/cs
    4. Copy the "Client secret" from the Basic information tab
    5. Paste it below (Intercom signs with X-Hub-Signature-256)
    """,
    }
    return guides.get(provider, "")


def _sample_payload(provider: str) -> dict:
    samples = {
        "richpanel": {
            "event": "ticket.created",
            "data": {
                "id": "rp-test-001",
                "subject": "Test refund request",
                "priority": "NORMAL",
                "status": "OPEN",
                "customer": {"email": "customer@test.example", "name": "Test Customer"},
                "messages": [{"body": "Hi, I'd like to return my recent order. Thanks!", "direction": "INBOUND", "created_at": "2026-04-21T12:00:00Z"}],
                "channel": "email",
                "tags": ["test"],
                "created_at": "2026-04-21T12:00:00Z",
            },
        },
        "gorgias": {
            "id": 424242,
            "subject": "Test inquiry",
            "priority": "normal",
            "channel": "email",
            "status": "open",
            "customer": {"email": "customer@test.example", "name": "Test"},
            "messages": [{"body_text": "Hello, I have a question.", "from_agent": False, "created_datetime": "2026-04-21T12:00:00Z"}],
            "tags": [{"name": "test"}],
            "created_datetime": "2026-04-21T12:00:00Z",
        },
        "zendesk": {
            "ticket": {
                "id": 777,
                "subject": "Test Zendesk ticket",
                "description": "This is a test ticket via webhook.",
                "priority": "normal",
                "via": {"channel": "email"},
                "requester": {"email": "customer@test.example", "name": "Test"},
                "tags": ["test"],
                "created_at": "2026-04-21T12:00:00Z",
            },
        },
        "intercom": {
            "type": "notification_event",
            "topic": "conversation.user.created",
            "data": {
                "item": {
                    "id": "conv-test-001",
                    "type": "conversation",
                    "source": {
                        "subject": "Intercom test",
                        "body": "<p>Hi, testing the receiver.</p>",
                        "author": {"email": "customer@test.example", "name": "Test", "type": "user"},
                    },
                    "tags": {"tags": [{"name": "test"}]},
                    "priority": "not_priority",
                    "created_at": 1713700800,
                },
            },
        },
    }
    return samples.get(provider, {})


# ─────────────────────────────────────────────────────────────────────────────

def register(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("webhook", help="Manage helpdesk webhook receivers")
    inner = p.add_subparsers(dest="webhook_action", required=True)

    sp = inner.add_parser("configure", help="Configure a provider's signing secret")
    sp.add_argument("provider", choices=wh_config.SUPPORTED)
    sp.add_argument("--generate", action="store_true", help="Generate a secret locally (then paste into helpdesk settings)")
    sp.set_defaults(webhook_func=cmd_configure)

    sp = inner.add_parser("list", help="List providers + receiver URLs")
    sp.set_defaults(webhook_func=cmd_list)

    sp = inner.add_parser("remove", help="Remove a provider configuration")
    sp.add_argument("provider", choices=wh_config.SUPPORTED)
    sp.set_defaults(webhook_func=cmd_remove)

    sp = inner.add_parser("set-endpoint", help="Set the public endpoint base URL (e.g. https://webhook.acme.com)")
    sp.add_argument("url")
    sp.set_defaults(webhook_func=cmd_set_endpoint)

    sp = inner.add_parser("test", help="Send a signed test payload to the local receiver")
    sp.add_argument("provider", choices=wh_config.SUPPORTED)
    sp.add_argument("--domain", default="cs")
    sp.add_argument("--host", default="127.0.0.1")
    sp.add_argument("--port", type=int, default=8788)
    sp.set_defaults(webhook_func=cmd_test)

    sp = inner.add_parser("status", help="Show service state + recent activity")
    sp.set_defaults(webhook_func=cmd_status)
