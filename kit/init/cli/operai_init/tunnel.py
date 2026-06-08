"""tunnel — Cloudflare Tunnel wrapper.

Creates a named tunnel, installs a systemd unit that keeps it running, and
routes <subdomain> → 127.0.0.1:<port> (the local MCP server).

Assumes `cloudflared tunnel login` has already been run (a one-time browser
auth step that the founder does once per machine).
"""
from __future__ import annotations
import json
import os
import shutil
import subprocess
from pathlib import Path

from operai_init import common


CLOUDFLARED_CONFIG_DIR = Path.home() / ".cloudflared"


def _require_cloudflared() -> str:
    path = shutil.which("cloudflared")
    if not path:
        common.err("cloudflared not installed. Run: apt-get install cloudflared (or re-run install.sh)")
        raise SystemExit(2)
    return path


def _require_login() -> None:
    cert = CLOUDFLARED_CONFIG_DIR / "cert.pem"
    if not cert.exists():
        common.err("Cloudflared is not logged in. Run first:\n      cloudflared tunnel login")
        raise SystemExit(2)


def _tunnel_exists(cf: str, name: str) -> str | None:
    try:
        out = subprocess.check_output([cf, "tunnel", "list", "--output", "json"], timeout=15)
        tunnels = json.loads(out.decode("utf-8"))
        for t in tunnels:
            if t.get("name") == name:
                return t.get("id")
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, json.JSONDecodeError):
        return None
    return None


def _create_tunnel(cf: str, name: str) -> str:
    subprocess.run([cf, "tunnel", "create", name], check=True, timeout=30)
    tunnel_id = _tunnel_exists(cf, name)
    if not tunnel_id:
        raise RuntimeError("tunnel created but not found in list")
    return tunnel_id


def _write_config(home: Path, brand: str, tunnel_id: str, subdomain: str, port: int) -> Path:
    cfg_path = home / "services" / "cloudflared.yml"
    credentials_file = CLOUDFLARED_CONFIG_DIR / f"{tunnel_id}.json"
    config = f"""tunnel: {tunnel_id}
credentials-file: {credentials_file}

ingress:
  - hostname: {subdomain}
    service: http://127.0.0.1:{port}
  - service: http_status:404
"""
    cfg_path.parent.mkdir(parents=True, exist_ok=True)
    cfg_path.write_text(config)
    return cfg_path


def _route_dns(cf: str, name: str, subdomain: str) -> None:
    try:
        subprocess.run([cf, "tunnel", "route", "dns", name, subdomain], check=True, timeout=30)
    except subprocess.CalledProcessError as e:
        common.warn(f"DNS route creation failed (already exists?): {e}")


def _install_systemd(home: Path, brand: str, cfg_path: Path) -> Path:
    unit = f"""[Unit]
Description=OperAI {brand} · Cloudflare Tunnel (MCP endpoint)
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=operai
Group=operai
ExecStart=/usr/local/bin/cloudflared tunnel --config {cfg_path} run
Restart=on-failure
RestartSec=10
StandardOutput=append:{home}/logs/cloudflared.log
StandardError=append:{home}/logs/cloudflared.log

NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
"""
    unit_path = Path("/etc/systemd/system/operai-tunnel.service")
    try:
        unit_path.write_text(unit)
    except PermissionError:
        common.err("Must run `operai-init tunnel` as root (for systemd unit install)")
        raise SystemExit(2)

    subprocess.run(["systemctl", "daemon-reload"], check=True)
    return unit_path


def run(subdomain: str, *, home: Path, brand: str, port: int = 8787) -> None:
    if "." not in subdomain:
        common.err(f"'{subdomain}' doesn't look like a subdomain (need FQDN, e.g. mcp.acme.com)")
        raise SystemExit(2)

    common.banner(f"Cloudflare Tunnel · {subdomain} → 127.0.0.1:{port}")

    cf = _require_cloudflared()
    _require_login()

    tunnel_name = f"{brand}-mcp"
    existing_id = _tunnel_exists(cf, tunnel_name)
    if existing_id:
        common.info(f"tunnel '{tunnel_name}' already exists (id: {existing_id[:8]}…)")
        tunnel_id = existing_id
    else:
        common.info(f"creating tunnel '{tunnel_name}'")
        tunnel_id = _create_tunnel(cf, tunnel_name)
        common.ok(f"tunnel created (id: {tunnel_id[:8]}…)")

    cfg_path = _write_config(home, brand, tunnel_id, subdomain, port)
    common.ok(f"config written to {cfg_path}")

    common.info(f"routing DNS: {subdomain} → {tunnel_name}")
    _route_dns(cf, tunnel_name, subdomain)
    common.ok("DNS route created (propagation: <60s)")

    common.info("installing systemd unit")
    unit_path = _install_systemd(home, brand, cfg_path)
    common.ok(f"systemd unit at {unit_path}")

    # Cache the resolved MCP URL for team-join
    meta = {
        "subdomain": subdomain,
        "port":      port,
        "tunnel_id": tunnel_id,
        "tunnel_name": tunnel_name,
    }
    (home / "services" / "tunnel.json").write_text(json.dumps(meta, indent=2))

    print(f"""
{common.BOLD}Next:{common.RESET}
  systemctl enable --now operai-tunnel
  systemctl status operai-tunnel
  curl -I https://{subdomain}/sse      # should return a 4xx from the MCP server
""")
