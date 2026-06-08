# Chapter 10g: The Knowledge Mining Loop — From Memory to Durable Skills

## Storage is not learning

A company brain can still fail if it only stores information.

Learning requires promotion. Something happens today. The system captures it in memory. Later, a human or agent decides whether it should become a durable policy, skill, pattern, checklist, or incident lesson.

Without that loop, memory becomes a chronological landfill. Agents can search it, but they cannot reliably know what is still true.

Knowledge Mining is the loop that turns short-term memory into durable operating knowledge.

## The layers

```text
memory/
  2026-05-12.md
    raw notes, incidents, decisions, tool quirks, examples

          |
          v

mining review
  extract durable lessons
  classify by domain
  dedupe against existing docs
  choose destination

          |
          v

knowledge/
  policies/
  operations/
  finance/
  marketing/
  product/
  lessons/

skills/
  executable procedures

patterns/
  anonymized reusable rules
```

Memory is the inbox. Knowledge is the library. Skills are the operating procedures. Patterns are reusable intelligence.

## The daily cron

A practical daily mining cron does five things:

1. Reads the last 24-72 hours of `memory/`.
2. Extracts candidate learnings: decisions, bugs, exceptions, API quirks, repeated customer issues, supplier changes, campaign findings.
3. Classifies each candidate by domain and durability.
4. Checks whether an existing doc or skill already covers it.
5. Drafts updates for human review or writes low-risk learnings to the correct location.

The output should be boring:

```text
Daily mining summary

New candidate learnings: 12
Promoted to knowledge docs: 3
Promoted to skills: 1
Promoted to pattern candidates: 2
Rejected as noise: 4
Needs owner review: 2
```

If the cron cannot explain what changed, it is not a learning loop. It is a background process.

## The `/learn` habit

Automation works better after the team builds a manual habit.

The `/learn` workflow is the low-friction way to capture something while it is fresh:

```text
/learn
category: api_gotcha
domain: finance
title: Accounting export omits draft invoices
content: The export endpoint excludes draft supplier invoices unless status=draft is passed. This caused the invoice intake check to undercount pending bills.
destination: knowledge/finance/invoice-rules.md
```

A good learning note has:

- What happened.
- Why it matters.
- Where it applies.
- Where it does not apply.
- Source or evidence.
- Suggested destination.

The repo includes `templates/learn-skill-template.md` as the starter artifact.

## `brain_learn`

The tool version of `/learn` removes routing friction. Instead of asking a user to know the folder structure, it accepts structured fields and writes to the right place.

Useful fields:

| Field | Why it matters |
|---|---|
| Category | Bug, decision, pattern, policy update, API gotcha, incident, example |
| Domain | Finance, CS, operations, marketing, product, retail, people, platform |
| Title | Searchable summary |
| Content | The actual learning |
| Evidence | Link, ticket, log, report, or human owner |
| Suggested destination | Optional path |
| Confidence | High, medium, low |
| Review owner | Who decides if this becomes durable |

This is where non-technical employees can participate. They do not need to know Git. They need to know what changed.

## Weekly digest

Daily mining catches facts. Weekly digest creates judgment.

A weekly digest should include:

- Top learnings promoted.
- Candidate learnings awaiting review.
- Docs updated.
- Skills changed.
- Patterns proposed.
- Incidents closed.
- Contradictions found.
- Stale docs that need owners.
- Search queries with poor results.

The last item is underrated. If employees keep searching for something and failing, the brain is missing a concept or using the wrong language.

## Routing rules

The hardest part of mining is deciding where a learning belongs.

Use simple routing rules:

| Learning type | Destination |
|---|---|
| Temporary observation | `memory/YYYY-MM-DD.md` |
| Stable company fact | `knowledge/<domain>/` |
| Repeatable procedure | `skills/` |
| Reusable anonymized workflow | `patterns/` |
| Incident or production failure | `lessons/` |
| Personal preference or working style | private/person-specific memory |

Examples:

- “Carrier X is delayed today” belongs in memory.
- “Carrier X requires a different claims flow for damaged parcels” belongs in operations knowledge.
- “How to file a damaged-parcel claim” belongs as a skill.
- “Damaged-parcel claims need photo evidence before refund approval” may become a pattern.
- “The claims API silently changed response fields” belongs in lessons and integration notes.

This routing keeps the brain from becoming one giant notes folder.

## Dedupe before promotion

Mining should always check existing docs before writing new ones. Many contradictions come from adding a fresh file instead of updating the old source of truth.

The safer procedure:

1. Search for the topic.
2. If a source doc exists, patch it.
3. If several docs conflict, create a review item instead of choosing silently.
4. If no doc exists, create a new one with owner and date.

This is especially important for policies, margins, claims, safety language, returns, and supplier rules. Duplicate knowledge is how agents become confidently wrong.

## What becomes a skill

Not every learning deserves a skill. A skill is for repeatable execution.

Promote to a skill when:

- The workflow happens repeatedly.
- The inputs are clear.
- The output format is clear.
- The decision rules can be written down.
- The failure cases can be escalated.

Examples:

- Food: classify supplier invoice and route cold-chain exceptions.
- Beauty: review product claims before publishing copy.
- Home: triage warranty claim with photo evidence.
- Pet: decide whether a subscription change is safe to process automatically.
- Outdoor: classify warranty request by use case, purchase date, and product category.

If the workflow is still ambiguous, keep it as a doc or checklist first.

## Limitations

Mining can produce junk. LLMs can over-summarize, promote anecdotes, or miss the operational nuance. Daily memory can contain stale assumptions. Human reviewers can approve too quickly.

The control is simple: every promoted learning needs a destination, owner, confidence, and date. Every skill needs test examples. Every pattern needs limitations.

## How to start this in your business

1. Create `memory/YYYY-MM-DD.md` and make the team capture five learnings per week: bugs, decisions, supplier quirks, customer patterns, policy exceptions.
2. Use `/learn` manually for 30 days before automating mining. Build the habit first.
3. Run a weekly review that promotes learnings into docs, skills, or pattern candidates.
4. Track rejected learnings too. Rejection teaches the system what is noise.
5. Fork `templates/learn-skill-template.md` as the artifact and add a weekly digest spec to your brain.
