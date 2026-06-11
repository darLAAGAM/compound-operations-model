# Agent Payments — Autonomous Purchase Skill

> AI agent skill for making purchases with a corporate virtual card, managing invoices, and uploading receipts to Payhawk.

## Overview

This skill enables an AI agent to autonomously make small operational purchases (domains, SaaS subscriptions, tools) using a Payhawk virtual card, while maintaining full audit trail and human oversight.

## Prerequisites

- Payhawk API access (see TOOLS.md)
- Card details stored in `<brain-root>/knowledge/agent-card.md (private, never in a public repo)`
- Browser automation capability (for checkout flows)
- WhatsApp messaging (for approval + notifications)

## Payment Flow

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  Identify    │────▶│  Propose to  │────▶│  the founder      │
│  Purchase    │     │  the founder (WA)  │     │  Approves 👍│
└─────────────┘     └──────────────┘     └──────┬──────┘
                                                 │
                    ┌──────────────┐     ┌───────▼──────┐
                    │  Upload to   │◀────│  Execute     │
                    │  Payhawk     │     │  Purchase    │
                    └──────┬───────┘     └──────────────┘
                           │
                    ┌──────▼───────┐
                    │  Notify      │
                    │  the founder (WA)  │
                    └──────────────┘
```

## Step-by-Step

### 1. Propose Purchase
Send WhatsApp message to the founder:
```
🛒 Purchase Proposal:
- Item: [domain/subscription/tool]
- Vendor: [Cloudflare/Namecheap/etc.]
- Amount: €XX.XX
- Billing: Your Company S.L. (<tax-id>)
- Reason: [why needed]

¿Confirmo? 👍/👎
```

### 2. Execute Purchase
Once approved:
1. Navigate to vendor checkout via browser automation
2. Enter card details from `<brain-root>/knowledge/agent-card.md (private, never in a public repo)`
3. Enter billing info: Your Company S.L., <tax-id>
4. Request factura/invoice during checkout
5. Complete purchase
6. Save confirmation/receipt locally

### 3. Post-Purchase
1. **Download invoice/receipt** (PDF preferred)
2. **Upload to Payhawk** via API:
   ```bash
   # Find the expense matching the transaction
   GET /accounts/<your-payhawk-account-id>/expenses?$filter={"cardId":{"$equal":"<card-id>"}}
   
   # Upload receipt
   POST /accounts/<your-payhawk-account-id>/expenses/{expense_id}/files
   Content-Type: multipart/form-data
   file: [invoice.pdf]
   ```
3. **Notify the founder** via WhatsApp:
   ```
   ✅ Purchase Complete:
   - Item: [what]
   - Amount: €XX.XX charged to the agent ops card
   - Invoice: ✅ obtained / ⏳ requested
   - Payhawk: ✅ receipt uploaded
   ```

### 4. If Invoice Not Available at Checkout
- Email vendor requesting invoice for:
  - Company: Your Company S.L.
  - Tax ID: <tax-id>
  - Email: your agent's mailbox (or the founder's)
- Set reminder to follow up in 48h

## Safety Rules

1. **NEVER exceed €50/transaction** without explicit approval
2. **NEVER make recurring commitments** (annual plans, auto-renewals) without approval
3. **ALWAYS verify the total** before confirming payment
4. **ALWAYS check card balance** before attempting purchase:
   ```bash
   curl -s GET "https://api.payhawk.com/api/v3/accounts/<your-payhawk-account-id>/cards/<card-id>" \
     -H "X-Payhawk-ApiKey: {key}" | jq '.budgetLeft'
   ```
5. **Log every transaction** in memory and `memory/YYYY-MM-DD.md`

## Card Details Reference

Stored in: `<brain-root>/knowledge/agent-card.md (private, never in a public repo)`
- Card <card-id>, virtual debit card
- Limit: <monthly-limit>
- Fund Account: <fund-account-id>

## Vendor Preferences

| Type | Preferred Vendor | Notes |
|------|-----------------|-------|
| Domains | Cloudflare Registrar | Cheapest, already have account |
| DNS | Cloudflare | Already managing the company domain |
| Hosting | Vercel | Already have account + token |
| Email | Google Workspace | Existing setup |
| SaaS | Case by case | Check if free tier sufficient first |
