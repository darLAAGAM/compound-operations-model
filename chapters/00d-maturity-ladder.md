# Chapter 00d: The Capability Maturity Ladder

## Autonomy is not one thing

Most AI conversations collapse into a bad binary: manual or autonomous.

That is not how real companies work. A customer-service reply, invoice classification, paid-media budget change, product reorder, payroll correction, and supplier payment do not deserve the same autonomy level.

Use a ladder. Map each capability honestly. Then move one rung at a time.

This chapter adapts Sarah Tavel's L0-L5 autonomy framing to the company brain. The important move is to assess capabilities, not agents. A finance agent might be L3 for invoice extraction, L2 for cash forecasting, and L0 for executing payments. A marketing agent might be L3 for campaign analysis and L1 for budget changes.

## The ladder

| Level | Name | What it means | Example |
|---:|---|---|---|
| L0 | Manual | AI is not involved | A human checks a supplier invoice and files the PDF |
| L1 | Assistant | AI helps, human drives | AI summarizes invoice fields; human copies them into accounting |
| L2 | Draft-only | AI drafts output, human approves before use | AI drafts a customer reply or weekly trading note |
| L3 | Human-approved action | AI prepares and queues an action; human approves execution | AI creates a refund draft, budget recommendation, or purchase order for approval |
| L4 | Bounded autonomy | AI executes within explicit limits and logs everything | AI sends tracking replies under high confidence or files low-risk invoices |
| L5 | Full autonomy | AI owns the workflow end to end, including exceptions | Rare in SMEs today; requires monitoring, rollback, and governance |

The reference brand maps mostly around L2-L3 today. That is the honest answer. There are pockets of L4 for bounded, low-risk, repeatable work. There is no serious claim of broad L5 autonomy.

## Why the brain changes the ladder

Without a brain, most AI work gets stuck at L1. The model can help, but it does not know your policy, inventory logic, customer tiers, supplier quirks, or accounting rules.

With a brain, L2 becomes practical. The AI can draft from source-of-truth documents. It can cite policy. It can explain confidence. It can write a decision note back.

With tools, L3 becomes practical. The AI can prepare the action in the system that matters: refund draft, order note, calendar event, invoice row, campaign brief, purchase-order check.

With logs, guardrails, and narrow thresholds, L4 becomes possible for specific workflows.

The ladder is not about model intelligence. It is about context, permissions, blast radius, and review design.

## Capability map

Start with a table like this:

| Capability | Current level | Safe next level | Why |
|---|---:|---:|---|
| Answer policy questions internally | L2 | L3 | Can cite brain docs; low external risk |
| Draft customer tracking replies | L2 | L4 for high confidence | Structured data, repetitive, reversible if tone is right |
| Approve refunds | L1 | L3 | Money movement and abuse risk require approval |
| Classify invoices | L2 | L4 for low-risk suppliers | Strong fields, review queue, no payment execution |
| Execute supplier payments | L0 | L1 | High financial risk; keep human-owned |
| Daily paid-media summary | L2 | L3 | Analysis can be queued; budget action needs approval |
| Increase ad budgets | L0-L1 | L3 | Requires dynamic margin checks and spend caps |
| Reorder inventory | L1 | L3 | Demand, lead time, cash, and supplier constraints |
| Publish product pages | L1 | L3 | Claims, pricing, legal, stock, creative must be reviewed |
| Create operational calendar events | L2 | L4 | Low-risk if read-only calendar and clear source docs |

For a beauty business, claims and ingredients keep autonomy lower. For food, allergens and batch traceability do the same. For home, warranty and safety claims matter. For pet, veterinary or safety language raises the bar. For outdoor, technical use claims and liability matter. The same ladder applies, but the risk boundary moves.

## Read-only versus draft-only versus action

Do not jump from “AI can answer” to “AI can act.”

Use four gates:

1. **Read-only:** The AI can search, summarize, and cite. No writes.
2. **Draft-only:** The AI can produce a draft in a review queue. No external send.
3. **Human-approved action:** The AI can prepare system changes, but a human clicks approve.
4. **Bounded autonomous action:** The AI can execute only inside explicit thresholds.

Each gate needs evidence.

Read-only needs retrieval accuracy. Draft-only needs output quality. Human-approved action needs system integration and clear approval UI. Bounded autonomy needs monitoring, rollback, audit logs, and a clear stop condition.

## Autonomy requires boring controls

The maturity ladder is only useful if it changes behavior.

For each capability, define:

- Owner.
- Source of truth.
- Allowed tools.
- Write permissions.
- Confidence threshold.
- Human approval rule.
- Rollback or correction path.
- Audit log location.
- What failures look like.

This is not bureaucracy. It is how you keep AI from becoming a pile of impressive demos nobody trusts.

## Common mistakes

The first mistake is mapping the whole company to one level. That produces nonsense.

The second mistake is mistaking frequency for safety. A task can be frequent and still risky. Refunds, discount codes, claims, payroll, and budget changes happen often. That does not mean they should be autonomous.

The third mistake is using “human in the loop” as a magic phrase. A rushed human approving unread drafts is not a control. The review step must show the source docs, proposed action, confidence, and reason for escalation.

The fourth mistake is refusing L4 everywhere. Some tasks are safe to automate once measured: filing documents, creating calendar events, sending internal digests, routing tickets, tagging invoices, capturing expiring social mentions, or posting low-risk internal updates.

## The reference position

The current reference deployment is AI-native in operating behavior, not fully autonomous. The brain is real. Tools are real. Domain agents are real. Review queues are real. The system has survived production incidents.

But the company is still not broadly L4. Non-technical employees cannot extend every connector or skill alone. Some workflows still need manual exports. Some auth is still migrating. Some docs contradict older snapshots. Those are not embarrassing details. They are the difference between a credible operating system and a marketing claim.

## How to start this in your business

1. List 20 workflows where AI already helps or could help: customer replies, invoice intake, campaign analysis, replenishment, returns, calendar sync, supplier follow-up.
2. Assign each workflow an L0-L5 level based on what happens today, not what you want to be true.
3. Pick three L2 workflows and design the L3 approval step: source docs, proposed action, owner, approval button or checklist, audit log.
4. Pick one low-risk workflow that could become bounded L4 after 30 days of reviewed outputs.
5. Fork `templates/autonomy-assessment.md` as the artifact and review it monthly.

