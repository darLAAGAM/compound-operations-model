# Chapter 10l: Brain v2 — from wiki to operational memory

## A wiki is not memory

Most companies already have a knowledge base. It may be Notion, Google Drive, Confluence, a folder of SOPs, a Slack channel full of pins, or a set of docs maintained by one unusually disciplined operator. That is useful, but it is not operational memory.

A wiki stores what someone decided to write down. Operational memory learns from work while the work is happening.

The difference matters because the most valuable knowledge in a consumer SME is rarely born as a polished document. It appears in the messy middle of operations: a founder answering a customer escalation, a finance lead explaining why the P&L looks wrong, a merchandiser spotting a stockout pattern, a store manager reporting a staff issue, a supplier changing lead times in an email thread, or a Monday meeting where a real decision gets made and never translated into a SOP.

A wiki can answer, "What did we document?" A living brain can answer, "What has the company learned recently, where did it come from, what should happen next, and what is now outdated?"

That is the conceptual leap behind Brain v2. The goal is not more documents. The goal is a bidirectional operating layer that captures real work, promotes useful signals, creates tasks and outputs, tracks health, refreshes the company model, and lets agents write back after they learn or execute something.

The reference implementation took months because it was built inside a real company with live tools, existing habits, privacy constraints, and plenty of false starts. A consumer SME starting from the open-source pattern should plan for 6-8 weeks with one strong engineer or technical operator to reach a serious first version. You can get a demo running faster. You cannot get trustworthy operational memory in a few rushed days without skipping the parts that make it trustworthy.

## The leap: consultive to bidirectional

A consultive brain is a library. The agent searches it, reads a document, and answers. That is already better than a generic chatbot, because the answer is grounded in company context.

But a consultive brain has a one-way failure mode: every agent can consume context, yet the company does not automatically get smarter from the work the agent just did. The founder still has to remember to update the doc. The operator still has to turn the meeting decision into a task. The engineer still has to write down the bug. The finance lead still has to document that the source-of-truth metric changed.

Brain v2 moves from read-only context to write-back. The agent is expected to leave a trace when something durable happened.

That trace can be a captured signal, a task card, a decision output, a health issue, a capability gap, or a world-model update. The important point is that the agent does not just solve the immediate prompt. It helps maintain the operating memory of the company.

The reference Brain v2 changelog, dated 2026-05-12, described the shift this way: before, the Brain was primarily consultive. Context depended on the founder or an agent explicitly writing a document. Private interactions disappeared from collective learning. Outputs had no lifecycle. After the upgrade, the Brain became a memory layer with capture pipelines from Slack, Meet/Gemini, Gmail, Drive, and manual capture; a distinction between raw input, promoted signal, task, output, and world model; and write-back through MCP tools and skills.

That is not a cosmetic change. It changes what an AI system can do inside a company.

A customer-service agent can now draft a reply and record that a new pattern is appearing in tickets. A finance agent can produce an analysis and record the output as a reviewed brief. An operations agent can detect a recurring vendor issue and create a task with owner, source, and next action. A founder can ask about the current state of the company and receive an answer shaped by recent work, not only by the last formal strategy document.

For a non-technical CEO or COO, the useful test is simple: if the AI disappeared tomorrow, would the company retain what the AI learned while doing the work? If the answer is no, you have a chatbot with context. If the answer is yes, you are closer to operational memory.

## The five functions of a living brain

The Brain v2 changelog defines a living brain with five functions. They are worth keeping as the operating checklist, because they prevent the system from becoming a smarter file dump.

First, it captures work from the places where work already happens. That means Slack or Teams, meeting notes, email, Drive or Docs, helpdesk, ecommerce, accounting, and the manual notes operators already create. The point is not to centralize every byte. The point is to avoid making memory depend on someone remembering to copy-paste context into a wiki after the fact.

Second, it preserves raw input when raw input is useful for audit. Raw input is not always promoted, and it is not always exposed to every agent. But for certain workflows, especially meeting notes, email intelligence, and tool outputs, it matters to know where a signal came from. In the reference system, `brain_capture` can write raw material under `knowledge/<company>/_raw/YYYY-MM-DD/` and normalized captures under `knowledge/<company>/_inbox/YYYY-MM-DD/`. That separation is intentional.

Third, it promotes signals with criteria. Promotion is the line between "the company saw this" and "the company should remember this." Good signals include decisions, owners, deadlines, risks, metrics, customer feedback, incidents, supplier changes, and new operating rules. Bad signals include social chatter, duplicated summaries, low-value operational noise, personal topics, and anything sensitive that does not belong in shared memory.

Fourth, it converts signals into the right lifecycle object: task, output, decision, health issue, capability gap, or world-model fact. This is where many knowledge systems fail. They store a useful note but do not decide what kind of thing it is. A task needs an owner and state. A decision needs source and implication. A health issue needs status and failure mode. A capability gap needs a blocker and a path to unblock. A world-model fact needs refresh cadence and confidence.

