# Chapter 10d: Advanced Operational Capabilities

## Why This Chapter Exists

Most AI agent demos show one capability at a time: "the CS agent answers a ticket" or "the finance agent generates a report". That is fine for a 5-minute demo.

But a system that has been running for 6+ months accumulates specialized capabilities that go far beyond the baseline. These are the features that didn't make the landing page because they're too specific to explain in one sentence — but they're where a lot of the real operational value lives.

This chapter documents the specialized capabilities that sit on top of the core agent architecture. Think of them as **skills the team can invoke** — not primary agent responsibilities, but features that ship alongside a mature deployment.

## How to Start From This Chapter

Do not install all of this at once. Pick one capability with a measurable baseline, copy the relevant artifact from the repo, run it in read-only mode, and promote it only after a human has reviewed the outputs. The public repository is the starting point once the neutral namespace is live. For hands-on help, use hello@usecompai.com.

---

## 1. AutoResearch — Self-Evolving Prompts

**What it does:** the CS agent continuously measures its own response quality. When the quality of a response category drops, it automatically mutates the underlying prompt, tests the mutation against a validation set, and promotes the mutation if it outperforms the baseline.

**How it works:**
1. Every CS response is scored (by a separate scoring model) on correctness, tone, and policy compliance
2. Aggregated scores per response category (WISMO, returns, sizing, ingredients, warranties, subscriptions, specs, etc.) are tracked over time
3. When a category's score drops below threshold, the system generates 3-5 prompt mutations
4. Each mutation is tested against the last 100 tickets in that category
5. If a mutation outperforms the baseline by >5%, it's promoted automatically
6. If all mutations underperform, a human is alerted

**Result:** CS accuracy on the baseline "tracking query" category reached 94.7% after 3 months of auto-evolution — up from 89% at launch. No human prompt engineering required.

**The principle:** the right prompt for a task is an empirical question, not a design question. Measure, mutate, test, promote. Treat prompts as code that evolves.

---

## 2. LLM Council — Multi-Expert Deliberation

**What it does:** for high-stakes decisions (strategic questions, board-level pitches, major vendor choices), the system can convene a "council" of six simulated domain experts, have each one respond independently, blind-review each other's responses, and synthesize a chairman's final answer.

**The domains:**
1. Strategy & Positioning
2. Customer Service Operations
3. Finance & Unit Economics
4. Retail & Physical Experience
5. Digital Marketing & Growth
6. Merchandising & Buying

**How it works:**
1. A question is submitted via `council_query("should we enter the DACH market in Q3?")`
2. Six panelists answer independently using domain-tuned system prompts
3. Three blind reviewers (randomly selected from the panel) rank each answer
4. A chairman model synthesizes the final answer with confidence level and dissenting views

**Cost per deliberation:** ~€0.80-1.20 in API tokens. Response time: 2-4 minutes.

