# Chapter 21: Webhook Receivers + Slack Digest — repo v3.0 Stable

> **Appendix · Technical depth.** This chapter is for operators or engineers deploying the brain themselves. It covers implementation details that aren't needed for understanding the conceptual architecture. Skip if you're reading for strategy.

## What v3.0 stable adds

Runtime v3.0-beta (Ch.20) shipped the autonomous daemon. Events arrived, sub-agents ran, review queue got written — but **the brand was still responsible for wiring their own event source**, typically by cron'ing their helpdesk API and dumping JSON into `/opt/operai/events/cs/pending/`.

v3.0 stable removes that last manual step. A production HTTP receiver runs on the brand's VPS, accepts authenticated webhooks from four major helpdesks, and drops canonical events straight into the factory queue. Plus: a daily Slack digest the founder actually reads.

## Prompt-injection boundary

HMAC verification proves the webhook came from the configured provider; it does not make the ticket body trustworthy. `subject`, `body`, `raw_ticket`, comments, attachments, links, and customer metadata remain untrusted data. The runtime must wrap them as data, ignore instructions inside them, and only execute actions from the domain allowlist. High-impact outputs stay in the review queue until a human approves them.

## The two new services

| Service | Port | Systemd unit | Purpose |
|---|---|---|---|
| Webhook receiver | 127.0.0.1:8788 | `operai-webhook.service` | Accepts helpdesk webhooks with HMAC verification |
| Daily digest (cron-based) | — | user crontab | Daily Slack summary to `#operai-ops` |

Both ship under the open-source repo. Brand exposes the webhook receiver via their Cloudflare Tunnel (`webhook.<brand>.com`), configures each helpdesk to POST there, and gets autonomous ticket processing.

## Supported helpdesks in v3.0

| Provider | HMAC scheme | Normalizer |
|---|---|---|
| **Richpanel** | `X-Richpanel-Signature: sha256=<hex>` | `richpanel.py` |
| **Gorgias** | `X-Gorgias-Hmac-SHA256: <base64>` | `gorgias.py` |
| **Zendesk** | `X-Zendesk-Webhook-Signature` + `-Timestamp` | `zendesk.py` |
| **Intercom** | `X-Hub-Signature-256: sha256=<hex>` | `intercom.py` |

Each normalizer converts the provider-specific payload into the same `CanonicalTicket` schema the factory runtime expects. If the brand uses a different helpdesk, they add a new normalizer (~50 lines) or use a workflow pre-hook to transform their custom source format.

## The `CanonicalTicket` schema

```json
{
  "raw_ticket":        "subject + body, extracted + merged",
  "ticket_summary":    "first 200 chars or subject",
  "customer_email":    "raw email (DLP-tokenized later)",
  "priority":          "P1|P2|P3|P4 (mapped from provider priority)",
  "channel":           "email|chat|form|intercom|...",
  "source_provider":   "richpanel|gorgias|zendesk|intercom",
  "source_ticket_id":  "provider-native id for idempotency",
  "source_created_at": "ISO timestamp from provider",
  "tags":              ["..."]
}
```

Anything else — `customer_order_history`, `brand_voice`, `applicable_policies` — is filled by `brain_lookup` and brand workflow hooks, just like in v0.9.1.

## Setup flow for the founder

One time, per helpdesk:

```bash
# 1. Expose the webhook receiver publicly
operai-init tunnel webhook.acme.com      # routes → 127.0.0.1:8788 via Cloudflare

# 2. Tell Compai where it's exposed (for status displays)
operai-init webhook set-endpoint https://webhook.acme.com

# 3. Configure a provider — paste the signing secret from the helpdesk
operai-init webhook configure richpanel
  # → shows step-by-step setup: URL to use in Richpanel dashboard + where to copy the secret
  # → paste secret (hidden input)

# 4. Test it locally
operai-init webhook test richpanel
  # → builds a signed test payload, POSTs to local receiver, prints response

# 5. Start the service
systemctl enable --now operai-webhook

# 6. Configure each helpdesk to POST to:
#      https://webhook.acme.com/webhook/richpanel/cs
#      https://webhook.acme.com/webhook/gorgias/cs
#      https://webhook.acme.com/webhook/zendesk/cs
#      https://webhook.acme.com/webhook/intercom/cs

# 7. Verify
operai-init webhook status
  # → shows: service active, providers configured, recent activity tail
```

## HMAC verification — fail-closed

Every webhook goes through these checks, in order:

1. **Provider known** — rejects unknown provider path → 400
2. **Secret configured** — rejects providers without a secret on file → 401
3. **Signature present** — rejects requests missing the header → 401
4. **HMAC matches** — constant-time comparison; mismatch → 401
5. **JSON parseable** — rejects malformed → 400
6. **Normalizer succeeds** — rejects shapes the provider doesn't match → 400
7. **`raw_ticket` non-empty** — rejects empty payloads → 400

Only if all seven pass does the event land in the queue. Every rejection logs with reason to `/opt/operai/logs/webhook.log`.

