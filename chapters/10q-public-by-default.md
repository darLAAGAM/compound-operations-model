# Chapter 10q: Public-by-default — why agents work in the open

## Private AI solves, public AI teaches

A private AI assistant can help one person move faster. A public AI operating system can teach the organization.

That distinction is central to Brain v2. If every employee uses AI in DMs, the immediate task may get solved, but the company does not learn from the work. The prompt disappears. The source path disappears. The reasoning disappears. The output may be copied somewhere, but the process that produced it is not visible. Another employee facing the same problem next week starts from zero.

Public-by-default changes the learning surface. When non-sensitive work happens in public channels, the whole company can observe how people ask, how agents execute, which sources they use, where they fail, and what good output looks like. A useful Slack thread can become a reusable prompt. A repeated question can become a skill. A strong answer can become a source document. A bug can become a gotcha. A decision can become a task or output record.

The reference Brain v2 upgrade explicitly connected this to the "shop floor" metaphor. In a physical operation, the floor is where work is visible. People learn by watching the process, not just reading the final report. Public agent work creates a digital shop floor: visible by default, private only when privacy or sensitivity requires it.

This is not about surveillance. It is about moving ordinary operational work out of private inboxes and into shared, searchable, teachable spaces. HR, legal, personal, health, compensation, and sensitive topics stay private or restricted. The rest should not disappear into DMs by default.

For a consumer SME, this cultural change matters as much as the tooling. A capture layer can only learn from work it can see. If the company's real decisions happen privately, the Brain will always be incomplete.

## The inspiration and the useful part

The reference implementation drew inspiration from Shopify's River: agents working in public Slack channels rather than private conversations. The useful lesson is not a specific product pattern. It is the operating principle that visible work compounds inside the organization.

When an agent works in public, four things happen.

First, the prompt becomes reusable. Someone can see how the founder asked for a finance variance, how the ops lead asked for a supplier risk summary, or how the CS lead asked for a policy-grounded response. Good prompts spread by observation.

Second, execution becomes observable. People can see whether the agent searched the Brain, used the source system, cited paths, stated uncertainty, and wrote back. This builds trust more effectively than a training deck.

Third, failures become teachable. If an agent answers from stale context, misses a source, or overreaches, the correction happens in the open. The team learns what to watch for, and the Brain can capture the gotcha.

Fourth, outputs become shared memory. A useful result can be recorded as an output, decision, task, or world-model update. The company keeps the learning instead of losing it in one person's private chat.

The pattern is not "everything public." It is "public unless there is a reason not to be." That distinction keeps the culture practical.

## The compounding pattern

The operating loop is simple:

```text
public conversation -> reusable prompt -> observable execution -> shared memory
```

A public conversation starts with real work: "Summarize the customer complaints about sizing this week," "Check whether campaign spend is outpacing contribution margin," "Turn this meeting thread into tasks," or "Draft a supplier reply based on the latest agreement."

A reusable prompt emerges because others can see the framing. They do not need formal training to learn that a good request includes source, timeframe, output format, and decision context. The company develops a prompt culture by watching the best operators.

Observable execution shows the standard. The agent searches the Brain, reads the right paths, calls the right source tools, states confidence, and produces an output. If it skips a step, someone can correct it.

Shared memory is the write-back. The useful artifact becomes a task card, output record, decision, health issue, gotcha, or updated source document. The thread itself may also be captured if it contains a durable signal.

This is internal compounding only. Another company's fork does not make your fork smarter. Your company gets smarter when your own people and agents work visibly, promote useful signals, and write back to your own Brain.

Month one feels like a new tool. Month six feels different if hundreds of public interactions have become reusable prompts, decisions, tasks, outputs, and source improvements.

## Public-by-default rules

Write the policy down. Otherwise every team will interpret "public" differently.

A practical policy for a consumer SME:

| Rule | Default |
|---|---|
| Agent work happens in public project or domain channels | Yes |
| DMs are used for sensitive personal, HR, legal, or private matters | Yes |
| Public channels are eligible for high-signal autocapture | Yes |
| Private channels and DMs are excluded by default | Yes |
| Agents cite sources and tool outputs in public work | Yes |
| Useful outputs are recorded back into the Brain | Yes |
| Sensitive data is redacted or moved to restricted paths | Yes |
| Social chatter is not promoted to memory | Yes |

