---
name: review-output
description: Use when an output produced by a human/agent needs to be checked, linked back to its task, and moved through review/done.
owner: the company Platform
risk: medium
---

> _Public, anonymized version of a skill running in the Compai reference deployment (an 8-figure consumer SME). Names, stores, channels and endpoints replaced with placeholders; the logic is unchanged. Adapt to your own context._


# Review Output

Use this skill after an agent/human produces a draft, brief, plan, decision, or sent artifact.

## Workflow

1. Read the task card and output.
2. Check whether output satisfies the task and cites/links required sources.
3. Record durable output with `brain_output_record` if not already recorded.
4. If review is pending, call `brain_task_move(..., status="review")`.
5. If accepted, call `brain_task_move(..., status="done")` with review notes.
6. If output created new knowledge, update entity pages or use `brain_learn`.

## Rules

- Outputs without task/source links are incomplete.
- High-risk outputs require human/domain owner review before `done`.
- Prefer concrete review notes over generic approval.
