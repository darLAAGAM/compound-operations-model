#!/usr/bin/env python3
"""agent-runner — minimal heartbeat runner for OperAI domain agents.

v0.5.x scope: each domain agent (cs, finance, ops, marketing, merch, retail, hr)
has a SOUL.md defining its role. The real agent logic (SOUL-driven LLM loops
with MCP tool access) lands in v0.6. Until then, this runner:

  1. Reads the agent's SOUL.md (proves the layout is correct)
  2. Emits a heartbeat to brain/memory/<agent>/YYYY-MM-DD.log every 60s
  3. Stays alive so systemctl reports 'active (running)'

This is a placeholder. Deploying a real brand should not expect autonomous
agent behaviour from this runner — that comes in v0.6 with the agent factory
refactor.
"""
from __future__ import annotations
import argparse
import json
import os
import signal
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


OPERAI_HOME = Path(os.environ.get("OPERAI_HOME", "/opt/operai"))


def log(msg: str) -> None:
    ts = datetime.now(timezone.utc).isoformat()
    print(f"{ts} {msg}", flush=True)


def heartbeat(agent: str, brand: str) -> None:
    mem_dir = OPERAI_HOME / "brain" / "memory" / agent
    mem_dir.mkdir(parents=True, exist_ok=True)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    path = mem_dir / f"{today}.log"
    ts = datetime.now(timezone.utc).isoformat()
    with path.open("a") as f:
        f.write(f"{ts}\theartbeat\t{agent}\t{brand}\n")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--agent", required=True, help="Agent slug (cs, finance, ops, marketing, merch, retail, hr, critic, guardrail, compliance)")
    ap.add_argument("--interval", type=int, default=60, help="Heartbeat interval seconds")
    args = ap.parse_args()

    brand = os.environ.get("OPERAI_BRAND", "unknown")
    agent_dir = OPERAI_HOME / "agents" / args.agent
    soul_path = agent_dir / "SOUL.md"

    log(f"agent-runner starting: agent={args.agent} brand={brand} home={OPERAI_HOME}")
    if soul_path.exists():
        size = soul_path.stat().st_size
        log(f"SOUL loaded from {soul_path} ({size} bytes)")
    else:
        log(f"WARN: no SOUL.md at {soul_path} — agent will run without prompt context")

    # Graceful shutdown on SIGTERM
    stopping = {"v": False}
    def _stop(signum, frame):
        log(f"signal {signum} received; shutting down")
        stopping["v"] = True
    signal.signal(signal.SIGTERM, _stop)
    signal.signal(signal.SIGINT, _stop)

    log(f"entering heartbeat loop (interval={args.interval}s)")
    while not stopping["v"]:
        try:
            heartbeat(args.agent, brand)
        except Exception as e:  # noqa: BLE001
            log(f"heartbeat write failed: {e}")
        # Sleep in 1s increments so we react to signals quickly
        for _ in range(args.interval):
            if stopping["v"]:
                break
            time.sleep(1)

    log("stopped cleanly")
    return 0


if __name__ == "__main__":
    sys.exit(main())
