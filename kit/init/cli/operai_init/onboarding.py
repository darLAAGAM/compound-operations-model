"""operai-init team-onboard + onboarding-pack — happy-path wrappers for employee onboarding.

Two composite commands:

  operai-init team-onboard <name> [--role admin|team] [--groups cs,retail,...]
    Chains:
      1. operai-init key create <name> --role <role> --groups <groups>
      2. operai-init assess <name>   (if --no-assess not passed)
      3. operai-init team-join --out /tmp/<name>-onboarding.sh --mcp-url <auto>
      4. Prints email template the founder copy-pastes to the employee

  operai-init onboarding-pack install
    Copies /opt/operai/services/init/onboarding-pack to /opt/operai/onboarding/
    Does find-replace of {BRAND} and {founder} across all templates
    Prints where the interpolated files live

  operai-init onboarding-pack show
    Prints paths + content summary of current pack

  operai-init onboarding-pack update
    Downloads https://usecompai.com/onboarding/pack.tar.gz
    Extracts to /opt/operai/services/init/onboarding-pack/
    Re-runs install (preserves any manual local edits — adds new files only)
"""
from __future__ import annotations
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

from operai_init import common


# ─────────────────────────────────────────────────────────────────────────────
# team-onboard — composite command
# ─────────────────────────────────────────────────────────────────────────────

def cmd_team_onboard(args, *, home: Path, brand: str):
    name = args.name
    role = args.role
    groups_csv = args.groups or ""

    common.banner(f"Team onboard · {name}")

    # 1. Create the API key
    from operai_init import key as key_cmd
    groups = [g.strip() for g in groups_csv.split(",") if g.strip()] or None
    common.info(f"Step 1 — generating {role} API key with groups {groups or 'default'}")
    key_cmd.create(home=home, name=name, role=role, groups=groups)

    # The token was printed by key_cmd.create. We re-read it from mcp-keys.json
    keys_path = home / "credentials" / "mcp-keys.json"
    token = None
    if keys_path.exists():
        try:
            keys = json.loads(keys_path.read_text())
            # Pick the newest key for this name
            cands = sorted(
                ((t, m) for t, m in keys.items() if m.get("name") == name and not m.get("revoked")),
                key=lambda kv: kv[1].get("created_at", ""),
                reverse=True,
            )
            if cands:
                token = cands[0][0]
        except Exception:
            token = None

    if not token:
        common.err("could not retrieve generated key token")
        return

    # 2. Run assess unless skipped
    if not args.no_assess:
        common.info("Step 2 — role profile assessment (M-shaped / T-shaped / frontline)")
        if not args.skip_interview:
            from operai_init import assess as assess_cmd
            try:
                assess_cmd.run(home=home, brand=brand, name=name, team=False)
            except SystemExit:
                pass
            except KeyboardInterrupt:
                common.warn("assessment skipped by user")

    # 3. Generate team-join.sh with MCP URL baked in
    common.info("Step 3 — generating team-join script")
    from operai_init import team_join as tj_mod
    out_dir = home / "onboarding" / "team-join-scripts"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{name}-team-join.sh"

    # Determine mcp_url
    tunnel_meta = home / "services" / "tunnel.json"
    mcp_url = None
    if tunnel_meta.exists():
        try:
            t = json.loads(tunnel_meta.read_text())
            sub = t.get("subdomain")
            if sub:
                mcp_url = f"https://{sub}/sse"
        except Exception:
            pass

    if args.mcp_url:
        mcp_url = args.mcp_url

    if not mcp_url:
        common.warn("could not auto-detect MCP URL — pass --mcp-url or run `operai-init tunnel` first")
        return

    tj_mod.run(out=str(out_path), home=home, brand=brand, mcp_url=mcp_url)

    # 4. Email template
    common.banner("Ready to send to " + name)

    email_template = f"""
  Subject: Welcome to {brand} — your AI swarm onboarding

  Hey {name.title()},

  Welcome to {brand}. To get you set up on our AI swarm (under 30 minutes):

  1. Run this in your terminal (Mac/Linux) or PowerShell (Windows):

     curl -fsSL 'https://usecompai.com/team-join?brand={brand}&mcp={mcp_url.replace("https://","").replace("/sse","")}' | bash

  2. When it asks for your API key, paste (send this separately/via secure channel):

     {token}

  3. After Claude Desktop reconnects, paste the custom instruction from:

     https://usecompai.com/onboarding/custom-instruction

  4. Your full onboarding checklist + 30-60-90 plan:

     https://usecompai.com/onboarding/checklist

  Step 6 of the checklist is the most important — takes 15 min and makes every
  future Claude chat personalized to you.

  Questions? DM me directly.

"""

    print(email_template)
    common.ok(f"team-join script written to {out_path} (alt channel if you prefer)")
    common.ok(f"API key for {name}: {token[:12]}… (full token copied above)")
    common.info("Track onboarding progress with: operai-init assess --team")


# ─────────────────────────────────────────────────────────────────────────────
# onboarding-pack — install/show/update
# ─────────────────────────────────────────────────────────────────────────────

def _pack_src(home: Path) -> Path:
    return home / "services" / "init" / "onboarding-pack"


def _pack_dst(home: Path) -> Path:
    return home / "onboarding"


