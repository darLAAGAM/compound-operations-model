---
name: create-task-card
description: Use when captured Brain context needs to become executable work. Creates a task card linked to sources/entities.
owner: the company Platform
risk: low
---

> _Public, anonymized version of a skill running in the Compai reference deployment (an 8-figure consumer SME). Names, stores, channels and endpoints replaced with placeholders; the logic is unchanged. Adapt to your own context._


# Create Task Card

Use this skill when a meeting, Slack thread, capture, or Brain doc contains a concrete next action that should not stay buried in notes.

## Workflow

1. Read the source capture/doc/thread summary.
2. Identify the task, owner, priority, due date if present, source paths, and entity pages.
3. Call `brain_task_create` with:
   - `title`
   - `summary`
   - `source_paths`
   - `entities`
   - `owner`
   - `priority`
   - `due_date`
   - `handoff_prompt`
4. Return the new task path and the next recommended status.

## Rules

- Do not create vague tasks. If no concrete action exists, update the entity/open thread instead.
- Link sources. A task without source context is weak.
- Link entities when possible.
- Handoff prompt must be self-contained enough for Claude/Codex/agent execution.
