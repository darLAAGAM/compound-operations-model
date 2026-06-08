# Chapter 10e: Profit Throttle — Dynamic Break-Even MER for Paid Marketing

## The problem with fixed ROAS targets

Most consumer SMEs manage paid marketing with a fixed ROAS target.

That target usually came from a spreadsheet, a board meeting, or an agency rule of thumb. “We need 3.0x.” “We scale above 2.5x.” “We pause below 2.0x.”

The problem is that the business underneath the target changes every day.

Your product mix changes. Return rate changes. Discounts change. Shipping costs change. Payment fees change. A campaign can shift from full-price bestsellers to low-margin bundles without the headline ROAS making that obvious. A food brand might move from ambient products to chilled products with higher logistics cost. A beauty brand might scale a shade with high exchange rates. A home brand might sell more bulky items. A pet brand might push subscription acquisition at lower first-order margin. An outdoor brand might spend into a warranty-heavy category.

A fixed ROAS target treats all of those days as the same day. They are not.

Profit Throttle is the decision layer that fixes this. It calculates the dynamic break-even MER every day and compares it against both blended and marginal efficiency.

## MER, not just ROAS

ROAS usually means attributed revenue divided by ad spend for one platform.

MER, marketing efficiency ratio, is broader:

```text
MER = net revenue / total paid media spend
```

Use MER because platform attribution is not a source of truth. Meta, Google, TikTok, affiliate platforms, and email tools all want credit. The business only cares whether total paid spend is buying profitable revenue.

But there are two MERs.

## Blended MER

Blended MER tells you the overall efficiency of paid marketing:

```text
blended MER = total net revenue / total paid spend
```

It is useful for the finance view. If the whole business spent €10,000 and generated €40,000 of net revenue, blended MER is 4.0.

Blended MER is weak for scale decisions. It averages yesterday's good spend with today's bad spend. You can have a healthy blended MER while the last €1,000 you added is destroying margin.

## Marginal MER

Marginal MER asks a harder question:

```text
marginal MER = incremental net revenue / incremental paid spend
```

If paid spend increased by €1,000 and net revenue increased by €2,100, marginal MER is 2.1. That is the number that answers “should we keep scaling?”

Marginal MER is noisy. It depends on time windows, attribution lag, promotions, stockouts, and seasonality. But it is still the right lens for spend changes. A noisy answer to the right question beats a precise answer to the wrong question.

## Dynamic break-even MER

Break-even MER is the minimum MER needed to avoid losing money after variable costs and target profit.

A practical version:

```text
gross margin after COGS
- return cost ratio
- logistics ratio
- payment fee ratio
- marketplace/partner fee ratio where relevant
- variable handling ratio
- target profit floor
= allowable marketing ratio

break-even MER = 1 / allowable marketing ratio
```

Example:

```text
Net revenue                         100.0%
COGS                                -35.0%
Returns and exchanges                -8.0%
Logistics                            -9.0%
Payment fees                         -2.0%
Variable ops                         -3.0%
Target contribution profit          -10.0%
------------------------------------------------
Allowable marketing ratio            33.0%
Break-even MER                       3.03
```

If the allowable marketing ratio is 33%, you need a MER above 3.03 to hit the profit floor.

Tomorrow, the product mix may push COGS to 42% and returns to 11%. Your break-even MER changes. That is the point.

## Traffic-light signals

Profit Throttle should be easy to read:

| Signal | Condition | Meaning | Action |
|---|---|---|---|
| Green | Blended and marginal MER above break-even with buffer | Spend is economically safe | Consider controlled scaling |
| Yellow | Blended above break-even, marginal near or below break-even | Existing spend okay, new spend questionable | Hold, test, segment |
| Red | Blended near or below break-even | Current spend risks margin | Cut waste, reduce budgets, inspect mix |
| Black | Data missing, attribution broken, or stock/fulfillment constraint | Decision unsafe | Freeze scale until source fixed |

The black state matters. Sometimes the correct paid-media decision is “do nothing because the data is not reliable.” If ad spend is live but product margin, return rate, or inventory data is stale, scaling is a gamble.

## What inputs you need

Do not wait for perfect attribution. Start with a daily sheet:

