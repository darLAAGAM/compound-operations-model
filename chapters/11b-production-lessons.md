# Chapter 11b: Lessons from Production — What We Learned the Hard Way

## Why This Chapter Exists

Every AI demo looks perfect. Every architecture diagram is clean. Then you deploy it, and reality hits.

This chapter is the antidote to demo-ware. These are real failures, real debugging sessions, and real solutions from running a multi-agent system in production. We share them because we wish someone had told us before we wasted days figuring them out.

---

## Lesson 1: The OAuth Token Death Spiral

**What happened:** One of our agents stopped responding. Then another. Then a third. Within minutes, 4 out of 6 agents were down.

**Root cause:** Four agents shared the same OAuth token (a reasonable-seeming cost optimization). One agent hit a rate limit, which triggered aggressive retry logic — 8 retries × 2 model fallbacks = 16 API calls in 25 seconds. This burned through the shared token's rate limit, which caused the other agents to fail, which triggered *their* retry logic, which burned more capacity. A classic cascading failure.

**The fix:**
1. **One auth token per agent.** Never share authentication across agents. Rate limits, cooldowns, and revocations should be isolated.
2. **Reduce retry aggressiveness.** Default retry configs are designed for single-user apps, not multi-agent fleets. Cap at 3 retries with exponential backoff.
3. **Use standard API keys over OAuth tokens.** OAuth tokens (`sk-ant-oat01-*`) can enter provider-wide cooldowns that persist across restarts. Standard API keys (`sk-ant-api03-*`) are more resilient.

**The deeper lesson:** When multiple agents share a token and only one fails, the token isn't the problem — look at what's different about that agent's behavior. The shared resource just amplifies the damage.

---

## Lesson 2: The Ghost in the Config

**What happened:** After fixing the token issue above, the agent still wouldn't authenticate. We swapped API keys, cleared auth profiles, set environment variables — nothing worked. The agent kept trying to use the old, exhausted token.

**Root cause:** OpenClaw caches OAuth credentials in `.claude.json` in the user's home directory. This cached `oauthAccount` takes priority over environment variables and `auth-profiles.json`. We were changing the configs, but the agent was reading a completely different file.

**The fix:** Always check `.claude.json` first when debugging auth issues. The priority order is:
1. `.claude.json` (OAuth cache) — **highest priority, often invisible**
2. `auth-profiles.json` (explicit config)
3. Environment variables (`ANTHROPIC_API_KEY`)

**Prevention:** Document the auth priority chain for your team. When onboarding a new agent, verify which auth mechanism it's actually using, not which one you think it's using.

---

## Lesson 3: LaunchDaemons vs. LaunchAgents (macOS)

**What happened:** We needed agents to run as persistent services on macOS (Mac Mini server). We used `nohup` with `sudo -u`, which seemed to work — until the first reboot, when nothing came back.

**Root cause:** `nohup` doesn't survive reboots on macOS, and `sudo -u` doesn't set the HOME directory correctly, which means the agent can't find its config files.

**The fix:**
- Use **LaunchDaemons** (system-level, in `/Library/LaunchDaemons/`) for agents that don't need a GUI session
- Use **LaunchAgents** (user-level) for agents that need browser or screen access (like a CS agent doing WhatsApp QR pairing)
- **Always set HOME explicitly** when running as a different user: `sudo -u finance_agent bash -c 'export HOME=/Users/finance_agent; openclaw start'`

**Critical gotcha:** `sudo -u <user>` does NOT set HOME. Your agent will look for configs in `/root/` instead of `/Users/<agent>/`. This causes silent failures — the process starts but can't find its SOUL.md, TOOLS.md, or knowledge base.

---

## Lesson 4: The Config Crash Loop

**What happened:** We edited an agent's config file to add a new feature. The agent immediately entered a crash loop — starting, failing, restarting, failing, restarting.

**Root cause:** A single invalid key in `openclaw.json`. Newer versions of OpenClaw had moved cron configuration to a separate system, but the old `cron` key was still in the agent config. The config validator rejected it on startup.

**The fix:** `openclaw doctor --fix` — a built-in diagnostic command that validates configuration and auto-repairs common issues.

**Prevention:**
1. **Never edit config files directly in production** without a backup
2. **Always run `openclaw doctor`** after any config change
3. **Read the gateway error log** (`gateway-error.log`) — it tells you exactly which key is invalid
4. If an agent stops responding: check process (`ps aux | grep openclaw`) → read logs → `openclaw doctor --fix`

