"""Factory runtime daemon — watches /opt/operai/events/<domain>/pending/ and processes.

Polls the filesystem every N seconds (default 3s). For each new .json file:
  1. Load event
  2. Determine domain from its folder
  3. Resolve factory config
  4. Auto-enrich event via brain_lookup
  5. Invoke workflow pre-hook if brand defined one
  6. Run the factory (parallel)
  7. Invoke workflow post-hook if brand defined one
  8. Route decision to review queue
  9. Move event to completed/ or failed/
 10. Emit Slack digest if configured + action is escalate_supervisor

This is a foreground process intended to run under systemd. Graceful shutdown
on SIGTERM: finishes the event currently in-flight, then exits clean.
"""
from __future__ import annotations
import argparse
import json
import logging
import os
import shutil
import signal
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

from operai_init.factory_runtime import brain_lookup, config as fc_cfg, parallel, review_queue, trace as trace_mod

log = logging.getLogger("operai-factory-runtime")


class Daemon:
    def __init__(
        self,
        home: Path,
        brand: str,
        *,
        poll_interval_sec: float = 3.0,
        mock_llm: bool = False,
    ):
        self.home = home
        self.brand = brand
        self.poll = poll_interval_sec
        self.mock = mock_llm
        self.stopping = False
        self._in_flight: str | None = None

    def _events_root(self) -> Path:
        p = self.home / "events"
        for bucket in ("pending", "completed", "failed", "in-flight"):
            (p / bucket).mkdir(parents=True, exist_ok=True)
        return p

    def _pending_events(self) -> list[Path]:
        root = self._events_root() / "pending"
        # Events live at pending/<domain>/<event_id>.json
        out: list[Path] = []
        for domain_dir in root.iterdir() if root.exists() else []:
            if domain_dir.is_dir():
                out.extend(sorted(domain_dir.glob("*.json")))
        return out

    def _load_factory(self, domain: str):
        factory_dir = self.home / "agents" / domain / "factory"
        if not factory_dir.exists():
            raise FileNotFoundError(f"factory not enabled for domain '{domain}'")
        fc = fc_cfg.load(factory_dir)
        issues = fc_cfg.validate(fc)
        if issues:
            log.warning("factory %s has issues: %s", domain, issues)
        return fc

    def _load_workflow_hooks(self, domain: str):
        """Load brand-specific workflow hooks if they exist."""
        hooks_path = self.home / "workflows" / domain
        pre_hook = hooks_path / "pre_process.py"
        post_hook = hooks_path / "post_process.py"
        hooks = {"pre": None, "post": None}
        import importlib.util
        for key, path in (("pre", pre_hook), ("post", post_hook)):
            if path.exists():
                try:
                    spec = importlib.util.spec_from_file_location(f"workflow_{domain}_{key}", path)
                    mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod)
                    if hasattr(mod, "run"):
                        hooks[key] = mod.run
                        log.info("loaded %s hook for %s from %s", key, domain, path)
                except Exception as e:  # noqa: BLE001
                    log.error("failed loading %s hook for %s: %s", key, domain, e)
        return hooks

    def process_event(self, event_path: Path) -> None:
        event_id = event_path.stem
        domain = event_path.parent.name
        self._in_flight = str(event_path)

        log.info("pick up event %s (%s)", event_id, domain)

        # Move to in-flight so another daemon / retry wouldn't double-process
        inflight = self._events_root() / "in-flight" / domain
        inflight.mkdir(parents=True, exist_ok=True)
        inflight_path = inflight / event_path.name
        shutil.move(str(event_path), str(inflight_path))

        try:
            event = json.loads(inflight_path.read_text())
        except json.JSONDecodeError as e:
            log.error("event %s: JSON decode error: %s", event_id, e)
            self._fail_event(inflight_path, domain, error=f"json decode: {e}")
            return

        # Enrich via brain_lookup
        try:
            event = brain_lookup.enrich_event(self.brand, event)
        except Exception as e:  # noqa: BLE001
            log.warning("brain_lookup failed for %s: %s", event_id, e)

        # Load workflow hooks (brand-specific)
        hooks = self._load_workflow_hooks(domain)
        if hooks["pre"]:
            try:
                event = hooks["pre"](event, {"home": self.home, "brand": self.brand, "event_id": event_id}) or event
            except Exception as e:  # noqa: BLE001
                log.error("pre-hook failed for %s: %s", event_id, e)

        # Load factory + run
        try:
            fc = self._load_factory(domain)
        except FileNotFoundError as e:
            log.error(str(e))
            self._fail_event(inflight_path, domain, error=str(e))
            return

        try:
            result = parallel.run_once_parallel(fc, event, mock=self.mock)
        except Exception as e:  # noqa: BLE001
            log.exception("factory run-once failed for %s", event_id)
            self._fail_event(inflight_path, domain, error=str(e))
            return

        # Post-hook
        if hooks["post"]:
            try:
                hooks["post"](result, {"home": self.home, "brand": self.brand, "event_id": event_id})
            except Exception as e:  # noqa: BLE001
                log.error("post-hook failed for %s: %s", event_id, e)

        # Route decision
        try:
            queue_path = review_queue.route_decision(self.home, event_id, domain, result)
            log.info("event %s → %s (%s)", event_id, result.final_action, queue_path)
        except Exception as e:  # noqa: BLE001
            log.exception("review queue write failed for %s", event_id)
            self._fail_event(inflight_path, domain, error=f"review queue: {e}")
            return

        # Write full trace JSON alongside the event
        trace_dir = self.home / "brain" / "memory" / domain / "traces"
        trace_dir.mkdir(parents=True, exist_ok=True)
        (trace_dir / f"{event_id}.json").write_text(trace_mod.to_json(result))

        # Archive event
        completed_dir = self._events_root() / "completed" / domain
        completed_dir.mkdir(parents=True, exist_ok=True)
        shutil.move(str(inflight_path), str(completed_dir / inflight_path.name))

        # Slack digest hook for escalate_supervisor
        if result.final_action == "escalate_supervisor":
            self._notify_escalation(event_id, domain, result)

        self._in_flight = None

    def _fail_event(self, inflight_path: Path, domain: str, *, error: str) -> None:
        failed_dir = self._events_root() / "failed" / domain
        failed_dir.mkdir(parents=True, exist_ok=True)
        target = failed_dir / inflight_path.name
        try:
            shutil.move(str(inflight_path), str(target))
        except Exception:
            pass
        # Also log a .error file alongside
        (failed_dir / f"{inflight_path.stem}.error").write_text(
            f"{datetime.now(timezone.utc).isoformat()}\n{error}\n"
        )

    def _notify_escalation(self, event_id: str, domain: str, result) -> None:
        """Send a Slack DM to the founder for escalated cases.

        v0.9.1: writes a marker file; integration with Slack MCP tool happens
        when the MCP server is running. For now we just log.
        """
        marker_dir = self.home / "events" / "escalations" / domain
        marker_dir.mkdir(parents=True, exist_ok=True)
        (marker_dir / f"{event_id}.txt").write_text(
            f"{datetime.now(timezone.utc).isoformat()}\n"
            f"action: {result.final_action}\n"
            f"rationale: {result.final_rationale}\n"
        )
        log.warning("ESCALATION: %s/%s — %s", domain, event_id, result.final_rationale)

    def run_forever(self) -> None:
        signal.signal(signal.SIGTERM, lambda *_: self._stop())
        signal.signal(signal.SIGINT,  lambda *_: self._stop())

        log.info("factory-runtime daemon starting: home=%s brand=%s poll=%.1fs mock=%s",
                 self.home, self.brand, self.poll, self.mock)
        self._events_root()  # ensure dirs exist

        while not self.stopping:
            try:
                events = self._pending_events()
                for event_path in events:
                    if self.stopping:
                        break
                    self.process_event(event_path)
            except Exception as e:  # noqa: BLE001
                log.exception("daemon loop error: %s", e)
            # Sleep with interruption tolerance
            slept = 0.0
            while slept < self.poll and not self.stopping:
                time.sleep(0.5)
                slept += 0.5

        log.info("daemon stopped cleanly")

    def _stop(self) -> None:
        log.info("stop signal received; finishing in-flight event before exit")
        self.stopping = True


def main() -> int:
    logging.basicConfig(
        level=os.environ.get("OPERAI_LOG_LEVEL", "INFO"),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    ap = argparse.ArgumentParser()
    ap.add_argument("--home",  default=os.environ.get("OPERAI_HOME", "/opt/operai"))
    ap.add_argument("--brand", default=os.environ.get("OPERAI_BRAND", "unknown"))
    ap.add_argument("--poll",  type=float, default=3.0)
    ap.add_argument("--mock-llm", action="store_true")
    args = ap.parse_args()

    d = Daemon(Path(args.home), args.brand, poll_interval_sec=args.poll, mock_llm=args.mock_llm)
    d.run_forever()
    return 0


if __name__ == "__main__":
    sys.exit(main())
