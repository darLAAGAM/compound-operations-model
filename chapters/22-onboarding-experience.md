# Chapter 22: The Onboarding Experience — Onboarding v3.1

> **Appendix · Technical depth.** This chapter is for operators or engineers deploying the brain themselves. It covers implementation details that aren't needed for understanding the conceptual architecture. Skip if you're reading for strategy.

## What this chapter ships

A team forking Compai now has the same onboarding experience that the reference deployment's employees live today: Claude Desktop connected, me.md created, custom instruction applied, Notion checklist in hand — in under 30 minutes per person.

Onboarding v3.1 closes the onboarding gap with three deliverables:

1. **Onboarding pack** shipped in `repo/init/onboarding-pack/` and mirrored at `usecompai.com/onboarding/*`
2. **`operai-init setup-brand`** — interactive wizard that runs the founder-facing happy path
3. **`operai-init team-onboard <name>`** — composite command that onboards one employee end-to-end

## The onboarding pack

Shipped assets, generic + portable:

```
onboarding-pack/
├── README.md
├── skills/
│   ├── me-md-interview/SKILL.md    Conversational personal profile creator
│   └── learn/SKILL.md               Session-end learning extractor
├── claude-desktop/
│   └── custom-instruction.md        4-rule operational contract (paste-once)
└── notion-templates/
    ├── 01-onboarding-checklist.md  Day 1 / Week 1 / 30-60-90
    ├── 02-step-6-personal-profile.md Detail: the me.md step
    └── 03-weekly-check-in.md        Friday 15-min reinforcement
```

Every markdown has two placeholders: `{BRAND}` and `{founder}`. The install command interpolates both. The result is brand-specific onboarding material ready to import into Notion.

## The 4 golden rules

Every employee's Claude Desktop runs under the same operational contract:

1. **Brain-query-first** — context-dependent questions trigger `brain_query` before answering
2. **Real data, never invented** — numbers come from MCP tools, not from LLM memory
3. **Read my me.md** — personalization loads at session start via `me_read`
4. **Propose /learn at the end** — session insights get saved to the shared brain

These 4 rules live in two places:
- The **custom instruction** employees paste into Claude Desktop (applied globally)
- Every **me.md** synthesized by the me-md-interview skill (included verbatim)

Neither the employee nor the brand's admin can remove them. They are the operational contract of the swarm.

## The founder's happy path

Before v3.1, the founder ran 12+ commands to go from install.sh to fully configured. v3.1 replaces that with one wizard:

```bash
# After curl usecompai.com/init | bash
operai-init setup-brand
```

The wizard chains:

1. **LLM providers** → `operai-init llm configure` (interactive)
2. **CS factory** → `operai-init factory enable --domain cs`
3. **Cloudflare tunnel** → `operai-init tunnel mcp.<brand>.com`
4. **Webhook receivers** (optional, per helpdesk) → `operai-init webhook configure`
5. **Slack digest** (optional) → `operai-init digest configure` + `schedule`
6. **Governance layer** (optional) → `operai-init governance enable`
7. **Onboarding pack install** → `operai-init onboarding-pack install --founder <name>`
8. **Admin key check** → create one if missing

Each step is skippable with a clear prompt. The wizard ends with a summary of what to start, what to verify, and what to do next.

**15-20 minutes** from `install.sh` finishing to a fully configured brand deployment.

## The employee's happy path

For every new employee the founder wants to onboard:

```bash
operai-init team-onboard laura --role team --groups cs,retail
```

Which chains:

1. **`operai-init key create laura --role team --groups cs,retail`** — generates `lgm_xxx` key with ACL groups
2. **`operai-init assess laura`** — 10-question interview classifying M-shaped / T-shaped / frontline + 90-day training path
3. **`operai-init team-join --out laura-team-join.sh`** — generates the employee's personalized install script with MCP URL baked in
4. **Email template output** — the founder copy-pastes this to laura, containing:
   - The `curl... | bash` one-liner with `brand` + `mcp` query params
   - The API key (sent via secure channel, NOT in the email)
   - Link to the custom instruction
   - Link to the checklist

The entire founder-side cost for onboarding one employee: **3 minutes** (+ the interview Q&A which takes another 8-10).

## The employee receives

The email template the founder sends:

