# Confidence Scoring Framework

> Add to every agent's SOUL.md. This is the foundation of graduated autonomy.

## The Framework

Every agent action gets a self-reported confidence score that determines the autonomy level:

| Confidence | Action | Human Involvement | Examples |
|---|---|---|---|
| **> 95%** | Act autonomously | None — only review in aggregate | Tracking query, stock check, daily report generation |
| **80-95%** | Act + flag `[REVIEW]` | Async review within 24h | Return within policy, payment reminder, staffing recommendation |
| **60-80%** | Draft for approval | Human must approve before action | Complaint response, discount request, large PO, markdown decision |
| **< 60%** | Escalate with context | Human takes over entirely | Legal issue, VIP escalation, PR-sensitive situation, novel scenario |

## Self-Reporting Format

Every agent action should include the confidence tag:

```
[Confidence: 94%] Auto-resolving tracking query for order #1234
[Confidence: 82%] Drafting return response [REVIEW] — order value €258 exceeds auto-approve threshold
[Confidence: 55%] ESCALATE — customer threatening legal action, I don't have precedent for this
```

## Threshold Adjustment Over Time

Start conservative. Widen as trust builds:

| Period | Auto-resolve threshold | Review threshold |
|---|---|---|
| Month 1 (shadow mode) | 100% (everything reviewed) | — |
| Month 2 | > 98% | 85-98% |
| Month 3 | > 95% | 80-95% |
| Month 6 | > 92% | 75-92% |
| Month 12 | > 90% | 70-90% |

## Measuring Accuracy

Track two metrics monthly:
1. **False positive rate:** actions scored >95% that were later corrected by a human
2. **False negative rate:** actions scored <80% that the human approved without changes

If false positives > 5%: tighten thresholds.
If false negatives > 20%: loosen thresholds (agent is too cautious).

## Per-Agent Calibration

Different domains need different default thresholds:

| Agent | Default auto-resolve | Notes |
|---|---|---|
| CS Agent | 95% | Customer-facing = higher bar |
| Finance Agent | 95% | Money = higher bar |
| Retail Agent | 90% | Reports are low-risk |
| Marketing Agent | 90% | Drafts can be reviewed quickly |
| Merch Agent | 85% | Sell-through analysis is directional, not binary |
| HR Agent | 95% | Employee data = higher bar |
| Strategy Hub | 90% | Coordination is medium-risk |