A simple employee-facing version:

```text
If the work can safely be seen by the team, do it in a public channel.
Use DMs only for personal, HR, legal, compensation, health, or sensitive matters.
When an AI produces something useful, record the output or ask the agent to do it.
```

The policy should also name examples.

Public by default:

- Campaign analysis.
- Customer complaint patterns without unnecessary PII.
- Supplier lead-time changes.
- Store operations questions.
- Product launch checklists.
- Finance variance explanations using approved source data.
- Internal tooling bugs and fixes.
- Meeting action items.

Private or restricted:

- Employee performance or HR issues.
- Compensation and payroll.
- Recruiting candidate details.
- Health, family, maternity/paternity, leave details.
- Legal personal matters.
- Sensitive customer data beyond approved systems.
- Credentials, tokens, security incidents requiring restricted handling.

The point is not to make employees anxious. It is to remove ambiguity. Most work in a consumer SME is not sensitive. Some work absolutely is. The policy should make both clear.

## Slack autocapture pairs with public work

Public-by-default becomes more powerful when paired with selective capture.

The reference Slack autocapture indexes public channels only. The bot joined 76 active public channels and excluded a health-check channel. It captures high-signal messages around campaigns, metrics, decisions, risks, owners, deadlines, finance, product, operations, and tech. It ignores reactions, social chatter, DRY-RUN messages, and bots without business terms.

This is the right pairing: public work creates observable traces; autocapture promotes only the durable parts.

Do not capture every public message. Public does not mean permanent. A channel can be visible without every sentence becoming institutional memory. The capture layer should filter for business value and sensitivity.

A good Slack or Teams implementation has three levels:

1. Visible conversation: the thread is public and learnable by humans.
2. Captured source: a thread or message is saved as raw or inbox context when it has durable value.
3. Promoted memory: only decisions, actions, metrics, risks, and useful patterns become durable signals.

Manual capture should exist too. A person should be able to mark a thread for Brain capture when it contains something important that automation missed. But manual capture should still go through the same privacy and promotion rules.

## Anti-pattern: private team agents

A common mistake is giving every team its own private agent and calling that adoption.

It feels efficient at first. Marketing has a marketing agent. Finance has a finance agent. CS has a CS agent. The founder has a stronger private agent. Each solves local problems. But the company AI culture fragments.

The marketing team does not see how finance asks for evidence. Finance does not see how CS turns customer feedback into product signals. Operations does not see how merchandising investigates stockouts. The founder's best prompts do not spread. Agent failures stay local. The Brain receives inconsistent write-back.

Private team agents are sometimes necessary for sensitive domains. HR and legal often need restricted channels. Finance may need restricted outputs. But "restricted when needed" is different from "private by default."

A healthier structure is:

| Domain | Working default |
|---|---|
| General AI learning | Public `#ai` or equivalent |
| Projects | Public project channels |
| Customer patterns | Public or internal CS channel with PII rules |
| Finance analysis | Public summary, restricted raw data when needed |
| HR/legal/personal | Private or restricted |
| Incidents/security | Restricted according to incident policy |

This lets the organization learn from most work while protecting the categories that genuinely need privacy.

## Cultural implementation

The cultural side is simple to describe and hard to install.

Leaders must use the public channels themselves. If the founder keeps asking the best AI questions in DMs, everyone else will copy that behavior. If operators see the founder ask in public, accept correction in public, and turn outputs into Brain records, the norm changes.

Managers should reward reusable work. A good AI thread is not just a solved problem; it is training material. It should be linked in onboarding, turned into a skill, or captured as a pattern.

The public AI channel should avoid becoming a showroom. It is not for polished demos only. It should include ordinary work, failures, corrections, and gotchas. A culture that only shares wins will not teach people how to use the system safely.

The company also needs a clear escape hatch. Employees should know they can move to private or restricted channels when the topic involves HR, personal data, legal sensitivity, health, family, compensation, or anything that feels inappropriate for a public channel. Public-by-default should not become social pressure to expose sensitive work.

A practical manager habit is to ask, "Can this be public?" before starting a DM with an agent. If yes, move it. If no, keep it restricted and label why.

