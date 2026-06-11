---
name: check-brain-health
description: Use to audit Brain execution hygiene: loose captures, raw/source gaps, outputs without tasks, and tasks stuck in review.
owner: the company Platform
risk: low
---

> _Public, anonymized version of a skill running in the Compai reference deployment (an 8-figure consumer SME). Names, stores, channels and endpoints replaced with placeholders; the logic is unchanged. Adapt to your own context._


# Check Brain Health

Use this skill before/after Brain v2 ingestion or weekly digest work.

## Workflow

1. Call `brain_health_check(write_report=true)`.
2. Read the returned counts and report path.
3. Prioritize issues:
   - captures without entities,
   - outputs without tasks,
   - raw files without capture references,
   - tasks stuck in review.
4. Convert repeated issues into task cards or skill candidates.

## Rules

- Health is not a vanity metric. The goal is fewer loose notes and more reusable execution context.
- Do not bulk-fix by deleting. Link, process, or archive intentionally.
