# /learn — Extract learnings from the current session

**Category:** Meta / Self-improvement
**When to use:** at the end of a working session where you've solved something non-trivial, discovered a gotcha, or changed how you do something.
**Duration:** 2-3 minutes

## What it does

Reviews the current conversation, extracts the genuine learnings, and saves them to the right places in the shared brain so the WHOLE swarm (other employees, AI agents, future Claudes) benefits. This is how you convert "I solved this once" into "nobody has to solve it again."

## How to use

At the end of your session, write:

> **"Run the learn skill"** or **"/learn"** or **"save learnings from this session"**

Claude will then:

1. **Analyze the current conversation** — identifies what was genuinely learned (not what was attempted, not typing errors — **real gotchas**, new techniques, patterns that worked/failed, tool info).

2. **Classify the learnings** into 3 categories:
   - **Personal / user-specific** → appends to `knowledge/<brand>/team/{your-name}/learnings.md`
   - **Corporate / swarm-wide** → writes to `knowledge/platform/gotchas/{tool}.md` or `knowledge/<brand>/{area}/learnings.md`
   - **Agent-specific** → if the learning is about how an agent should behave, suggests updating its SOUL

3. **Proposes diffs BEFORE applying** — shows what will be written where, asks confirmation.

4. **Applies via `brain_learn` MCP tool** which saves + emits a summary of captured items.

## Philosophy (what to save vs discard)

### ✅ DO save
- **Reproducible tool gotchas**: "Stockagile URLs WITHOUT trailing slash, with slash → 404"
- **Patterns that worked with evidence**: "To find angry customers, richpanel_query filter priority=HIGH then cross-reference Shopify LTV"
- **Permanent user decisions**: "{Founder name} prefers tables vs bullets for reports with >5 items"
- **Bugs + workarounds**: "Notion API doesn't accept `[callout]`, use `<callout>` instead"
- **New useful integrations or endpoints**: "pinterest_ads_query with endpoint `analytics` + UPPERCASE columns works"

### ❌ DON'T save
- Trivial conversation details
- Typing errors / autocorrect
- Answers that came out perfect on first try (no learning there)
- Sensitive user info (passwords, private personal data)
- Unvalidated assumptions ("I think maybe...")

## Example invocation

**User:** `/learn`

**Claude (real example):**
```
Reviewed the session. 3 learnings identified:

1. **[Tool gotcha]** Notion update-page with `[callout]` SQUARE bracket syntax fails — renders as plain text. Correct syntax is `<callout icon="X">` HTML-like.
   → Save to: knowledge/platform/gotchas/notion-api.md

2. **[Pattern]** To add new blocks to a Notion doc without deleting existing ones, use update_content with old_str/new_str instead of replace_content.
   → Save to: knowledge/platform/gotchas/notion-api.md

3. **[Personal — {Founder}]** You prefer deadlines in bold + red color in team comms.
   → Save to: knowledge/<brand>/team/{founder}/learnings.md

Confirm + write to brain? (yes/no/adjust)
```

## Technical implementation

The skill uses the MCP tool `brain_learn(category, location, content)` which:
- Creates files/directories if missing
- Appends to existing files (never overwrites)
- Timestamps each entry (`## YYYY-MM-DD — {title}`)
- Logs globally to `memory/learnings-log.md` with summary

## Variants

- **`/learn quick`** — no confirmation, auto-saves just the tool gotchas (low friction, high-confidence items)
- **`/learn personal`** — only updates the user's personal learnings (not corporate)
- **`/learn [topic]`** — only captures learnings about that specific topic

## Relation to other practices

- Complements manual **brain_write** (used when you consciously document something)
- Enforces **Boil the Ocean** — a learning unsaved is a loose thread
- Feeds corporate **context docs** periodically (every month, consolidate learnings.md into the strategic context)

## Usage log

Every `/learn` invocation appends one line to `memory/learnings-log.md` with: date, user, # items saved, categories. This measures how collective knowledge grows.