---

## Lesson 5: The Messaging Channel Reconnection Storm

**What happened:** An agent had both Slack and Mattermost connected. Mattermost would disconnect every 30 minutes (a known "stale socket" issue). On reconnection, it replayed queued messages, each triggering API calls, which (combined with Lesson 1) created a retry storm.

**The fix:** Disable unused messaging channels. If you're not actively using Mattermost, don't leave it connected "just in case." Every connected channel is a potential source of message replay storms.

**The broader principle:** In multi-agent systems, **minimize surface area.** Every integration, every channel, every connection is something that can fail. Only connect what you actively use. You can always re-enable later.

---

## Lesson 6: API Header Formats Are Not Universal

**What happened:** Our inventory sync kept returning 401 Unauthorized from Stockagile, despite having the correct API key.

**Root cause:** Stockagile requires `Authorization: Token X` — not `Bearer X`, not `Token: X` (with colon), not `Authorization: X`. The exact format varies by API, and most documentation is ambiguous.

**The fix:** Always verify the exact header format by testing with `curl` first:
```bash
# Test each variation
curl -H "Authorization: Bearer TOKEN" https://api.example.com/test
curl -H "Authorization: Token TOKEN" https://api.example.com/test
curl -H "Authorization: TOKEN" https://api.example.com/test
```

**Related gotchas we've hit:**
- Stockagile URLs must NOT have trailing slashes (returns 404), except the base `/v2/` path
- Richpanel status filters are case-sensitive: `OPEN` works, `open` doesn't
- Holded's HR/leave endpoints are web-only — the API key that works for invoicing returns 404 on team endpoints

---

## Lesson 7: Memory Pollution Is Real

**What happened:** After 3 months, agent responses started degrading. The CS agent would reference outdated policies. The finance agent would cite last quarter's numbers as current.

**Root cause:** SuperMemory (semantic memory layer) accumulates everything. "[Name] is the CEO" gets stored 15 times with slight variations. Troubleshooting notes from months ago linger. Old API access facts crowd out current ones.

**The fix:** Automated nightly deduplication cron on every agent:
- Runs at 3:45 AM (staggered per agent to avoid resource conflicts)
- Searches for duplicate/redundant memories
- Keeps the most informative version, deletes noise
- Result: ~90+ duplicates removed per agent per week

**The principle:** Memory systems need garbage collection, just like any database. Build dedup into your deployment from day one, not after you notice degradation.

---

## Lesson 8: The Knowledge Base Is Never "Done"

**What happened:** We launched a new product collection and updated the website, Shopify, and email templates. Three days later, the CS agent was telling customers the old collection was "our latest." The merchandising agent was allocating based on last season's category structure.

**Root cause:** Nobody updated the knowledge base. The agents' "brain" still had last season's product info.

**The fix:**
- **Add knowledge base updates to your product launch checklist.** Right next to "update website" and "send email blast," add "update agent knowledge base."
- **Knowledge Mining cron** that auto-extracts new info from daily operational logs into the knowledge base
- **Quarterly knowledge audit:** review every file in the Context Tree for staleness

**The hard truth:** A knowledge base that was perfect on Day 1 is 10% wrong by Day 30 and 30% wrong by Day 90. Budget ongoing maintenance — 2-3 hours/month minimum.

---

## Lesson 9: Shadow Mode Is Non-Negotiable

**What happened:** We were excited. The CS agent's shadow mode results looked great after a week. We went live at 100% autonomy. Within 48 hours, a customer received a response with incorrect shipping timeframes for international orders — a case the shadow period hadn't surfaced.

**The fix:** Shadow mode → graduated autonomy:
1. **Week 1-2:** Shadow mode (agent drafts, human sends)
2. **Week 3:** Autonomy on simplest categories only (tracking queries, stock checks)
3. **Week 4:** Expand one category at a time, monitoring each for 48h
4. **Week 5+:** Full autonomy on proven categories, shadow mode on new ones

**The principle:** One bad automated response costs more in customer trust than a month of slower manual rollout. Build trust incrementally.

---

## Lesson 10: The 2FA Dependency Trap

**What happened:** We built a microservice that scrapes leave/absence data from our HR system (Holded) because the API doesn't expose it. The service authenticates via web session cookies. Every few weeks, the session expires and requires a new 2FA code — sent to a team member's email.

**The fix:** Accept the dependency and plan for it:
- Health endpoint that reports session validity
- Cron job that alerts when the session expires
- Documented procedure: "When you get the alert, log in, enter the 2FA code, and the service auto-recovers"

