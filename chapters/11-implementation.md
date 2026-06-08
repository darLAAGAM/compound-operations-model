# Chapter 11: Implementation — Open-Source Build Paths

> **Appendix · Technical depth.** This chapter is for operators or engineers deploying the brain themselves. It covers implementation details that aren't needed for understanding the conceptual architecture. Skip if you're reading for strategy.

You've read the architecture. You've seen the agent blueprints. Now: how do you actually deploy this?

We offer three paths, designed as a progression. Start wherever matches your team today. Upgrade when you're ready.

## How To Build With AI — The 3-Phase Rule

Before you touch a single config file, a note on methodology. The most important lesson from 6+ months of building this system has nothing to do with OpenClaw or Claude or Shopify APIs. It's about **how humans work with AI during the build**.

After trying every variation, one pattern consistently produces working systems faster than anything else: the **3-phase rule** — Research → Plan → Implement.

> *Credit: this methodology is adapted from [the implementation protocol Tane's Claude Code workflow](https://boristane.com/blog/how-i-use-claude-code/), battle-tested over months of real builds.*

### Phase 1 — Research

Before writing a single line of code or config, **read deeply**. Read the existing codebase. Read the relevant docs. Read the brain. Read every file that could possibly be affected. Document your findings in a `research.md` file.

The AI is good at reading fast. Use that. Ask it to summarize modules, trace dependencies, list assumptions. The written artifact forces the AI to verify its understanding before you trust it to plan.

**Anti-pattern:** skipping research because "it's a small change". The AI will happily generate plausible-looking code for a system it doesn't fully understand, and you'll spend 10× the saved time debugging.

### Phase 2 — Plan

Based on the research, write a detailed `plan.md`. It should contain:

- The approach (not the code)
- File paths that will be touched
- Code snippets for the critical paths
- Trade-offs considered and rejected
- Open questions that need human input

**Critical:** do not implement yet. Send the plan to your human reviewer. Let them annotate it inline — corrections, constraints, domain knowledge the AI didn't have. Iterate 1-6 times until the plan is approved.

This is where the real value happens. The annotation cycle is where human judgment meets AI speed. Skip it and you'll get working code that solves the wrong problem.

### Phase 3 — Implement

Once the plan is approved, **execute everything without stopping**. Mark tasks completed as you go. No unnecessary comments, no jsdocs nobody asked for, no scope creep. Implementation should be boring — the creative work happened in Phase 2.

If something fails: revert and re-scope. Don't patch. Don't improvise. Go back to Phase 2, update the plan, then re-implement.

### When To Skip The 3 Phases

- Trivial fixes (typos, config tweaks, small bug fixes)
- Urgent production issues (fix first, document the fix after)
- Direct instructions with zero ambiguity ("change variable X from 5 to 10")

For everything else — especially new features, refactors, and multi-file changes — follow the full loop. It feels slower on the first step and is measurably faster by the third.

### Why This Matters For Your Deployment

Every chapter of this playbook was written using the 3-phase rule. Every agent in production was deployed using the 3-phase rule. Every post-mortem in Ch.11b was the direct result of *not* following the 3-phase rule on some specific day.

When you start building your own deployment, resist the urge to go straight to "install OpenClaw". Start with a research doc. Write the plan. Get it annotated. Then build. You'll skip most of the lessons in Ch.11b the first time through.

---

## Choose Your Path

This is not a checkout funnel. There is no paid repo path in the playbook. The progression is:

```
Read the playbook  →  Fork the repo  →  Run one local workflow  →  Connect one real tool  →  Add agents gradually
```

| Path | Best for | What you do | Output |
|---|---|---|---|
| **A. Read** | Founders and operators validating the idea | Read Chapters 1-3, 12, and the relevant agent chapter | A clear decision on whether the architecture fits your business |
| **B. Fork** | Technical operators | Fork the public playbook repository and inspect the artifacts before running anything | A private working copy you can adapt |
| **C. Local pilot** | Teams with one painful workflow | Run one agent in shadow mode against copied/exported data | Draft outputs, no production risk |
| **D. Production adaptation** | Teams ready to connect live systems | Add one API at a time, keep human approval gates, measure ROI weekly | A controlled deployment that compounds |
| **E. Hands-on help** | Teams without spare technical capacity | Email `hello@usecompai.com` with your stack, channels, and first workflow | Scoped implementation support, not a product checkout |

---

## Path A: Read the Playbook

Start with the business case before touching infrastructure. For most consumer SMEs, the first useful answer is not “which model?” It is “which operational loop is repetitive, rules-driven, high-volume, and measurable?”

Good first loops by vertical:

| Vertical | Strong first loop examples |
|---|---|
| Beauty | ingredient questions, shade recommendations, replenishment reminders |
| Food & beverage | subscription changes, allergen questions, delivery exceptions |
| Home | warranty claims, delivery damage, bundle availability |
| Pet | size/fit recommendations, recurring orders, product compatibility |
| Outdoor | model/spec questions, spare parts, warranty and repair triage |
| Fashion & retail | size/fit, returns, store stock, transfer recommendations |

Write the current human baseline before building: weekly hours, error rate, response time, and escalation categories. Chapter 12 shows the exact ROI math.

## Path B: Fork the Repo

Fork the repo and make a private branch for your company:

```bash
git clone YOUR_PRIVATE_FORK_URL
cd ai-native-playbook
```

Start by copying only the documents you need:

```
brain/
├── knowledge/
│   ├── company/
│   │   ├── operations/policies.md
│   │   ├── product/catalog.md
│   │   ├── cs/faqs.md
│   │   ├── marketing/brand-voice.md
│   │   └── team/escalations.md
└── memory/
    └── README.md
```

Do not paste secrets into the repo. Keep API keys in your runtime environment or secret manager.

## Path C: Local Pilot — One Workflow, Shadow Mode

Pick one agent. Customer service is usually first because volume is high and quality is easy to review. Run it against exported or copied tickets before connecting to a live helpdesk.

**Week 1 target:** the agent drafts responses, but a human sends everything.

**What to monitor:**
- Accuracy: product, policy, stock, price, delivery, warranty
- Tone: brand voice, empathy, directness
- Escalation: does it know when not to answer?
- Evidence: does every answer cite where it found the information?

### Day 1-2: Knowledge Base

Create a minimal Context Tree:

```
workspace/
├── SOUL.md
├── TOOLS.md
├── MEMORY.md
└── brain/knowledge/company/
    ├── operations/policies.md
    ├── product/catalog.md
    ├── cs/faqs.md
    ├── marketing/brand-voice.md
    └── team/escalations.md
```

### Day 3-7: Shadow Mode

Feed the agent your last 50-100 real cases. For each draft, mark:

| Outcome | Meaning | Action |
|---|---|---|
| Correct | Could have been sent | Add to approved pattern library |
| Correct but off-tone | Facts right, voice wrong | Update brand voice examples |
| Missing evidence | Answer may be right but not grounded | Add source requirement |
| Wrong | Unsafe to send | Fix knowledge or escalate category |

## Path D: Production Adaptation — 30-Day Plan

### Week 1: Foundation

- Define one domain owner and one reviewer.
- Build the Context Tree.
- Run shadow mode against historical cases.
- Document every miss as a brain update, not a one-off prompt tweak.

### Week 2: Calibration

- Enable autonomy only for categories with >95% reviewed accuracy.
- Keep approval required for refunds, discounts, legal, HR, VIP, safety, and high-value exceptions.
- Review the audit log daily.

### Week 3: Second Agent

Choose the next agent by pain:
- **Ops** if stockouts, oversells, supplier lead times, or 3PL exceptions are the problem.
- **Finance** if reporting, invoices, AR, reconciliation, or cash visibility are the problem.
- **Marketing** if campaign analysis, replenishment campaigns, SEO/GEO, or promo reporting is the problem.

### Week 4: ROI Assessment

Calculate the actual result:

```
Hours saved per week:  ___ hours
× Equivalent hourly cost: €___/hour
= Weekly savings: €___

Monthly AI system cost: €___
Monthly savings: €___
ROI ratio: ___:1
```

If the math does not work, stop expanding and fix the workflow. The reference deployment reached **62h/week** reclaimed and **18:1 ROI**, but those numbers only matter if your own baseline validates them.

## Common Implementation Mistakes

### 1. Skipping the Knowledge Base

Without accurate catalog data, policies, procedures, and brand voice, the agent will hallucinate. Garbage in, garbage out.

### 2. Going Full Autonomy Too Fast

Shadow mode feels slow. One bad automated response to a customer, supplier, employee, or partner costs more than a week of manual review. Build trust incrementally.

### 3. Treating the Repo as a Product

The repo is an educational portfolio and a set of working artifacts, not a universal installer. Fork it, read it, delete what does not apply, and adapt it to your actual stack.

### 4. Using the Cheapest Model First

Start with the best model you can justify, prove the workflow works, then optimize costs. A wrong customer response, finance note, or HR draft costs more than a few cents in tokens.

### 5. No Human Review Process

Even with high autonomy, someone needs to review escalations and periodically audit autonomous actions. Build this into the team’s workflow.

## AutoResearch: The Autonomous Optimization Loop

Once your agents are running, the next frontier is **autonomous iteration**. The pattern is optimize → measure → keep:

```
1. Define objective + metric
2. Agent modifies one target file with one hypothesis
3. Run evaluation
4. Better? Keep. Worse? Revert.
5. Repeat N times and produce a report
```

Real applications we use:

| Domain | What it optimizes | Metric |
|---|---|---|
| Email flows | Klaviyo templates | Open rate, click rate, revenue per recipient |
| Landing pages | Page HTML/CSS | Core Web Vitals, conversion rate |
| Agent prompts | SOUL.md / system prompts | Task completion, policy compliance |
| Ad copy | Creative variants | CTR, CPA, MER |
| Commerce theme | Sections and PDP content | Speed, conversion, support deflection |

Start with read-only evaluation. Let optimization write only after a human approves the metric, the test set, and the rollback rule.

## After Day 30

- **Month 2:** Deploy agents 2-3, usually Ops + Finance.
- **Month 3:** Add Marketing, Retail, Wholesale/Partner Ops, or HR depending on your channel mix.
- **Month 4-6:** Build cross-agent intelligence and a weekly knowledge-mining loop.
- **Month 6+:** Your job shifts from operating systems manually to supervising the operating system.

## Getting Help

The default path is self-serve: read the playbook and fork the repo. If you want hands-on implementation help, email **hello@usecompai.com** with:

- Your vertical and revenue band
- Your stack (commerce, helpdesk, inventory, finance, email, analytics)
- Your first workflow target
- Whether you need read-only pilot, shadow mode, or production deployment

There is no checkout step. The artifact is the repo and the playbook; services are scoped separately when a team wants help.

---

*Next: [Chapter 12 — ROI: Real Numbers, Real Results →](12-roi.md)*