| Input | Source | Notes |
|---|---|---|
| Net revenue | Ecommerce/POS source of truth | Exclude tax where possible |
| Paid spend | Ad platforms or finance export | Use total spend, not platform-reported revenue |
| COGS ratio | ERP/product master/accounting | Product mix matters |
| Return ratio | Ecommerce/helpdesk/accounting | Use rolling window by category if possible |
| Logistics ratio | 3PL/carrier/accounting | Split bulky, chilled, international, or fragile where relevant |
| Payment fees | PSP/accounting | Include cross-border and installment fees |
| Discounts | Ecommerce | Already reflected if using net revenue |
| Target profit floor | Finance | Explicit management choice |

Month one does not need SKU-level perfection. It needs a decision-grade break-even threshold and a reconciliation habit.

## How agents use it

The marketing agent should not say “ROAS is good.” It should say:

```text
Yesterday:
- Blended MER: 3.42
- Marginal MER, 7-day spend increase: 2.61
- Dynamic break-even MER: 3.08
- Signal: Yellow

Reason:
Overall spend remains above break-even, but the latest increment is below
the current profit floor. The issue is concentrated in prospecting Campaign B
and a lower-margin product mix.

Recommendation:
Hold total budget. Move 15% from Campaign B to retention and high-margin
category campaigns. Recheck after two full conversion windows.
```

That is an operating decision, not a vanity metric.

## The daily ritual

Profit Throttle works best as a daily trading ritual, not a quarterly analytics project.

Every morning, the owner should see:

- Yesterday's net revenue.
- Yesterday's paid spend.
- Seven-day blended MER.
- Seven-day marginal MER.
- Current break-even MER.
- Signal.
- The one reason behind the signal.
- Recommended action.

The reason field is important. A yellow signal caused by low-margin product mix is different from a yellow signal caused by rising CPMs. A red signal caused by missing revenue data is different from a red signal caused by real spend inefficiency. A black signal caused by stale COGS should stop budget decisions until finance fixes the input.

For a non-technical CEO, the output should read like this:

```text
Signal: Yellow
Decision: hold spend
Why: blended efficiency is still profitable, but the latest scale increment
is below today's break-even. The issue is mostly product mix, not CPM.
Next: move spend toward high-margin categories and recheck after 48 hours.
```

The goal is not to create another dashboard. It is to make the paid-media meeting shorter and more economically honest.

## Product mix matters more than agencies admit

Two campaigns with the same ROAS can have opposite profit outcomes.

Campaign A sells full-price replenishable products with low returns and cheap shipping. Campaign B sells discounted bulky products with high returns and higher fulfillment cost. Both report 3.0x platform ROAS. Campaign A may be strongly profitable. Campaign B may be destroying cash.

That is why Profit Throttle should eventually move from account-level to category-level and then product-group-level. It does not need perfect attribution. It needs enough segmentation to avoid scaling revenue that the business should not want.

Start with three buckets:

- High-margin products you are happy to scale.
- Strategic products you will tolerate at lower contribution.
- Margin-risk products that need stricter thresholds.

Then compare the daily product mix against the break-even calculation. This is where marketing, finance, and merchandising stop arguing from different dashboards.

## Limitations

Profit Throttle is not magic. It can be wrong if COGS is stale, returns are delayed, ad platform spend is incomplete, or revenue includes channels unrelated to paid spend. Marginal MER is especially sensitive to noise. Promotions, stockouts, retail events, PR mentions, and email campaigns can make paid spend look better or worse than it is.

The answer is not to abandon the framework. The answer is to label confidence and avoid automating budget changes until the model has survived reviewed use.

Use it in read-only mode first. Then draft recommendations. Then human-approved budget moves. Autonomous budget changes should come much later, with hard caps and rollback rules.

## How to start this in your business

1. Build a daily break-even MER sheet with net revenue, paid spend, COGS, returns, logistics, payment fees, and target profit floor.
2. Calculate both blended MER and marginal MER. Do not use blended MER alone for scaling decisions.
3. Add traffic-light logic and a black state for missing or stale data.
4. Run it read-only for 30 days against the paid-media decisions you would have made anyway.
5. Fork `templates/profit-throttle-calculator.md` as the artifact, then connect it to a Google Sheet only after the formula is understood.
