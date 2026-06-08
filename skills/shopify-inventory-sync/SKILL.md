# Shopify Multi-Location Inventory Sync

Synchronize inventory across Shopify, retail POS systems, and third-party logistics (3PL) providers. Prevents oversells, detects discrepancies, and generates real-time stock alerts.

## When to Use

- User asks to check stock levels across locations
- User mentions inventory sync, stock reconciliation, or oversell prevention
- User wants alerts when stock drops below threshold
- User needs to transfer inventory between locations
- User asks about 3PL inventory status

## Capabilities

1. **Multi-Location Stock Check** - Query inventory levels across all Shopify locations
2. **Discrepancy Detection** - Compare Shopify vs. external systems (Stockagile, Amphora, etc.)
3. **Low Stock Alerts** - Proactive notifications when SKUs drop below configurable thresholds
4. **Transfer Recommendations** - Suggest optimal inventory transfers based on sell-through velocity
5. **3PL Reconciliation** - Match 3PL counts against Shopify expected quantities

## Required Configuration

In your TOOLS.md, include:

```markdown
## Shopify
- **Shop:** your-store.myshopify.com
- **API Version:** 2024-01
- **Token:** shpca_xxxxxxxxxxxxx
- **Base URL:** https://your-store.myshopify.com/admin/api/2024-01/
- **Header:** X-Shopify-Access-Token
- **Locations:** Online (ID), Store1 (ID), Warehouse (ID)
```

For 3PL integration, add the relevant API credentials (Amphora, ShipStation, etc.).

## Usage Examples

### Check All Inventory

```
"Check inventory levels for SKU ABC-123 across all locations"
```

The skill will:
1. Query Shopify Admin API: `GET /inventory_levels.json?inventory_item_ids={id}`
2. Map location IDs to human-readable names
3. Return formatted stock summary

### Low Stock Alert Setup

```
"Alert me when any product drops below 5 units at the online warehouse"
```

Configure threshold in SOUL.md or as cron job:

```markdown
## Inventory Rules
- Online warehouse minimum: 5 units
- Retail stores minimum: 2 units
- Alert channel: Slack #ops-alerts
```

### Sync Check

```
"Compare Shopify inventory against Stockagile for all locations"
```

The skill will:
1. Pull Shopify inventory via Admin API
2. Pull external system inventory via its API
3. Compute delta per SKU per location
4. Report discrepancies exceeding threshold (default: ±2 units)

## API Patterns

### Shopify Inventory Query

```bash
GET https://{shop}/admin/api/2024-01/inventory_levels.json?location_ids={ids}
Authorization: X-Shopify-Access-Token {token}
```

### Adjust Inventory (Use with Caution)

```bash
POST https://{shop}/admin/api/2024-01/inventory_levels/adjust.json
{
  "location_id": 123456,
  "inventory_item_id": 789012,
  "available_adjustment": -5
}
```

## Best Practices

1. **Read-only by default** - Only enable write operations after thorough testing
2. **Buffer stock** - Always maintain buffer (2-5 units) to account for sync delays
3. **Hourly sync max** - Don't poll more frequently than every 30-60 minutes (API limits)
4. **Log everything** - Maintain audit trail of all inventory changes

## Integration with Other Agents

- **CS Agent:** When customer asks "is X in stock?", CS agent queries this skill
- **Ops Agent:** Uses this skill's alerts to trigger reorder workflows
- **Finance Agent:** Uses inventory data for COGS calculations

## Limitations

- Shopify API rate limits: 40 requests/second (burst), 2 requests/second (sustain)
- Real-time sync not possible; near-real-time (5-15 min lag) is the target
- Bundle/kit inventory requires special handling

## Support

Author: AgentivAI
Version: 1.0.0
License: MIT
