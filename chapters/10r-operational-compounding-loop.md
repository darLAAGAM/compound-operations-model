# Chapter 10r: Operational Compounding Loop

## The June 2026 Upgrade: From Memory to Operating Cadence

Brain v2 made the company memory bidirectional. The next step was making that memory operationally accountable.

A living brain is only useful if it can answer four questions every week:

1. What new signal came in?
2. What should become a task, skill, workflow, or decision?
3. What is stale, broken, or missing metadata?
4. Which repeated workflows are ready to become semi-autonomous action queues?

The reference deployment now runs that loop as an executable operating cadence, not as a manual review.

---

## The Loop

```text
Raw signal
  -> inbox triage
  -> promoted memory
  -> task / output / decision / gotcha
  -> skill or workflow packaging
  -> L3 action queue
  -> health audit
  -> shared memory contract
  -> next run
```

This is the difference between a knowledge base and a compounding operating system. A knowledge base stores answers. An operating system detects work, packages repeatable work, routes it to owners, and audits whether the memory is still trustworthy.

---

## What Changed in the Reference Deployment

On 2026-06-08, the reference deployment ran a full AI-native ops rollup across Brain health, inbox triage, skill packaging, shared memory, L3 action queues, and workflow mining.

The useful lesson is not the exact number. The useful lesson is the shape of the control plane:

| Layer | What it checks | Why it matters |
|---|---|---|
| Brain health audit | Missing owner, source, verification date, stale date | Prevents old docs from becoming false authority |
| Brain inbox sweeper | Raw items processed, skipped, converted to writes, tasks, skills | Keeps capture pipelines from becoming a junk drawer |
| Skill eval harness | Skill clarity, trigger quality, output contract, verification | Makes skills reliable enough for non-technical operators |
| Skillify loop | Repeated patterns that deserve a skill, automation, or queue | Turns repeated work into reusable company capability |
| Shared memory contract | Schemas for decisions, tasks, gotchas, tools, workflows, raw signals | Keeps agents from storing incompatible private memories |
| L3 action queues | Human-approved operational queues for repeatable actions | Moves from advice to controlled execution |
| Workflow mining | Candidate workflows with owner, metric, and approval telemetry | Finds where agentic operations should go next |

The rollup found exactly the kind of uncomfortable truth a good operating system should find: memory quality was not good enough, skill quality was uneven, and some proposed workflows were not packaged yet. That is not a failure. That is the point of the loop.

---

## Shared Memory Contract

Private agent memory is useful, but it becomes dangerous when it diverges from the shared Brain.

The portable rule is simple:

- Shared Brain is canonical.
- Private memory must sync back or be marked local-only.
- Every durable memory needs source paths and confidence.
- Operational facts prefer source systems over old docs.
- Actions require audit trail and owner.

The reference contract uses six memory record types:

| Type | Writes to | Required fields |
|---|---|---|
| Decision | `knowledge/platform/memory/decisions/` | id, date, owner, decision, rationale, source_paths, confidence |
| Task | `knowledge/<company>/_tasks/` | id, title, owner, priority, status, source_paths, definition_of_done |
| Gotcha | `knowledge/platform/gotchas/` | id, date, system, symptom, root_cause, workaround, fix_status |
| Tool behavior | `knowledge/platform/tools/` | id, tool, observed_at, input, output, failure_mode, confidence |
| Workflow state | `knowledge/platform/workflows/` | id, workflow, owner, state, last_run, artifacts, next_action |
| Raw signal | `knowledge/platform/brain-inbox/raw/` | id, source_type, source_ref, captured_at, raw_excerpt, triage_status |

If a client implementation copies only one thing from this chapter, copy this contract. It keeps every agent, script, and human-facing AI client writing memory in the same shape.

---

## Skillify Loop

The reference system now audits repeated work and asks whether it should become a reusable capability.

Decision rule:

- If it happened once, document it only if it changed a decision or exposed a gotcha.
- If it happened twice and has stable inputs, propose a skill or automation.
- If it has an owner, metric, approval path, and repeatable action, consider an L3 action queue.
- If it is sensitive, ambiguous, or weakly evidenced, keep it as a proposal, not automation.

The June rollup produced five packaging outcomes:

| Capability | Form | Status |
|---|---|---|
| X likes intelligence | automation + skill | created |
| Brain inbox sweeper | skill | created |
| Skill eval harness | skill | created |
| L3 action queue | skill | proposed |
| Workflow mining | skill | proposed |

This is how an AI-native company compounds without waiting for a quarterly transformation project. The system watches the work and packages the repeated parts.

---

## L3 Action Queues

L3 does not mean "agent acts without control." It means a queue of proposed actions where the human approval surface is explicit.

A good L3 queue has:

- owner
- source paths
- proposed action
- confidence
- risk class
- approval button or equivalent decision path
- metric after execution
- audit trail

The first reference queues were:

| Queue | Owner domain | Example action |
|---|---|---|
| CS resolution queue | Customer Service | Draft resolution for repeated support cases |
| Finance invoice QA queue | Finance | Flag invoice anomalies before booking |
| Marketing/Merch action queue | Marketing + Merchandising | Suggest stock-aware campaign or product action |

For a client deployment, start with queues where mistakes are reversible and review is cheap. Do not start with high-risk HR, legal, payments, or irreversible customer actions.

---

## Workflow Mining Candidates

Workflow mining is the discipline of finding repeatable work that has enough structure to become an agent-assisted workflow.

The June candidates in the reference deployment were:

| Workflow | Owner | Metric |
|---|---|---|
| CS lead to resolution | CS | time saved, error reduction, approved action rate |
| Invoice intake QA | Finance | time saved, error reduction, approved action rate |
| Stock-aware marketing action | Marketing/Merch | time saved, revenue/cost impact, approved action rate |
| Supplier follow-up tracker | Merch/Ops | time saved, fewer missed follow-ups |
| Weekly CEO intelligence digest | Strategy | decision speed, context quality |
| Retail issue escalation | Retail | resolution time, fewer repeated issues |
| Returns reason analysis | CS/Product | product feedback quality, fewer repeated returns |
| SEO opportunity queue | Digital | ranked opportunities shipped |
| Cash anomaly monitor | Finance | anomaly detection latency |
| Meeting-to-work loop | Platform | decisions converted to tasks/outputs |

The portable method is more important than the list:

1. Identify repeated workflow.
2. Assign owner.
3. Define metric.
4. Require source paths.
5. Create review queue before automation.
6. Measure approved action rate for two weeks.
7. Only then increase autonomy.

---

## Porting Checklist

To add this layer to a new Compai deployment:

- [ ] Define memory schemas before agents start writing durable facts.
- [ ] Add frontmatter requirements: owner, source_of_truth, last_verified, stale_after, confidence.
- [ ] Run a weekly Brain health audit.
- [ ] Run an inbox sweeper over raw captures.
- [ ] Add a skill evaluation harness before scaling skills to non-technical teams.
- [ ] Run skillify monthly or after any heavy operating sprint.
- [ ] Create L3 queues only for reversible, owner-approved workflows.
- [ ] Track approved action rate, not just time saved.
- [ ] Write every new gotcha back to the Brain.

---

## The Real Lesson

Most AI operating systems fail quietly. They do not crash. They just become stale, private, and untrusted.

The operational compounding loop exists to prevent that. It makes the system inspect itself, package what repeats, expose what is stale, and keep the shared Brain ahead of the private memories around it.

That is what makes month six different from month one.
