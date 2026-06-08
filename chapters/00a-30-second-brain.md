# Chapter 00a: The 30-Second Company Brain

## The shortest useful explanation

A company brain is a structured folder that tells AI how your business works.

That is the whole primitive. Not a chatbot. Not a dashboard. Not a vendor contract. A folder.

Inside the folder are the facts, policies, procedures, decisions, examples, and operating lessons your team already uses every day. The difference is that they are written in a shape an AI agent can search, cite, and act from.

If you run a consumer SME, your company brain starts as the place where these questions stop being tribal memory:

- What is our returns policy by country, product type, and customer tier?
- Which supplier needs a 12-week lead time and which one can move in 10 days?
- How do we classify an invoice from a logistics provider?
- What does a good customer-service reply sound like in our brand?
- Which products can paid marketing scale profitably this week?
- What broke last time we changed the warehouse integration?

The brain is the substrate. Agents are applications on top of it.

## The one-page diagram

```text
                    Your team
      CEO / ops / finance / marketing / CS / retail
                         |
                         v
              AI surface your team already uses
        Claude Desktop / ChatGPT / Cursor / Codex / Slack
                         |
                         v
                    MCP tools
      search brain | read docs | query systems | write learnings
                         |
                         v
    ---------------------------------------------------------
    COMPANY BRAIN
    ---------------------------------------------------------
    knowledge/
      company/
        policies/        refund rules, warranties, claims
        operations/      fulfillment, suppliers, purchase orders
        finance/         invoice rules, margin logic, close process
        marketing/       campaigns, segments, creative learnings
        product/         specs, ingredients, materials, variants
        retail/          stores, partners, events, staffing
        people/          onboarding, leave, expense policy
      platform/
        agents/          instructions, guardrails, tool contracts
        integrations/    API notes, auth quirks, runbooks
      lessons/
        incidents/       what broke, fix, rule learned
        patterns/        repeatable workflows and thresholds

    skills/
      triage-refund.md
      invoice-intake.md
      weekly-pnl.md
      campaign-review.md

    memory/
      2026-05-12.md      what happened today, raw learnings

    templates/
      decision-record.md
      sop-template.md
      product-launch.md
    ---------------------------------------------------------
                         |
                         v
                 Business systems
      ecommerce | ERP | helpdesk | accounting | ads | email | sheets
```

The important line is the one between `memory/` and `knowledge/`. `memory/` is where the system captures what just happened. `knowledge/` is where durable truth goes after review. A brain that only stores memory becomes a junk drawer. A brain that only stores polished docs goes stale. You need both.

## The smallest viable brain

Start smaller than you want to.

The first version should fit in one afternoon. It should not contain every document in your company. It should contain the minimum context needed for an AI assistant to answer operational questions without hallucinating.

Use this starter shape:

```text
brain/
  README.md
  knowledge/
    company-profile.md
    policies/
      returns.md
      shipping.md
      customer-exceptions.md
    operations/
      systems-map.md
      suppliers.md
    finance/
      unit-economics.md
      invoice-rules.md
    marketing/
      brand-voice.md
      campaign-patterns.md
    product/
      catalog-rules.md
  skills/
    answer-customer-policy-question.md
    classify-invoice.md
    write-weekly-trading-note.md
  memory/
    README.md
  templates/
    decision-record.md
    learning-note.md
```

The repo includes a starter skeleton at `templates/brain-starter/`. Fork it. Do not over-design it.

## The starter README

Your `brain/README.md` is the instruction manual for humans and agents. It should be blunt:

```markdown
# Company Brain

This folder is the source of truth for how the business operates.

Rules:
1. Search here before answering company-specific questions.
2. Cite the file used when giving factual answers.
3. If a policy, workflow, supplier rule, or incident changes, update the relevant file.
4. Capture temporary notes in `memory/YYYY-MM-DD.md`.
5. Promote durable lessons from memory into `knowledge/` or `skills/`.

Confidence:
- High: answer is supported by a current file.
- Medium: answer is inferred from files but not explicitly stated.
- Low: answer is missing, stale, or requires a human owner.
```

That README does more work than most teams expect. It tells the AI not to freewheel. It tells the human team where truth belongs. It creates a shared habit: if the answer matters, it should become searchable.

## What goes in first

The best first documents are not strategy decks. They are high-friction operating rules.

For a beauty brand, start with ingredient claims, shade matching, returns hygiene, and creator usage rights. For a food brand, start with shelf life, allergen handling, batch traceability, cold-chain exceptions, and wholesale delivery windows. For a home brand, start with assembly issues, warranty rules, bulky shipping, spare parts, and supplier lead times. For a pet brand, start with sizing, safety claims, subscription changes, and vet-sensitive language. For an outdoor brand, start with warranty boundaries, technical specs, repair policy, and weather-use guidance.

The brain is useful when it answers the questions that slow your team down today.

## What does not go in first

Do not dump your entire Drive into the brain. That creates the illusion of coverage while making retrieval worse.

Do not add private employee data unless you have a clear access model.

Do not let AI write permanent policy without a human owner.

Do not pretend search equals truth. If two files disagree, the brain is telling you your company has a governance problem, not that the model needs a better prompt.

## Why folder structure beats one mega-doc

A single document is easy on day one and unusable on day ninety. Agents need paths, ownership, and update boundaries.

`knowledge/finance/invoice-rules.md` can have a finance owner. `knowledge/product/catalog-rules.md` can have a product owner. `knowledge/marketing/campaign-patterns.md` can change every week without touching returns policy.

Folders also make permissions easier. A customer-service agent may need returns, shipping, and product specs. It probably does not need payroll. A finance agent needs invoices and accounting runbooks. It does not need unreleased product copy. The folder tree becomes the first version of your access model.

## How to start this in your business

1. Create `brain/` from `templates/brain-starter/` and fill only the README, company profile, systems map, returns policy, shipping policy, and brand voice.
2. Pick 20 real questions your team answered last week. Add only the docs needed to answer those questions accurately.
3. Give one AI client access to the folder and require it to cite file paths when answering company-specific questions.
4. Run a weekly 30-minute brain hygiene review: stale docs, missing docs, contradictions, and learnings to promote from memory.
5. Download or fork `templates/brain-starter/` as the artifact. The first useful brain is a skeleton plus discipline, not a data lake.

