# Chapter 10f: The Pattern Library — The Compounding Layer

## The problem with isolated deployments

Every company learns the same operational lessons in private.

A beauty brand learns that shade-match tickets should be classified before refund policy is applied. A food brand learns that delivery complaints spike when cold-chain tracking is delayed. A home brand learns that replacement-part requests need order lookup and assembly-step diagnosis. A pet brand learns that sizing exchanges require breed and measurement context. An outdoor brand learns that warranty triage needs use-case classification before goodwill decisions.

The details differ. The pattern often repeats.

The Pattern Library is where those repeatable lessons go after anonymization. It is the compounding layer across deployments.

## What a pattern is

A pattern is not a case study. It is a reusable operating rule.

It should answer:

- What situation triggers this?
- What workflow works?
- What evidence supports it?
- What threshold or rule matters?
- Where does it not apply?
- What data is required?
- What should be anonymized?

Example:

```yaml
pattern_id: customer-service-tracking-resolution
domain: customer_service
confidence: high
trigger: Customer asks where an order is after fulfillment
mechanism: Query ecommerce order status and logistics tracking in parallel
rule: Auto-draft when both systems agree and tracking URL is available
human_review: Required when status differs, parcel is stalled, or customer is VIP
evidence: Tested across repeated tracking inquiries
limitations: Does not apply to custom, pre-order, or wholesale shipments
```

That pattern can help a beauty brand, a food brand, a pet brand, or a home brand because “where is my order” is not vertical-specific.

## Current shape

The reference system documents 21 patterns across 9 domains. The exact number will change. The important structure is:

```text
patterns/
  _schema.yaml
  customer-service-tracking.yaml
  finance-invoice-intake.yaml
  marketing-margin-throttle.yaml
  ...
```

The internal service exposes patterns through a small REST API on port `18830`:

```text
GET  /patterns
GET  /patterns/{domain}
GET  /stats
POST /patterns/contribute
```

You do not need the API to start. A folder of YAML files is enough. The API matters once multiple agents or multiple deployments need to fetch patterns consistently.

## The YAML schema

A pattern should be strict enough to be useful:

```yaml
pattern_id: string
title: string
domain: customer_service | finance | marketing | operations | merchandising | retail | people | platform | governance
summary: string
trigger: string
context: string
mechanism:
  - step: string
data_required:
  - source: string
rule: string
confidence: low | medium | high
evidence: string
limitations:
  - string
anonymization:
  removed:
    - brand_names
    - employee_names
    - customer_data
    - absolute_financials
reuse_notes: string
```

The repo includes the canonical schema at `patterns/_schema.yaml` plus three sample anonymized patterns.

## Anonymization rules

The Pattern Library only works if it is safe to share.

Rules:

- No brand names.
- No employee names.
- No customer personal data.
- No raw order IDs, invoice IDs, or ticket IDs.
- No exact revenue, margin, payroll, or cash figures.
- No precise location identifiers.
- No supplier names unless already public and explicitly allowed.
- Use ratios, ranges, thresholds, and workflow shape.

Bad pattern:

```text
Store X in Barcelona loses money under €4,200 daily sales.
```

Better pattern:

```text
Small retail locations should alert when contribution after staffing
falls below the weekly floor for three consecutive trading days.
```

The second version travels. The first leaks.

## Weekly auto-extraction

The compounding loop:

1. Read recent memory, incidents, audits, and review queues.
2. Detect repeated workflows, bugs, thresholds, or decisions.
3. Draft candidate patterns.
4. Strip identifiers and sensitive numbers.
5. Route to a human reviewer.
6. Promote accepted patterns into `patterns/`.
7. Serve patterns back to agents and new deployments.

Do not skip human review. Pattern extraction can overfit. A one-off workaround is not a pattern. A lucky campaign result is not a pattern. A workflow that worked because one employee had private context is not a pattern until the context is written down.

## The G-Brain thesis in practice

The strategic thesis is simple: every deployment should make the next deployment better.

The company brain captures private operating context. The Pattern Library captures portable operating intelligence. Together, they avoid the blank-page problem.

A new food brand should not inherit another company's supplier names, margin data, or customer list. It can inherit the pattern “batch-expiry events need native calendar visibility and escalation before sell-by date.” A new home brand should not inherit private warranty tickets. It can inherit the pattern “replacement-part triage needs product version, purchase date, photo evidence, and assembly-step classification before refund.”

That is compounding without data leakage.

## How agents consume patterns

Patterns should not sit in a folder waiting for a human to remember them. Agents should retrieve them when doing work.

Examples:

- A customer-service agent handling a delayed parcel searches the customer-service patterns before drafting.
- A finance agent processing invoices loads the invoice-intake pattern before deciding whether a low-confidence extraction can move forward.
- A marketing agent reviewing spend loads the margin-throttle pattern before recommending a budget change.
- An operations agent investigating stockouts loads replenishment and lead-time patterns before blaming demand.

The agent should cite the pattern it used. This keeps the process inspectable:

```text
Applied pattern: marketing-margin-throttle
Reason: budget change requested while marginal MER is below dynamic break-even.
Action: recommend hold, not scale.
```

This is the difference between “AI remembered something vaguely” and “AI applied a reviewed operating pattern.”

## Pattern quality control

Bad patterns are worse than no patterns because they give poor decisions institutional authority.

Review candidates against five tests:

1. **Repeatability:** has this happened more than once?
2. **Portability:** can it apply outside the original context?
3. **Evidence:** is there data, incidents, or repeated review behind it?
4. **Boundaries:** does it say where it does not apply?
5. **Anonymization:** has sensitive context been removed?

If a candidate fails repeatability, keep it as a lesson. If it fails portability, keep it as company knowledge. If it fails evidence, keep it as low confidence. If it fails anonymization, do not share it.

## Limitations

Patterns are not laws. A workflow validated in a high-AOV home brand may fail in low-AOV consumables. A pet subscription pattern may not apply to one-time outdoor purchases. A customer-service threshold may depend on carrier reliability, language, and local regulation.

Confidence should reflect evidence. Most new patterns should start as medium or low. Promote them only after repeated use.

## How to start this in your business

1. Create `patterns/` with `_schema.yaml` and three seed patterns: one CS, one finance, one marketing or ops.
2. After every incident or repeated workflow, ask: is this a reusable pattern, a company-specific rule, or just noise?
3. Write patterns using triggers, mechanisms, evidence, confidence, and limitations. Remove sensitive details immediately.
4. Run a weekly 30-minute review to promote or reject candidate patterns from memory.
5. Fork `patterns/_schema.yaml` and the three sample anonymized patterns as the artifact.
