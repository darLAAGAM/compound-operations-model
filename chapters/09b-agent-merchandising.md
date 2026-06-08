# Chapter 9b: Agent #7 — Merchandising & Assortment (Merchandising Agent)

## The Agent That Speaks Buyer

Every other agent in this playbook operates downstream — after the product exists, after the inventory is allocated, after the customer shows up. The Merchandising Agent operates upstream: **what to buy or produce, how much, which variant mix, where to put it, when to replenish, and when to mark it down.**

For consumer brands, merchandising decisions drive everything. Buy too much → markdowns destroy margin. Buy too little → stockouts kill revenue. Allocate wrong → one city sells out while the other sits. React late to sell-through signals → the season is over before you adjust.

Most brands under €20M do this in spreadsheets. The Merchandising Agent turns those spreadsheets into a living intelligence system.

## What the Merchandising Agent Does

### 1. Sell-Through Analysis

The core of merchandising intelligence: how fast is each product selling, and what does that mean?

- **Daily sell-through tracking** by SKU, category, and channel
- **Velocity alerts:** "SKU-2847 Product X is selling 3x forecast in DTC. At current rate, stockout in 8 days. Store B has 14 units sitting — recommend transfer."
- **Category performance:** "Category A is 22% behind plan at Week 6. Category B is 15% ahead. For another vertical, that might be cleanser vs serum, kibble flavor vs treat, candle scent vs diffuser, or tent model vs accessory pack. Consider reallocation of open-to-buy."
- **Channel comparison:** Same product can sell completely differently online vs. in-store. The agent tracks this and flags divergence.

### 2. Allocation Optimization

Deciding where inventory should go across your channels:

- **Initial allocation** based on historical sell-through by location, season, and category
- **Replenishment recommendations:** "Store A converts Product X at 2x the rate of Store B. Shift 8 units accordingly."
- **Channel priority:** When stock is limited, who gets it? DTC (higher margin), wholesale (committed orders), or retail (foot traffic driven)?
- **Pre-order management:** When Shopify shows negative stock, the agent flags it as pre-order status and monitors delivery timeline to set customer expectations.

### 3. Pricing & Markdown Intelligence

- **Margin tracking** by product, category, and channel
- **Markdown trigger detection:** "Product X has been at 40% sell-through for 4 weeks. At this trajectory, 35% of inventory will remain at end of season. Recommend 20% markdown to accelerate."
- **Competitive price monitoring:** Tracks how key competitors price similar categories
- **Wholesale vs. DTC pricing alignment:** Ensures wholesale pricing (typically 2.5-2.8x markup from cost) doesn't undercut or create channel conflict

### 4. Assortment Planning Support

While final buying decisions are human judgement (taste, trends, relationships), the agent provides the analytical foundation:

- **Historical performance by category, variant, format, color, flavor, scent, model, bundle, pack size, and price point**
- **Variant distribution analysis:** "Your standard variant mix is 5% off from actual demand. In fashion that might be size. In beauty it might be shade or scent. In food it might be flavor or pack size. In outdoor it might be model or capacity. The agent flags the consistently understocked variant before it becomes a stockout."
- **Seasonality patterns:** What sold when, and how does that inform next season's buy
- **Supplier lead time tracking:** Time from PO to warehouse, by supplier, trending over time

### 5. Inventory Health Scoring

A weekly scorecard that tells you the truth about your stock:

| Metric | What It Measures | Target |
|--------|-----------------|--------|
| Weeks of Supply (WOS) | How many weeks current stock will last at current velocity | 8-12 |
| Sell-Through Rate | % of initial buy sold to date | On plan |
| DIO (Days Inventory Outstanding) | Average days a unit sits before selling | < 90 |
| Stock-to-Sales Ratio | Current stock ÷ trailing 4-week sales | 2.5-4.0 |
| Markdown Risk | Units likely to need discounting to clear | < 15% |

## Configuration Blueprint

### The SOUL.md

```markdown
# Merchandising Agent — Merchandising Agent

You are Merchandising Agent, the merchandising and assortment intelligence agent.

## Mission
Maximize full-price sell-through and gross margin through
data-driven allocation, pricing, and inventory optimization.

## Communication Style
- Buyer's language: sell-through, OTB, WOS, DIO — not tech jargon
- Always compare to plan: actual vs. forecast, this year vs. last year
- Think in seasons and drops, not quarters
- Lead with the commercial implication, then the data

## Decision Authority
- Sell-through reporting: autonomous
- Allocation recommendations (store-to-store transfers): recommend
- Markdown recommendations: recommend with margin impact analysis
- variant distribution adjustments: recommend with data
- Buying decisions: NEVER autonomous — provide analysis for human buyer
- Price changes: NEVER autonomous — flag for merchandising lead

## Escalation Triggers
- Sell-through below 30% at midseason for any major category
- Single SKU representing >15% of category stock with <10% sell-through
- Margin below target by >3 percentage points for any channel
- Variant stockout on a top-10 seller (size, shade, scent, flavor, model, bundle, or pack)

## Key Stakeholders
- Buyer/Head of Merchandising (primary)
- Ecommerce lead (DTC allocation)
- Retail manager (store allocation)
- Finance (margin reporting)
```

### Key Integrations

| Integration | What For |
|------------|---------|
| **Shopify** | Product catalog, online sales, variant-level stock |
| **Stockagile** | Multi-warehouse inventory, purchase orders, transfers |
| **Amphora (3PL)** | Fulfillment stock levels, inbound tracking |
| **Google Sheets** | OTB planning sheets, buying budgets |
| **Shopify POS** | Store-level sales data for allocation |

## Real Metrics

| Metric | Before | After | Impact |
|--------|--------|-------|--------|
| Time to weekly sell-through report | 5 hours | 20 minutes | -93% |
| Allocation accuracy (units in right location) | ~60% | ~82% | +37% |
| End-of-season residual stock | 28% | 19% | -32% |
| Full-price sell-through | 61% | 72% | +18% |
| Manual hours/week on merch reporting | 12+ | 2 | -83% |

## Why This Agent Pays for Itself

The math is brutal: a 1% improvement in full-price sell-through on a €5M brand = €50,000 in preserved margin. A 5-point reduction in end-of-season residual = €75,000+ in avoided markdowns.

The Merchandising Agent doesn't make taste decisions. It doesn't pick next season's variant palette. What it does is make sure the products your buyer chose are in the right place, at the right time, at the right price — and that you know exactly what's working before it's too late to react.

Most brands discover sell-through problems 3-4 weeks late because nobody has time to run the reports. This agent runs them daily.

## Implementation Checklist

- [ ] Map all product categories and their hierarchy (department → category → subcategory)
- [ ] Connect Shopify for online sales and product data
- [ ] Connect Stockagile/inventory system for multi-location stock
- [ ] Define sell-through targets by category and season
- [ ] Import last season's data for baseline comparison
- [ ] Configure allocation rules (channel priority, minimum stock levels)
- [ ] Set up weekly inventory health scorecard
- [ ] Build variant distribution analysis from historical data
- [ ] Run in reporting-only mode for 4 weeks
- [ ] Enable allocation recommendations after calibration

---

*Next: [Chapter 10 — The Stack: What We Use and Why →](10-stack.md)*
