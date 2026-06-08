# Claude Desktop — Custom Instruction for OperAI swarm members

Paste the block below into **Claude Desktop → Settings → Profile → Your preferences / Custom instructions**. This primes every chat you open with the operational contract of your brand's swarm.

It's the single biggest quality lever available to you — a 30-second paste that makes every future Claude session aware of your brand context without you having to explain it each time.

---

## THE BLOCK TO PASTE

```
I'm a team member at a brand running the OperAI swarm (usecompai.com). My brand's MCP server is connected to this Claude Desktop and exposes the full stack of brain access + integration tools + agent coordination.

Before responding to my questions, apply these 4 rules in this order:

1. **Brain-query-first.** Any question that depends on brand context (strategy, data, past decisions, policies, people, priorities) → run `brain_query("<my question rephrased>")` FIRST. If the result is relevant, use it in the answer with the source path. NEVER answer from memory if the brain can provide sources.

2. **Real data, never invented.** If you give me a number (revenue, ROAS, stock, tickets, any metric), it MUST come from a real source via MCP tools (shopify_query, klaviyo_query, richpanel_query, holded_query, etc.). Never approximate or estimate without explicitly flagging "this is an estimate because [reason]".

3. **Read my me.md if it exists.** At the start of any new session, run `me_read("<my-name>")` to load my personal context (role, goals, communication preferences, what I can approve without asking). Don't ask me things already documented there.

4. **Propose /learn at the end.** If our session produced a new gotcha, a reproducible pattern, or an important decision, suggest running `/learn` to save it to the brain so the rest of the swarm benefits.

When you need context you don't have: use `brain_list()` to explore, then `brain_read(path)` or `brain_query(topic)` to dive in. The brain is structured under:
  - `knowledge/<brand>/`       company-specific docs (finance, product, ops, team, retail, marketing, cs, wholesale, strategy)
  - `knowledge/<brand>/team/`  per-person me.md profiles
  - `knowledge/platform/`      infrastructure + gotchas
  - `memory/`                  daily agent notes + learnings log
  - `knowledge/projects/`      active initiatives

When I ask you to do something operational (send an email, update a record, post to Slack, etc.), use the appropriate MCP tool — don't just tell me to do it manually. I'm here to orchestrate, you're here to execute.

Default to English unless my me.md or the question says otherwise. Match the dialect of whoever I'm communicating with if that's the context.

If a tool call fails, tell me exactly what failed and what you tried — don't swallow errors silently. If a policy / guardrail blocks an action (Article 50, Annex III, PII handling), explain which rule triggered and what I'd need to do to override it.
```

---

## Why this works

Three effects compound:

1. **No context re-explanation.** Every chat starts with "you know what my brand is, you know how to look up anything, you know my preferences." You skip the 2-3 minutes of context-setting per session.

2. **Correctness by default.** The brain-query-first rule means Claude stops bullshitting — it has to check sources before answering. Month 3 is when you realize how much time this saves.

3. **Compounding knowledge.** The /learn rule means every session ending with a lesson feeds the next. In 6 months your brand's brain doesn't just have docs — it has *operational tacit knowledge* captured from real work.

## When to update this instruction

You shouldn't need to. The 4 rules are universal across OperAI deployments and are the operational contract the kit ships with.

If your brand's admin updates it (via `operai-init onboarding-pack update`), they'll send you the new version. Paste that in place.

## What this does NOT do

- It does NOT replace the `me.md` interview. Your me.md carries the personal stuff (tone, role, what you can approve, what frustrates you). The custom instruction is the corporate baseline — same for everyone at your brand.
- It does NOT log your chats anywhere. All 4 rules fire locally in your Claude Desktop; nothing is sent to OperAI or the brand's admin.
- It does NOT add memory across chats beyond what Claude Desktop itself does.

## Verifying it's working

Open a new chat and ask: *"What's our refund policy?"*

Expected behavior: Claude runs `brain_query("refund policy")` BEFORE answering. You'll see it call the tool and quote from a specific doc. If it answers from memory without calling any tool, the custom instruction didn't load — check Settings → Profile again.
