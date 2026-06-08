# Klaviyo Fashion Brand Optimization

Email and SMS marketing optimization specifically designed for fashion and apparel brands. Covers flow optimization, segment analysis, campaign performance, and fashion-specific automation patterns.

## When to Use

- User asks about email performance, open rates, click rates, conversions
- User wants to optimize abandoned cart, browse abandonment, or post-purchase flows
- User needs fashion-specific segments (size, category preference, seasonal buyers)
- User asks about email revenue attribution
- User wants to A/B test subject lines or send times

## Capabilities

1. **Flow Performance Analysis** - Audit all active flows with conversion benchmarks
2. **Segment Intelligence** - Identify high-value segments specific to fashion buying patterns
3. **Campaign Analysis** - Post-send reporting with revenue attribution
4. **Fashion-Specific Flows** - Back-in-stock, size restock, new arrivals by category
5. **List Health Monitoring** - Deliverability, bounce rates, engagement decay

## Required Configuration

In your TOOLS.md:

```markdown
## Klaviyo
- **API Key:** pk_xxxxxxxxxxxxxxx
- **Public Key:** XXXXXX
- **Base URL:** https://a.klaviyo.com/api/
- **Header:** Authorization: Klaviyo-API-Key {key}
```

## Fashion-Specific Flow Templates

### 1. Browse Abandonment (Category-Aware)

Trigger: Viewed product but didn't add to cart
Timing: 1 hour → 24 hours → 72 hours (3-email sequence)

```
Email 1: "Still thinking about that {product_category}?"
- Show the specific product viewed
- Include 2-3 similar items in same category

Email 2: "Your style, waiting for you"
- Emphasize limited stock if applicable
- Social proof (reviews, "X people bought this")

Email 3: "Last chance to grab this look"
- Urgency messaging
- Consider 10% incentive for first-time buyers only
```

### 2. Post-Purchase: Complete the Look

Trigger: Order placed
Timing: 7 days after delivery (use fulfillment event)

```
"Complete your look"
- Recommend complementary products to what they bought
- Example: Bought blazer → recommend matching trousers, blouse
- Use Klaviyo's product recommendations or custom catalog logic
```

### 3. Size Restock Notification

Trigger: Customer browsed product in their size, was out of stock, now back
Timing: Immediately on restock

```
"Your size is back in stock"
- Single product focus
- Direct CTA to product page
- Limited stock urgency if true
```

### 4. Seasonal VIP Preview

Segment: Customers with LTV > €300 + bought from new collection last season
Timing: 24-48 hours before public launch

```
"You get early access"
- New collection preview
- VIP-only early access window
- Make them feel special, not sold to
```

## Key Metrics & Benchmarks (Fashion)

| Flow | Open Rate | Click Rate | Conversion |
|------|-----------|------------|------------|
| Welcome Series | 45-55% | 8-12% | 3-5% |
| Abandoned Cart | 40-50% | 10-15% | 5-10% |
| Browse Abandon | 30-40% | 5-8% | 2-4% |
| Post-Purchase | 50-60% | 8-12% | 2-4% |
| Win-Back | 20-30% | 3-5% | 1-2% |

If your flows underperform these benchmarks, optimization is needed.

## API Patterns

### Get Flow Performance

```bash
GET https://a.klaviyo.com/api/flows/
Authorization: Klaviyo-API-Key {key}
Accept: application/json
```

### Get Campaign Metrics

```bash
GET https://a.klaviyo.com/api/campaigns/{campaign_id}/
Authorization: Klaviyo-API-Key {key}
```

### Query Segment Size

```bash
GET https://a.klaviyo.com/api/segments/{segment_id}/profiles/
Authorization: Klaviyo-API-Key {key}
```

## Segment Recipes for Fashion

### High-Value Repeat Buyers
```
LTV > €500 AND order_count > 2 AND last_order < 90 days
```

### Category Enthusiasts
```
(ordered from category "Dresses" 2+ times) OR (viewed category "Dresses" 5+ times in 30 days)
```

### Size-Specific (for Targeted Restocks)
```
profile.size_preference = "M" AND last_browsed_oos = true
```

### Seasonal Buyers
```
(ordered in November OR December) AND NOT (ordered in June-August)
```

### At-Risk Loyalists
```
order_count > 3 AND last_order > 120 days AND LTV > €300
```

## Common Optimization Wins

1. **Subject line personalization** - Include product category or color in subject line (+15-25% open rate)
2. **Send time optimization** - Fashion emails perform best Tue-Thu, 10AM and 7PM local time
3. **Segment by engagement** - Suppress unengaged (no open in 90 days) from regular sends
4. **Dynamic product blocks** - Use recommendations vs. static images (+20-40% CTR)
5. **Mobile-first design** - 70%+ of fashion email opens are mobile

## Integration with Other Agents

- **CS Agent:** Check if customer is in VIP segment before offering concessions
- **Marketing Agent:** Pulls Klaviyo metrics for weekly marketing report
- **Finance Agent:** Uses email revenue attribution for channel P&L

## Limitations

- Klaviyo API v2023-10 or later required
- Some advanced metrics require Klaviyo Pro plan
- Real-time profile updates may have 1-5 minute delay

## Support

Author: AgentivAI
Version: 1.0.0
License: MIT
