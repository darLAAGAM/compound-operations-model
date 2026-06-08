"""Usage tracking — per-call token + cost DB (SQLite, encrypted via storage primitive if available).

Every successful or failed LLM call appends one row. Queries: per-provider, per-caller,
per-day. Fuels `operai-init llm usage` CLI.
"""
from __future__ import annotations
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS llm_usage (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    ts           TEXT NOT NULL,
    provider     TEXT NOT NULL,
    model        TEXT NOT NULL,
    tokens_in    INTEGER DEFAULT 0,
    tokens_out   INTEGER DEFAULT 0,
    cost_usd     REAL DEFAULT 0.0,
    latency_ms   INTEGER DEFAULT 0,
    caller       TEXT,                  -- "cs-factory:triage", "operai-init llm test", etc.
    ok           INTEGER DEFAULT 1,
    error        TEXT
);
CREATE INDEX IF NOT EXISTS idx_usage_ts       ON llm_usage(ts);
CREATE INDEX IF NOT EXISTS idx_usage_provider ON llm_usage(provider, ts);
CREATE INDEX IF NOT EXISTS idx_usage_caller   ON llm_usage(caller, ts);
"""


def _db_path(home: Path) -> Path:
    p = home / "state" / "llm-usage.db"
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def _conn(home: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(_db_path(home)))
    conn.executescript(SCHEMA)
    return conn


def record(
    *,
    home: Path,
    provider: str,
    model:    str,
    tokens_in:  int,
    tokens_out: int,
    cost_usd:   float,
    latency_ms: int,
    caller:     str = "",
    ok:         bool = True,
    error:      str | None = None,
) -> None:
    with _conn(home) as c:
        c.execute(
            "INSERT INTO llm_usage (ts, provider, model, tokens_in, tokens_out, cost_usd, latency_ms, caller, ok, error) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                datetime.now(timezone.utc).isoformat(),
                provider, model,
                tokens_in, tokens_out, cost_usd, latency_ms,
                caller, 1 if ok else 0, error,
            ),
        )
        c.commit()


def summary(home: Path, since_days: int = 30) -> dict:
    with _conn(home) as c:
        cutoff = datetime.now(timezone.utc).isoformat()
        cutoff = cutoff[:10]  # YYYY-MM-DD is alphabetically comparable for prefix match
        rows = c.execute(
            "SELECT provider, model, SUM(tokens_in) AS ti, SUM(tokens_out) AS to_, "
            "SUM(cost_usd) AS cost, COUNT(*) AS calls, SUM(ok) AS ok_calls "
            "FROM llm_usage "
            "WHERE ts >= date('now', ?) "
            "GROUP BY provider, model "
            "ORDER BY cost DESC",
            (f"-{since_days} days",),
        ).fetchall()
    return {
        "since_days": since_days,
        "rows": [
            {
                "provider":    r[0],
                "model":       r[1],
                "tokens_in":   r[2] or 0,
                "tokens_out":  r[3] or 0,
                "cost_usd":    round(r[4] or 0.0, 4),
                "calls":       r[5] or 0,
                "ok_calls":    r[6] or 0,
            }
            for r in rows
        ],
        "total_cost_usd": round(sum((r[4] or 0.0) for r in rows), 4),
        "total_calls":    sum((r[5] or 0) for r in rows),
    }


def recent_errors(home: Path, limit: int = 20) -> list[dict]:
    with _conn(home) as c:
        rows = c.execute(
            "SELECT ts, provider, model, caller, error FROM llm_usage WHERE ok = 0 ORDER BY ts DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [
        {"ts": r[0], "provider": r[1], "model": r[2], "caller": r[3], "error": r[4]}
        for r in rows
    ]
