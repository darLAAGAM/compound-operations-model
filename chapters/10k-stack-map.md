# Chapter 10k: Consumer SME Stack Map — Where Each Tool Fits

## Do not copy the tools. Copy the roles.

The reference stack uses specific vendors. Your company may not.

That is fine. The architecture is not “use Shopify, Klaviyo, and this exact accounting tool.” The architecture is “your AI operating layer needs reliable access to the systems that play these roles.”

If you copy vendor names without understanding roles, you will overfit. If you map roles clearly, you can adapt the playbook to beauty, food, home, wellness, pet, outdoor, fashion, retail, or any other physical-products SME.

## The map

| Role | What it owns | Common options |
|---|---|---|
| Ecommerce source of truth | Orders, products, customers, discounts, refunds, web revenue | Shopify, BigCommerce, WooCommerce, Magento, custom storefront |
| POS / retail | Store orders, staff sales, locations, cash register events | Shopify POS, Lightspeed, Square, Cegid, custom POS |
| Inventory / ERP | Stock, warehouses, transfers, purchase orders, COGS | Stockagile, Cin7, Katana, Odoo, NetSuite, ERPNext, custom ERP |
| Accounting | Invoices, chart of accounts, P&L, tax, payables | Holded, Xero, QuickBooks, Sage, A3, NetSuite |
| Expense management | Cards, receipts, approvals, reimbursements | Payhawk, Pleo, Spendesk, Ramp, Brex |
| Helpdesk | Customer tickets, conversations, tags, SLA | Richpanel, Gorgias, Zendesk, Intercom, Freshdesk |
| Email/SMS lifecycle | Campaigns, flows, segments, attributed revenue | Klaviyo, Attentive, Mailchimp, Braze, Customer.io |
| Ads | Spend, campaign structure, creative, platform metrics | Meta, Google Ads, TikTok, Pinterest, Amazon Ads |
| Analytics | Web sessions, conversion, channel analysis | GA4, Plausible, PostHog, Triple Whale, Northbeam |
| Search visibility | Queries, pages, indexing, AI search audits | Google Search Console, Ahrefs, Semrush, custom GEO trackers |
| Logistics / 3PL | Fulfillment, tracking, returns, inbounds | ShipBob, ShipStation, warehouse APIs, 3PL portals |
| Workspace | Email, Drive, Docs, Sheets, Calendar | Google Workspace, Microsoft 365 |
| Team chat | Operational alerts, digests, escalations | Slack, Teams, Discord |
| Knowledge base | Company brain, docs, skills, patterns, memory | Markdown repo, Notion export, Drive docs, internal wiki |
| AI tool interface | Human access to brain/tools/agents | Claude Desktop, ChatGPT, Cursor, Codex, internal app |
| MCP/tool server | Secure bridge between AI and systems | FastMCP, custom API service, Zapier/N8N as transitional layer |
| Runtime / queues | Event processing, review queues, traces | Filesystem queues, Redis, Postgres, Temporal, custom daemon |

## Source-of-truth rules

Every metric should have one owner.

Sales usually come from ecommerce/POS, not web analytics. Web analytics is useful for sessions and channel behavior, but it misses offline, delayed, blocked, and platform-specific data. Accounting owns financial close. Inventory owns stock. Helpdesk owns ticket state. Email owns campaign sends. Ads own spend but not final truth on revenue.

Write this down. Many AI mistakes are source-of-truth mistakes disguised as reasoning mistakes.

## Integration priority

Connect in this order:

1. Brain and docs.
2. Ecommerce orders/products/customers.
3. Helpdesk.
4. Inventory or ERP.
5. Accounting/invoices.
6. Email marketing.
7. Ads and analytics.
8. Workspace/calendar/drive.
9. Logistics and partner systems.

The order reflects operational leverage. A customer-service agent without order access is weak. A finance workflow without invoices is theater. A marketing agent without contribution margin will optimize for vanity.

## Vendor alternatives by vertical

A food business may need batch/lot traceability and expiry before advanced marketing analytics. A beauty business may need claims and ingredient documentation. A home business may need bulky freight and replacement-parts workflows. A pet business may need subscription and sizing logic. An outdoor business may need warranty, repair, and seasonal demand planning.

The stack map should make those vertical differences explicit while preserving the common architecture.

## What not to integrate first

Do not start with the hardest proprietary vendor. Do not start with bank payments. Do not start with payroll mutations. Do not start with autonomous ad-budget writes. Do not start with every Slack channel.

Start with read access to the systems that answer daily questions. Then draft. Then approve. Then bounded writes.

## Limitations

Some vendors have poor APIs. Some require manual exports. Some data is messy. Some systems disagree because they define the same word differently. A stack map will not solve that. It will surface it.

That is useful. Once the disagreement is visible, you can decide which source wins for which decision.

## How to start this in your business

1. Create a one-page stack map with roles, vendors, owners, API/export method, and source-of-truth rules.
2. Mark each integration as read-ready, export-only, manual, or unavailable.
3. Connect the brain, ecommerce, helpdesk, and one finance source before adding advanced systems.
4. For every dashboard or agent answer, require source citation: which system produced the number?
5. Fork `integrations/_stack-map.md` as the artifact.

