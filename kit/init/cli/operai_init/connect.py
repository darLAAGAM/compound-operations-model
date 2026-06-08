"""connect dispatcher — delegates to per-service modules."""
from __future__ import annotations
from pathlib import Path

from operai_init import common
from operai_init.connectors import shopify, klaviyo, google_workspace, slack


_HANDLERS = {
    "shopify":          shopify.connect,
    "klaviyo":          klaviyo.connect,
    "google-workspace": google_workspace.connect,
    "slack":            slack.connect,
}


def run(service: str, *, home: Path, brand: str, force: bool = False) -> None:
    common.banner(f"Connecting {service} · {brand}")
    if service not in _HANDLERS:
        common.err(f"Unknown service: {service}")
        raise SystemExit(2)
    common.existing_integration_check(home, service, force)
    _HANDLERS[service](home=home, brand=brand)
