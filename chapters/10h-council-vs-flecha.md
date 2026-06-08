# Chapter 10h: Council vs Punta de Flecha — When to Use Which Decision Tool

## Two tools, different jobs

Not every difficult decision needs the same deliberation process.

The LLM Council is a multi-perspective tool. It asks several operating perspectives to analyze the same question, blind-review one another, and produce a synthesis.

Punta de Flecha is an adversarial convergence tool. It asks two or more different model architectures to critique one another across rounds until the remaining disagreement is explicit.

Use the Council when you need breadth. Use Punta de Flecha when you need pressure.

## The LLM Council

The Council simulates six operating perspectives inside one deliberation:

1. Strategy and positioning.
2. Customer experience.
3. Finance and unit economics.
4. Marketing and growth.
5. Operations and supply chain.
6. Product, category, or merchandising.

The exact names should match your business. A food brand might include food safety and wholesale. A beauty brand might include claims/compliance. A home brand might include logistics and warranty. A pet brand might include subscriptions and safety. An outdoor brand might include technical product and seasonality.

The Council is useful because many business decisions fail through functional blindness. Marketing wants growth. Finance wants margin. Operations wants simplicity. Customer experience wants trust. Product wants coherence. The Council forces those tensions into the open.

The Council should output:

- Recommendation.
- Consensus points.
- Dissenting views.
- Risks.
- Evidence needed.
- Confidence.
- Next action.

## Punta de Flecha

Punta de Flecha is for decisions where polite brainstorming is not enough.

Protocol:

1. Model A and Model B answer independently.
2. Model A critiques Model B.
3. Model B critiques Model A.
4. Each model revises.
5. Repeat until improvements are cosmetic or max rounds hit.
6. Final synthesis records consensus, resolved divergences, unresolved divergences, confidence, and owner decision.

The key is architectural diversity. Six personas inside one model can still share the same blind spots. Two different models often fail differently. That is useful.

Use it for decisions where a bad answer is expensive: margin framework, strategic positioning, supplier dependency, platform migration, hiring plan, financing structure, safety-sensitive claims, or a public methodology you plan to publish.

## Decision matrix

| Situation | Use Council | Use Punta de Flecha | Use neither |
|---|---:|---:|---:|
| Need many functional viewpoints | Yes | Maybe | No |
| Need adversarial error-finding | Maybe | Yes | No |
| Routine factual lookup | No | No | Yes |
| Reversible decision under €1,000 impact | Maybe | No | Often |
| Irreversible or >€50K impact | Maybe | Yes | No |
| High uncertainty but low stakes | Yes | No | Maybe |
| Publishing a framework or claim | Maybe | Yes | No |
| Postmortem after incident | Yes | Maybe | No |
| Creative campaign ideas | Yes | No | Maybe |
| Legal, medical, safety, or employment risk | Use only as analysis, not authority | Use only as analysis, not authority | Human expert required |

## Examples

Council examples:

- Should a wellness brand prioritize subscription retention or retail expansion this quarter?
- Should a food brand enter a marketplace with lower margin but higher reach?
- Should a home brand reduce SKU breadth to improve fulfillment reliability?
- How should a pet brand redesign its returns policy without damaging trust?

Punta de Flecha examples:

- Is our dynamic break-even paid-media formula economically correct?
- Should we migrate the whole ecommerce stack before peak season?
- Is this public AI-autonomy claim defensible?
- Should we commit to a large inventory buy with uncertain demand?

Neither:

- What were sales yesterday?
- Which invoice is overdue?
- What is the returns policy?
- Draft three subject lines for a low-risk campaign.

Those are ordinary agent or tool tasks.

## Cost and speed discipline

Decision tools are seductive because they feel rigorous. Use limits.

The Council is usually fast enough for weekly operating decisions. It can run in minutes, produce a synthesis, and give a CEO a clearer view of tradeoffs. It should still be reserved for questions where multiple functions have legitimate tension.

Punta de Flecha is slower by design. It burns attention because each round creates new critique. That is the point when the question is expensive. It is waste when the question is routine.

Create thresholds:

- Under €1,000 impact and reversible: normal agent or human decision.
- €1,000-€50,000 impact or cross-functional: Council if disagreement is useful.
- Above €50,000, irreversible, safety-sensitive, or public claim: Punta de Flecha or human expert review.

The thresholds are illustrative. A small food brand may lower them for safety claims. A larger home brand may raise them for ordinary merchandising decisions. The rule is that deliberation cost should match decision risk.

## What evidence to attach

Both tools perform better when the question includes evidence:

- Current numbers.
- Source docs.
- Options under consideration.
- Constraints.
- Deadline.
- Decision owner.
- What is reversible.
- What would make the decision wrong.

Bad input:

```text
Should we scale paid ads?
```

Useful input:

```text
Should we increase paid spend by 20% next week given current break-even MER
of 3.1, blended MER of 3.5, marginal MER of 2.7, two hero products at
low stock, and a replenishment arriving in 12 days?
```

## Common failure modes

The Council can become theater if the perspectives are generic. “Marketing expert” is less useful than “paid acquisition owner optimizing contribution margin under stock constraints.”

Punta de Flecha can become expensive debate if the question is vague. It needs a clear claim, decision, or artifact to attack.

Both tools can produce false authority. They improve reasoning; they do not replace source data, legal advice, accounting judgment, or accountable human ownership.

## Output discipline

Every deliberation should end with a decision record:

```text
Question:
Tool used:
Recommendation:
Confidence:
Consensus:
Dissent:
Evidence checked:
Evidence missing:
Owner decision:
Review date:
Brain path:
```

The last line matters. A decision not written back to the brain disappears.

## How to start this in your business

1. Define your six Council perspectives around real functions, not generic personas.
2. Use Council for broad operating tradeoffs and Punta de Flecha for adversarial review of expensive, irreversible, or publishable decisions.
3. Require every run to produce a decision record with confidence and unresolved disagreement.
4. Limit usage: if a normal tool lookup can answer it, do not convene deliberation.
5. Fork `prompts/council-query.md`, `prompts/punta-de-flecha.md`, and the decision matrix as the artifact.
