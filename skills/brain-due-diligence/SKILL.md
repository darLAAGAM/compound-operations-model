---
name: brain-due-diligence
description: Run a full due diligence audit of a company Brain (the company or a Compai customer): verify infra claims on the host, measure the execution loop (generators vs consumers), find security/DR/attribution gaps, and output findings by severity + a phased hardening plan. Use when asked to "audit the brain", "due diligence del brain", quarterly brain reviews, or before deploying a Brain to a new company.
tools_needed: brain_search, brain_read, brain_list, brain_health_check, shell_exec (or SSH to host), granola_search, skill_search, brain_write
owner: platform
created: 2026-06-09
created_by: claude-fable-5
validated_on: the company brain DD 2026-06-09 (knowledge/platform/strategy/brain-due-diligence-claude-2026-06-09.md)
---

> _Public, anonymized version of a skill running in the Compai reference deployment (an 8-figure consumer SME). Names, stores, channels and endpoints replaced with placeholders; the logic is unchanged. Adapt to your own context._


# Brain Due Diligence

Audit a company Brain end-to-end: **don't trust the docs — verify on the host**, then judge the system by its *closed loops*, not its ingestion volume.

## Core principle

A Brain has four layers. Audit all four, but weight them by failure cost:

1. **Capture** (sources → raw artifacts) — usually the mature part; don't start here.
2. **Curation/retrieval** (index, canary, hot/cold split) — verify the canary actually covers what the tools advertise.
3. **Protection** (versioning, rollback, attribution, backup, scoping) — verify every claim with commands.
4. **Execution** (context → tasks → actions → closed) — almost always the broken part. The killer metric: **closed-loop rate** = (done + archived-with-reason) / created. Healthy >30%. A Brain that only accumulates is a wiki with extra steps.

## Protocol (5 phases, ~2-3 h)

### Phase 1 — Context (~20 min)
1. Read the handoff/state docs: search `brain_search("brain current state audit handoff")` + read everything `knowledge/platform/strategy/brain-*` from the last 30 days.
2. Read the latest founder/owner conversation about the Brain (granola_search) — the owner's stated bottleneck frames the whole audit.
3. `brain_health_check` + `brain_list(".")` for the raw counts. Red flags: tasks todo:done ratio > 10:1, docs claimed vs indexed mismatch.

### Phase 2 — Host verification (~40 min)
SSH to the host(s) and verify every infra claim. Standard battery:

```bash
# Versioning/rollback (if git-based)
systemctl list-timers --all | grep -Ei "brain|backup"
git -C <brain_root> status --short          # clean?
# mirror heads == repo heads?
tail -20 <change-ledger>.jsonl               # rows complete? actor attribution?
# Attribution quality (the % anonymous is a headline number)
tail -2000 <action-ledger>.jsonl | <count callers/agents/tools>
# Backup reality: WHERE do backups physically live? Same disk = no DR.
# Disk pressure: df -h (a full disk silently kills autocommit)
# The full loop map: systemctl list-timers + crontab -l (who generates, who consumes)
# Task creation rate: ls _tasks/todo | group by date prefix
# Search health: index status, pending embeddings, canary coverage vs tool descriptions
```

Also verify **every sync path between nodes** (rsync/syncthing/git): direction, conflict resolution, attribution, whether it undermines the versioning guarantees. rsync `--update` (newest-mtime-wins) = silent data loss + anonymous writes.

### Phase 3 — Execution-loop forensics (~30 min)
1. Count generators (every cron/timer that *creates* tasks/signals) vs consumers (anything that reads, routes, closes). List them explicitly.
2. Inspect the proactive/outbox queue for **duplicate signals** (same title, different hash, same day) — broken dedupe means the queue is noise.
3. Find the meta-signal: alerts *about* the backlog that go *into* the backlog (e.g. "N tasks older than 7 days" filed as another task). That is the proof the loop is open.
4. Find at least one signal repeated daily for >1 week with no action — name it in the report; it makes the problem concrete for the owner.

### Phase 4 — Security & sensitivity (~20 min)
1. `brain_list("credentials")` and grep for secret-looking md files. Secrets in markdown inside a versioned/synced Brain = P0 (durable history + replicated to every node + readable via MCP without scoping).
2. Attribution: % anonymous callers in the action ledger.
3. Scoping: can any node/employee read finance/HR/sensitive docs? (Test one path.)
4. DR: enumerate what is lost if the primary host disappears entirely.

### Phase 5 — Report + handoff (~40 min)
Write `knowledge/platform/strategy/brain-due-diligence-<actor>-<date>.md` with frontmatter (owner, generated_by, last_verified, stale_after, related_docs) and EXACTLY this structure:

1. **Independent verification table** — claim by claim, PASS/FAIL, evidence.
2. **Findings by severity** — P0/P1/P2, each with verified evidence (numbers, paths, dates). No finding without evidence.
3. **What is solid (do not touch)** — explicit, prevents re-litigating.
4. **Strategic response** — map findings to the owner's stated bottleneck; phased plan (build the consumer first, then wire L3 execution, guardrails in parallel). Include the sequencing rule: *no new ingestion sources until closed-loop rate > 30%*.
5. **Technical hardening plan in lotes** — each lote ≤ 2 days of work, handoff-ready.
6. **Decisions requiring the owner** — only genuine owner decisions (money, irreversible, policy).
7. **Audit limitations** — what you could not verify and why.

Then: synthesize for the owner (TLDR first), and hand the approved lote to the executor (Codex/agent) as a self-contained prompt with verification + documentation requirements built in.

## Severity rubric

- **P0**: data loss possible (single-host backups), secrets exposed, execution layer non-functional (closed-loop ≈ 0), no actor attribution at scale.
- **P1**: versioning/rollback gaps (no batch revert, no alerting, infra unversioned), sync paths that undermine guarantees, search quality silently degraded vs advertised.
- **P2**: health-check noise (self-alerting), root hygiene, stale state docs, missing canonical index policy.

## Anti-patterns
- Auditing only what the handoff asks. The handoff frames; the host decides.
- Reporting infrastructure findings while ignoring that 3,000 tasks have 3 closures. Loop-closure IS the product.
- Findings without numbers ("tasks accumulate" vs "3,017 todo / 3 done, ~180/day since May 26").
- Proposing a rebuild. Brains improve by closing loops, not by re-platforming.
- Printing secret values while reporting a secrets exposure.

## Validated example
the company DD 2026-06-09: `knowledge/platform/strategy/brain-due-diligence-claude-2026-06-09.md` → produced Lote 1 hardening handoff (offsite restic backup, alerting, rollback-range, infra versioning, health-check noise fix, outbox dedupe, backlog bulk-archive) executed by Codex same day.