**The broader lesson:** Not every integration has a clean API. Sometimes you're scraping web UIs, parsing HTML tables, and managing browser sessions. That's fine — just build monitoring around the fragile parts so you know when they break, rather than discovering it when someone asks "why haven't I seen absence data this week?"

---


---

## Lesson 11: SuperMemory — When to Remove a Feature

**What happened:** After 6 months, we noticed agents were getting *worse* at certain tasks despite having more context. Investigation revealed SuperMemory was the culprit.

**Root cause:** Semantic memory accumulates indiscriminately. Even with nightly dedup removing 90+ entries per agent per week, noise was outpacing signal. Old troubleshooting states, duplicate facts, stale operational context — all competing for the limited recall slots injected into each prompt.

**The fix:** We removed SuperMemory entirely from all 6 agents. Replaced it with a stronger Context Tree (structured, deterministic lookup) and Knowledge Mining cron (daily distillation of session logs into the brain).

**The lesson:** More memory isn't always better. Structured, curated knowledge beats unstructured semantic recall for operational tasks. RAG-style "throw everything in a vector store" works for search engines; it doesn't work for business operations where precision matters.

---

## Lesson 12: The Dual-Host Architecture

**What happened:** Running all agents on one VPS seemed efficient — until we hit memory limits. Six agents × 1GB each + the gateway + the MCP server + cron jobs = constant memory pressure on a single €40/month server.

**The fix:** Split the fleet across two hosts:
- **Cloud VPS (EU):** Strategy Agent (hub/strategy) + MCP server + cron jobs + brain source of truth
- **Mac Mini (secondary host):** 5 domain agents (CS Agent, Finance Agent, Retail Agent, Marketing Agent, Merchandising Agent)

Connected via Tailscale mesh (encrypted, zero-config). Brain syncs bidirectionally every 30 minutes.

**Why Mac Mini?** Apple Silicon is incredibly cost-effective for always-on compute. M-series chips idle at <10W. The Mac Mini was a one-time €800 purchase — no monthly hosting fee. 228GB disk, 16GB RAM, more than enough for 5 agents.

**The gotcha:** macOS service management (LaunchDaemons) is non-obvious. Always set HOME explicitly. Use LaunchDaemons (system-level) for headless agents, LaunchAgents (user-level) for anything needing GUI/browser access.

---

## Lesson 13: The Cloudflare Tunnel for MCP

**What happened:** We initially used Tailscale Funnel to expose the MCP server. It worked but required Tailscale on every client machine, which was a barrier for team rollout.

**The fix:** Switched to a Cloudflare Tunnel. Free. Custom domain (`mcp.yourdomain.com`). HTTPS by default. No client-side software needed.

```bash
cloudflared tunnel create your-brand-mcp
cloudflared tunnel route dns your-brand-mcp mcp.yourdomain.com
# config.yml points to localhost:<mcp-port>
systemctl enable --now cloudflared-mcp
```

**Result:** Any team member with Claude Desktop can connect to the MCP server by adding one line to their config. No VPN, no Tailscale, no SSH keys.

---

## Lesson 14: Environment Variables in Cron Jobs

**What happened:** We wrote beautiful automation scripts. They worked perfectly when run manually. They failed silently in cron.

**Root cause:** Cron jobs run with a minimal environment — no `.bashrc`, no `PATH`, no API tokens. Every script needs to explicitly source its environment.

**The fix:** Every script starts with:
```bash
#!/bin/bash
source /root/.bashrc 2>/dev/null || true
```

**And for Python scripts inside shell scripts:** Don't rely on `os.environ` — read credentials from `.bashrc` as a fallback.

---

## Lesson 15: Skills as Institutional Knowledge

**What happened:** We built 152+ skills (marketing, SEO, CRO, analytics, etc.) but they were siloed in individual agent workspaces.

**The fix:** Made all skills accessible via the MCP server with three tools:
- `skills_list` — Browse by category
- `skill_search` — Keyword search across all skills
- `skill_read` — Read full methodology

Now every Claude Desktop user and every agent can access the complete skills library. A marketing question asked to the finance agent? It can look up the relevant marketing skill and apply the methodology.

**The broader principle:** Skills are reusable operational knowledge — step-by-step procedures, evaluation frameworks, best practices. They're the "how to" complement to the brain's "what we know." Make them accessible to everyone, not locked to one agent.


---

