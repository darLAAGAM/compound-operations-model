# me.md Interview — Create your personal profile in the swarm

**Category:** Onboarding
**When to use:** once in your first week, after connecting Claude Desktop to the brand's brain.
**Duration:** 5-10 minutes
**Template:** see `~/.claude/skills/me-md-interview/interview-questions.md`

## What it does

Interviews you conversationally to create your `me.md` — a personal profile that every Claude in your brand's swarm will read when working with you. This lets them:

- Adapt the tone to how you communicate
- Prioritize the metrics that matter to *you*
- Know which tools you use daily
- Understand your context (experience, manager, recurring frustrations)
- Skip recommendations you already know

## How to use

Paste this as the first message of a new Claude Desktop chat:

> **"Run the me-md-interview skill. My name is {YOUR-NAME-LOWERCASE}"**

Claude will ask 6-8 conversational questions. **Don't fill in a form** — reply like you would to a colleague getting to know you. At the end it writes your me.md to the brain automatically via the `me_write` tool.

## The internal flow Claude follows

1. **Context** — `brain_read("knowledge/<brand>/team/_template-me.md")` to see the expected format (if a template exists; else uses the default below).
2. **Conversational interview** — 6-8 questions:
   - Who are you + your role + how long at the brand
   - Who you work with daily (names)
   - What you're trying to achieve this year (goals)
   - What tools you use daily
   - How you like to communicate (tone, format, language)
   - What frustrates you / recurring feedback you've received
   - Outside work: interests, values, context (optional)
   - Specific Claude instructions: what to do / not do without asking
3. **Synthesis** — Claude writes a personalized me.md in your voice (does NOT copy the template literally).
4. **Confirmation** — shows you the draft and asks *"anything to add or remove before saving?"*
5. **Save** — `me_write(name, content)` writes to `knowledge/<brand>/team/{your-name}/me.md`
6. **Verify** — `me_read({your-name})` confirms it saved.

## How other Claudes read it

Any Claude in the swarm can `me_read("laura")` before replying to Laura, which automatically adapts responses to:

- **Tone:** if your me.md says *"I'm direct, skip small talk"*, Claude skips small talk
- **Format:** if it says *"I prefer tables for >5 items"*, Claude uses tables unprompted
- **Autonomy:** if it says *"you can draft CS replies without waiting for approval"*, Claude won't ask each time
- **Metrics:** if your goal is *"increase AOV"*, when you look at sales data Claude highlights AOV automatically

## MANDATORY — Claude ALWAYS includes these 4 golden rules in EVERY me.md it generates

When synthesizing a me.md (Step 3 of the workflow), **before** the personal sections, include this block verbatim (these are operational contracts that apply to everyone in the swarm):

```markdown
## Golden rules for Claude when working with me

These rules are enforced ALWAYS, before any chat-specific instruction:

1. **Brain-query-first** — before answering ANY question that depends on brand context (strategy, data, past decisions, policies, people, priorities), RUN `brain_query("<rephrased question>")` first. If the result has relevant info, use it in the answer. Do NOT answer from memory if the brain can provide sources.
2. **Real data, never invented** — if you give me a number (revenue, ROAS, stock, sales, tickets), it must come from a real source via MCP tools (shopify_query, klaviyo_query, etc.). Never approximate or estimate without explicitly flagging it as an estimate.
3. **Read my me.md if it exists** — run `me_read("<my-name>")` at the start of new sessions to load my personal context. Don't ask me things that are already there.
4. **Use /learn at the end** — if the session produced a new gotcha, a reproducible pattern, or an important decision, propose running `/learn` to save it to the brain.
```

These 4 rules are NON-NEGOTIABLE. Claude must NOT shorten or personalize them during the interview. They are the operational contract of the swarm. If the user tries to remove them, explain they are part of how every employee's Claude works.

## When to update

Review and update your me.md when:
- Your role or responsibilities change
- You change manager
- You get important new feedback
- Your quarterly goal changes

To update: *"Claude, I want to edit my me.md. Read it and help me adjust X"*

## Minimal example (perfect for first onboarding)

You don't need to write an essay. 10 lines is enough:

```markdown
# me.md — Laura Pérez

I'm Laura, CS lead at {brand} for 2 years. I report to {founder} and work with the {CS agent name} AI agent.

Goal this year: bring first-response-time to <2h and automate 40% of simple tickets.

Daily tools: Richpanel, Gmail (hi@brand.com), Shopify (read-only), Slack.

Preferences: short replies, emojis OK, Catalan for Catalonia customers, Spanish for others.

Pet peeves: "I'll get back to you later" without a deadline.

For Claude: you can draft ticket replies without waiting for my OK, mark them [DRAFT]. Never send email to a customer without me seeing it first. If you detect a VIP ticket (>5 historical orders), flag it red.
```

## Privacy

- The me.md is saved at `knowledge/<brand>/team/{your-name}/me.md` — visible to the rest of the swarm (the brand's AI agents + colleagues' Claudes via `me_read`).
- **Do NOT include sensitive personal data** (salaries, passwords, private health issues, etc.)
- DO include professional context (role, goals, frustrations at work, manager).

## Troubleshooting

- **Claude can't find the skill:** run `brain_search("me-md-interview")` first.
- **`me_write` returns an error:** probably the name has special characters. Use lowercase, no accents (`maria` not `María`).
- **Not sure what to write:** say *"show me examples of other team profiles"* and Claude will `me_read()` to list existing ones as reference.
