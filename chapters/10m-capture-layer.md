# Chapter 10m: The capture layer — Slack, Meet, Email, Drive

## Knowledge is created where work happens

Most consumer SMEs do not have a knowledge problem in the abstract. They have a capture problem.

The company already knows a lot. The issue is that the knowledge is scattered across places that were never designed to become operational memory: Slack threads, Google Meet notes, email chains, Drive files, customer conversations, weekly reports, and the founder's quick decisions. People assume the important parts will be written down later. Later rarely happens.

A static knowledge base reverses the natural flow of work. It asks busy people to stop operating, open a wiki, create a page, decide where it belongs, write the context cleanly, tag it, and remember to update it when reality changes. That works for policies and handbooks. It fails for the live edge of operations.

The capture layer changes the default. It lets the company keep working where it already works, then turns selected signals into structured memory.

This does not mean dumping every message, email, and file into the brain. That is the fastest way to create a polluted memory system and a privacy problem. The goal is selective capture: preserve enough source context to audit, normalize the signal, promote only what is useful, and route actionable items into tasks, outputs, health, or world model.

The reference implementation took months to reach this shape because it had to work around real permissions, real employee communications, real false positives, and real operational noise. A consumer SME starting now should expect 6-8 weeks with one engineer to get the first serious version across chat, meetings, email, and Drive. The technical connectors are only half the work. The hard part is deciding what deserves memory.

## `brain_capture` as the universal contract

The core design choice is to make every source speak one contract. In the reference system, that contract is `brain_capture`.

A capture tool should accept a normalized record with fields such as:

| Field | Why it matters |
|---|---|
| `title` | Human-readable summary of the captured item |
| `body` or `content` | The normalized text the Brain can read |
| `source_type` | Slack, meeting, email, Drive, manual, tool output, etc. |
| `source_url` or `source_id` | Traceability back to the original material |
| `occurred_at` | When the work happened, not only when it was captured |
| `author` or `source_owner` | Who produced or owned the source |
| `domains` | CS, finance, ops, marketing, retail, merchandising, HR, tech |
| `sensitivity` | Public, internal, restricted, sensitive, or source-specific labels |
| `entities` | Explicit people, companies, projects, campaigns, suppliers, stores |
| `create_task` | Whether an actionable signal should become a task |
| `raw_payload` | Optional source material for audit or recovery |

The outputs should also be predictable:

```text
knowledge/<company>/_raw/YYYY-MM-DD/       optional raw source material
knowledge/<company>/_inbox/YYYY-MM-DD/     normalized capture documents
knowledge/<company>/_indexes/capture-log.md
knowledge/<company>/entities/...           deterministic entity propagation
knowledge/<company>/_tasks/todo/...        if the capture creates action
```

This contract gives you a stable boundary. Slack, Meet, Email, Drive, and manual notes can evolve independently as long as they produce the same capture shape. Agents can reason over one inbox structure rather than learning five source-specific formats.

The reference system also propagates deterministic entities into folders such as `people`, `companies`, `projects`, `campaigns`, `suppliers`, and `stores`. That sounds like detail, but it matters. A founder asking, "What do we know about this supplier?" should not depend on the exact words used in one meeting note. Entity propagation gives the Brain a second way to find context.

`brain_capture` is not an ingestion free-for-all. It is the front door. Everything that enters through it should carry source, sensitivity, and action semantics.

## Slack: public signals, not chatter

Chat is where a company thinks out loud. It is also noisy.

The reference Slack pipeline was inspired by a public-by-default working model: agents and people working in public channels where the organization can observe, reuse, and learn. The implementation expanded autocapture from a narrow marketing subset to 76 active public channels, excluding a health-check channel. The Slack app received `channels:join` scope so it could join public channels instead of waiting for manual invites.

But the important design is not the channel count. It is the filter.

The pipeline captures only high-signal material: campaigns, metrics, decisions, risks, owners, deadlines, finance, product, operations, and technical context. It ignores social chatter, reactions, DRY-RUN messages, and bots without business terms. Every run updates QMD when it finishes, so captured signals become searchable promptly.

The initial 24-hour backfill captured only 7 messages from finance, marketing, office, and web channels. That is a good sign. A capture layer that grabs hundreds of messages per day from a 35-person company is probably preserving noise.

For a consumer SME, the Slack or Teams pipeline should start with a narrow definition of signal:

| Capture | Ignore |
|---|---|
| Decisions with clear implication | Reactions and acknowledgements |
| Metrics and performance facts | Social chatter |
| Customer complaints or repeated issues | Birthday, lunch, travel, memes |
| Owners, deadlines, blockers | Bot pings without business content |
| Incidents and operational risks | DRY-RUN/test messages |
| Supplier/customer/partner changes | Duplicate reminders |

Only public channels should be indexed by default. DMs and private channels should be excluded unless there is a specific, documented, narrow reason and a higher privacy process. In most companies, you do not need DMs for an operational brain. If your AI operating model depends on private chat mining, your working culture and privacy posture are probably wrong.

