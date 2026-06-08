# Step 6 — Create your personal profile (me.md)

*Detail sub-page of the onboarding checklist. ~15 min.*

This is the most important step of onboarding. It's what makes every future Claude interaction personalized to *you*.

## What is a me.md

A markdown file at `knowledge/{BRAND}/team/{your-name}/me.md` that every Claude in the swarm reads before working with you. It captures:

- Your role + tenure
- Your manager + team
- Your current goals
- Tools you use daily
- Communication preferences (tone, format, language)
- Recurring frustrations + pet peeves
- Specific instructions for Claude (what to do / not do without asking)

It's 10-30 lines of markdown. Not a novel. Not a formal document. Your voice.

## How to create it — the interview

1. Open a new Claude Desktop chat
2. Paste this as your first message, replacing `{your-name}` with your lowercase first name:

```
Run the me-md-interview skill. My name is {your-name}.
```

3. Claude asks you 6-8 questions. Examples:
   - "Who are you and what's your role at {BRAND}?"
   - "Who do you work with most days?"
   - "What are you trying to accomplish this year?"
   - "How do you prefer to communicate — short and direct? With examples? Tables?"
   - "What frustrates you when asking someone for help?"
   - "What should Claude do on your behalf without asking permission?"

4. **Answer like a human.** Not bullet points. Not formal. Think "introducing yourself to a new colleague."

5. Claude synthesizes a me.md and shows it to you. You review and say "OK save it" or "adjust this sentence".

6. Claude writes it via `me_write("{your-name}", <content>)` to the brain.

7. Verify: in a fresh chat, ask *"what's in my me.md?"* — Claude should `me_read("{your-name}")` and show it.

## The 4 golden rules (automatically included)

Every me.md has a mandatory top section — the "Golden Rules for Claude when working with me":

1. **Brain-query-first** before answering context-dependent questions
2. **Real data, never invented** — numbers come from MCP tools, not from LLM memory
3. **Read my me.md** at the start of new sessions
4. **Propose /learn** when a session produced a useful insight

You can't remove these — they're the operational contract every employee's Claude follows. The skill won't let you delete them, and if you try Claude will explain why.

## Privacy

- Your me.md is visible to:
  - Your brand's AI agents (cs, finance, ops, etc.)
  - Other employees' Claude sessions (when they `me_read("{your-name}")`)
  - {founder} or any admin-key holder
- Your me.md is NOT visible to:
  - Anyone outside your brand
  - OperAI the company
  - Any other brand running OperAI

**Do NOT include sensitive personal data.** Don't write your salary, your private health, your passwords, or things you wouldn't tell a colleague. This is professional context, not a diary.

## Updating your me.md

Update it whenever:
- Your role changes
- Your manager changes
- Your quarterly goal changes
- You get important new feedback
- You realize a preference you didn't articulate initially

To update: *"Claude, I want to edit my me.md. Read the current version and help me adjust {specific thing}."*

## Example me.md (from a real CS manager)

```markdown
# me.md — Laura Pérez

## Golden rules for Claude when working with me
[auto-generated — do not edit]
...

## Who I am
I'm Laura, CS lead at {BRAND} for 2 years. Before that I was 4 years at another beauty brand doing the same role.

I report to {founder} and work with Mafalda (our CS AI agent) + a team of 3 agents across ES and IT.

## Goal this year
Bring first-response-time to <2h and automate 40% of simple tickets with Mafalda.

## Daily tools
Richpanel, Gmail (hi@brand.com shared inbox), Shopify (read-only), Slack.

## Communication preferences
- Short replies, no padding
- Emojis OK
- Use Catalan when I write Catalan, Spanish otherwise
- Tables for anything with >5 items

## For Claude
- You can draft ticket replies without waiting for my OK — just mark them [DRAFT]
- Never send an email to a customer without me seeing it first
- If you detect a VIP ticket (>5 historical orders), flag it with 🔴
- When I ask for "the numbers" on anything, default to last-7d + last-30d side-by-side
```

10 lines of "Who I am / Goal / Tools", 10 lines of preferences + Claude instructions. That's the whole thing.

## If you skip this step

Every Claude session starts cold. You'll re-explain your role, your tools, your preferences every single time. You'll get generic answers instead of personalized ones. You'll waste 2-5 minutes per session.

Over a year, at 10 sessions/day, that's ~150 hours of re-explanation you avoid by spending 15 minutes once.

This is the biggest lever in the whole onboarding. Don't skip.
