# Chapter 10s: Hardening the Brain — Security, Resilience, and the Execution Loop

## When the demo becomes infrastructure

There is a moment in every brain deployment where the system stops being an experiment and becomes infrastructure. Agents act on it. Finance numbers flow through it. The team trusts it by default. That moment changes your obligations: infrastructure gets audited, versioned, backed up, and access-controlled — or it eventually hurts you.

We hit that moment, and we did what we'd want any vendor to do: we ran a due-diligence audit on our own system. Two lenses at once — an attacker's lens (who can touch this, and what can they do?) and a CFO's lens (is this thing actually producing closed work, or just activity?).

The findings were uncomfortable. We're publishing them anyway, because the fixes are the most portable part.

## What the audit found

**Finding 1 — the execution gap.** Capture had compounded beautifully; closure had not. The task layer held roughly three thousand open items and a single-digit number of completed ones. The brain had become a world-class librarian and a poor operator. If you only measure documents ingested, you will miss this completely.

**Finding 2 — anonymous writes.** 84% of writes to the brain carried no identity: agents, cron jobs, and humans all writing as "anonymous." In a system that agents *act* on, provenance is not a nice-to-have. If you can't answer "who wrote this fact and when," you can't debug a bad decision after the fact.

**Finding 3 — single-point disaster recovery.** Everything lived on one server. Backups existed but had never been restored. A backup you have never restored is a hypothesis, not a backup.

If you run a brain and none of these sound familiar, audit harder.

## Security: the auth maturity ladder

You don't need enterprise IAM on week one. You need a ladder, and you need to know which rung you're on:

- **Level 0 — open.** Anyone with the endpoint can read and write. Fine for a single-founder prototype. Not fine the day an agent can execute anything.
- **Level 1 — protect.** Anonymous callers can read team knowledge but cannot write, execute shell commands, or message agents. This closes the worst hole — remote code execution by strangers — without putting friction on the team. **Close writes before reads.**
- **Level 2 — enforce.** Every human and every machine carries its own token. Sensitive domains (finance, HR, legal) become scoped spaces that only the right identities can read. This is the rung that unlocks deploying beyond your own walls.

Two orderings matter. First: **machine identity before personal identity.** Giving each server, laptop, and agent node its own token is cheap and frictionless — it took our anonymous-write rate from 84% to roughly 13% in a day. Personal tokens involve humans and take longer; don't block on them. Second: **scope sensitive domains before exposing anything externally.** Salary data readable by every employee is a culture decision; readable by every *caller* is an incident.

On secrets: they live in environment variables or keychains, never in markdown, never in the brain itself. Assume the brain will eventually be read by more people and machines than you planned. Rotate anything that ever touched a file.

## Resilience: version everything, back up twice

The brain is now the company's memory. Treat it like one:

- **Git-version the whole thing.** Auto-commit every 15 minutes with a change ledger. This converts "someone overwrote the pricing doc" from a crisis into a `git revert`. Build a rollback tool that can revert a *range* of bad automated writes in one move — when a misbehaving generator floods the brain, you'll want batch undo, not file archaeology.
- **Back up to two destinations.** One on-premise box, one offsite in a different datacenter, both encrypted. Daily, with a 7-day / 4-week / 6-month retention ladder and a weekly integrity check.
- **Verify restores by checksum.** Restore a real file from each destination and diff it against the source. Until you've done this, you don't have backups — you have hope.
- **Alert on two things:** backup failures, and *anomalous change volume*. A mass-deletion looks exactly like a busy day unless something is counting.

None of this is exotic. All of it is the difference between a system you run a company on and a folder of markdown.

## The execution loop: from capture to closure

Here is the uncomfortable physics of operational memory: **ingestion compounds on its own; execution doesn't.** Every pipeline you add writes more, forever. Closing loops takes a human or a very disciplined agent. Left alone, the ratio of captured-to-closed work only gets worse.

What actually moved the needle for us:

- **Backlog hygiene with an anti-boomerang rule.** We bulk-archived stale tasks — roughly two-thirds of the backlog — with a weekly job that re-archives anything that drifts back without an owner. Dead tasks don't just sit there; they bury the live ones.
- **Throttle the generators.** Our context-to-work pipeline ran 24 times a day. We cut it to 2. Nothing was lost except noise. More tasks created is not more work done; past a threshold it's the opposite.
- **A daily triage digest, capped at ten.** Every morning the system scores everything new and sends the founder at most ten actionable items. The first run compressed 116 candidates into 10. Attention is the scarcest resource in the company; the brain's highest-value job is to spend it well, not to demand more of it.
- **Watch your queue depths.** We found two thousand documents sitting unembedded — which means semantic search had been silently degraded for weeks while doc counts looked great. Dashboards should show queues (embedding backlog, outbox, unprocessed captures), not just totals.

## The sequencing rule

After the audit we adopted one rule and wrote it down where every agent can read it:

> **No new ingestion sources and no new generators until the closed-loop rate is above 30%.**

It's deliberately blunt. Adding inputs is fun and feels like progress; closing loops is work and feels like maintenance. The rule exists so that when the next shiny capture pipeline shows up, the system itself reminds you which side of the ledger needs you.

## Porting checklist

- [ ] Run an honest audit twice a year: attacker lens + CFO lens, findings written down.
- [ ] Know your rung on the auth ladder; move to *protect* now, plan *enforce*.
- [ ] Machine tokens per node before personal tokens per human.
- [ ] Scope finance/HR/legal before any external exposure.
- [ ] Git-version the brain with auto-commits and a change ledger; build batch rollback.
- [ ] Two encrypted backup destinations; weekly integrity checks; restores verified by checksum.
- [ ] Alert on backup failure and anomalous change volume.
- [ ] Weekly backlog archive with an anti-boomerang rule.
- [ ] Daily triage digest, hard-capped at ten items.
- [ ] Watch queue depths, not just document counts.
- [ ] Adopt the sequencing rule: no new inputs until loops close.

## For Compai readers

This chapter is the third act of the brain's story. Act one was capture (chapters 10l–10n): get the context in. Act two was the operating cadence (10r): health checks, sweeps, memory contracts. Act three is the one nobody demos on launch day: making the thing safe to depend on, and forcing it to finish what it starts. If you only take one sentence: **the bottleneck moves from context to closure — plan for it before it surprises you.**
