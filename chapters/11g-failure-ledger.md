# Chapter 11g: The Failure Ledger — 32 Production Lessons

## Credibility comes from the failures

The fastest way to spot a fake AI operating-system story is the absence of incidents.

Real systems fail. Tokens expire. APIs paginate silently. Cron runs without environment variables. Agents answer from stale memory. Dashboards show old data. A model migration changes tone. A webhook receiver misses expiring media. A cheap model works in testing and collapses under load.

The reference deployment is credible because it has a failure ledger. Chapter 11b contains the longer production lessons. This chapter is the index: what failed, what fixed it, and the one rule worth carrying forward.

Use it before you build.

## The ledger

| # | What failed | Fix | One-rule lesson |
|---:|---|---|---|
| 1 | Shared OAuth tokens caused cascading rate-limit failures across agents | One token per agent, capped retries, health checks | Isolate credentials by worker |
| 2 | Cached credentials overrode environment settings | Inspect true auth priority chain and clear hidden caches | Debug the credential actually used |
| 3 | macOS services launched in the wrong mode | Use the right LaunchDaemon/LaunchAgent pattern and explicit `HOME` | Service managers are part of the app |
| 4 | Invalid runtime config created crash loops | Add config doctor and validation after edits | Validate before restarting the fleet |
| 5 | Unused messaging channels replayed messages and caused storms | Reduce channel surface and disable unused listeners | Fewer channels means fewer failure modes |
| 6 | API header assumptions broke Stockagile-style auth | Test auth with curl before coding wrappers | Vendor auth formats are not universal |
| 7 | Semantic memory filled with duplicates and noise | Deduplicate, curate, and prefer structured docs | Memory without hygiene degrades agents |
| 8 | Policies changed but the brain did not | Add brain updates to product and policy launch checklists | If it is not in the brain, agents do not know it |
| 9 | Autonomy was tempting before quality was proven | Shadow mode, review queues, confidence thresholds | Draft first, approve later, automate last |
| 10 | Reverse-engineered sessions depended on 2FA state | Add session health checks and relogin runbooks | Browser sessions are operational dependencies |
| 11 | A memory product created more noise than recall | Remove harmful components even if they sounded strategic | Kill features that hurt the system |
| 12 | One host could not comfortably run everything | Split primary VPS and local/secondary host roles | Architecture follows operational load |
| 13 | VPN-only MCP access slowed team rollout | Use a public HTTPS tunnel with auth | Access friction kills adoption |
| 14 | Cron jobs failed because env vars were missing | Source config explicitly inside cron scripts | Cron is not your shell |
| 15 | Skills lived inside one workspace | Expose skills through MCP/shared brain | Procedures must be shared infrastructure |
| 16 | Plugin config overwrote existing settings | Extend configs instead of replacing them | Merge, do not clobber |
| 17 | An important workflow had no official API | Build a small microservice around the actual need | Missing APIs require owned adapters |
| 18 | Interactive permissions hung unattended agents | Configure headless-safe permission modes | Background agents cannot wait for prompts |
| 19 | World-writable plugin paths looked like a quick fix | Fix ownership and permissions properly | Never use `chmod 777` as operations |
| 20 | Local loopback services were not reachable safely | Use explicit private-network port forwarding | Secure reachability needs design |
| 21 | Cheap models passed light tests and failed peak load | Route by reliability and workload, not sticker price | Cheapest reliable beats cheapest token |
| 22 | Prompt injection hardening was uneven | Roll out standard anti-injection language fleet-wide | Every agent needs hostile-input assumptions |
| 23 | Humans resent silent agents and resend work | Add an ACK rule for task receipt | Acknowledge fast, execute carefully |
| 24 | Free-tier LLMs were treated like production capacity | Keep free/cheap models as fallback only | Free tiers are not infrastructure |
| 25 | Runtime process behavior did not match `systemd Type=simple` | Use the correct process manager pattern | Know whether your process forks |
| 26 | Vendor APIs changed silently | Monitor successful semantic calls, not just uptime | HTTP 200 is not proof of correctness |
| 27 | Async Playwright/scraper code collided with MCP event loop | Process-isolate blocking or complex async work | Keep tool servers responsive |
| 28 | Heartbeat schema drift broke runtime validation | Add doctor/fix after runtime upgrades | Schema migration is an operations task |
| 29 | Existing subscriptions were not used in model routing | Reuse reliable paid seats where appropriate | Cost optimization can be architectural |
| 30 | Model migration changed personality and output style | Retune SOUL/prompts per model | Provider swaps are behavior changes |
| 31 | Fleet updates were done too broadly | Stage config fixes and validate agent by agent | Roll out swarm changes in waves |
| 32 | Node 25 broke streaming CLI behavior | Pin affected wrappers to Node 22 LTS | Pin runtimes that affect IO |

## How to read this

Do not read the ledger as a list of embarrassing bugs. Read it as a build order.

If you are setting up your first company brain, lessons 7, 8, and 15 matter immediately. If you are deploying agents, lessons 1, 4, 9, 18, 21, 22, 23, and 30 matter. If you are exposing tools to a team, lessons 13, 16, 20, 26, and 27 matter. If you are automating scheduled workflows, lessons 14, 25, 28, 31, and 32 matter.

The ledger is a map of where naive implementations break.

## Cross-vertical examples

A food brand running invoice intake will hit lessons 14 and 26 when supplier portals export late or cron lacks credentials. A beauty brand using AI for claims review will hit lesson 22 because customer messages can contain hostile instructions. A home brand automating warranty triage will hit lesson 8 if product version docs are stale. A pet brand running subscription workflows will hit lesson 9 if it auto-changes plans before review. An outdoor brand with seasonal spikes will hit lesson 21 if a cheap model collapses during peak warranty volume.

Different verticals, same failure modes.

## What a good failure note contains

Each detailed incident file should include:

```text
Title:
Date:
Severity:
Area:
What failed:
User/business impact:
Root cause:
Fix:
Verification:
Prevention rule:
Owner:
Related files/tools:
```

The prevention rule is the most valuable line. A postmortem that does not change a rule is just storytelling.

## Limitations

The ledger is not complete forever. New failures will appear as the stack changes. It also reflects one reference deployment; your stack will have different vendors and constraints.

Still, the classes of failure travel: auth, memory, process management, stale docs, unsafe autonomy, API drift, permissions, model routing, and human adoption.

## How to start this in your business

1. Create `lessons/_ledger.md` before you have 32 lessons. Start with the first five things that already went wrong.
2. For every incident, write the one-rule lesson within 24 hours while the fix is fresh.
3. Link each ledger row to a detailed incident file only when the detail changes future behavior.
4. Review the ledger before every new automation project.
5. Fork `lessons/_ledger.md` as the artifact and use Chapter 11b as the detailed reference model.

