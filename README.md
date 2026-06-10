# The Compound Operations Model

Open-source AI operations playbook for consumer SMEs, published by Compai.

[![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-c9a667.svg)](LICENSE)
[![Built in public](https://img.shields.io/badge/built-in%20public-1a1a1a.svg)](https://usecompai.com)
[![Playbook](https://img.shields.io/badge/playbook-53%20chapters-1a1a1a.svg)](https://usecompai.com/playbook)
[![PRs welcome](https://img.shields.io/badge/PRs-welcome-c9a667.svg)](CONTRIBUTING.md)

> **The operating system behind an 8-figure consumer brand running on AI for €352/month.** Read it. Fork it. Build your own.



This repository documents the operating system pattern behind a real 8-figure consumer brand running AI agents in production: company Brain, MCP tools, domain agents, employee onboarding, health audits, shared memory, and controlled action queues.

This is not a SaaS repo. It is an educational implementation portfolio: read it, fork it, adapt it, and keep humans in the approval loop where actions carry risk.

## Current Version

**v2.2 - 10 June 2026**

Latest update: hardening the brain. We ran a due-diligence audit on our own system and published the findings and fixes as [`chapters/10s-hardening-the-brain.md`](chapters/10s-hardening-the-brain.md):

- The auth maturity ladder: open -> protect -> enforce, machine identity per node (anonymous writes 84% -> ~13%)
- Resilience: git-versioned brain (15-min auto-commits + change ledger), dual encrypted backups, checksum-verified restores, batch rollback
- The execution loop: backlog hygiene with anti-boomerang archiving, throttled generators, a daily triage digest hard-capped at 10 items
- The sequencing rule: no new ingestion sources until the closed-loop rate is above 30%

v2.1 (9 June 2026) added the operational compounding loop (`10r`): health audits, inbox sweeper, skill eval harness, skillify loop, shared memory contract, L3 action queues, and workflow mining.

## What Is Inside

| Path | Contents |
|---|---|
| `chapters/` | Full public playbook source (53 chapters), including Brain v2, the operational loop, and brain hardening |
| `kit/` | Starter implementation kit: init CLI, MCP server template, compliance scaffold, onboarding pack, SOUL templates, systemd templates, monitoring scripts |
| `skills/` | Public starter skills for Shopify inventory, Klaviyo, CS triage, payments, and autoresearch |
| `pattern-library/` | Anonymized operational patterns and schema |
| `case-study/` | Anonymized reference case study |

## Start Here

1. Read [`chapters/00-index.md`](chapters/00-index.md).
2. Read the architecture: [`chapters/03-architecture.md`](chapters/03-architecture.md).
3. Read the Brain chapters: [`chapters/10l-brain-v2-living-memory.md`](chapters/10l-brain-v2-living-memory.md) through [`chapters/10s-hardening-the-brain.md`](chapters/10s-hardening-the-brain.md).
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

## Community

This is built in public, and it's meant to be copied. The best thing you can do is fork it, run it, and tell us what happened.

- **Share what you built** — [open a showcase issue](../../issues/new?template=share-what-you-built.md). We keep a public list of real deployments.
- **Improve the playbook** — fixes, clarifications, validated patterns, translations. See [CONTRIBUTING.md](CONTRIBUTING.md).
- **Ask a question** — [open a question](../../issues/new?template=question.md) if a chapter left you stuck.
- **Report a bug** — [bug report](../../issues/new?template=bug-report.md). Security issues go to [SECURITY.md](SECURITY.md), not public issues.

Be useful and be kind: [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## License

Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International. See [`LICENSE`](LICENSE).

Commercial usage or implementation help: hello@usecompai.com.