def _interpolate_file(path: Path, brand: str, founder: str) -> None:
    try:
        text = path.read_text()
    except Exception:
        return
    new = text.replace("{BRAND}", brand).replace("{founder}", founder)
    if new != text:
        path.write_text(new)


def cmd_pack_install(args, *, home: Path, brand: str):
    src = _pack_src(home)
    dst = _pack_dst(home)
    if not src.exists():
        common.err(f"pack source not found at {src} — re-run install.sh or `operai-init onboarding-pack update`")
        return

    common.banner(f"Installing onboarding pack to {dst}")
    dst.mkdir(parents=True, exist_ok=True)

    founder = args.founder or "the founder"

    # Copy each sub-dir and interpolate markdowns
    for sub in ("skills", "claude-desktop", "notion-templates"):
        sub_src = src / sub
        sub_dst = dst / sub
        if not sub_src.exists():
            continue
        if sub_dst.exists():
            # Preserve previously customized files — only copy new ones
            for p in sub_src.rglob("*"):
                if p.is_file():
                    rel = p.relative_to(sub_src)
                    tgt = sub_dst / rel
                    if not tgt.exists():
                        tgt.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(p, tgt)
                        _interpolate_file(tgt, brand, founder)
                        common.ok(f"added {tgt.relative_to(dst)}")
            continue
        shutil.copytree(sub_src, sub_dst)
        for md in sub_dst.rglob("*.md"):
            _interpolate_file(md, brand, founder)
        common.ok(f"{sub}/ copied ({sum(1 for _ in sub_dst.rglob('*.md'))} templates)")

    # Top-level README
    readme_src = src / "README.md"
    readme_dst = dst / "README.md"
    if readme_src.exists() and not readme_dst.exists():
        shutil.copy2(readme_src, readme_dst)
        _interpolate_file(readme_dst, brand, founder)

    common.ok(f"onboarding pack ready at {dst}")
    common.info(f"Public URLs (your brand brain): https://usecompai.com/onboarding/*")


def cmd_pack_show(args, *, home: Path, brand: str):
    dst = _pack_dst(home)
    if not dst.exists():
        common.warn("onboarding pack not installed. Run: operai-init onboarding-pack install")
        return
    print(f"\n  {common.BOLD}Onboarding pack — {dst}{common.RESET}\n")
    for p in sorted(dst.rglob("*")):
        if p.is_file():
            rel = p.relative_to(dst)
            size = p.stat().st_size
            print(f"    {str(rel):<50} {size:>7} bytes")
    print()


def cmd_pack_update(args, *, home: Path, brand: str):
    url = "https://usecompai.com/onboarding/pack.tar.gz"
    common.info(f"Downloading latest pack from {url}")
    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            data = resp.read()
    except Exception as e:  # noqa: BLE001
        common.err(f"download failed: {e}")
        return

    # Write tarball to temp + extract
    src = _pack_src(home)
    backup = src.parent / "onboarding-pack.bak"
    if src.exists():
        if backup.exists():
            shutil.rmtree(backup)
        shutil.move(str(src), str(backup))
        common.info(f"previous pack backed up to {backup}")

    with tempfile.NamedTemporaryFile(suffix=".tar.gz", delete=False) as tf:
        tf.write(data)
        tmp_path = tf.name
    try:
        import tarfile
        with tarfile.open(tmp_path, "r:gz") as tar:
            tar.extractall(src.parent)
    finally:
        os.unlink(tmp_path)

    common.ok("pack updated. Re-run `operai-init onboarding-pack install` to apply template changes.")


# ─────────────────────────────────────────────────────────────────────────────
# Argparse
# ─────────────────────────────────────────────────────────────────────────────

def register(subparsers: argparse._SubParsersAction) -> None:
    # team-onboard
    p = subparsers.add_parser("team-onboard", help="Happy-path onboarding for a single employee (key + assess + team-join + email template)")
    p.add_argument("name", help="Employee slug (e.g. laura)")
    p.add_argument("--role", choices=["admin", "team"], default="team")
    p.add_argument("--groups", help="Comma-separated ACL groups (e.g. cs,retail)")
    p.add_argument("--mcp-url", help="Override MCP URL (else auto-detected from tunnel.json)")
    p.add_argument("--no-assess", action="store_true", help="Skip the role profile assessment")
    p.add_argument("--skip-interview", action="store_true", help="Assessment entry but no interactive prompts (batch onboarding)")
    p.set_defaults(onboarding_func=cmd_team_onboard)

    # onboarding-pack
    pp = subparsers.add_parser("onboarding-pack", help="Manage the onboarding pack (skills + custom instruction + Notion templates)")
    inner = pp.add_subparsers(dest="pack_action", required=True)

    sp = inner.add_parser("install", help="Install + interpolate the pack to /opt/operai/onboarding/")
    sp.add_argument("--founder", help="Founder name for interpolation (e.g. 'Diego')")
    sp.set_defaults(onboarding_func=cmd_pack_install)

    sp = inner.add_parser("show", help="List installed pack files")
    sp.set_defaults(onboarding_func=cmd_pack_show)

    sp = inner.add_parser("update", help="Download latest pack from usecompai.com/onboarding/")
    sp.set_defaults(onboarding_func=cmd_pack_update)