Fifth, it refreshes and audits itself with timers, canaries, and health checks. The reference system uses `brain-qmd-update.timer` every roughly 15 minutes for search freshness, `brain-slack-autocapture.timer` hourly, `meeting-sync.timer` and `meeting-intelligence.timer` every 2 hours, `email-intelligence.timer` every 2 hours, and `company-world-model-refresh.timer` weekly on Monday 08:30 Europe/Madrid. This is the unglamorous part, but it is what keeps the brain from decaying silently.

Those five functions are the minimum standard. If one is missing, the system can still be useful, but it is not yet a living operational memory.

## What changed in the reference week

The 2026-05-12 Brain v2 changelog is useful because it shows what an upgrade looks like in concrete terms. It was not a rebrand. It was a set of operational layers added around the existing brain.

Findability was hardened first. `brain_search` and `brain_query` were aligned on QMD lexical/BM25 with substring fallback. Hybrid/vector search was deliberately not the default because native dependencies introduced noise and operational risk. A QMD update timer was enabled every 15 minutes, backed by `/usr/local/bin/company-brain-qmd-update.sh` and a canary script at `/usr/local/bin/company-brain-qmd-canary.py`. A previous canary result was 20/20. That kind of boring reliability matters more than impressive retrieval language.

An action ledger was added at `/var/lib/company/action-ledger.jsonl` so mutating actions could be traced. Auth observe was introduced for MCP callers: not a hard break for existing clients, but telemetry on who was calling what. That is the right transitional move for a live company. You do not lock everyone out to improve attribution. You observe first, then tighten.

`brain_capture` became the universal contract for turning context into memory. It writes to inbox, optional raw storage, capture indexes, entity files, and tasks when the signal is actionable. The company then expanded capture beyond manually written documents.

Slack autocapture moved from a narrow subset to 76 active public channels, excluding a health-check channel, with high-signal filtering. It ignores chatter, reactions, DRY-RUN messages, and bots without business terms. The first backfill captured 7 messages from the previous 24 hours across finance, marketing, office, and web channels. That number is intentionally low: the point is not "capture everything." The point is selective memory.

Meet/Gemini notes became a company-wide source. The meeting sync scanned 59 active users, found 41 users with notes, captured 228 unique documents, and had 0 failures. The meeting intelligence layer then processed those 228 docs, extracted 1043 signals, promoted 1019, and restricted 24. That is the difference between storage and intelligence: the system did not just copy notes; it classified durable signals.

Email Intelligence processed Gmail with hard privacy stops. In the pilot, 250 messages produced 552 promoted signals, 79 restricted, 92 ignored, and 0 failures after recovery. A manager wave processed 68 messages and found 117 signals. The accumulated state in the changelog was 485 processed ids, 1048 total signals, 917 promoted, and 179 ignored. The important detail is the false-positive recovery: a private boat thread was detected, removed, and filters were tightened. Any serious email pipeline needs that humility.

Drive Intelligence audited 1974 files across active users and classified them: 172 high priority, 412 medium, 149 low, 1184 archive, 48 already covered by existing pipelines, 9 restricted, 39 duplicate groups, and 0 account errors. Drive Digest then processed 20 documents, created 20 artifacts, promoted 16, and removed 10 supplier/order manual digests that were over-inferred. Again, promotion quality mattered more than volume.

Tasks, outputs, health, and world model were added as explicit filesystem layers. The system created `_tasks/todo`, `_tasks/handoff`, `_tasks/review`, `_tasks/done`, `_tasks/archived`, `_outputs/drafts`, `_outputs/briefs`, `_outputs/plans`, `_outputs/decisions`, `_outputs/sent`, `_health/sources`, `_health/jobs`, `_health/issues`, templates, and MCP tools such as `brain_task_create`, `brain_task_move`, `brain_output_record`, and `brain_health_check`. The world model added `current-state.md`, `customer-signal.md`, `capabilities.md`, `capability-gaps.md`, and `dri-map.md`.

Finally, onboarding caught up with the architecture: one-command Claude Desktop setup, a canonical master prompt v1.7, and onboarding rules that make every employee enter the same operating contract.

The reference week changed the Brain from a place to search into a system that captures, classifies, acts, and audits.

## The operating model: raw to world model

The simplest way to explain Brain v2 is the pipeline:

```text
raw -> inbox -> promoted signal -> task/output/decision/health -> world model
```

Raw is the original or near-original material: meeting note export, email metadata and body when allowed, Drive inventory record, Slack thread, tool output, or a manual operator note. Raw is not the same as shared knowledge. It may have a narrower audience, a retention period, or no promotion at all.

Inbox is the normalized capture. It should have a title, source type, source reference, date, author or source owner, domains, sensitivity, body, and explicit entities. This is where `brain_capture` creates a document the rest of the system can reason over.

Promoted signal is the durable extract. A meeting note might contain two decisions, one owner, one risk, and twenty lines of irrelevant discussion. A living brain promotes the two decisions, owner, and risk, not the entire transcript as if every sentence deserves equal weight.

