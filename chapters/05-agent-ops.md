# Chapter 5: Agent #2 — Inventory & Operations (Strategy Agent Hub)

## The Silent Killer of Growing Brands

Inventory problems don't announce themselves. They're silent — until a customer buys something that's not in stock, or your bestseller sits in the wrong warehouse, or your 3PL ships the wrong variant, flavor, shade, size, bundle, or pack.

For brands selling across multiple channels (DTC, wholesale, retail stores, marketplaces, subscriptions, pop-ups, or concessions), inventory is a nightmare of synchronization. And it only gets worse as you grow.

## What the Ops Agent Does

### Real-Time Multi-Location Sync

A typical deployment manages inventory across 6 locations:
- Online store (Shopify)
- 2 retail stores, counters, pop-ups, or partner locations
- 2 department store concessions, marketplaces, or distributor pools
- 1 third-party logistics warehouse (3PL)

Before the Ops Agent, inventory was "synced" via a weekly spreadsheet. The result: 23 sync errors per month, oversells, stockouts, and manual reconciliation that took 6+ hours weekly.

Now: every inventory movement — sale, return, transfer, adjustment — propagates across all systems within minutes.

### How It Works

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Shopify    │     │  Stockagile  │     │   Amphora    │
│   (Online)   │◄───►│  (Retail/ECI) │◄───►│    (3PL)     │
└──────┬───────┘     └──────┬───────┘     └──────┬───────┘
       │                    │                    │
       └────────────┬───────┘────────────────────┘
                    │
              ┌─────▼─────┐
              │  Ops Agent │
              │  (Central) │
              └─────┬─────┘
                    │
          ┌─────────┼─────────┐
          │         │         │
    ┌─────▼──┐ ┌────▼───┐ ┌──▼─────┐
    │ Alerts │ │ Auto   │ │ Reports│
    │        │ │ Reorder│ │        │
    └────────┘ └────────┘ └────────┘
```

### Key Capabilities

**1. Stock Level Monitoring**
- Checks all locations every 30 minutes via automated cron (`inventory-monitor.sh`)
- Alerts when any SKU drops below threshold (customizable per product)
- Distinguishes between "low stock" (reorder now) and "critical" (pause marketing)

**2. Oversell Prevention**
- When online stock drops to last 2 units, automatically buffers for in-store demand
- Syncs "reserved" stock across platforms to prevent double-selling
- If an oversell occurs, immediately alerts CS agent with affected orders

**3. Transfer Recommendations**
- Analyzes sell-through rates by location
- Recommends transfers: "Store A sells 3x more of SKU-2847 than Store B. Transfer 12 units."
- Calculates transfer cost vs. lost-sale cost to determine if transfer is worth it

**4. 3PL Management**
- Monitors fulfillment SLA compliance
- Tracks receiving accuracy (inbound shipments)
- Flags delayed shipments before customers notice
- Reconciles 3PL inventory counts with system counts

**5. Demand Signal Detection**
- Monitors velocity changes: "SKU-3921 sales velocity increased 340% after Instagram feature"
- Cross-references with marketing calendar: "This increase correlates with email campaign sent today"
- Alerts when unexpected demand may cause stockout within 7 days

## Configuration Blueprint

### The SOUL.md (Personality)

```markdown
# Ops Agent — Strategy Agent (Hub)

You are the operations and inventory intelligence agent.

## Mission
Keep every product available where and when customers want it.
Prevent stockouts, oversells, and inventory errors before they happen.

## Communication Style
- Data-first. Lead with numbers, not opinions.
- Proactive. Don't wait for problems — predict them.
- Clear severity levels: 🟢 Info, 🟡 Warning, 🔴 Critical
- Always include recommended action, not just the problem.

## Decision Authority
- Stock transfers < €500 in product value: recommend, don't require approval
- Pause marketing on low-stock SKU: autonomous
- Adjust buffer stock levels: autonomous within ±20% of baseline
- New vendor/supplier contact: always escalate to human
- Inventory write-offs > €100: always escalate to human

## Reporting Cadence
- Real-time: Critical alerts (stockouts, oversells)
- Daily: Stock level summary, fulfillment SLA
- Weekly: Full inventory report, transfer recommendations, demand analysis
```

### Key Integrations

| Integration | What For | API Used |
|------------|---------|---------|
| **Shopify** | Online stock levels, orders | Admin API |
| **Stockagile** | Retail & concession inventory | REST API |
| **Amphora** | 3PL stock, fulfillments, inbounds | REST API |
| **Google Sheets** | Reporting dashboards | Sheets API |
| **Slack/WhatsApp** | Real-time alerts | Messaging |

## Real Metrics

| Metric | Before | After | Impact |
|--------|--------|-------|--------|
| Inventory sync errors/month | 23 | 2 | -91% |
| Oversells/month | 8 | 0.5 | -94% |
| Manual reconciliation time/week | 6 hours | 30 min | -92% |
| Stockout incidents/month | 12 | 3 | -75% |
| Transfer efficiency (units moved optimally) | ~40% | ~85% | +113% |

## Implementation Checklist

- [ ] Audit all inventory locations and systems
- [ ] Set up API connections to each inventory source
- [ ] Define stock thresholds per SKU category (basics vs. seasonal vs. limited; flavor, scent, size, color, model, bundle, or pack variants)
- [ ] Configure alert channels and severity levels
- [ ] Build initial buffer stock rules
- [ ] Run in monitoring-only mode for 2 weeks
- [ ] Review and calibrate thresholds
- [ ] Enable active management (transfers, buffer adjustments)
- [ ] Set up weekly inventory health report

---

*Next: [Chapter 6 — Agent #3: Finance & Reporting →](06-agent-finance.md)*
