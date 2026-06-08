# Chapter 00c: Downloadable Artifacts Index

## What the repo gives you

The playbook is the explanation. The artifacts are the parts you can fork.

The public repository should live under a neutral namespace before launch. It is published as open educational infrastructure: free to use, attribution requested. That means you can copy the templates, adapt the prompts, rewrite the skills, and use the schemas inside your own company. If you publish derivative work, attribution is requested. There is no warranty.

This chapter is the navigation layer for the downloadable pieces.

## Folder map

```text
docs/
  The essay-style playbook chapters.

templates/
  Starting documents and checklists you can copy into your own brain.

skills/
  Executable procedures written as markdown contracts.

prompts/
  Reusable prompt files for decision tools, extraction, review, and agents.

patterns/
  Anonymized operational patterns and the schema used to store them.

integrations/
  Stack maps and integration notes for ecommerce, finance, helpdesk, ads,
  analytics, Google Workspace, inventory, logistics, and team chat.

lessons/
  Production failure ledger and incident-learning records.
```

The repo is deliberately boring. Markdown files are easier to inspect, diff, fork, and adapt than a locked SaaS workspace.

## Templates

Templates are the fastest starting point for non-technical operators.

| Artifact | Use it when | What to change first |
|---|---|---|
| `templates/brain-starter/` | You are creating your first company brain | Company profile, systems map, returns, shipping, brand voice |
| `templates/autonomy-assessment.md` | You need to map what AI can safely do | Capability list, current level, approval owner |
| `templates/profit-throttle-calculator.md` | You want dynamic paid-media break-even logic | Margin inputs, returns, logistics, payment fees, profit floor |
| `templates/learn-skill-template.md` | You want a repeatable way to capture learnings | Categories, routing rules, review cadence |
| `templates/dashboard-data-spec.md` | You are building or auditing a live dashboard | Source systems, freshness, caveats |
| `templates/calendar-taxonomy.md` | You want a native operational calendar | Event streams, naming convention, owner |

Do not fill every template on day one. Pick the one tied to an active pain. A food brand with recurring batch-expiry issues should start with calendar taxonomy. A pet subscription brand drowning in support tickets should start with the brain starter and policy docs. A home brand spending heavily on paid acquisition should start with the profit throttle.

## Skills

Skills are procedures an AI client can run. A good skill has a trigger, required inputs, steps, output format, guardrails, and escalation rules.

Current starter artifacts include:

| Artifact | Use it when |
|---|---|
| `skills/invoice-pipeline.md` | You want to turn finance inbox PDFs into structured review rows |

The pattern is more important than the specific skill. You can write a skill for refund triage, weekly trading notes, purchase-order checks, supplier-delay escalation, product copy review, retail event prep, or warranty classification. The skill should read like a contract, not a motivational memo.

## Prompts

Prompts are useful when the workflow is still human-supervised.

| Artifact | Use it when |
|---|---|
| `prompts/council-query.md` | You want six operating perspectives to examine a decision |
| `prompts/punta-de-flecha.md` | You need adversarial cross-model review |
| `prompts/invoice-extract.md` | You need structured fields from invoice text |

Prompts should not pretend to be autonomy. They are a way to create consistency before you have a full tool or agent.

## Patterns

Patterns are anonymized lessons that can travel across companies.

| Artifact | Use it when |
|---|---|
| `patterns/_schema.yaml` | You want a strict format for reusable patterns |
| `patterns/customer-service-tracking.yaml` | You handle repeated “where is my order” questions |
| `patterns/finance-invoice-intake.yaml` | You process supplier invoices from email |
| `patterns/marketing-margin-throttle.yaml` | You need spend decisions tied to margin |

Patterns should never include brand names, employee names, precise revenue numbers, customer personal data, or location identifiers. Ratios, thresholds, workflow shape, and failure modes are the portable parts.

## Integrations

The integration folder should be read as roles, not vendor endorsements.

| Artifact | Use it when |
|---|---|
| `integrations/_stack-map.md` | You need to understand which category each tool occupies |

You do not need Shopify specifically. You need an ecommerce source of truth. You do not need one named helpdesk. You need a place where customer conversations can be read, classified, and drafted against. The stack map keeps that distinction clear.

## Lessons

The lessons folder is the antidote to polished case studies.

| Artifact | Use it when |
|---|---|
| `lessons/_ledger.md` | You want the one-line version of production failures and fixes |

Read lessons before building. The fastest way to waste time is to repeat known failures: shared OAuth tokens, stale memory, missing environment variables in cron, event-loop collisions, and dashboards with undefined metrics.

## How to fork

1. Open the public repository once the neutral namespace is live.
2. Fork it into your own GitHub account or copy the folders you need.
3. Start from `templates/brain-starter/`, not from the whole playbook.
4. Rename generic examples into your own domains: product, operations, finance, marketing, customer, retail/channel, people.
5. Keep your company-specific copy private unless you deliberately publish anonymized patterns back.

## How to contribute back

Contribute back only what can be shared safely:

- A better template.
- A generic prompt.
- A vendor integration note with no credentials or sensitive paths.
- An anonymized pattern with ratios instead of raw numbers.
- A production lesson with no employee, customer, or brand identifiers.

The strongest contribution is usually a failure note. “This broke because the API paginated silently” helps more operators than another polished diagram.

## How to start this in your business

1. Fork the repo and copy only `templates/brain-starter/`, `templates/autonomy-assessment.md`, and one skill or prompt tied to an immediate workflow.
2. Create a private branch for your company-specific edits. Never put customer data, credentials, employee records, or raw financials in a public fork.
3. Assign one owner per artifact folder: templates, skills, prompts, integrations, patterns, lessons.
4. After 30 days, contribute back one anonymized improvement: a corrected checklist, schema field, or production lesson.
5. Use this chapter as the index artifact; the canonical navigation remains the GitHub repo.

