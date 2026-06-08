# Program Template — Autoresearch

Copy and customize this template to define your optimization objective.

---

## Objective

[What are we optimizing? Be specific about the goal.]

Example: "Minimize validation bits-per-byte (val_bpb) for a GPT model trained on FineWeb-Edu."

## Target File(s)

[Which file(s) can the agent modify?]

- `path/to/file.py` — [what it contains, what's fair game to change]

## Eval Command

[How to run one evaluation cycle.]

```bash
uv run train.py
```

## Metric

- **Name:** val_bpb
- **Direction:** lower is better
- **Extraction:** Last line of stdout, format: `val_bpb: X.XXXX`
- **Baseline:** [run once manually and record]

## Time Budget

- **Per iteration:** 5 minutes (wall clock)
- **Max iterations:** 50
- **Total budget:** ~4 hours

## Constraints

[What the agent must NOT do.]

- Do not modify `prepare.py`
- Do not change the evaluation methodology
- Do not exceed 1 GPU
- [Add domain-specific constraints]

## Hypothesis Priorities

[Optional: guide the agent's search strategy.]

1. Try architectural changes first (depth, width, attention pattern)
2. Then optimizer tuning (learning rate, schedule, warmup)
3. Then training tricks (data ordering, augmentation)
4. Last: micro-optimizations (numerical precision, kernel choices)

## Notes

[Any additional context the agent should know.]
