# The Compound Operations Model

Open-source AI operations playbook for consumer SMEs, published by Compai.

This repository documents the operating system pattern behind a real 8-figure consumer brand running AI agents in production: company Brain, MCP tools, domain agents, employee onboarding, health audits, shared memory, and controlled action queues.

This is not a SaaS repo. It is an educational implementation portfolio: read it, fork it, adapt it, and keep humans in the approval loop where actions carry risk.

## Current Version

**v2.1 - 9 June 2026**

Latest update: the operational compounding loop from the last month of internal Brain/Swarm work:

- Brain health audits with owner/source/verification/staleness requirements
- Brain inbox sweeper for raw capture triage
- Skill evaluation harness and skillify loop
- Shared memory contract for decisions, tasks, gotchas, tool behavior, workflow state, and raw signals
- L3 action queue pattern for human-approved operational actions
- Workflow mining candidates with owner, metric, approval telemetry, and reversibility checks

## What Is Inside

| Path | Contents |
|---|---|
| `chapters/` | Full public playbook source, including Brain v2 and the June operational loop |
| `kit/` | Starter implementation kit: init CLI, MCP server template, compliance scaffold, onboarding pack, SOUL templates, systemd templates, monitoring scripts |
| `skills/` | Public starter skills for Shopify inventory, Klaviyo, CS triage, payments, and autoresearch |
| `pattern-library/` | Anonymized operational patterns and schema |
| `case-study/` | Anonymized reference case study |

## Start Here

1. Read [`chapters/00-index.md`](chapters/00-index.md).
2. Read the architecture: [`chapters/03-architecture.md`](chapters/03-architecture.md).
3. Read the Brain chapters: [`chapters/10l-brain-v2-living-memory.md`](chapters/10l-brain-v2-living-memory.md) through [`chapters/10r-operational-compounding-loop.md`](chapters/10r-operational-compounding-loop.md).
4. Inspect the implementation kit: [`kit/README.md`](kit/README.md).
5. Use the patterns as a starting point, not as a blind install script.

## Operating Model

The model has four layers:

1. **Brain** - structured company memory, source paths, world model, tasks, outputs, health.
2. **Tools** - MCP interfaces to business systems and operational data.
3. **Agents** - domain-specific agents with clear ownership, tools, and escalation rules.
4. **Compounding loop** - capture, triage, package, queue, audit, and write back.

The key shift is bidirectionality. Agents do not only read the Brain. They write decisions, gotchas, workflow state, and completed work back into the shared memory.

## What Changed Since the Original v1 Repo

The original public repo only contained three introductory chapters. This version publishes the full current playbook and public-safe starter artifacts.

Important corrections:

- Current brand: **Compai**. OperAI was the legacy/internal name.
- Current repo: `darLAAGAM/compound-operations-model`.
- The playbook is no longer just a multi-agent architecture essay. It now includes Brain v2, employee onboarding, setup 1-click, shared memory, health, and workflow mining.
- ROI language now uses the audited 18:1 model from the public playbook, not older 31:1/50:1 marketing claims.

## What Not To Copy Blindly

Do not copy a reference deployment's private data, credentials, Slack channels, Google Workspace accounts, HR records, customer records, or source-system tokens.

Copy the contracts:

- source paths on durable facts
- owner and stale dates on docs
- privacy hard-stops
- human approval for risky actions
- action ledger
- health checks
- explicit escalation rules

## Live Site

- Playbook and dashboard: https://usecompai.com
- Contact: hello@usecompai.com

## License

Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International. See [`LICENSE`](LICENSE).

Commercial usage or implementation help: hello@usecompai.com.
