# Chapter 10p: Tasks, outputs, decisions, health — the operating loop

## A wiki does not know what kind of thing it stores

A knowledge base can store a meeting note, a customer complaint, a decision, a draft plan, a finished memo, a bug report, a broken integration, and a task. But unless the system knows the difference between those objects, operations still depend on humans remembering what to do next.

That is the gap Brain v2 closes.

A consumer SME does not need a prettier wiki. It needs an operating loop. When a signal enters the Brain, the system should know whether it is context, a task, an output, a decision, a health issue, or a capability gap. It should know what state that object is in, who owns it, where the source came from, and whether it should refresh the current understanding of the company.

Without lifecycle layers, the Brain stagnates. It can answer questions from stored context, but it cannot manage work. A meeting action item becomes a paragraph in a note. A bug becomes a Slack complaint. A decision becomes something everyone half-remembers. A generated analysis becomes a draft in one person's downloads folder. A broken pipeline stays broken because nobody turned the failure into a tracked health issue.

The reference Brain v2 upgrade added explicit task, output, health, and world-model layers because the company had outgrown a consultive knowledge base. The next step was not more documents. It was state.

This is the minimum operating loop:

```text
source signal -> capture -> classify -> task/output/decision/health/gap -> execute -> record result -> refresh world model
```

A company can implement a simple version in a few weeks, but a trustworthy deployment across live sources usually takes 6-8 weeks with one engineer. The discipline is more important than the tooling. You can start with markdown files and a few MCP tools. What matters is that signals stop dying as notes.

## The filesystem layout

The reference structure is intentionally plain. It uses folders and markdown so humans can inspect the system, agents can write to it, and the company can recover if a fancy interface fails.

The task layout:

```text
knowledge/<company>/_tasks/
  todo/
  handoff/
  review/
  done/
  archived/
```

The output layout:

```text
knowledge/<company>/_outputs/
  drafts/
  briefs/
  plans/
  decisions/
  sent/
```

The health layout:

```text
knowledge/<company>/_health/
  sources/
  jobs/
  issues/
```

The template layout:

```text
knowledge/<company>/_templates/
  task-card.md
  output-record.md
  health-report.md
```

In the reference deployment, these paths lived under `knowledge/<company>/`. For a portable fork, keep the shape and change the namespace. Do not copy company-specific folder names, employees, tokens, or data.

The states are deliberately simple.

`todo` means the task exists and is not yet being actively transferred. `handoff` means work is being passed to a person or agent with enough context to execute. `review` means an output or action needs human or agent review. `done` means the task is completed with a traceable result. `archived` means it is no longer active but should remain available for audit.

Outputs have a different lifecycle. A draft is unfinished work. A brief is a concise analysis or memo. A plan is an execution proposal. A decision is a committed choice with source and implication. Sent means the output left the system: sent to a customer, posted to Slack, delivered to a team, or otherwise used.

Health is separate because broken systems are not tasks in the same sense as business work. A source can be stale, a job can fail, an integration can lose permissions, a search canary can fail, or the world model can go out of date. These are operating-system issues, not normal tasks.

The simplicity is a feature. A founder or COO should be able to open the folders and understand the state of the AI operating layer.

## Templates that force clarity

Templates keep the system from accumulating vague notes.

A task card should answer: what needs to happen, why, who owns it, what source created it, what is the expected output, what is blocked, and what state it is in.

```markdown
# [Task title]

Status: todo
Owner: [person or agent]
Created: [YYYY-MM-DD]
Due: [YYYY-MM-DD or none]
Source: [brain path, Slack URL, meeting note, tool output]
Domain: [cs/ops/finance/marketing/retail/merch/hr/tech]
Sensitivity: [internal/restricted]

## Context

[Why this exists. Include source facts, not only interpretation.]

## Expected output

[What should exist when this is done.]

## Acceptance criteria

- [ ] [Concrete check]
- [ ] [Concrete check]

## Notes

[Execution notes, blockers, links.]
```

An output record should distinguish between draft, plan, brief, decision, and sent artifact. It should cite sources and say whether the output was reviewed.

```markdown
# [Output title]

Kind: [draft/brief/plan/decision/sent]
Status: [draft/reviewed/sent/superseded]
Created: [YYYY-MM-DD]
Owner: [person or agent]
Task: [task path or none]
Sources:
- [brain path or tool output]
Entities:
- [company/project/customer/supplier/etc.]

## Summary

[Short statement of what this output says or does.]

## Content

[The output or link to artifact.]

## Review

Reviewer: [name or none]
Decision: [approved/rejected/needs changes/not reviewed]
```

A health report should make freshness and failures visible.

