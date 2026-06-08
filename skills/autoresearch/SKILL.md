---
name: autoresearch
description: Autonomous iteration loop for optimizing any measurable target. Use when asked to "optimize", "iterate", "A/B test", "autoresearch", "improve automatically", or "run experiments" on code, config, prompts, templates, or workflows where a metric can be measured after each change. Inspired by Karpathy's autoresearch pattern.
---

# Autoresearch — Autonomous Iteration Loop

Run an autonomous optimize→measure→keep/discard loop on any target file with a measurable metric.

## Core Pattern

```
┌─────────────────────────────────────┐
│  1. Read program.md (objective)     │
│  2. Read target file (current best) │
│  3. Propose ONE change (hypothesis) │
│  4. Apply change → run eval         │
│  5. Compare metric to baseline      │
│  6. BETTER? → commit + new baseline │
│     WORSE?  → revert                │
│  7. Log result → go to 3            │
└─────────────────────────────────────┘
```

## How to Use

### 1. Define the program

Create (or have the user provide) a `program.md` that specifies:

- **Objective** — what to optimize (e.g., "lower val_bpb", "increase open rate", "reduce response time", "improve Lighthouse score")
- **Target file(s)** — what the agent can modify (e.g., `train.py`, `template.liquid`, `flow.json`, `prompt.md`)
- **Eval command** — how to measure the metric (e.g., `uv run train.py`, `curl API`, `lighthouse --url`, `python eval.py`)
- **Metric extraction** — how to parse the result (e.g., "last line of stdout", "JSON field .score", "grep 'accuracy:'")
- **Direction** — whether lower or higher is better
- **Constraints** — what NOT to touch, time budget per iteration, safety guardrails
- **Max iterations** — how many experiments to run (default: 20)

If the user doesn't provide a formal program.md, extract these parameters from conversation and confirm before starting.

### 2. Run the loop

```
baseline = run_eval()
log = []

for i in 1..max_iterations:
    # Save current state
    snapshot = read(target_file)
    
    # Propose change (ONE hypothesis per iteration)
    hypothesis = generate_hypothesis(program, log)
    apply(hypothesis, target_file)
    
    # Evaluate
    result = run_eval()
    
    # Decision
    if result is_better_than baseline:
        baseline = result
        commit(f"Experiment {i}: {hypothesis.summary} → {result}")
        log.append({i, hypothesis, result, "KEPT"})
    else:
        revert(target_file, snapshot)
        log.append({i, hypothesis, result, "DISCARDED"})
    
    # Report progress every 5 iterations
    if i % 5 == 0: summarize(log)
```

### 3. Key rules

- **ONE change per iteration.** Never bundle multiple hypotheses — you can't attribute improvement.
- **Always measure.** No "I think this is better." Run the eval command, get a number.
- **Always revert on failure.** The target file must stay at the best-known state.
- **Log everything.** Every experiment gets recorded: hypothesis, metric before, metric after, kept/discarded.
- **Monotonic improvement.** The baseline only moves in the desired direction. Never accept regressions.
- **Time-box if needed.** If each eval takes >5 min, ask user about iteration budget.

### 4. Hypothesis generation strategy

Use the experiment log to guide next hypotheses:

- **Early iterations (1-5):** Try broad, high-impact changes (architecture, major params)
- **Mid iterations (6-15):** Refine what worked, explore related changes
- **Late iterations (16+):** Fine-tune, try combinations of previous wins
- **Never repeat** a discarded hypothesis verbatim
- **Learn from failures** — if increasing X failed, try decreasing it or changing a related parameter

### 5. Reporting

After the loop completes (or on user request), produce a summary:

```markdown
## Autoresearch Report

**Objective:** [from program.md]
**Target:** [file(s) modified]  
**Iterations:** X total (Y kept, Z discarded)
**Baseline:** [starting metric]
**Final:** [ending metric]  
**Improvement:** [delta and %]

### Experiments Log
| # | Hypothesis | Metric | Δ | Status |
|---|-----------|--------|---|--------|
| 1 | Increased batch size 2x | 1.42 | -0.03 | ✅ KEPT |
| 2 | Added dropout 0.1 | 1.45 | +0.03 | ❌ DISCARDED |
...

### Key Findings
- [What worked and why]
- [What didn't work]
- [Suggested next directions]
```

## Example Applications

| Domain | Target File | Eval Command | Metric |
|--------|------------|--------------|--------|
| ML training | `train.py` | `python train.py` | val_bpb (↓) |
| Email marketing | `template.html` | Klaviyo API → send variant → wait → check stats | open_rate (↑) |
| Landing page | `index.html` | `lighthouse --url` | performance_score (↑) |
| Prompt engineering | `prompt.md` | `python eval_prompt.py` | accuracy (↑) |
| Shopify theme | `section.liquid` | `lighthouse --url` + CWV | LCP (↓) |
| Agent optimization | `SOUL.md` | Run test suite → score | task_completion (↑) |
| Ad copy | `ad_variants.json` | Meta API → create test → wait → check CTR | CTR (↑) |
| CSS/perf | `styles.css` | `lighthouse --url` | CLS (↓) |

## Safety

- **Never run destructive commands** in eval (no `rm`, no `DROP TABLE`, no production writes without explicit user approval)
- **For live systems** (Klaviyo, Meta Ads, Shopify): always confirm with user before first iteration that involves real traffic/spend
- **Git commit each improvement** when a repo is available, so the full history is recoverable
- **Stop and report** if 5 consecutive experiments are discarded — the search space may be exhausted or the approach needs rethinking
