# Reference Architecture

## Canonical Topology

OperAI is packaged as seven domain agents plus Claude Code as the founder command center.

- Strategy hub
- Customer service
- Finance
- Retail
- Marketing
- Merchandising
- HR / people ops
- Claude Code command center

## Hosting Pattern

### Primary host
- Linux VPS
- shared brain
- MCP server
- cron layer
- strategy hub / orchestration

### Secondary host
- optional but recommended
- domain agents with isolation
- local services requiring dedicated runtime or session handling

## MCP Transport

- Default: Streamable HTTP
- Legacy fallback: SSE only where compatibility is still required temporarily
- Public endpoint should be stable and documented before onboarding users

## Data Flow Principle

Each system remains source of truth in its own domain.

Agents do not replace Shopify, ERP, analytics, or helpdesk. They orchestrate across them.

## Required Layers

### Execution layer
- agent runtime
- cron schedules
- watchdog / health checks
- audit logging

### Memory layer
- shared brain
- context tree / indexes
- session-to-knowledge distillation
- human-readable operating docs

### Interface layer
- Claude Code for power users
- Slack / email / helpdesk where the team already works
- optional employee AI clients if you standardize them

## Security Defaults

- least privilege per agent
- write actions only where required
- hard escalation rules
- public telemetry must be governed and anonymized

## Deployment Goal

By day 30 you should have a working operating surface, not a pile of prompts.