The Slack capture tool should also support manual thread capture. Automation catches recurring signals; humans should still be able to say, "This thread is important, capture it." The reference system includes `brain_capture_slack_thread` for that pattern.

## Meet and Gemini notes: decisions from meetings

Many real decisions happen in meetings. If meeting output does not enter the Brain, the Brain will be systematically incomplete.

The reference pipeline uses `meeting-sync.py` to ingest Google Meet/Gemini notes company-wide. It uses Google Admin Directory Domain-Wide Delegation to list active users, searches Google Docs titled `Notes by Gemini` or `Notas de Gemini`, deduplicates by file id, exports text, saves raw, calls `brain_capture`, creates a mirror in `knowledge/meetings/`, and propagates deterministic entities.

The initial result was concrete:

| Metric | Result |
|---|---:|
| Active users scanned | 59 |
| Users with notes | 41 |
| Unique documents found | 228 |
| Documents captured | 228/228 |
| Failures | 0 |

Capture is only phase one. The meeting-intelligence layer then reads `knowledge/meetings/*.md` and promotes durable signals into `knowledge/<company>/meetings-intelligence/`, including `index.md`, `latest.md`, `digests/`, and `domains/`.

Its signal schema includes source, date, domain, type, owner, due date, entities, confidence, sensitivity, and source reference. That schema matters because a meeting note without owner, date, and source can become a vague memory instead of an operational input.

The initial backfill produced:

| Metric | Result |
|---|---:|
| Meeting docs processed | 228/228 |
| Signals extracted | 1043 |
| Signals promoted | 1019 |
| Signals restricted | 24 |

Those numbers show the advantage of separating capture from promotion. The company did not merely dump 228 meeting notes into search. It extracted what was durable, routed sensitive material out of the shared path, and made the promoted layer easier for agents to use.

For a portable implementation, meeting capture should be one of the first unstructured pipelines after public chat. It has a higher signal-to-noise ratio than broad email and less privacy complexity than personal mailboxes. Start with generated meeting notes, not raw audio. Deduplicate by file id. Keep source references. Require a promoted signal to have at least a type, date, source, and confidence.

## Email Intelligence: useful context with hard stops

Email is dangerous because it is high-value and high-risk. It contains supplier changes, agency updates, wholesale negotiations, customer escalations, invoices, legal context, recruiting, payroll, health, family, and private life. A naive email ingest will eventually capture something it should not.

The reference design did not build a mailbox dump. It built Email Intelligence: a pipeline that extracts company context from selected manager accounts with relevance and privacy filters.

The configuration in the changelog used Google Workspace Domain-Wide Delegation, a manager wave of accounts, a base query of `newer_than:30d -in:spam -in:trash`, a maximum of 250 messages per account, a throttle of 10 emails per account per run, and a timer every 2 hours.

Outputs land in:

```text
knowledge/<company>/email-intelligence/index.md
knowledge/<company>/email-intelligence/latest.md
knowledge/<company>/email-intelligence/domains/
knowledge/<company>/email-intelligence/digests/
knowledge/<company>/email-intelligence/sources/
```

The privacy principle is the important part: the origin account is not enough to make a message relevant. A founder's mailbox contains business and non-business material. The pipeline requires company or business markers and has hard stops for HR-sensitive content, recruiting, candidates, CVs, interviews, payroll, health, maternity/paternity, leaves, family, and personal non-work context.

The reference numbers show both value and risk control:

| Run | Result |
|---|---|
| Founder pilot | 250 messages, 552 promoted signals, 79 restricted, 92 ignored |
| Manager wave smoke | 68 messages, 117 signals |
| First production post-privacy | 247 new signals, 0 failures |
| Accumulated state | 485 processed ids, 1048 total signals, 917 promoted, 179 ignored |

The most important event was not a big number. It was a false-positive recovery: a private boat thread was detected and removed, then filters were tightened. That is exactly what you should expect in a live email pipeline. The standard is not "we never make an error." The standard is "we have hard stops, review, removal, and stronger rules after an error."

For Compai readers, start email with a pilot, not a rollout. Use a few founder/operator accounts, narrow recent windows, strict throttles, and explicit hard stops. Do not ingest HR, payroll, health, legal personal, family, recruiting, or private contexts. Do not promote a signal just because it came from a senior person.

## Drive Intelligence: inventory before digestion

Drive is where formal knowledge goes to be forgotten. It is also where overconfident AI systems can hallucinate structure from outdated decks, supplier manuals, draft contracts, invoices, duplicate sheets, and old planning files.

The reference system split Drive into two phases.

Phase 0, `drive-intelligence.py`, is a non-destructive audit. It scans Google Drive via Domain-Wide Delegation across active users, uses a Notion title index as a taxonomy/overlap signal, includes recent docs modified since 2025-01-01, includes older structural exceptions such as contracts, agreements, leases, retail/store, corporate/legal, finance/tax/cash, and suppliers, and excludes or segregates Meet/Gemini notes so it does not duplicate the meeting pipeline.