## Lesson 16: ByteRover Plugin Deployment — Config Compatibility

**What happened:** We installed ByteRover via npm and added it to every agent's `openclaw.json`. Four agents immediately failed to start.

**Root cause:** Two issues collided:
1. We added a `"source": "npm:@byterover/byterover"` field to the plugin config. OpenClaw's config validator rejected the unrecognized `"source"` key.
2. For agents without existing `openclaw.json` files (finance_agent, retail_agent, marketing_agent, merchandising_agent), we created minimal configs with only the plugin entry — missing the full gateway configuration (auth, channels, agents list, bindings).

**The fix:**
1. Remove unrecognized fields: only `"enabled"` and `"config"` are valid plugin entry keys. No `"source"`.
2. Never create a new `openclaw.json` with only plugin config — always start from the agent's existing config and add the plugin entry to it.
3. Run `openclaw doctor --fix` after any config change.
4. Keep config backups: the `agents-config` repo at `/root/agents-config/agents/` saved us.

**The principle:** Plugin installation should be additive — add to existing config, never replace it. And always validate with `openclaw doctor` before restarting.


---

## Lesson 17: When the API Doesn't Exist — Build a Microservice

**What happened:** HR Agent (HR agent) needed leave/absence data from Holded (our payroll system). Holded's API covers invoicing, contacts, and products — but NOT time-off or leave balances. No endpoint. No webhooks. Nothing.

**The hacky-but-working solution:** We built a microservice that:
1. Maintains an authenticated web session with Holded (via stored cookies)
2. Scrapes the time-off pages with headless Chrome
3. Exposes clean REST endpoints: `/api/holded/leaves`, `/leaves/today`, `/leaves/week`
4. Runs as a systemd service on a dedicated port
5. The MCP server wraps it as `holded_leaves(period)` — invisible to end users

**The gotcha:** Web session cookies expire periodically. A monitoring cron alerts when the session dies — someone (human) needs to re-authenticate via the Holded web UI.

**The lesson:** Not every integration has a clean API path. Sometimes the right answer is a 200-line scraper running as a microservice. The key is making the ugly hack invisible to the rest of the system — consumers call `holded_leaves("today")` and get clean JSON, never knowing about the cookie monster underneath.

**Cost:** €0/month. Runs on the same VPS. 200 lines of Python.



---

## Lesson 18: ACPX Permission Mode — approve-all vs. approve-reads

**What happened:** The marketing agent entered a crash loop after a config update. It would start, process one message, then hang indefinitely.

**Root cause:** The `acpx` (Agent Communication Protocol eXtended) permission mode was set to `approve-reads` instead of `approve-all`. In `approve-reads` mode, every incoming ACP read request requires interactive confirmation — which doesn't exist in headless agent mode. The agent blocked on a confirmation prompt that would never arrive.

**The fix:** Set `acpx.permissionMode: "approve-all"` for all headless agents. Reserve `approve-reads` only for interactive sessions where a human is present to approve requests.

**The principle:** When agents run headless (which is 99% of the time), every interactive prompt is a hang. Audit your config for anything that assumes a human is watching.

---

## Lesson 19: Never chmod 777 on OpenClaw Plugin Paths

**What happened:** During a rushed ByteRover deployment, someone ran `chmod -R 777` on the plugin directory to fix a permission error. The agent immediately refused to start.

**Root cause:** OpenClaw's security layer blocks world-writable paths for plugins. This is intentional — a world-writable plugin directory means any process on the system could inject code into the agent's runtime. The security scan (`openclaw security-scan`) flags this as a critical vulnerability and the gateway refuses to load plugins from insecure paths.

**The fix:**
1. Reset permissions: `chmod -R 755` for directories, `chmod 644` for files
2. Ensure the plugin directory is owned by the agent's user: `chown -R <agent>:<agent> ~/.openclaw/plugins/`
3. Run `openclaw security-scan` to verify no remaining issues

**The principle:** When you hit permission errors, fix ownership (`chown`), not permissions (`chmod`). World-writable anything in a production agent is a security hole the runtime correctly refuses to tolerate.

---

## Lesson 20: Port Forwarding Pattern for Loopback-Bound Gateways

**What happened:** After hardening security, we bound all OpenClaw gateways to `127.0.0.1` (loopback only). This is best practice — no external access to the gateway port. But it broke the MCP server and monitoring tools running on the VPS, which needed to reach agents on the Mac Mini.

**Root cause:** Loopback binding means the gateway only accepts connections from the same machine. Remote clients (even on the Tailscale mesh) get "connection refused."