```
Subject: Welcome to Acme — your AI swarm onboarding

Hey a team member,

Welcome to Acme. To get you set up on our AI swarm (under 30 minutes):

1. Run this in your terminal (Mac/Linux) or PowerShell (Windows):

   curl -fsSL 'https://usecompai.com/team-join?brand=acme&mcp=mcp.acme.com' | bash

2. When it asks for your API key, paste (separately/securely):

   lgm_XXXXXXXXXXXX

3. After Claude Desktop reconnects, paste the custom instruction from:

   https://usecompai.com/onboarding/custom-instruction

4. Your full onboarding checklist + 30-60-90 plan:

   https://usecompai.com/onboarding/checklist

Step 6 of the checklist is the most important — takes 15 min and makes every
future Claude chat personalized to you.

Questions → DM me directly.
```

The employee runs the curl, pastes the key, opens Claude Desktop, applies the custom instruction, runs `Run the me-md-interview skill. My name is laura` in Claude Desktop, and in under 30 minutes they are a fully onboarded swarm member.

## Mapping to the reference deployment

| What the reference deployment's employees do today | How Onboarding v3.1 replicates it |
|---|---|
| Install Node + Claude Desktop | `team-join.sh` detects OS, installs fnm + Node, writes MCP config |
| Paste API key | Script prompts for `lgm_xxx`, puts it as env var referenced by `Authorization:Bearer` header |
| Connect to `mcp.<brand>.com/sse` | Script uses the brand's `mcp.<brand>.com/sse` — per-brand MCP |
| Get 95 MCP tools | Get 11 brand-scoped MCP tools (brain, memory, me, status, integrations passthroughs) |
| Custom instruction (brain-query-first, etc.) | `usecompai.com/onboarding/custom-instruction` served with same 4 rules |
| me.md interview via skill | `me-md-interview` skill shipped in pack + invokable via Claude Desktop |
| Notion onboarding doc | `notion-templates/01-onboarding-checklist.md` — Day 1 / Week 1 / 30-60-90 |
| L0-L3 + M/T/frontline frameworks | Ch.14 + `operai-init assess` command |
| /learn skill for session-end knowledge capture | `learn` skill shipped in pack |
| Paso 6 (personal profile creation) | `02-step-6-personal-profile.md` with step-by-step |
| Weekly check-in ritual | `03-weekly-check-in.md` Friday 15-min template |

The only thing the reference deployment has that the repo doesn't automatically give you: **12 months of accumulated brain content** (3,007 docs, 352 skills, 21 Pattern Library entries). That's the non-transferable part — every brand accumulates its own over time.

## Pack updates

When Compai improves the onboarding assets, brands pull updates without redeploying the full repo:

```bash
operai-init onboarding-pack update     # downloads latest from usecompai.com
operai-init onboarding-pack install    # re-interpolates for your brand
```

New files get added. Existing files that you've customized locally are preserved. The `update` command backs up the previous pack before overwriting.

## What happens on the brand's brain

After the pack install, the brand has:
- `/opt/operai/onboarding/` with interpolated templates ready to paste into Notion
- `/opt/operai/services/init/onboarding-pack/` with the pristine (non-interpolated) originals for reference
- `/opt/operai/brain/skills/me-md-interview/SKILL.md` + `/learn/SKILL.md` (needs to be copied from the pack to the brand's brain skills folder — install.sh v3.1 does this automatically)

The brand's MCP server's `skill_read("me-md-interview")` returns the SKILL.md content, so when an employee types `Run the me-md-interview skill` Claude can look up how to execute it.

## Commercial framing (same rule)

Everything in Onboarding v3.1 is in the open-source repo. No separate onboarding SKU. The pack + the wrappers ship with every deployment.

The logic: the hardest part of AI adoption is not the technology, it's the habits. The onboarding pack is the lever that moves the habits. Keeping it in the base repo maximizes adoption across every brand using Compai, which in turn maximizes the Pattern Library's cross-company learning (which IS a moat).

## Scope explicitly NOT in v3.1

1. **No training content beyond Notion templates.** If a brand wants custom video training, that's a Custom Engagement (Ch.13).
2. **No automatic me.md interview trigger.** The employee has to type the command. Making Claude Desktop auto-open a session with that command is a Claude Desktop feature request, not an Compai one.
3. **No integrated onboarding tracker.** The brand uses their own HRIS or Notion for tracking. `operai-init assess --team` shows profile distribution but not onboarding completion state.
4. **No certification / testing.** Philosophy: adoption is measured by real use (`/learn` count, brain writes, workflow improvements) not by test scores.

---

→ Back to [Ch.21 Webhooks + Slack Digest](21-webhooks-digest.md) · Forward to Ch.23 *(v3.2 — coming)*
