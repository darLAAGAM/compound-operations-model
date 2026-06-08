# Chapter 00b: Live Dashboard — The Wow Factor Tour

## What the dashboard is for

The live dashboard exists for two reasons.

First, it proves the system is not a slide deck. A serious AI-native operating system should have a pulse: agents online, tool calls, recent learnings, review queues, business signals, and warnings. If the public story says the system runs every day, the dashboard should show what is running.

Second, it is an operating surface. A dashboard that only impresses investors is decoration. A useful dashboard tells an operator what needs attention today.

The right mental model is not “analytics BI.” It is closer to an aircraft status panel for a consumer SME: what is healthy, what is delayed, what is manual, what is unknown, and what changed.

## The tour

The public live view at `usecompai.com/live` should be read as a map of the operating layer, not as a claim that every metric is fully autonomous.

```text
LIVE DASHBOARD

1. System pulse
   agents online, last heartbeat, recent errors, MCP health

2. Brain activity
   docs indexed, recent writes, learnings captured, stale-doc warnings

3. Work queues
   CS drafts, invoice exceptions, review items, failed automations

4. Business signals
   sales, paid efficiency, inventory risk, cash reminders, campaign health

5. Capability demos
   Council, adversarial review, pattern library, profit throttle, calendar

6. Metric glossary
   definitions, source systems, freshness, whether live/manual/demo
```

The credibility is in the labels. Each tile should say whether it is streaming from a live source, calculated from a scheduled job, manually refreshed, or illustrative. Hiding that distinction makes the dashboard less trustworthy.

## What is actually streaming

A mature deployment can stream infrastructure and workflow status with high confidence:

| Area | Typical source | Freshness | Notes |
|---|---|---:|---|
| Agent health | runtime heartbeat files or service status | 1-5 min | Shows online/offline, last run, model, errors |
| MCP health | MCP `/health` or tool-call counters | 1-5 min | Useful for detecting auth, timeout, or tool failures |
| Brain writes | filesystem or action ledger | near real-time | Shows whether the system is learning |
| Review queue | local queue folder or database | near real-time | Shows work waiting for human approval |
| Webhook intake | helpdesk/ecommerce receiver logs | near real-time | Shows new events entering the system |

These are the safest live metrics because they describe the operating system itself.

Business metrics are different. Sales, contribution margin, ad spend, returns, inventory, and cash all depend on source freshness and reconciliation. A good dashboard shows them, but it should also show lag and confidence.

## What belongs in the metric glossary

Every metric needs a short definition. Not because the team is naive, but because dashboards rot when definitions are implicit.

Examples:

| Metric | Definition | Source of truth | Caveat |
|---|---|---|---|
| Net sales | Gross sales less discounts, refunds, and taxes where available | Ecommerce platform | POS and marketplace timing can differ |
| Blended MER | Net revenue divided by total paid media spend | Ecommerce + ads | Good for overall efficiency, weak for scaling decisions |
| Marginal MER | Incremental revenue divided by incremental spend | Ecommerce + ads | Sensitive to attribution and date windows |
| Inventory risk | Variants projected to stock out before next replenishment | ERP/inventory tool | Requires lead-time accuracy |
| Open review items | Agent outputs waiting for a human | Review queue | Not the same as unresolved customer tickets |
| Brain writes | Durable docs or learnings added to the brain | Brain/action ledger | Quantity is not quality |

For a food business, the dashboard might include batch expiry and cold-chain exceptions. For a beauty business, shade stockouts and claims review. For a home business, bulky-shipping delays and warranty backlog. For a pet business, subscription churn and sizing exchanges. For an outdoor business, warranty claims by use case and seasonal inventory risk.

## Proof versus control

Public dashboards over-index on proof. Internal dashboards need control.

The proof layer answers: is this real?

The control layer answers: what should we do?

A CEO does not need 80 tiles. They need the five states that change decisions:

- Is the system healthy?
- Is any workflow stuck?
- Is any customer-facing action waiting too long?
- Are we spending money below break-even?
- Did the brain learn anything worth reviewing?

If a tile cannot trigger a decision, demote it to the glossary or history view.

## Screenshot map

Use a simple map when documenting the dashboard:

```text
┌──────────────────────────────────────────────────────────┐
│ Header: live status, last refresh, environment            │
├──────────────┬──────────────┬──────────────┬─────────────┤
│ Agent health │ MCP health   │ Brain writes │ Review queue│
├──────────────┴──────────────┬──────────────┴─────────────┤
│ Profit throttle             │ Inventory / operations risk │
├─────────────────────────────┼────────────────────────────┤
│ Recent learnings            │ Recent incidents / warnings │
├─────────────────────────────┴────────────────────────────┤
│ Metric glossary + data source table                       │
└──────────────────────────────────────────────────────────┘
```

The best dashboard screenshot is not the prettiest one. It is the one where an operator can tell which values are live, which are stale, and what needs review.

## Limitations

Dashboards can create false confidence. APIs go stale. Attribution shifts. A failed cron can make yesterday look calm. Some metrics have a three-day delay. Some partner systems still require manual export. Some “AI activity” metrics are vanity metrics unless tied to outcomes.

The answer is not to remove the dashboard. The answer is to label source, freshness, owner, and confidence.

## How to start this in your business

1. Build the first dashboard around operating health, not vanity analytics: agent/service status, queue depth, recent failures, and review items.
2. Add a data source table with owner, API/export method, refresh frequency, and known delay for each metric.
3. Add a metric glossary before adding more charts. Force every metric to define source of truth and caveat.
4. Mark each tile as live, scheduled, manual, or demo. Trust comes from visible limitations.
5. Fork `templates/dashboard-data-spec.md` as the artifact and fill it before writing dashboard code.