```markdown
# Health report — [YYYY-MM-DD]

Scope: [source/job/system]
Status: [healthy/degraded/failing/unknown]
Owner: [person or agent]
Last checked: [timestamp]

## Signals

- Freshness: [ok/stale/unknown]
- Failures: [count and last error]
- Search canary: [pass/fail/not run]
- Open gaps: [count]

## Issues

[What is broken or risky.]

## Next action

[Concrete owner/action/date.]
```

These templates are not bureaucracy. They prevent the system from turning important signals into prose that nobody can act on.

## MCP tools for lifecycle state

The reference system added MCP tools for the lifecycle layers:

```text
brain_task_create
brain_task_move
brain_output_record
brain_health_check
```

A portable implementation can start with the same contracts.

`brain_task_create` should create a task card with title, owner, source, domain, sensitivity, expected output, and acceptance criteria. It should not create ownerless work unless the task is explicitly a triage item.

`brain_task_move` should move a task between `todo`, `handoff`, `review`, `done`, and `archived`. The move should preserve history or at least append a state-change note. If a task moves to done, it should link to the output, decision, or source that proves completion.

`brain_output_record` should write a structured record under the appropriate output folder. In the reference system, the tool accepts fields such as title, kind, content, status, task path, sources read, and entities read. That matters because outputs without sources are hard to trust later.

`brain_health_check` should inspect the Brain's own operating state: loose captures, raw without capture, tasks without owner, outputs without source, open gaps, stale world model, and search canary status.

You can implement these tools over plain files first. You do not need a complex task database on day one. The important thing is to make lifecycle transitions explicit enough for agents and humans to inspect.

## Health signals to watch

Health is not optional maintenance. It is part of the operating loop.

The reference Brain v2 health check looked for signals such as:

| Signal | Why it matters |
|---|---|
| Loose captures | Context entered but was not classified or linked |
| Raw without capture | Source material exists but no normalized memory exists |
| Tasks without owner | Work exists but nobody is accountable |
| Tasks without sources | Work cannot be traced to a real signal |
| Outputs without source | An artifact may be ungrounded |
| Outputs without task | Useful work may bypass the operating loop |
| Open capability gaps | The system knows it cannot do something yet |
| Stale world model | Current-state docs no longer reflect reality |
| Search canary failure | Agents may fail to find known knowledge |
| Timer freshness | Capture pipelines may have silently stopped |

The initial observed health in the reference changelog included 253 captures, 252 raw files, 2 done tasks plus 1 todo after registering a world-model/Mac Mini gap, 1 plan output, 3 loose captures, 3 raw without capture, 0 outputs without task, and 1 open capability gap.

Those numbers are not the point. The point is that the system can inspect itself. A Brain without health checks decays quietly. It looks fine until a founder asks a question and receives a stale answer.

For a CEO or COO, health should answer five questions:

1. Are the sources fresh?
2. Are jobs failing?
3. Are signals becoming tasks or outputs?
4. Are outputs grounded in sources?
5. Are known gaps shrinking or accumulating?

If the answer is unknown, the Brain is not operational yet.

## Capability gaps are first-class

A capability gap is a known inability of the system. It should be logged, not hand-waved.

The reference world model added `brain_capability_gap` and recorded a concrete first gap: `skill-propagation-to-mac-mini`. The blocker was SSH failing with `Too many authentication failures`, which prevented skill propagation to Mac Mini agents. The gap created a task at:

```text
knowledge/<company>/_tasks/todo/2026-05-12-capability-gap-skill-propagation-to-mac-mini.md
```

That is the right pattern. Instead of saying "some agents might not have the latest skills," the system recorded the gap, source, blocker, and task.

A portable `brain_capability_gap` tool should capture:

| Field | Purpose |
|---|---|
| gap id | Stable slug for the missing capability |
| description | What the system cannot do |
| impact | Why it matters operationally |
| blocker | Technical, permission, source, or human blocker |
| owner | Who can resolve or triage it |
| source | Where the gap was discovered |
| next action | Concrete unblock step |
| status | open, blocked, resolved, archived |

Capability gaps prevent AI systems from pretending they can do everything. They also give leadership a realistic map of what to fund, fix, or ignore.

## World Model MVP

The world model is the layer that turns operational traces into current company understanding.

The reference MVP created:

```text
knowledge/<company>/_world-model/README.md
knowledge/<company>/_world-model/current-state.md
knowledge/<company>/_world-model/customer-signal.md
knowledge/<company>/_world-model/capabilities.md
knowledge/<company>/_world-model/capability-gaps.md
knowledge/<company>/_world-model/dri-map.md
```

A portable fork should use the same shape under `knowledge/<company>/_world-model/`.

`current-state.md` should say what is true now: current priorities, open operational constraints, major active projects, recent decisions, and known risks. It should not be a quarterly strategy deck copied once and forgotten.

