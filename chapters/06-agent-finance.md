# Chapter 6: Agent #3 — Finance & Reporting (Finance Agent)

## The CFO That Never Sleeps

Most brands under €20M don't have a CFO. They have a founder who hates spreadsheets, an accountant who comes once a month, and a bookkeeper who's always 3 weeks behind.

The Finance Agent changes this by turning financial data into real-time, actionable intelligence.

## What the Finance Agent Does

### 1. Automated P&L Generation

Every Monday morning at 7:00 AM, the Finance Agent delivers a weekly P&L to the founder's inbox. Not a spreadsheet to interpret — a narrative summary:

> **Week 10 Summary (Mar 3-9, 2026)**
>
> Revenue: +12% WoW, +23% YoY
> - DTC Online: 39% of revenue
> - Wholesale: 32%
> - Store A (flagship): 13%
> - Store B (neighborhood): 9%
> - Department Store: 7%
>
> Gross Margin: 67.8% (target: 67%) ✅
> EBITDA margin: 8.6% — trending toward 10.7% annual target
>
> ⚠️ Flag: Shipping costs +18% vs. last week. Cause: 3PL surcharge for oversized packages (new product collection). Recommend negotiating volumetric pricing.
>
> 🟢 Cash runway: 6+ months at current burn rate.

### 2. Invoice Processing & Reconciliation

- Extracts data from supplier invoices (PDF/email)
- Matches invoices against POs and delivery notes
- Flags discrepancies: "Invoice from Supplier X is higher than PO amount. Possible: extra units shipped?"
- Queues approved invoices for payment

### 3. Cash Flow Forecasting

- Projects 4-week cash flow based on:
  - Historical revenue patterns
  - Known upcoming expenses (rent, salaries, supplier payments)
  - Outstanding wholesale receivables
  - Seasonal adjustments
- Alerts when projected cash drops below safety threshold

### 4. Tax & Compliance Prep

- Tracks all transactions for quarterly VAT filing
- Separates domestic vs. intra-EU vs. international sales
- Prepares data export compatible with accounting software (Xero, QBO, A3)
- Flags transactions that need human review for tax categorization

### 5. Board / Investor Reporting

- Monthly executive summary with KPIs
- Quarterly board deck data preparation
- YoY comparisons, trend analysis, cohort data
- Exportable to Google Slides / Notion

## Configuration Blueprint

### The SOUL.md

```markdown
# Finance Agent — Finance Agent

You are Finance Agent, the financial intelligence agent. Los números son sagrados — nunca inventas uno.

## Mission
Provide accurate, timely, actionable financial data.
Make the founder feel like they have a real CFO.

## Communication Style
- Precise. Numbers always rounded to meaningful precision.
- Contextualized. Never report a number without comparison (WoW, MoM, YoY, vs target).
- Highlight exceptions, not norms. If something is on track, say so briefly. If something is off, explain why and recommend action.
- Use plain language. The audience is a founder, not an accountant.

## Rules
- NEVER make financial decisions autonomously (payments, transfers, investments)
- ALWAYS flag when actual differs from forecast by > 10%
- Revenue recognition: only count when order is fulfilled, not when placed
- Multi-currency: always convert to EUR using daily ECB rate
- Wholesale revenue: recognize on shipment, not on invoice

## Reporting Schedule
- Daily: Quick revenue snapshot (by channel)
- Weekly: Full P&L + narrative (Monday 7AM)
- Monthly: Executive summary + cash flow projection
- Quarterly: Board-ready KPI package
```

### Key Integrations

| Integration | What For |
|------------|---------|
| **Shopify** | Sales data, refunds, discounts |
| **Stripe** | Payment processing, payouts, fees |
| **Google Sheets** | P&L templates, dashboards |
| **Holded** | ERP — invoicing, payment reconciliation, accounting |
| **Payhawk** | Corporate cards, expense tracking, bank statements |
| **Bank feeds** (via accounting software) | Cash position, reconciliation |
| **Stockagile** | COGS data, purchase orders |
| **Google Drive** | Invoice storage, report archive |

## Real Metrics

| Metric | Before | After | Impact |
|--------|--------|-------|--------|
| Time to weekly P&L | 8 hours | 45 minutes | -91% |
| Financial data lag | 2-3 weeks | Real-time | -100% |
| Invoice processing time | 2 days avg | 2 hours | -96% |
| Reconciliation errors/month | 15 | 2 | -87% |
| Cash flow visibility | 1 week ahead | 4 weeks ahead | +300% |

## The Most Valuable Output: Pattern Detection

The real magic isn't in automating reports — it's in seeing patterns humans miss:

- "Wholesale account X has increased payment terms from 30 to 45 days over the last 3 invoices. Flag for relationship review."
- "Shipping cost as % of revenue has increased from 8.2% to 9.7% over 6 weeks. At current trend, this erodes margin significantly over a full year."
- "Revenue from UK customers dropped 22% after the price increase. Other markets unaffected. Consider UK-specific pricing."

These insights exist in the data. Humans just don't have time to look for them.



### Advanced Capabilities (Production)

**Zero-Touch Invoice Pipeline**
The finance agent scans email inboxes daily and automatically:
1. Detects PDF invoice attachments using content heuristics (keywords: factura, IVA, CIF)
2. Extracts 16 structured fields (provider, tax ID, base amount, VAT, due date, etc.)
3. Classifies by category (supplier, utilities, services, etc.)
4. Uploads to Google Drive in organized month/sender folders
5. Logs to a reconciliation tracking spreadsheet
6. First batch: 117 invoices auto-processed from 2 months of email backlog. Zero manual data entry.

**Bank Credit Line Monitoring**
Monitors multiple bank credit lines (confirming, factoring, export instruments) by reading from a live spreadsheet:
- Daily alerts if amortizations are due within 48 hours
- Weekly summaries on Mondays
- Monthly overviews on the 1st
- Color-coded urgency levels
- Prevents missed payments that could affect credit relationships

**Multi-Currency Treasury Visibility**
Real-time view across multiple bank accounts in 6+ currencies (EUR, USD, GBP, CAD, HKD, JPY):
- OAuth2 JWT integration with banking APIs
- PayPal Business transaction data
- Accounting system treasury module
- All accessible by the agent for cash position queries in natural language

**Profitability Engine**
Goes beyond revenue reporting to calculate actual per-product profitability:
- Cross-references 9 live APIs (ecommerce, accounting, inventory, advertising)
- Calculates CM3 (Contribution Margin 3) per product
- Integrates cost data from inventory management with revenue and ad spend
- Provides true margin visibility, not just top-line numbers

## Implementation Checklist

- [ ] Map all revenue sources and their data APIs
- [ ] Define chart of accounts (simplified for agent use)
- [ ] Create P&L template in Google Sheets
- [ ] Connect Shopify, Stripe, and accounting software
- [ ] Set up invoice inbox (dedicated email for suppliers)
- [ ] Define reporting schedule and recipients
- [ ] Run parallel with manual reporting for 1 month
- [ ] Validate accuracy, calibrate categorization rules
- [ ] Go live with automated reporting
- [ ] Add cash flow forecasting once 3 months of data collected

---

*Next: [Chapter 7 — Agent #4: Marketing & Email →](07-agent-marketing.md)*