**The fix:** An asyncio TCP proxy running as a LaunchDaemon on the Mac Mini. For each agent:

```
[Remote client] → [Tailscale IP:port] → [asyncio proxy] → [127.0.0.1:gateway_port]
```

Each agent now has **3 LaunchDaemons:**
1. **Gateway** — the OpenClaw agent itself (`com.<agent>.openclaw-gateway.plist`)
2. **Watchdog** — monitors gateway health, auto-restarts on failure (`com.<agent>.openclaw-watchdog.plist`)
3. **Port forwarder** — asyncio TCP proxy from Tailscale IP to loopback (`com.<agent>.port-forward.plist`)

**The principle:** Loopback binding + port forwarding gives you the security of restricted binding with the accessibility of network binding. The proxy is 30 lines of Python. The LaunchDaemon ensures it survives reboots.

---

## Lesson 21: Cheap Models Look Great Until They Break Under Load

**What happened:** LLM costs were climbing toward €600/month as agents scaled. We needed a way to reduce costs without sacrificing quality on critical paths.

**The experiment:** We tested free-tier and low-cost models aggressively for reporting, data extraction, inventory checks, retail metrics, and merchandising workflows. On quiet days they looked good enough. Under real operational peaks they degraded, rate-limited, or became unreliable in ways that were unacceptable for production.

**What we learned:** The right question was not "what is the cheapest model?" but "what is the cheapest reliable routing strategy?" The answer turned out to be:
- **GPT-5.4 via ChatGPT OAuth** wherever the team already had subscriptions and the work was internal
- **Claude Sonnet** for customer-facing and sensitive workflows like CS and HR
- **Opus fallback** only for edge cases that genuinely need it

**Result:** Costs still dropped to ~€93/month on the API layer, but the durable saving came from routing five agents through existing team subscriptions instead of pretending free-tier models were a stable production default.

**The principle:** Cheap is not the goal. Reliable is the goal. If a low-cost model creates operational fragility, it is expensive.

---

## Lesson 32: Node Version Compatibility — When the Runtime Breaks Your Tools

**What happened:** After updating the Mac Mini to Node 25.6.1, the `summarize` CLI tool (used by all agents for transcript processing) started throwing EPIPE errors on every invocation. The tool worked fine on Node 22.

**Root cause:** Node 25 changed how pipe buffering works for child processes. The summarize CLI's streaming output pattern, which relied on specific pipe behavior, became incompatible.

**The fix:** Install Node 22 LTS alongside Node 25 and create a wrapper script that forces Node 22 for the summarize command:

```bash
#!/bin/bash
# /usr/local/bin/summarize-wrapper
NODE22=$(ls -d ~/.local/share/fnm/node-versions/v22*/installation/bin/node | head -1)
exec "$NODE22" "$(which summarize)" "$@"
```

**The rule:** when a CLI tool breaks after a Node upgrade, don't immediately debug the tool. Test with the previous Node version first. If it works there, the fix is a version-pinned wrapper — takes 2 minutes instead of 2 hours of debugging pipe internals.

## The Meta-Lesson

Every one of these lessons follows the same pattern:

1. **Something worked in testing but failed in production**
2. **The failure mode was non-obvious** (shared tokens cascading, cached configs overriding, silent HOME mismatches)
3. **The fix was simple once understood** but took hours/days to diagnose
4. **Documentation prevented recurrence**

The value of this chapter isn't the specific fixes — your stack will have different failures. The value is the mindset: **assume every integration will fail in a way you didn't predict, build monitoring to detect it quickly, and document every fix so you only solve each problem once.**

---

*Next: [Chapter 12 — ROI: Real Numbers, Real Results →](12-roi.md)*

---

## Lesson 32: Node Version Compatibility — When the Runtime Breaks Your Tools

**What happened:** After updating the Mac Mini to Node 25.6.1, the summarize CLI tool (used by all agents for transcript processing) started throwing EPIPE errors on every invocation. The tool worked fine on Node 22.

**Root cause:** Node 25 changed how pipe buffering works for child processes. The summarize CLI streaming output pattern became incompatible.

**The fix:** Install Node 22 LTS alongside Node 25 and create a wrapper script that forces Node 22 for the summarize command. Takes 2 minutes instead of 2 hours debugging pipe internals.

**The rule:** when a CLI tool breaks after a Node/Python/runtime upgrade, test with the previous version first. If it works there, use a version-pinned wrapper.