A spray of unsigned POSTs from a scanner gets **only 401 responses** — no tickets land, no LLM calls fire, no cost incurred.

## The daily Slack digest

Once the factory is running, the founder rarely opens the CLI. The digest exists so they don't have to.

```bash
operai-init digest configure         # paste Slack incoming webhook URL
operai-init digest now               # send one immediately
operai-init digest schedule          # install daily cron at 08:00 UTC
operai-init digest status            # current counters + config
```

Each digest shows:

```
*Compai digest — acme — 2026-04-21 08:00 UTC*

• 4 tickets pending human review
• 2 escalations on record (2 most recent below)
• 17 auto-sent decisions in last 24h
• 23 completed events in last 24h
• 1 failed events in last 24h

*Recent escalations:*
• `gorgias-4719-a8f3` (cs) — VIP customer threatening churn + press mention
• `richpanel-9001-42db` (cs) — Refund request >€500 requires approval
```

One Slack post, once a day, is typically enough for an M-shaped supervisor managing a 500-ticket/week CS flow. For urgent escalations, the existing `operai-factory-runtime.service` emits markers to `events/escalations/` which a future v3.1 will wire directly to founder DMs.

## End-to-end autonomous flow

Runtime v3.0 stable delivers this without any manual intervention:

```
┌──────────────────────────────────────────────────────────────────┐
│ 1. Customer emails the brand's support address                    │
└───────────────────────────────┬──────────────────────────────────┘
                                ▼
┌──────────────────────────────────────────────────────────────────┐
│ 2. Richpanel/Gorgias/Zendesk/Intercom creates ticket              │
│    → fires webhook to webhook.<brand>.com/webhook/<provider>/cs  │
└───────────────────────────────┬──────────────────────────────────┘
                                ▼
┌──────────────────────────────────────────────────────────────────┐
│ 3. operai-webhook receiver:                                       │
│    • verifies HMAC signature (fail-closed)                        │
│    • normalizes to CanonicalTicket                                │
│    • saves raw payload for audit                                  │
│    • drops canonical into events/cs/pending/<event_id>.json       │
│    • returns 200 in ~50ms                                         │
└───────────────────────────────┬──────────────────────────────────┘
                                ▼
┌──────────────────────────────────────────────────────────────────┐
│ 4. operai-factory-runtime daemon picks up within 3s:              │
│    • brain_lookup enriches with brand_voice + policies            │
│    • workflow pre-hook (brand's Python) runs                      │
│    • 10 sub-agents execute in parallel via configured LLMs        │
│    • escalation-scorer decides action                             │
│    • review queue markdown written                                │
│    • trace JSON indexed into QMD                                  │
│    • event archived to events/cs/completed/                       │
└───────────────────────────────┬──────────────────────────────────┘
                                ▼
┌──────────────────────────────────────────────────────────────────┐
│ 5. M-shaped supervisor checks review queue via CLI or digest      │
│    or waits for the daily Slack digest at 08:00 UTC               │
└──────────────────────────────────────────────────────────────────┘
```

No Python script in a cron job. No brand-built pollers. **One curl-bash install, one Cloudflare tunnel, one webhook URL per helpdesk.**

## What remains brand-responsibility

Honest scoping — this is still v3.0, not v4:

1. **Sending the actual reply** (v3.1). Today auto_send decisions are logged to `review/auto-sent/`. The brand either: (a) builds a small cron that reads this folder and POSTs replies via their helpdesk API, (b) waits for v3.1, or (c) buys Managed Operations.
2. **6 other factories** (finance / ops / marketing / merch / retail / hr) — CS is shipped, others are templates-only until v3.2-v3.3.
3. **Custom normalizers** for non-supported helpdesks. `CanonicalTicket` is stable; writing a new normalizer is ~50 lines.
4. **Brand-specific enrichment** — CRM lookups, inventory checks, dialect overrides. Workflow hooks at `/opt/operai/workflows/<domain>/pre_process.py`.
5. **Error recovery** — failed events land in `events/cs/failed/` with `.error` files. Founder decides whether to retry via `operai-init event replay --id <X>`. Automated retry logic is v3.1.

## Commercial framing

Everything in this chapter is in the open-source repo. the founder's open-source inclusion rule holds through v3.0. What remains as separate tiers:

- **Custom Ingest Engagement** (Ch.13 Path 3b, €5-15K): unstructured data ingestion (Gmail, Slack, Notion, Drive)
- **Managed Operations** (Ch.13 Path 3a, €5-15K/mo): Compai runs + tunes the full swarm for the brand

A buyer today goes from `curl usecompai.com/init` to autonomous helpdesk ticket processing in a single afternoon. That is the closest anyone has gotten to "a reference-deployment-in-a-box" without crossing into the custom engagement tiers.

---

→ Back to [Ch.20 Runtime v3.0-beta MVP](20-mvp-runtime.md) · Forward to Ch.22 *(v3.1 action executor — coming)*