## Risks

The first risk is noise capture. Public channels contain acknowledgements, reactions, half-thoughts, tests, jokes, and repeated bot messages. The reference pipeline explicitly ignores reactions, chatter, DRY-RUN, and bots without business content. Your implementation should do the same.

The second risk is sensitive leakage. Public channels can still contain sensitive information because humans make mistakes. Hard stops are necessary: HR, payroll, health, family, recruiting, candidates, CVs, interviews, maternity/paternity, absences, personal legal matters, credentials, and private customer data should not be promoted. When detected, restrict or remove.

The third risk is performative AI. If people know the channel is visible, they may share only polished interactions. That reduces learning. Leaders should model ordinary, useful work rather than demos.

The fourth risk is channel sprawl. If every project creates a channel and none have owners, capture becomes noisy. Public-by-default needs channel hygiene: owners, naming, archiving, and clear purpose.

The fifth risk is overconfidence from visibility. A public answer is not automatically correct. Agents still need source discipline, tool calls, confidence, and review. Visibility helps catch errors; it does not eliminate them.

## Adjacent lessons

Two adjacent ideas informed the reference design.

The first is the second-brain principle associated with Omar Ismail: useful memory is not passive storage. It is retrieval, synthesis, and action. Public work supports that because the raw interaction can become a promoted signal, task, output, or decision. Storage alone is not enough.

The second is the shift from hierarchy to intelligence described in Block's operating ideas: organizations should route work through distributed intelligence rather than only static hierarchy. In Brain v2, that appears as public work, DRI maps, capability gaps, health checks, and a world model. The company can see what it knows, who owns what, and where the system is blocked.

These are not slogans to paste into a deck. They are design constraints. Work should be visible when safe. Memory should be actionable. Ownership should be explicit. Gaps should be logged. The world model should refresh from real signals.

## Implementation checklist

For Compai readers, start with this checklist:

- Create a public AI channel for examples, questions, and shared learning.
- Define which project and domain channels are public by default.
- Write the DM/private-channel exceptions: HR, legal, personal, health, compensation, recruiting, credentials, and sensitive customer data.
- Put the policy in the master prompt.
- Configure the chat bot to join public channels only.
- Add high-signal autocapture for decisions, metrics, risks, owners, deadlines, customer patterns, operations, finance, product, and tech.
- Ignore reactions, social chatter, test messages, DRY-RUN, and bot noise.
- Add manual thread capture for important misses.
- Route captured signals through `brain_capture`.
- Promote selectively into tasks, outputs, decisions, health, and world model.
- Review false positives weekly in the first month.
- Turn good public threads into onboarding examples or skills.

Do not start by indexing private DMs. Do not make every public message permanent. Do not create one private agent per team and call it a company operating system.

A realistic rollout is cultural and technical. The policy can be written in one day. The capture layer and review loop take longer. As part of a full Brain v2 rollout, expect 6-8 weeks with one engineer for a serious consumer SME implementation.

## What to measure

Measure the behavior, not only the bot activity. Useful early metrics include number of public AI threads, number of threads captured manually, number of promoted signals from public channels, number of outputs recorded from public work, number of gotchas created from visible failures, and number of onboarding examples generated from real threads.

Also measure the negative side. Count false positives, restricted removals, noisy captures, and cases where a sensitive topic had to move from public to private. These are not embarrassing metrics. They are how the company learns the boundary. A public-by-default policy without a correction loop will either become too loose or too timid.

The best sign is qualitative: employees start linking to prior threads instead of asking the same question again. That means public work is becoming shared memory.

## Start with leaders

Do not launch public-by-default as a policy memo and expect behavior to change. Start with three visible leaders: the founder, one operator, and one domain lead. Ask them to move ordinary AI work into public channels for two weeks, including imperfect attempts. Then turn the best threads into onboarding examples.

This creates proof before enforcement. Employees see real work, not theory. They see what belongs in public, what gets moved to private, and how useful outputs become Brain records. After that, the written policy has something concrete to point at.

The behavior has to be visible before it can be copied. Treat the first two weeks as culture seeding, not compliance.

If you want help, hello@usecompai.com. Most don't.