**When to use it:** never for routine decisions (that's what agents are for). Only for irreversible calls where the cost of being wrong exceeds €1,000. Example: vendor selection, positioning statements, major inventory buys, hiring framework choices.

---

## 3. Invoice Pipeline — Email OCR → Drive → Sheet

**What it does:** incoming supplier invoices (by email) are automatically OCR'd, classified, filed in Google Drive with consistent naming, reconciled against purchase orders, and logged in a master spreadsheet for the finance agent to process.

**The pipeline:**
1. **Ingestion** — a dedicated inbox (`invoices@<brand>`) receives invoices
2. **OCR** — attachments are extracted and run through OCR
3. **Classification** — the finance agent categorizes (supplier, amount, category, due date)
4. **Filing** — PDFs are renamed to `<supplier>_<invoice#>_<date>.pdf` and filed in Drive
5. **Reconciliation** — matched against PO database; discrepancies are flagged
6. **Logging** — a row is added to the master invoices sheet with links
7. **Approval routing** — invoices >€1,000 get routed for human approval before payment

**Result:** invoice processing time dropped from ~5 minutes/invoice to <30 seconds/invoice. Error rate (wrong amounts, missed invoices, late payments) near zero.

---

## 4. Profitability Engine — CM3 Per Product

**What it does:** real-time contribution margin 3 (revenue - COGS - fulfillment - marketing attribution) calculated at the individual product level, refreshed daily, across 9 different data sources.

**The data sources:**
1. **Shopify** — revenue, unit sales
2. **Stockagile** — cost of goods
3. **Amphora** — fulfillment + shipping costs
4. **Meta Ads** — paid social attribution
5. **Pinterest Ads** — paid discovery attribution
6. **Klaviyo** — email attribution (last-click)
7. **GA4** — organic + direct attribution
8. **Google Ads** (via GA4) — paid search attribution
9. **Holded** — returns and refunds

**Result:** every product has a live CM3 number. The merchandising agent uses this for reorder decisions, markdown candidates, and category expansion. The finance agent uses it for weekly P&L narrative. The marketing agent uses it to kill unprofitable paid campaigns.

**Why it's hard:** attribution across 9 sources requires resolving cookie matches, deduplicating conversions, and applying a consistent attribution window. Most brands never build this because it's too much plumbing. A mature deployment of this system builds it once and amortizes the cost across every decision.

---

## 5. Copy Engine — Campaign Pattern Learning

**What it does:** every sent email campaign's subject line, body, CTA, and performance (open rate, click rate, revenue per recipient) is logged. A dedicated pattern extractor identifies which copy elements correlate with performance.

**Real findings from 1,114 analyzed campaigns:**
- ALL CAPS subject lines generate **2.7× revenue per recipient** vs. sentence case (when used sparingly — <15% of sends)
- Questions in subject lines beat statements by 18% in open rate
- Plain-text emails beat HTML emails by 12% in click-through on mobile
- Emoji in subject lines: +8% open rate on B2C, -4% open rate on B2B segments
- The phrase "just for you" is the single strongest personalization signal tested

**How the marketing agent uses it:** when drafting a new campaign, the agent checks the pattern library for the target segment and applies learned patterns to the draft. This isn't a black box — the agent cites which patterns it's applying and why.

**The principle:** every campaign is a data point. Over 18+ months, you accumulate hundreds of data points across dozens of segments. That's a real edge — and it compounds.

---

## 6. GEO Optimization — AI Search Engine Ranking

**What it does:** tracks the brand's visibility in AI-powered search engines (ChatGPT, Perplexity, Claude, Google AI Overviews) and optimizes content to improve ranking.

**Why it matters:** traditional SEO targets Google's ranking algorithm. GEO (Generative Engine Optimization) targets the LLMs that increasingly sit between users and search results. When someone asks ChatGPT "best mineral sunscreen under €30, best dog raincoat, best compact sofa bed, or best minimalist sneakers under €150", your brand's position in that answer matters more than its position in Google's #5-10 organic results.

**How the marketing agent works it:**
1. Weekly queries to all major AI search engines with target keywords
2. Capture the text of the answer (not just the links)
3. Score the brand's mention position (not mentioned / mentioned / featured)
4. Reverse-engineer which content the AI is citing
5. Optimize that content for clearer entity attribution

**Result:** brand mention rate in AI search engines for target keywords improved from ~35% to ~60% over 4 months.

---

## 7. Amortization Alerts — 48h Advance Warning

**What it does:** tracks all active credit lines (5 in the current deployment) and sends 48-hour advance warnings before any amortization payment is due.

**Why it's needed:** credit line payments that miss the date cost 1-3% in penalties and trigger reporting to credit bureaus. A single missed payment wipes out months of the system's ROI. Humans forget. Cron jobs don't.

**How it works:**
1. A Google Sheet maintains the master credit line schedule (principal, interest, amortization dates)
2. A daily cron (run by the finance agent) checks for payments due in the next 48 hours
3. Alerts are sent to Slack with the exact amount, the destination account, and the deadline
4. The finance lead confirms the payment has been scheduled by thumbs-up reaction
5. If no confirmation within 24 hours, the alert escalates to the founder

**Cost of this capability:** ~5 lines of Python + 1 Google Sheet + 1 cron entry. **Value:** prevents every missed-amortization penalty for the lifetime of the system.

---

## 8. Video Transcription — Local, Zero Cost

**What it does:** transcribes audio from videos (meeting recordings, product reviews, customer interviews) using a **local** faster-whisper model running on the Mac Mini. No cloud transcription service, no per-minute costs.

**The stack:**
- `faster-whisper` running locally on Apple Silicon
- `ffmpeg` for audio extraction
- Output routed to the brain as searchable markdown

**Use cases:**
- Meeting recordings → brain (searchable via `brain_search`)
- Customer interview videos → CS agent for pattern extraction
- Product review videos → merchandising agent for feedback synthesis across sizing, flavor, scent, model, bundle, pack, defect, or warranty patterns
- Competitor demo videos → strategy hub for competitive intelligence

**Cost:** €0. The model runs on hardware that's already sitting idle.

---

## 9. Taskmaster Protocol — Cascading Contracts

**What it does:** for complex multi-step operations that span multiple agents, the system uses a **contract-based cascading protocol**. Each step is a formal contract with inputs, outputs, and acceptance criteria. If any step fails its acceptance criteria, the entire chain is rolled back.

**Example: "launch a new product"**
1. **Merchandising agent** creates the product in Shopify → contract: product ID returned, status = draft
2. **Operations agent** allocates initial stock across warehouses → contract: total stock ≥ threshold
3. **Marketing agent** drafts launch email in Klaviyo → contract: preview renders, subject line passes brand check
4. **Marketing agent** drafts social posts → contract: posts saved as drafts
5. **Finance agent** verifies COGS is entered → contract: CM3 calculable
6. **Strategy hub** publishes the product (flips status from draft to active) → contract: product live on site

If any step fails, the previous steps are rolled back (product un-allocated, email un-drafted, etc.) and the operation is escalated to a human.

**Why it matters:** in a multi-agent system, partial failure is the biggest risk. Half-launched products are worse than unlaunched products. The Taskmaster Protocol ensures every multi-step operation is atomic — either all steps succeed, or none take effect.

---

## 10. Pattern Library — The Cold-Start Advantage

**What it does:** the system extracts **anonymized operational patterns** from every deployment and maintains a shared library that new deployments can bootstrap from. Instead of starting with zero institutional knowledge, a new deployment's agents start with 21+ battle-tested patterns across 9 domains.

**The patterns are strict about anonymization:**
- NO brand names
- NO employee names
- NO absolute revenue/cost numbers
- NO location identifiers
- Only ratios, thresholds, workflows, and templates

**Example pattern (CS domain):**
```yaml
pattern_id: cs-tracking-automation
domain: customer_service
confidence: high
description: |
  97% of tracking queries can be auto-resolved by checking Shopify
  order status + 3PL tracking in parallel, then drafting a response
  that includes: order number, current status, ETA, and the tracking URL.
threshold: >95% confidence = auto-send; 80-95% = draft for review
tested_in: 5 deployments, 12,000+ tickets
```

**The architecture:**
- **Level 1 (curated):** Manually reviewed patterns in `/operai/pattern-library/` — the highest-quality patterns go here
- **Level 2 (automated):** Weekly cron extracts candidate patterns from memory logs, anonymizes them, and submits for review
- **REST API:** port 18830 serves patterns to new deployments via `GET /patterns/<domain>`

**Why it's a differentiator:** every new team can start with accumulated wisdom, not a blank slate. Month 1 of a new deployment looks like month 6 of a deployment that started from scratch. This is the compounding lesson — every deployment teaches reusable patterns, as long as the sharing is anonymized and consented.

**Start here:** fork the public playbook repository, inspect `/operai/pattern-library/`, and adapt only the patterns you can validate in your own data.

---


---

## 10. Punta de Flecha — Adversarial Cross-Model Convergence

**What it does:** for the highest-stakes strategic decisions (>€50K impact, irreversible, high uncertainty), the system runs two LLMs of **different architectures** against each other in iterative rounds until they converge on a recommendation.

**How it differs from the LLM Council:**
- Council = 6 perspectives, 1 model, 1 round → same architectural biases
- Punta de Flecha = 2+ models (e.g., Claude + GPT-5.4), N iterative rounds → cross-architecture, verifiable convergence

**The protocol:**
1. Both models analyze the question independently (Round 0 — uncontaminated)
2. Model A's output is sent to Model B for critical review
3. Model B's refined output is sent back to Model A
4. Repeat until delta between rounds is cosmetic, or both models say "I can't improve this"
5. Final output: recommendation + consensus points + resolved divergences + unresolvable divergences + confidence level

**When to use it:** never for routine decisions. Only for calls where the cost of being wrong exceeds €50K — vendor selection, market entry decisions, major inventory commitments, strategic positioning.

**Cost:** €0 — both models run on existing subscriptions (Claude Pro Max + ChatGPT). Typical deliberation: 3-5 rounds, 10-15 minutes.

**The principle:** the best analysis comes from forcing two different architectures to criticize each other. Same-model deliberation (like the Council) shares biases. Cross-model deliberation reveals blind spots.

---

## 11. Ads Audit System — Automated Health Scoring

**What it does:** the marketing agent runs a structured audit of all paid advertising campaigns monthly, scoring them against 46 Meta checks and 74 Google checks. Each check has a severity weight (critical/high/medium/low) and produces a weighted health score per platform.

**Key rules built in:**
- **3× Kill Rule:** if spend > 3× target CPA with 0 conversions → pause immediately
- **20% Scale Rule:** if CPA < target by >10% → increase budget 20% (never more)
- **Decreasing Returns:** if CPA rises >15% after budget increase → revert
- **Frequency saturation:** Meta >4.0 (7-day) or TikTok >3.0 → refresh creative

**Scoring formula:** weighted sum of (check_result × severity × category_weight), normalized to 0-100. Grades A through F.

**Quick wins list:** 12 actions that take <15 minutes each and address critical/high findings — the agent can execute most of them autonomously.

## 12-16: Other Capabilities Worth Mentioning

Shorter descriptions because they're more niche:

- **Anti-prompt-injection CS hardening** — the CS agent has an extra security block because it processes untrusted customer content. See Lesson 22 in Ch.11b.
- **Multi-currency operations** — the finance agent handles 6 currencies simultaneously (EUR, USD, GBP, MXN, JPY, CHF) via Revolut Business, with automatic FX reconciliation.
- **Agent + corporate credit card** — the strategy hub has its own Visa Platinum corporate card (€100/month limit) for autonomous expense management on approved categories.
- **Wholesale order creation via Stockagile v3** — the merchandising agent can create wholesale orders end-to-end, from quote to invoice, with human approval gates for accounts above a configurable value threshold.
- **Meeting recordings pipeline** — Gemini Notes (Google Workspace) are automatically enabled for all hosted meetings, transcripts flow to the brain, and the strategy hub extracts action items weekly.

---

## The Meta-Point

None of these capabilities are core to the agent architecture. They're **extensions** — specialized tools built on top of the base system to solve specific operational problems.

The lesson: once you have a working multi-agent system with a shared brain and an MCP server, adding capabilities is fast. AutoResearch is ~300 lines of Python. The Invoice Pipeline is ~200 lines. The LLM Council is ~150 lines.

A mature deployment will accumulate dozens of these capabilities over time. Each one solves a specific pain point, none of them require a new agent, and all of them compound into operational leverage that no single-purpose SaaS tool can match.

**Start with one painful workflow, then fork the public playbook repository and copy only the capability you can measure. If you need help adapting it to a real stack, contact hello@usecompai.com. Add capabilities as you encounter operational pain. In 6 months, you'll have a system that looks nothing like where you started — and that's exactly the point.**

---

*Next: [Chapter 11 — Implementation →](11-implementation.md)*

---

## 10. Punta de Flecha — Adversarial Cross-Model Convergence

**What it does:** for the highest-stakes strategic decisions, the system runs two LLMs of different architectures against each other in iterative rounds until they converge on a recommendation.

**How it differs from the LLM Council:** Council = 6 perspectives, 1 model, 1 round (same biases). Punta de Flecha = 2+ models (e.g., Claude + GPT-5.4), N iterative rounds (cross-architecture convergence).

**The protocol:**
1. Both models analyze the question independently (Round 0)
2. Model A output sent to Model B for critical review and refinement
3. Model B refined output sent back to Model A
4. Repeat until convergence (delta is cosmetic) or max rounds reached
5. Final: recommendation + consensus + divergences + confidence level

**When to use:** decisions where cost of being wrong exceeds the equivalent of a month's revenue. Vendor selection, market entry, strategic positioning.

**Cost:** zero incremental. Both models run on existing subscriptions. 3-5 rounds, 10-15 minutes.

---

## 11. Ads Audit System — Automated Health Scoring

**What it does:** the marketing agent runs 46 Meta checks + 74 Google checks monthly with weighted health scoring (A-F grades).

**Key rules:** 3x Kill (spend > 3x target CPA + 0 conversions = pause), 20% Scale (CPA below target = increase 20%), frequency saturation thresholds per platform. Quick wins list: 12 high-impact actions under 15 minutes each.

