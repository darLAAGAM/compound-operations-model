# Chapter 9a: Agent #6 — Retail & Physical Stores (Retail Agent)

## Bridging the Online-Offline Divide

If your brand has offline locations, pop-ups, counters, concessions, showrooms, clinics, tastings, workshops, or partner locations, you have a data problem: your online world is tracked to the pixel, while offline demand is usually a black box.

The Retail Agent connects physical store data to the rest of your operations, turning offline locations from cost centers into measurable, optimizable channels.

## What the Retail Agent Does

### 1. Foot Traffic Analytics

Using TC Analytics (or similar people-counting systems):
- Daily traffic reports per store
- Conversion rate: visitors → purchases
- Peak hours identification
- Day-of-week and seasonal patterns
- Correlation with weather, events, and marketing campaigns

**Example insight:** "Location A traffic dropped 22% on Tuesday. Weather was 38°C. Pattern: traffic drops 15-25% when temp exceeds 35°C. Consider shifting Tuesday marketing budget to online, moving the workshop time, or changing staff coverage."

### 2. Store Performance Scoring

Weekly performance card per store:

| Metric | Store A (flagship) | Store B (neighborhood) | Target |
|--------|----------|----------|--------|
| Conversion | 8.2% | 7.1% | 8% |
| Avg. Transaction Index | 1.01x | 1.09x | 1.00x |
| UPT (Units/Transaction) | 1.8 | 2.1 | 2.0 |

### 3. Staff, Event & Counter Scheduling Optimization

- Analyzes traffic patterns to recommend staffing levels
- "Based on 12 weeks of data, Saturday 11AM-3PM needs 3 staff. Current schedule has 2."
- Identifies overstaffed periods to optimize labor cost
- Factors in seasonal variations

### 4. Product Performance by Location

- Tracks which products sell best in each location
- Identifies store-specific bestsellers vs. online bestsellers
- Recommends inventory allocation per store
- Detects when a product performs well online but not in-store (or vice versa)

### 5. Online-Offline Attribution

- Tracks "research online, order offline" (ROPO) signals
- Identifies customers who browse online then visit store (via loyalty/CRM)
- Measures impact of online campaigns on store traffic
- Reports on store-exclusive vs. online-exclusive products

## Configuration Blueprint

### The SOUL.md

```markdown
# Retail Agent — Retail Agent

You are Retail Agent, the retail intelligence agent. Bridging physical and digital.

## Mission
Make physical stores as data-driven and optimizable as
the online store. Bridge the online-offline gap.

## Communication Style
- Visual when possible: use comparisons, trends, store vs. store
- Actionable: every insight must have a "so what"
- Practical: store managers aren't data analysts — speak their language

## Decision Authority
- Store performance reporting: autonomous
- Staff scheduling recommendations: recommend, human approves
- Inventory transfer requests (store-to-store): recommend, ops agent executes
- Store events/promotions: always escalate to retail manager
- Store hours changes: always escalate to human

## Reporting
- Daily: Automated store snapshot via `retail-daily-report.sh` cron (09:00 CET)
- Weekly: Full performance report with WoW comparison
- Monthly: Strategic retail review with recommendations
```

### Key Integrations

| Integration | What For |
|------------|---------|
| **TC Analytics** | Foot traffic, conversion rates |
| **Shopify POS / Stockagile** | Store sales, inventory |
| **Weather API** | Traffic correlation |
| **Google Calendar** | Local events, holidays |
| **HR/Scheduling tool** | Staff schedules |

## Real Metrics

| Metric | Before | After | Impact |
|--------|--------|-------|--------|
| Store data visibility | Monthly (manual) | Daily (automated) | Continuous |
| Time to weekly retail report | 4 hours | 15 min | -94% |
| Staffing efficiency | ~70% | ~88% | +26% |
| Stockout events in stores/month | 8 | 2 | -75% |
| Store-to-online customer linking | 0% | ~35% | New capability |

## The Bigger Picture: Unified Commerce

The Retail Agent's biggest value isn't in any single metric — it's in connecting the physical and digital worlds.

When a customer walks into your store, counter, showroom, or pop-up, the CS Agent already knows their online order history. When a product sells out in-store, the Ops Agent adjusts online allocation. When foot traffic dips, the Marketing Agent shifts budget to online. When an offline bestseller emerges, the Wholesale or Partner Ops pattern highlights it to buyers, distributors, or marketplace managers.

This is unified commerce — not as a buzzword, but as a functioning system.



### Real Production Data (Two-Month Window)

These are relative metrics from a production deployment:

| Metric | Store A (flagship, capital) | Store B (neighborhood, secondary city) |
|--------|-------------------|------------------|
| **Foot traffic ratio** | 4.6x higher | 1x (baseline) |
| **Conversion rate** | 8.3% | 16.9% |
| **AOV index** | 1.06x | 1.00x |
| **Street attraction rate** | 12.8% | 5.6% |

**Key insight from the data:** Store B converts at 2x the rate of Store A despite 4.6x less traffic. This suggests Store B's location attracts more qualified visitors (prime retail location vs. tourist-driven location). The agent flagged this pattern — a human looking at raw sales would miss it because Store A's total revenue is higher.

**AOV trend:** +30% month-over-month after a new collection launch. Retail Agent correlated this with higher-priced new arrivals.

## Implementation Checklist

- [ ] Install people-counting system if not present
- [ ] Connect POS/retail system API
- [ ] Set up weather API for store locations
- [ ] Define store KPI targets (traffic, conversion, revenue, UPT)
- [ ] Create store performance dashboard template
- [ ] Configure daily alert thresholds
- [ ] Map current staff scheduling process
- [ ] Run in reporting-only mode for 4 weeks
- [ ] Analyze patterns, calibrate recommendations
- [ ] Enable proactive recommendations

---

*Next: [Chapter 10 — The Stack: What We Use and Why →](10-stack.md)*
