---
name: log-capability-gap
description: Use when an agent or human cannot complete work because the company lacks data, tool access, permission, skill, process, or context.
owner: the company Platform
risk: low
---

> _Public, anonymized version of a skill running in the Compai reference deployment (an 8-figure consumer SME). Names, stores, channels and endpoints replaced with placeholders; the logic is unchanged. Adapt to your own context._


# Log Capability Gap

Use this skill when execution fails or stalls due to missing capability.

## Workflow

1. State the attempted task clearly.
2. Classify the missing type: `data`, `tool`, `permission`, `skill`, `process`, `context`, or `other`.
3. Estimate business impact in one concrete paragraph.
4. Suggest owner/DRI.
5. Call `brain_capability_gap`.
6. If it creates a task, include the task path in your response.

## Rules

- Do not hide failures in chat history.
- A gap should be specific enough to resolve.
- If the gap is sensitive/security-related, keep details redacted and mark risk high.