Outputs include:

```text
knowledge/<company>/drive-intelligence/index.md
knowledge/<company>/drive-intelligence/departments/
knowledge/<company>/drive-intelligence/contracts.md
knowledge/<company>/drive-intelligence/corporate_legal.md
knowledge/<company>/drive-intelligence/retail_projects.md
knowledge/<company>/drive-intelligence/finance_structural.md
knowledge/<company>/drive-intelligence/duplicates.md
knowledge/<company>/drive-intelligence/review-queue.md
knowledge/<company>/drive-intelligence/inventory/YYYY-MM-DD.json
```

The initial inventory audited 1974 unique files: 172 high priority, 412 medium, 149 low, 1184 archive, 48 existing-pipeline items, 9 restricted, 39 duplicate groups, and 0 account errors.

Phase 1, `drive-digest.py`, creates useful summaries from the inventory. It promotes documents only when they have real utility, avoids overinferring manuals, granular invoices, and low-life-span documents, and includes fallback handling for slides. The initial run processed 20 documents, created 20 artifacts, promoted 16, did not promote 4, and had 0 failures. The team also deleted 10 supplier/order manual digests because they over-inferred from material that did not deserve durable memory.

The lesson is simple: inventory before digestion. Do not point an LLM at the whole Drive and ask it to build the brain. First classify, dedupe, restrict, and queue review. Then summarize only the files that are likely to matter.

For a consumer SME, the first Drive pass should focus on current operating documents, contracts, finance structures, retail/store projects, customer-facing policies, product docs, and strategic plans. It should not try to summarize every invoice, every supplier manual, every old deck, or every spreadsheet with unclear ownership.

## Privacy by design

Privacy is not a separate chapter you add after capture works. It is part of the capture layer.

A practical hard-stop list for consumer SMEs should include:

| Category | Default action |
|---|---|
| HR investigations or performance issues | Restrict or exclude |
| Recruiting, candidates, CVs, interviews | Exclude from shared memory |
| Payroll, compensation, personal finance | Exclude or admin-only with legal basis |
| Health, medical, family, maternity/paternity | Hard exclude |
| Legal personal matters | Hard exclude |
| Leaves and absences | Use HR system tool, not open memory |
| Personal emails or private threads | Hard exclude |
| Credentials, secrets, tokens | Redact and alert |
| Customer PII outside approved systems | Tokenize or exclude |

False-positive recovery should be designed before launch. You need a way to remove promoted material, update filters, record the incident, and rerun affected indexes. If your system can only add memory but not correct it, it is not ready for unstructured sources.

The capture layer should also distinguish between raw retention and promoted memory. Some raw material may be useful for audit but should not be broadly searchable. Some promoted signals may be safe because they strip sensitive details. Some sources may be metadata-only. Do not pretend one storage tier can satisfy every privacy need.

## Anti-patterns

The most common capture anti-pattern is volume worship. Teams show how many messages, files, or emails they ingested as if that proves intelligence. It proves only that they can move data.

A second anti-pattern is source flattening. A Slack joke, a signed contract, a founder decision, a meeting action item, and a customer complaint should not all land as equivalent markdown notes. They have different confidence, sensitivity, lifespan, and action requirements.

A third anti-pattern is private-first AI. If every team uses a private agent in DMs, the immediate problem may get solved but the organization learns nothing. Public work, when non-sensitive, creates reusable prompts, observable execution, and shared memory.

A fourth anti-pattern is trusting the LLM to decide privacy alone. Use deterministic hard stops, source allowlists, throttles, review queues, and conservative defaults. The LLM can help classify, but it should not be the only barrier between private employee content and shared memory.

A fifth anti-pattern is failing to route action. A captured decision without a task, owner, output, or world-model update is a note. Notes are useful, but operations need lifecycles.

## Portable 4-pipeline architecture

For Compai readers, a portable capture layer starts with four pipelines:

1. Public chat capture: public channels only, high-signal filtering, manual thread capture, no DMs by default.
2. Meeting notes capture: generated notes, dedupe by document id, raw archive, promoted signal schema with date/source/type/owner/confidence.
3. Email intelligence: small manager pilot, strict hard stops, 30-day windows, throttles, relevance markers, false-positive recovery.
4. Drive intelligence: Phase 0 inventory and classification before Phase 1 digestion, with review queues for high-risk categories.

All four should write through the same `brain_capture` contract. All four should produce source references. All four should update search. All four should have health checks and freshness monitoring.

Do not copy another company's tokens, accounts, Slack channel list, Drive taxonomy, or employee names. Copy the shape: capture where work happens, preserve raw only when useful, promote selectively, route action, audit health, and correct mistakes.

A serious first implementation is 6-8 weeks for a consumer SME with one engineer. The first version does not need every connector. It needs the full loop on a few sources.

If you want help, hello@usecompai.com. Most don't.
