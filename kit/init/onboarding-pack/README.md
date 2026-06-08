# OperAI Onboarding Pack

*Generic onboarding assets for any brand running OperAI. Ships in Kit v3.1+.*

The goal of this pack: every employee of a brand using OperAI goes through **the same onboarding experience the reference deployment employees get today** — 30 min, one command, Claude Desktop connected, me.md created, custom instruction applied, checklist imported into Notion.

## What's in the pack

```
onboarding-pack/
├── README.md                              (this file)
├── skills/
│   ├── me-md-interview/SKILL.md           Conversational personal profile creation
│   └── learn/SKILL.md                     Session-end learning extraction
├── claude-desktop/
│   └── custom-instruction.md              Paste-into-profile operational contract
└── notion-templates/
    ├── 01-onboarding-checklist.md         Day 1 / Week 1 / 30-60-90 plan
    ├── 02-step-6-personal-profile.md      Detail: how to run the me.md interview
    └── 03-weekly-check-in.md              Friday 15-min reinforcement ritual
```

## How the founder uses this pack

At setup time (once per brand):

```bash
# As part of the happy path
operai-init setup-brand
  → when you reach "team onboarding", the wizard:
    1. Copies this pack to /opt/operai/onboarding/ for the brand
    2. Does a find-replace of {BRAND} and {founder} across all templates
    3. Generates a team-join.sh customized to your MCP URL
    4. Emits a ready-to-paste email template for sending to employees
```

Or standalone:

```bash
operai-init onboarding-pack install   # copy + interpolate templates
operai-init onboarding-pack show      # print the paths
operai-init onboarding-pack update    # re-pull latest from usecompai.com/onboarding/
```

## How a new employee uses this pack

The founder sends them one message:

```
Hey Laura,

Welcome to {BRAND}. To get you set up on our AI swarm (under 30 minutes):

1. Run this in your terminal (Mac / Linux) or PowerShell (Windows):
   curl -fsSL "https://usecompai.com/team-join?brand={BRAND}&mcp=mcp.{BRAND}.com" | bash

   When it asks for your API key, paste: lgm_XXXXXX (I'll send this separately for security)

2. After Claude Desktop reconnects, paste the custom instruction from:
   https://usecompai.com/onboarding/custom-instruction

3. Your full onboarding checklist is in Notion:
   {notion-link}

   Step 6 is the most important — takes 15 min and makes every future Claude chat personalized to you.

Questions → DM me directly.
```

The employee follows the 3 steps, done in ~30 min. The checklist covers Day 1 / Week 1 / monthly + 90-day progression.

## How to customize for your brand

Three find-replace placeholders in every template:

- `{BRAND}` — the brand's display name (e.g. "Acme" or "Nuvo")
- `{founder}` — the founder's name or role ("Diego" or "the founder")
- `{your-name}` — appears in `me.md` examples; employee fills this in

The `setup-brand` wizard does this automatically. If you're customizing manually:

```bash
cd /opt/operai/onboarding
sed -i 's/{BRAND}/Acme/g; s/{founder}/Diego/g' notion-templates/*.md claude-desktop/*.md
```

## Adding your own skills

The pack ships 2 skills (me-md-interview + learn). To add more:

1. Create a new folder under `skills/<name>/SKILL.md`
2. Copy the structure of an existing skill (header, when-to-use, how-to-use, implementation notes)
3. Push it to the brand's MCP skills directory so `skill_read("<name>")` works

Each brand's MCP already exposes `skills_list()` and `skill_read(name)` as standard tools. Anything in `/opt/operai/brain/skills/<name>/SKILL.md` on the VPS becomes available to every connected Claude.

## Updating the pack

OperAI ships updates to this pack as the product evolves. To pull the latest:

```bash
operai-init onboarding-pack update
```

This re-downloads from `usecompai.com/onboarding/pack.tar.gz` and overwrites the templates **but preserves your brand-customized interpolations** (only updates template bodies, re-applies your {BRAND}/{founder} substitutions).

For the skills, the updates are additive — new skills appear, existing ones get improvements. If you've customized a skill's SKILL.md yourself, `update` asks before overwriting.

## Relationship with the kit

This pack is **shipped inside the €299 Kit** at `kit/init/onboarding-pack/`. It's also served at `usecompai.com/onboarding/*` for brands that want to inspect before buying or pull updates without redeploying the full kit.

No separate tier. No upsell. It's the onboarding experience baked into every deployment.

## Philosophy

Most AI transformation pilots fail at adoption, not technology. The transformation isn't "we bought an AI tool" — it's "every employee uses the brain habitually." The skills + the custom instruction + the 30-60-90 checklist are what get you from tool-installed to habit-formed.

The metric we track is the **socioemotional time ratio** — the % of an employee's week spent with humans (customers, team, partners) vs systems. Pre-OperAI: ~30%. Post-OperAI, once adoption crosses the Month-3 threshold: 70%+.

This pack is the mechanism that makes the ratio move.
