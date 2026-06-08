# Chapter 8: Agent #5 — Wholesale & B2B (Finance Agent — Dual Role)

> **Optional chapter.** Wholesale and B2B operations are not universal in consumer SMEs. If your business is purely DTC, you can skip this. If you have wholesale partners, distributors, or marketplaces, this chapter applies directly. The same pattern (an agent for partner-facing operations) generalizes to anyone who deals with B2B customers.

## The Most Underserved Area in Consumer AI

Everyone talks about DTC. Nobody talks about wholesale — even though for many consumer brands, it's 25-40% of revenue.

A typical brand in this model does 25-35% of revenue through wholesale. That's 50+ retail accounts across Europe, each with their own ordering cadence, payment terms, delivery requirements, and communication preferences.

Managing this manually requires a dedicated person (or team). Managing it with AI requires understanding the unique workflows of B2B consumer brand.

> **Production note:** In a production deployment, wholesale operations are managed by Finance Agent — the same agent that handles finance. This makes sense because the same person (the finance manager) oversees both domains, and wholesale is heavily invoice/payment-driven. The architecture supports this dual-role pattern: one agent, two domain sections in its SOUL.md.

## What the Wholesale Agent Does

### 1. Order Processing

When a buyer places an order (usually via email, PDF linesheet, or B2B portal):

1. Agent extracts order details (styles, sizes, quantities, delivery date)
2. Checks availability against production calendar and allocated stock
3. Generates order confirmation with delivery timeline
4. Creates draft invoice
5. Syncs with Ops Agent for fulfillment scheduling
6. Sends confirmation to buyer

**Before:** 2.5 days average processing time
**After:** 4 hours, with human review only for large orders (>€10K)

### 2. Buyer Communication

B2B relationships require consistent, professional communication. The agent handles:

- Order status updates (proactive, not reactive)
- Delivery delay notifications (with new ETAs)
- Payment reminders (graduated: friendly → firm → final)
- Season preview invitations
- Reorder suggestions based on sell-through data

### 3. Linesheet Generation

- Generates digital linesheets from product catalog
- Customizes per buyer/market (pricing, currency, available styles)
- Includes product imagery, descriptions, and wholesale pricing
- Updates automatically when new products are added or prices change

### 4. Payment Tracking

- Tracks outstanding invoices by account
- Calculates days outstanding vs. agreed terms
- Flags overdue accounts: "Buyer X is 15 days past 30-day terms on €4,200 invoice"
- Generates accounts receivable aging report weekly

### 5. Account Intelligence

- Tracks reorder patterns by account
- Identifies growth/decline trends: "Account Y ordered 30% less this season — schedule check-in"
- Ranks accounts by revenue, reliability, and growth potential
- Suggests optimal allocation when stock is limited

## Configuration Blueprint

### The SOUL.md

```markdown
# Wholesale Agent — Finance Agent (Dual Role with Finance)

You are the wholesale and B2B operations agent.

## Mission
Manage wholesale accounts with the professionalism
and attentiveness of a dedicated account manager.

## Communication Style
- Professional and warm. These are long-term relationships.
- Proactive: inform buyers before they need to ask.
- Always include specific order/invoice references.
- Multilingual: communicate in buyer's preferred language.

## Decision Authority
- Order confirmation (standard terms, stock available): autonomous
- Delivery date changes (< 5 days shift): autonomous, notify buyer
- Delivery date changes (> 5 days): escalate to human
- Payment reminders (first and second): autonomous
- Payment escalation (legal/collections): always escalate to human
- New account setup: always escalate to human
- Discount/special terms: always escalate to human

## Rules
- Never promise delivery dates without checking production + logistics
- Always confirm stock allocation before confirming order
- Payment terms are per-account (check account record)
- Large accounts (>€50K/season) get priority allocation
- Communicate delivery issues BEFORE the buyer's shipping window
```

### Key Integrations

| Integration | What For |
|------------|---------|
| **Email** | Buyer communication, order receipt |
| **Shopify / ERP** | Product catalog, pricing, order management |
| **Google Sheets** | Order tracking, linesheet data |
| **Stockagile** | Stock allocation, production calendar |
| **Accounting** | Invoice generation, AR tracking |

## Real Metrics

| Metric | Before | After | Impact |
|--------|--------|-------|--------|
| Order processing time | 2.5 days | 4 hours | -83% |
| Payment collection (% on time) | 72% | 89% | +24% |
| Buyer response time | 24 hours | 2 hours | -92% |
| Manual hours/week on wholesale | 15+ | 3 | -80% |
| Missed reorder opportunities | ~8/season | ~2/season | -75% |

## Why This Agent Is Underrated

The wholesale agent might seem less sexy than the CS or Marketing agents, but consider this:

- One missed wholesale order can cost €5,000-50,000
- One late delivery can damage a multi-year retail relationship
- One forgotten payment reminder can mean €10K+ sitting in AR for months
- Consistent, proactive communication turns one-season buyers into multi-year partners

In this deployment, the wholesale agent paid for the entire AI operations system in its first month — by recovering several overdue payments that had simply been forgotten in the chaos of manual management.

## Implementation Checklist

- [ ] Map all wholesale accounts with contact info, terms, history
- [ ] Set up order intake workflow (email parsing or B2B portal)
- [ ] Define order confirmation templates per market/currency
- [ ] Configure payment terms per account
- [ ] Build linesheet template from product catalog
- [ ] Set up AR tracking and reminder schedules
- [ ] Connect to production calendar for delivery date accuracy
- [ ] Run in shadow mode for first order cycle
- [ ] Calibrate based on buyer feedback
- [ ] Go live with standard order processing autonomy

---

*Next: [Chapter 9 — Agent #6: Retail & Physical Stores →](09-agent-retail.md)*
