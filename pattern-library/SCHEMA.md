# OperAI Pattern Library — Schema

## What is a Pattern?

A pattern is a reusable operational insight extracted from running AI agents inside a real business. It captures WHAT worked, WHY it worked, and HOW to apply it — without exposing any brand-specific data.

## Pattern Format

```yaml
id: PAT-CS-001
domain: customer-service | inventory | finance | marketing | wholesale | retail | merchandising | hr
type: resolution-template | threshold | timing | workflow | rule | metric-benchmark
confidence: high | medium | low
source_deployments: 1  # how many brands validated this
created: 2026-03-28
updated: 2026-04-02

title: "3-strike payment reminder cadence recovers 40% of overdue B2B invoices"

context: |
  When wholesale accounts go past payment terms, most brands either 
  send one reminder and give up, or escalate to legal too fast.

pattern: |
  Day 7 past terms: friendly reminder (automated, agent sends)
  Day 21 past terms: firm follow-up with statement attached (automated)
  Day 45 past terms: escalation warning — "next step is collections" (human reviews draft)
  
  Recovery rate at each stage: ~25% at Day 7, ~10% at Day 21, ~5% at Day 45.
  Total: ~40% of overdue invoices recovered without legal involvement.

conditions:
  - B2B wholesale with net-30 or net-60 terms
  - Invoice amount €500-€50K
  - Established account (2+ prior orders)

anti_patterns:
  - Sending legal threats before Day 30 — damages relationship, rarely accelerates payment
  - Automated emails only — Day 45 needs human judgment

metrics:
  - recovery_rate: "~40% of overdue invoices"
  - avg_days_to_payment: "reduced from 67 to 34 days"

tags: [wholesale, payments, AR, collections, B2B]
```

## Domain Categories

| Domain | Pattern Types |
|--------|-------------|
| **customer-service** | Resolution templates, escalation rules, response timing, VIP handling |
| **inventory** | Reorder thresholds, stockout prediction, multi-location allocation, size curves |
| **finance** | Payment terms, expense benchmarks, reporting cadences, reconciliation rules |
| **marketing** | Send time optimization, segment definitions, ROAS thresholds, flow triggers |
| **wholesale** | Payment collection, reorder detection, account scoring, margin thresholds |
| **retail** | Staffing ratios, conversion benchmarks, traffic patterns, store comparison |
| **merchandising** | Sell-through targets, markdown timing, category mix, pricing elasticity |
| **hr** | Onboarding sequences, leave management, payroll prep timing, policy templates |
| **operations** | Cron schedules, alert thresholds, sync frequencies, error handling |

## Confidence Levels

| Level | Meaning | Criteria |
|-------|---------|----------|
| **high** | Validated across 3+ deployments or 6+ months in production | Battle-tested |
| **medium** | Validated in 1-2 deployments, 2+ months | Works but needs more validation |
| **low** | Extracted from single deployment, <2 months | Promising but unproven |

## Anonymization Rules

1. NO brand names, domains, or identifiable business names
2. NO employee names — use roles ("the CS lead", "the buyer")
3. NO absolute revenue/financial figures — use % and ratios
4. NO customer names or emails
5. NO location names — use "Store A", "Store B"
6. NO API keys, Notion IDs, or system-specific identifiers
7. YES to: percentages, ratios, timing, workflows, thresholds, templates, rules

## File Structure

```
pattern-library/
├── SCHEMA.md          # This file
├── README.md          # How to use the library
├── extract.py         # Automated extraction pipeline
├── anonymize.py       # Anonymization pipeline  
├── api/
│   └── server.py      # Pattern API server
├── patterns/
│   ├── customer-service/
│   ├── inventory/
│   ├── finance/
│   ├── marketing/
│   ├── wholesale/
│   ├── retail/
│   ├── merchandising/
│   ├── hr/
│   └── operations/
└── stats.json         # Library stats (count, last updated, etc.)
```
