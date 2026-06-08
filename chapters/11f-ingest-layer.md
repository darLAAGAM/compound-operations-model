# Chapter 11f: Ingest Layer — Feeding the Brain Safely

> **Appendix · Technical depth.** This chapter is for operators or engineers deploying the brain themselves. It covers implementation details that aren't needed for understanding the conceptual architecture. Skip if you're reading for strategy.

## Why this chapter exists

Chapter 11e covers the bootstrap: one command and the swarm is running with a brain that contains the founder's discovery interview and not much else. This chapter covers what comes next: **how do you actually feed the brain real company data** — orders, products, campaigns, metrics — without accidentally importing half the GDPR fine schedule into your MCP server?

The short answer is the ingest layer, shipped in repo v2.4 as `operai-init ingest …`. The long answer is this chapter. It documents what the layer does, why it was redesigned twice under adversarial review, and what you can — and cannot — wire up safely today.

## The design was not free

The first version (v0.3 planning) was simple: walk Gmail, Notion, Drive, Slack, Shopify — pipe everything through a classifier LLM — land the result in the brain. A senior GDPR counsel running an adversarial review [rejected](https://usecompai.com/playbook/) the design with 14 structural criticisms, starting with:

> **Hashing is not anonymization. You are storing PII in `raw/` and then sending PII to the LLM.** The pipeline is inverted.

Version 0.4 (this chapter) fixes the order of operations. Every shipped line in the repo reflects one or more of those 14 criticisms. Five bloqueantes remain open — they are the reason high-risk unstructured sources (Gmail, Slack, Notion, Drive, Richpanel) are **deliberately out of scope** in Phase 1.

## What Phase 1 ships (v0.4)

| Component | Purpose |
|---|---|
| `operai-init ingest allow …` | Explicit per-source allowlist. No connector runs without a documented legal-basis justification. |
| Subject Registry | Canonical identity store (SQLCipher-encrypted) with deterministic-only linking — no heuristic merges. |
| Delete Ledger | Per-subject RTBF tracking with propagation status per store. Realistic SLAs, not marketing. |
| DLP Stage A | Deterministic secret scanning (AWS, Stripe, Anthropic, GitHub, JWTs, private keys). Hard refuse. |
| DLP Stage B | Deterministic PII tokenization (email, phone, DNI/NIE, IBAN, credit card) with validation checksums. |
| Evidence Store | Per-source SQLCipher databases, TTL 30-365d, never indexed, admin-only access. |
| Retrieval Store | ACL-group-partitioned markdown files under `knowledge/<brand>/ingested/<group>/YYYY/MM/`. |
| ACL at the index boundary | Per-group QMD collections. A principal's query only touches collections whose groups match their key. |
| Shopify connector | Product catalog + aggregated orders + customer counts. No individual orders, no PII. |
| Klaviyo connector | Metrics + campaign aggregates. No individual profiles. |
| Meta/Google Ads connectors | Account-level metric stubs (full implementation in v0.5). |

## What Phase 1 does NOT ship (and why)

The following sources are technically blocked in the allowlist CLI — you can attempt to add them, but without additional controls that Phase 1 does not include, the repo refuses to run them through the pipeline:

- **Gmail (personal accounts)** — killed. Consent in employment contexts is legally weak and revocable. Gmail is shared-inbox-only, and even then Phase 1 does not ship the connector.
- **Slack DMs / private channels** — killed for the same reason.
- **Slack public channels** — deferred. Codex's objection: public channels still contain performance, health, bajas, reorgs, sindicato — i.e. "employee data" in the Annex III sense. Without a high-recall special-category detector, this source risks AI Act contagion.
- **Notion full workspace / Drive "average employee perms"** — deferred. These are the crown jewels of mass ingestion. Phase 1 refuses to walk.
- **Richpanel full ticket bodies** — deferred. Customer PII density is too high for deterministic DLP alone.

Each of these requires at least one of the five Phase 2 prerequisites (§5) resolved before unlock.

## The pipeline in v0.4

```
┌─────────────────────────────────────────────────────────────┐
│ 1. operai-init ingest allow --source X --unit-id Y          │
│    --reason "legítimo interés – …"                          │
│    Entry persisted in allowlist.db.enc with approver + date │
└───────────────────────────┬─────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. Connector fetches only allowlisted units                 │
│    Writes CanonicalDoc to in-memory pipeline                │
└───────────────────────────┬─────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. DLP Stage A — Secret scan (deterministic, regex)         │
│    Any hit → redacted stub only, never indexed              │
└───────────────────────────┬─────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. DLP Stage B — Structured PII tokenization                │
│    emails, phones, DNI/NIE, IBAN, CC — all with validation  │
│    Each PII token resolves via Subject Registry             │
└───────────────────────────┬─────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. Evidence Store (per-source SQLCipher DB, TTL, sealed)    │
│    Original canonical doc — NEVER indexed, NEVER read       │
│    by agents. Accessed only via `ingest audit` (admin).     │
└───────────────────────────┬─────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 6. Retrieval Store (markdown with ACL front-matter)         │
│    Written to knowledge/<brand>/ingested/<acl_group>/       │
│    YYYY/MM/doc_id.md                                        │
│    Only contains sanitized body + tokens                    │
└───────────────────────────┬─────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 7. QMD indexes `ingested/<acl_group>/` as a collection      │
│    per group — NOT one global index                         │
└───────────────────────────┬─────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 8. brain_query routes only to collections the principal's   │
│    acl_groups permit. ACL enforcement is at the index       │
│    boundary, not at read.                                   │
└─────────────────────────────────────────────────────────────┘
```

## Setting it up on your brand

After `curl usecompai.com/init | bash` and `operai-init connect shopify`:

```bash
# 1. Document why you're ingesting (legal basis + retention)
operai-init ingest allow --source shopify --unit-type resource --unit-id products \
  --reason "legítimo interés — catalog sync para CS + merchandising agents; retention 90d"
operai-init ingest allow --source shopify --unit-type resource --unit-id orders_aggregate \
  --reason "legítimo interés — KPIs finance/retail; aggregated only, no individual orders"

# 2. Show what's allowed
operai-init ingest allowlist

# 3. Run the connector
operai-init ingest run --source shopify --days 90

# 4. Check what landed
operai-init ingest stats

# 5. Give team members scoped access
operai-init key create laura --role team --groups cs,retail
operai-init key create juan  --role team --groups finance
operai-init key create founder --role admin
```

a team member (`cs,retail` groups) will only receive results from the `cs` and `retail` QMD collections — she cannot discover docs written to `finance` by the Shopify aggregated-orders ingest. a team member sees `finance` but not `cs`. the founder sees everything.

## RTBF — how real it is

A subject asks to be forgotten. You run:

```bash
# By canonical id (preferred — resolves all aliases):
operai-init ingest forget --subject <uuid> --reason "RTBF request 2026-04-18"

# OR by email (resolved through registry):
operai-init ingest forget --email alice@example.com --reason "RTBF request 2026-04-18"

# Check progress:
operai-init ingest forget --status
```

Realistic propagation times:

| Store | SLA |
|---|---|
| Evidence + retrieval stores | <5 min |
| QMD reindex | <15 min (cron tick) |
| Summaries / derived contexts | <1h (next classification batch) |
| Logs | <24h (log rotation cycle) |
| Backups | <30 days (max retention) |
| LLM provider (non-ZDR) | <30 days per Anthropic retention default |

The Ledger tracks each column independently. Until all columns are `done`, the deletion is `pending` and must be reported as such to the data subject.

**ZDR matters.** `install.sh` prints a warning if no ZDR agreement with Anthropic is on file — in that case the LLM-provider column of the Ledger takes up to 30 days to close. Brands that need same-day full RTBF must have ZDR. This is pre-filled into the DPIA template the repo ships.

## Subjects are canonical, aliases are not

Under Codex's criticism of "forget --email is a toy", the Subject Registry stores:

- A UUID per person (`subject_id`)
- A list of aliases: `(alias_type, alias_value, source)` — email, phone, DNI, Slack user ID, Shopify customer ID, order ID, etc.
- Only **deterministic linking** is auto-applied: two aliases link if and only if a single source record (e.g. one Shopify customer row with both email and phone) asserts them together.

There is no `name_literal` column. Names only appear inside documents, as tokens.

Merges require admin + explicit reason:

```bash
operai-init ingest subjects merge <old_id> <new_id> --reason "RTBF followup — same person, dup'd via diff phone format"
```

Merge decisions are append-only to the audit log.

## Why ACL is at the index boundary

Codex's §12 criticism (v2 review):

> Filtering in `brain_query`/`brain_read` after indexing is not enough if QMD generates snippets and embeddings globally before the check.

v0.4 solves this by partitioning the retrieval store and QMD's collections per ACL group. The collections exposed to a principal's queries are determined by the groups on their API key — QMD never indexes docs outside those scopes into the principal's query space.

Legacy curated knowledge (under `knowledge/<brand>/cs/_index.md`, `knowledge/<brand>/finance/_index.md`, etc., i.e. hand-written docs that were never ingested) remains role-gated: team reads everything hand-curated, admin can also write it.

## Cost

For a 8-figure consumer brand using Phase 1 (Shopify + Klaviyo + Ads):

- **First pass (90 days of data):** ~$2-5. Almost entirely Klaviyo/Shopify API calls; no classifier LLM cost because structured data auto-accepts.
- **Ongoing (daily sync):** ~$0.10/day.
- When Phase 2 (unstructured sources) ships, add a classifier LLM cost of $15-60/month for a medium brand, $50-150/month for a large one (Haiku 4.5 batch pricing).

## Five Phase 2 prerequisites

Before we open Gmail / Slack / Notion / Drive / Richpanel:

1. **Employee-scope exclusion** — either technical filters that reliably exclude worker communications, or a commercial restriction to customer-facing/ops contexts only.
2. **High-recall special-category detection** — keyword-level detection is insufficient for recall on medical/union/performance content. v0.5 will ship either a proper model-based detector or a review-before-persist queue for every unstructured doc.
3. **Subject Registry hardening** — additional audit + access review before we centralize 10K+ aliases in one encrypted DB.
4. **Proof of ACL-at-index isolation under edits** — test harness showing that revoking someone's group access + source upstream membership change both invalidate their cache/snippets reliably.
5. **Evidence Store encryption review** — SQLCipher is now our primitive; before scaling we want a third-party review.

These are tracked in the brain at `knowledge/projects/operai/brand-bootstrap-v0.2.md`.

## What to tell a DPO who asks

Compai's ingest layer, as of v0.4:

- **Does not ingest** employee communications (Gmail personal, Slack DMs/private groups, arbitrary Notion/Drive).
- **Does ingest** structured commercial data (Shopify catalog + aggregates, Klaviyo metrics, ad account metrics) with documented legal basis per source.
- **Pseudonymizes** all detected PII before any indexing — never after.
- **Refuses** any document containing detected secrets (AWS, Stripe, OAuth tokens, private keys).
- **Stores originals** only in encrypted evidence databases with TTL and admin-only access.
- **Enforces ACL** at the retrieval index boundary, not at read time.
- **Supports RTBF** with canonical identity resolution and per-store propagation tracking.
- **Operates under the DPIA and AI System Register** shipped in the compliance package (repo v2.0+).

For the parts that are NOT yet shipped, the product docs and Ch.11f explicitly tell customers "not yet" — we don't market a feature before it's defensible.

---

→ Back to [Chapter 11e — Brand Bootstrap](11e-brand-bootstrap.md) · Next: [Chapter 12 — ROI Analysis](12-roi.md)

---

## Update 2026-04-21 — Phase 2 frozen in repo

This section documents why Phase 2 (Gmail, Slack public channels, Notion, Google Drive, Richpanel) is **frozen in the public repo** and moved to a custom engagement tier. The decision is the result of three adversarial design reviews.

### The three design passes

**v1 (14 Codex criticisms, no-go):** pipeline fundamentally inverted — PII stored raw before minimization, hashing claimed as anonymization, mass workspace crawl, "forget --email" was a toy API. Architecture had to be rebuilt.

**v2 (9 criticisms, partial go):** major corrections accepted. Phase 1 (structured low-risk sources) green-lit. Phase 2 blocked on 5 structural issues:
1. Employee-scope exclusion (technical, not declared)
2. High-recall special-category detection (not keyword-only)
3. Subject Registry hardening (boundary, not CLI-gate)
4. ACL isolation at index boundary with upstream change handling
5. Evidence Store encryption verifiable including `-wal`/`-shm`/temp/logs/backups

**v3 (rejected with 8 additional findings):**

- `scope` field was operator declaration, not technical exclusion
- Override flag `--i-accept-annex-iii-risk` reopened the exact door it claimed to close
- `batch-accept` destroyed the "human-only promotion" thesis
- Review Queue introduced a new sensitive store without defined ACL/encryption
- Classifier had prompt but no evaluation corpus, no recall metric, no model pinning, no fail-closed
- Subject Registry "role-gated at CLI" remained crossable via local tooling
- Revocation SLA still depended on cron with 15-min staleness
- Notion sub-scope (subpages, rows, comments, synced blocks, attachments, mentions) undefined

### Why we're not iterating to v4 for the repo

The 7 remaining Codex requirements — synchronous revocation via Notion webhooks, employee-domain detector separate from Art. 9, classifier validated against a labelled corpus with explicit recall targets and version pinning, Subject Registry behind a real service/DB boundary, leak-surface verifier covering `-wal`/`-shm`/temp/logs/backups/swap, encrypted admin-only Review Queue, per-document scope reclassification on upstream ACL changes — collectively represent **2-4 engineer-months** of compliance platform work.

At a one-size-fits-all packaged SKU, the economics do not close. A brand that **actually needs** unstructured-source ingestion with DPO-grade compliance is paying for a bespoke implementation, not a productized tier. That's how professional services work everywhere else; Compai will be honest about that line.

### What Phase 2 looks like now

**In the public repo (frozen):**

```bash
# Attempts to allow an unstructured source return:
operai-init ingest allow --source notion...
  → Error: source 'notion' is frozen in the public repo (v2.6+).
    See playbook Ch.13 Custom Engagement tier.
    Contact: hello@usecompai.com
```

**As a Custom Ingest Engagement (see Ch.13):**

- Scope + compliance requirements captured per brand
- Dedicated implementation matching the brand's DPO requirements
- Source-specific hardening (e.g. Notion webhook revocation, employee-domain detector tuned to brand's taxonomy)
- DPIA amendments co-signed with brand's legal counsel
- Typical delivery: 4-8 weeks
- Price: €5-15K one-time + €500-1500/month ongoing depending on sources enabled

### What remains in the repo for unstructured data

You can still populate your brain with:

- **Manual writes via MCP** — the CS manager reads a Notion doc, asks Claude to summarize it, and uses `brain_write` to save the summary
- **Discovery interview answers** (`brain-bootstrap.py`) — the ground-truth brand context
- **Per-employee `me.md` profiles** via the `me-md-interview` skill
- **Memory logs from agents** (`memory_write`) as they observe patterns in their tool calls
- **Direct file edits** under `brain/knowledge/<brand>/` by any admin-key holder

This covers most real-world knowledge accumulation. The value proposition — "the brain gets smarter every day" — remains intact without automated unstructured ingestion.

### Why this is the right call

Codex acted as a stand-in for the DPO any serious consumer brand will have. The rational reading of its v3 review is:

> "You can build this correctly, but not at repo pricing. Sell it as an engagement."

We accept that reading. Freezing Phase 2 in the repo removes the single biggest legal exposure the product has, prevents selling to brands whose compliance function would reject the deployment, and preserves the repo's  simplicity.

Structured sources (Shopify, Klaviyo, Ads) — shipped in v0.4 — cover 80%+ of the numeric signal a brand needs. Unstructured sources are where tacit knowledge lives, and tacit knowledge benefits from human curation anyway.

---

→ See [Chapter 13 — What's Next](13-whats-next.md) for the Custom Engagement tier details.
