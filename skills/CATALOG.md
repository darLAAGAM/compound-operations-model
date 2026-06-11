# The Skills Catalog — what the 352 actually are

When we say the reference deployment runs **352 skills**, people fairly ask: *"why are only 5 in this repo?"* Honest answer: the 352 are three different layers, and they can't all be published the same way.

| Layer | ~Count | Can it be published? |
|---|---|---|
| **1. Operational skills we wrote** for our own workflows | ~80 | Yes, after anonymization (they contain store names, people, real thresholds, internal URLs) — releasing in batches |
| **2. Brain-ops skills** (the operating loop itself) | ~15 | Yes — highest priority to release |
| **3. Community / installed skills** (CLIs, marketplace packs, vendor doc packs) | ~250 | Not ours to publish — most are already public in their own registries |

The **5 starter skills** in this repo today are public-safe versions from layer 1. Below is the catalog of what exists, so you can see the breadth — and tell us what to anonymize first (open an issue).

---

## Layer 2 — Brain-ops skills (the operating loop)

These run the brain itself. Being prepared for release:

- `check-brain-health` — audits execution hygiene: loose captures, raw/source gaps, outputs without tasks, tasks stuck in review
- `create-task-card` — turns captured context into an executable task card linked to sources
- `handoff-task` — delegates a task card to any AI client or agent with all context included
- `review-output` — checks an output, links it back to its task, moves it through review/done
- `log-capability-gap` — records when an agent or human can't complete work because the company lacks data, access, or process
- `refresh-world-model` — regenerates the company's current-state from tasks, outputs, health reports and capability gaps
- `brain-due-diligence` — full audit of a company brain: infra claims, execution loop, closure rate
- `suggest-skills` — end-of-session audit that proposes which repeated patterns deserve to become skills
- `release-rollout` — one repeatable workflow for publishing updates across repo, playbook, site, deploy, verification

## Layer 1 — Operational skills (examples, anonymized names)

**Retail & merchandising**
- `restock-trigger` — detects high-velocity / low-stock SKUs and drafts a restock proposal with forecast
- `sell-through-dashboard-sync` — pulls sales + stock, computes ROS/WOS/sell-through per SKU, updates the sheet, alerts the channel
- `omnichannel-foot-traffic-attribution` — crosses store foot traffic with paid geo spend, web sessions and POS to estimate halo effect per store

**Customer service**
- `cs-triage-finalization` — closes the escalation loop: carrier duty mis-charges, label regeneration, baseline metrics

**Marketing & growth**
- `weekly-top5-digital` — weekly digital report: pulls commerce + analytics + email + ads, top 5 SKUs, insights, Monday-ready draft
- `omnichannel-growth-loop` — closed-loop methodology: diagnoses ICP from real commerce/analytics data and proposes actions
- Ads operations pack (~60 skills): account audits, wasted-spend finder, creative-fatigue detection, budget pacing alerts, anomaly detection, daily WhatsApp/Slack summaries, A/B monitors, competitor ad spy

**People**
- `employee-onboarding` — one-command onboarding: workspace accounts, channels, tool access, day-1/week-1 checklist, buddy, brain starter links

**Cross-model**
- `adversarial-deliberation` — forces two different models to critique each other's analysis before a high-stakes decision

## Layer 3 — Community & installed (~250)

CLIs and packs from the open ecosystem (terminal tools for commerce, analytics, email, search, infra...). We didn't write these and won't republish them — but the playbook documents *how* we wire them in. This layer is the reason the system grows weekly without us writing everything.

---

**Want one prioritized?** [Open an issue](../../issues/new?template=question.md) naming the skill. Attribution-friendly forks of your own versions are exactly the point of this repo.