`customer-signal.md` should summarize recurring customer feedback from tickets, reviews, Slack summaries, meeting notes, and support escalations. It should distinguish anecdote from repeated pattern.

`capabilities.md` should list what the AI operating system can currently do: connected tools, read/write permissions, active pipelines, agents, skills, and review flows.

`capability-gaps.md` should list what is missing or broken, with owner and next action.

`dri-map.md` should map domains to directly responsible individuals or teams. Agents need to know who owns finance, CS, retail, merchandising, marketing, operations, HR, and technical infrastructure.

The reference refresh tool, `/usr/local/bin/company-world-model-refresh.py`, is called by `company-world-model-refresh.timer` every Monday at 08:30 Europe/Madrid. The exact timer can change, but weekly refresh is a good baseline. Also allow manual refresh after major events: new integration, reorg, product launch, policy change, or incident.

The world model should be fed by completed tasks, reviewed outputs, decisions, health issues, customer signals, meeting intelligence, email intelligence, Drive digests, and capability gaps. It should not be authored from vibes.

## Decisions need a home

Many companies say they have a decision log. Few use it.

Brain v2 can start with `_outputs/decisions/` as the decision layer. A decision record should include the decision, date, owner, source, alternatives considered if relevant, implications, and follow-up tasks.

A useful decision record is short:

```markdown
# Decision — change return exception policy

Date: 2026-05-12
Owner: COO
Source: knowledge/meetings/2026-05-12-ops-weekly.md
Status: active
Domains: cs, ops, finance

## Decision

[What changed.]

## Why

[Source facts and trade-off.]

## Implications

- [CS macro update]
- [Finance refund reporting impact]
- [Ops exception handling]

## Follow-up tasks

- knowledge/<company>/_tasks/todo/[task].md
```

If `_outputs/decisions/` becomes too broad, create a dedicated decision log later. Do not start with a complex governance tool unless you need it. The initial requirement is traceability.

## For Compai readers

This is the minimum operating loop. Without it, the Brain stagnates.

Start with the filesystem layout, three templates, and four tools: `brain_task_create`, `brain_task_move`, `brain_output_record`, and `brain_health_check`. Add `brain_capability_gap` and `brain_world_model_refresh` as soon as the first pipelines are live.

Do not wait for perfect automation. A markdown task card written by an agent is enough to start. A weekly health report is enough to reveal decay. A simple world model is enough to stop every agent from rediscovering the same company state.

For a consumer SME with one engineer, the lifecycle layer can be built early in the 6-8 week rollout. Build it before you scale capture. If you capture from Slack, Meet, Email, and Drive without task/output/health/world-model routing, you will create a searchable archive, not an AI operating system.

## Review cadence

The loop needs a calendar. Otherwise the folders exist, but nobody uses them to steer the company. A practical cadence is lightweight: daily task review for active domains, weekly health review, weekly world-model refresh, and monthly cleanup of archived or stale items.

Daily review does not need a meeting. An agent or operator can scan `_tasks/todo`, `_tasks/review`, and `_health/issues`, then post a short summary in the public AI or operations channel. The goal is to surface ownerless tasks, blocked handoffs, and outputs waiting for review.

Weekly health review should check source freshness and pipeline failures. Are Slack captures still running? Did meeting sync process new notes? Is email intelligence failing silently? Did Drive digest overpromote low-value files? Did the search canary pass? This review is where the Brain stays trustworthy.

Monthly cleanup prevents the system from becoming cluttered. Archive tasks that are no longer relevant, mark superseded outputs, close resolved gaps, and update templates when repeated mistakes appear. A living brain needs pruning as much as capture.

## Human approval gates

Lifecycle state does not mean autonomous execution everywhere. Some tasks should remain draft-only or review-required: refunds, discounts, payroll, HR, legal, high-value supplier commitments, paid media budget changes, customer compensation, and public external communications.

The task card should make the approval gate explicit. If an agent can draft but not send, say so. If a human must approve a decision before the output moves to `sent`, say who. This keeps the operating loop useful without pretending every workflow is safe for full autonomy.

## Start smaller than you think

The first version can be almost embarrassingly simple. One task folder, one output folder, one health report, and one weekly review already change behavior. The mistake is waiting for a perfect workflow UI before enforcing state. Agents are good at writing structured markdown. Humans are good at reading it. Use that.

Add sophistication only when the pain is real: labels when search is hard, a dashboard when weekly review becomes slow, stricter schemas when agents write inconsistent cards, and database-backed state when file operations become a bottleneck. Most consumer SMEs will get months of value before they need more than files, templates, and a few tools.

The principle is state before scale. If the team cannot see task state, output state, and system health on a small corpus, adding more capture sources will only hide the problem under more text.

If you want help, hello@usecompai.com. Most don't.