Task, output, decision, and health layers turn signal into operations. If the signal says "supplier lead times changed," it may become a task for operations. If it says "we approved the new returns policy," it may become a decision record and an update to the customer-service source of truth. If it says "email timer is not appearing in list-timers," it becomes a health issue. If it says "skill propagation to Mac Mini is blocked by SSH Too many authentication failures," it becomes a capability gap.

The world model is the current representation of the company: what is true now, what customers are saying, which capabilities exist, which gaps block execution, and who is responsible for what. The world model should not be hand-written strategy theater. It should refresh from tasks, outputs, health, customer signals, source digests, and capability gaps.

This pipeline is what makes month six qualitatively different from month one.

In month one, the system can answer from the documents you seeded. It can draft, summarize, and search. That is valuable, but brittle. The answer quality depends heavily on the initial corpus and the discipline of a few people.

By month six, if the loop is working, the system has seen hundreds of real company interactions. It has a record of decisions, false starts, operational bugs, source-of-truth rules, privacy exceptions, customer patterns, and recurring tasks. Agents can stop asking beginner questions because the company has taught them through use. Not by magic, and not because another company's deployment made them smarter. Each fork is independent. The compounding happens inside one company when its own public work, write-back, and review loops accumulate.

This is also why shortcuts are dangerous. A company can import 10,000 documents and still have a bad brain if it has no promotion layer, no task lifecycle, no health checks, and no write-back. Another company can start with 200 high-quality captures and become operationally useful if every signal is classified and acted on.

## Risks and limits

Brain v2 adds power, but it also adds risk. The changelog is clear about the current limits, and a portable implementation should keep them visible.

The technical risks start with dependencies. Capture pipelines rely on Google Workspace Domain-Wide Delegation, Slack scopes, live credentials, and timers. If Workspace permissions change, meeting and email pipelines can fail. If Slack scopes drift, autocapture can silently lose coverage. If timers do not appear in `systemctl list-timers`, the system may look healthy while freshness decays. The reference changelog specifically noted that `email-intelligence.timer` needed monitoring if it failed to show the next execution.

Search can also fail quietly. The reference system chose QMD lexical/BM25 as the stable baseline and kept hybrid/vector out of the default path because native dependencies were noisy. This is the right trade-off for a CEO/COO audience: boring search that works beats impressive retrieval that fails under CMake, Vulkan, or local model dependency issues.

Quality risks are larger than technical risks. Drive Digest can overinfer from documents that are operational but not strategic. Email Intelligence can promote private or irrelevant material if privacy filters are weak. Slack autocapture can turn social noise into durable memory if the high-signal filter is too broad. Meeting Intelligence can promote an action item without enough source context if the schema is loose.

The reference system had one important recovery pattern: when the email pilot found a false positive private thread, it removed it and tightened filters. A living brain needs that kind of reversal path. Privacy-by-design does not mean you will never make a mistake. It means the system has hard stops, review queues, audit trails, and a way to correct mistakes without pretending they did not happen.

Organizational risks matter too. If everyone continues working in private DMs, the brain will miss the real operating layer. If agents do not write outputs and tasks back to the Brain, the system becomes read-only again. If no one reviews health and gaps, the Brain accumulates broken assumptions.

For a consumer SME, the practical governance is simple:

1. Start with public, work-related sources.
2. Promote selectively.
3. Keep sensitive categories out by default.
4. Assign an owner to every recurring pipeline.
5. Review health weekly.
6. Require agents to record meaningful outputs and gaps.

That is enough to start. It is not enough to run forever without maintenance.

## For Compai readers

The pattern is portable. The company-specific tokens are not.

Do copy the operating shape: `brain_capture`, raw/inbox/promoted separation, task and output lifecycles, health checks, world model, action ledger, search canary, setup script, and master prompt. Do not copy private company data, employee lists, Slack scopes, Drive folders, Gmail accounts, MCP tokens, or paths that assume one company's taxonomy.

In the reference system, many paths live under `knowledge/<company>/`, such as `knowledge/<company>/_inbox/`, `knowledge/<company>/_raw/`, `knowledge/<company>/_tasks/`, `knowledge/<company>/_outputs/`, `_health`, and `_world-model`. In your fork, those become `knowledge/<company>/...` or whatever namespace your operating model uses. The path shape matters more than the name.

A realistic first deployment for a consumer SME is 6-8 weeks with one engineer or technical operator. Week one is base brain, search, write tools, action ledger, and source-of-truth rules. Week two is capture, task/output/health templates, and employee setup. Weeks three and four are public chat and meetings. Weeks five and six are email and Drive with stricter privacy review. Weeks seven and eight are world model, health dashboard, and habit reinforcement.

You can compress or expand that timeline based on your stack, but do not remove the lifecycle layers. Without them, you have a better wiki, not operational memory.

If you want help, hello@usecompai.com. Most don't.
