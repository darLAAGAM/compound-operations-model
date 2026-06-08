# Chapter 11c: Setting Up Agents in OpenClaw — The Step-by-Step Guide

> **Appendix · Technical depth.** This chapter is for operators or engineers deploying the brain themselves. It covers implementation details that aren't needed for understanding the conceptual architecture. Skip if you're reading for strategy.

## What This Chapter Covers

This is the practical "how to actually do it" chapter. The architecture is in Ch.3. The agent roles are in Ch.4-9. The production lessons are in Ch.11b. This chapter is the step-by-step setup — from a blank server to a running agent that responds to messages.

---

## Prerequisites

Before you start:

- A VPS or server (Hetzner recommended, €15/month, EU region)
- Node.js installed (v22 LTS recommended — see Lesson 32 on Node version compatibility)
- A Slack workspace (or WhatsApp Business, or email — wherever your team lives)
- An LLM API key (Anthropic, OpenAI, or existing ChatGPT subscription for OAuth)
- ~2 hours for the first agent, ~30 minutes for each subsequent one

---

## Step 1: Install OpenClaw

```bash
# Install globally
npm install -g openclaw@beta

# Verify
openclaw --version
```

**If you're on macOS and using Homebrew:**
```bash
# npm might need explicit path
sudo /opt/homebrew/bin/npm install -g openclaw@beta --no-fund --no-audit
```

---

## Step 2: Create Your First Agent (Strategy Hub)

### 2.1 Initialize the workspace

```bash
# Create a workspace directory
mkdir -p ~/my-brand-hub
cd ~/my-brand-hub

# Initialize OpenClaw
openclaw init
```

This creates the basic directory structure and a default `openclaw.json`.

### 2.2 Configure the gateway

Edit `~/.openclaw/openclaw.json`:

```json
{
  "gateway": {
    "bind": "loopback",
    "port": 18789
  },
  "permissionMode": "approve-all",
  "nonInteractivePermissions": "deny",
  "agents": {
    "defaults": {
      "model": {
        "primary": "anthropic/claude-sonnet-4",
        "fallbacks": [
          "anthropic/claude-opus-4-6"
        ]
      }
    }
  },
  "heartbeat": {
    "every": "30m",
    "activeHours": {
      "start": "08:00",
      "end": "23:00",
      "timezone": "Europe/Madrid"
    }
  },
  "plugins": {
    "entries": {
      "@byterover/byterover": {
        "enabled": true,
        "config": {
          "ownsCompaction": false,
          "contextTree": {
            "basePath": "brain/knowledge",
            "enabled": true
          }
        }
      }
    }
  }
}
```

**Critical config notes:**
- `gateway.bind: "loopback"` — never expose gateway to the network directly (see Lesson 20)
- `permissionMode: "approve-all"` — headless agents cannot prompt for approval (see Lesson 18)
- `heartbeat.every: "30m"` — agent checks in every 30 minutes during active hours
- `plugins.entries` — only `enabled` and `config` are valid keys. Never add `source` (see Lesson 16)

### 2.3 Write the SOUL.md

Create `~/my-brand-hub/SOUL.md` using the template from the repo (`templates/souls/strategy-hub.md`). At minimum:

```markdown
# SOUL.md — Strategy Hub

## Identity
I am the Strategy Hub for [YOUR BRAND].

## Personality
- Concise. Direct. Executor.

## What I Do
- Morning briefings
- Cross-domain coordination
- Knowledge mining

## What I Don't Do
- Direct customer communication
- Motivational speeches or disclaimers

## Confidence Scoring
| Confidence | Action |
|---|---|
| > 95% | Act autonomously |
| 80-95% | Act + flag [REVIEW] |
| 60-80% | Draft for approval |
| < 60% | Escalate with context |

## Security
[Copy anti-injection template from repo]
```

### 2.4 Create the knowledge base

```bash
mkdir -p brain/knowledge/{your-brand/{finance,operations,team,marketing,strategy},platform/{agents,config}}
```

Populate the essentials on Day 1:
- `your-brand/operations/products.md` — product catalog
- `your-brand/operations/policies.md` — return/shipping/warranty policies
- `your-brand/team/org-chart.md` — who does what

### 2.5 Start the gateway

```bash
# First time — interactive, to verify it works
openclaw gateway run

# You should see:
# Gateway started on 127.0.0.1:18789
# Model: anthropic/claude-sonnet-4
```

### 2.6 Connect a messaging channel

Add Slack to `openclaw.json`:

```json
{
  "channels": {
    "slack": {
      "enabled": true,
      "botToken": "SLACK_BOT_TOKEN_PLACEHOLDER",
      "appToken": "xapp-your-app-token"
    }
  }
}
```

Restart the gateway. Send a message in Slack. The agent should respond.

### 2.7 Validate

```bash
# Check health
curl http://127.0.0.1:18789/health
# Should return: {"ok":true,"status":"live"}

# Check config
openclaw doctor --fix
# Should report no issues
```

---

## Step 3: Make It Persistent

### On Linux (VPS)

**Use cron @reboot. Never systemd Type=simple** (see Lesson 25 — OpenClaw forks a child process and exits, which causes systemd restart loops).

```bash
# Add to crontab
crontab -e
# Add:
@reboot cd /root/my-brand-hub && nohup openclaw gateway run --force >> /var/log/openclaw-hub.log 2>&1 &
```

### On macOS (Mac Mini)

Create a LaunchDaemon at `/Library/LaunchDaemons/ai.openclaw.hub.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>ai.openclaw.hub</string>
    <key>ProgramArguments</key>
    <array>
        <string>/opt/homebrew/bin/openclaw</string>
        <string>gateway</string>
        <string>run</string>
        <string>--force</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/Users/hub-agent/hub</string>
    <key>UserName</key>
    <string>hub-agent</string>
    <key>GroupName</key>
    <string>staff</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>EnvironmentVariables</key>
    <dict>
        <key>HOME</key>
        <string>/Users/hub-agent</string>
        <key>PATH</key>
        <string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin</string>
    </dict>
    <key>StandardOutPath</key>
    <string>/Users/hub-agent/hub/openclaw.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/hub-agent/hub/openclaw-error.log</string>
</dict>
</plist>
```

Load it:
```bash
sudo launchctl load /Library/LaunchDaemons/ai.openclaw.hub.plist
```

**Always set HOME explicitly.** `sudo -u <user>` does NOT set HOME on macOS — the agent will look for configs in `/root/` instead of `/Users/<agent>/` (see Lesson 3).

---

## Step 4: Add Domain Agents

For each domain agent (CS, Finance, Marketing, etc.):

### 4.1 Create a separate OS user (Mac Mini)

```bash
AGENT_NAME="cs-agent"
AGENT_UID=501  # Use next available
sudo sysadminctl -addUser $AGENT_NAME -UID $AGENT_UID -home /Users/$AGENT_NAME -shell /bin/zsh
sudo mkdir -p /Users/$AGENT_NAME/$AGENT_NAME
sudo chown -R $AGENT_NAME:staff /Users/$AGENT_NAME
```

### 4.2 Copy and customize config

```bash
# Copy config from the hub (as starting point)
sudo mkdir -p /Users/$AGENT_NAME/.openclaw
sudo cp ~/.openclaw/openclaw.json /Users/$AGENT_NAME/.openclaw/openclaw.json
# Edit: change port, model, channel
sudo chown -R $AGENT_NAME:staff /Users/$AGENT_NAME/.openclaw
```

**Each agent needs a unique port.** Suggested allocation:
- Hub: 18789
- CS: 18791
- Finance: 18794
- Retail: 18790
- Marketing: 18795
- Merch: 18799
- HR: 18797

### 4.3 Write its SOUL.md

Use the appropriate template from `templates/souls/` in the repo. Each agent's soul defines its personality, tools, confidence thresholds, and escalation chain.

### 4.4 Create 3 LaunchDaemons per agent

Every agent on the Mac Mini needs three persistent services:

1. **Gateway** — the OpenClaw agent itself
2. **Watchdog** — monitors health, auto-restarts on failure (every 5 minutes)
3. **Port forwarder** — TCP proxy from Tailscale IP to loopback (if using multi-host setup)

Templates for all three are in `templates/launch-daemons/` in the repo.

### 4.5 Link to shared brain

```bash
# Create shared brain directory
sudo mkdir -p /Users/Shared/shared-brain/knowledge
# Symlink from each agent's workspace
sudo ln -s /Users/Shared/shared-brain /Users/$AGENT_NAME/$AGENT_NAME/brain
```

---

## Step 5: LLM Model Strategy

### Option A: API keys (simplest)

Set `ANTHROPIC_API_KEY` as environment variable. Each agent uses its own allocation.

### Option B: ChatGPT OAuth (cheapest)

If team members already have ChatGPT Plus/Pro subscriptions, agents can piggyback via OAuth at zero incremental cost (see Lesson 29):

1. Team member logs into ChatGPT on the agent's machine
2. OAuth tokens stored in `~/.codex/auth.json` with auto-refresh
3. Agent config uses `openai-codex/gpt-5.4` as model string
4. Each subscription can comfortably run 1-2 agents

### Option C: Mixed (recommended)

- **Customer-facing agents** (CS, HR): Anthropic API key for tone quality and audit trail
- **Internal agents** (Finance, Retail, Marketing, Merch): ChatGPT OAuth for zero cost
- **Hub agent**: best model available (GPT-5.4 or Opus) for orchestration reasoning
- **All agents**: Opus as fallback for edge cases

---

## Step 6: Health Monitoring

### Install openclaw-ops toolrepo

The repo includes three monitoring scripts:

```bash
# Copy to a shared location
cp scripts/monitoring/heal.sh /usr/local/bin/
cp scripts/monitoring/watchdog.sh /usr/local/bin/
cp scripts/monitoring/security-scan.sh /usr/local/bin/
chmod +x /usr/local/bin/{heal,watchdog,security-scan}.sh
```

### Set up watchdog cron

```bash
# Check all agents every 5 minutes
*/5 * * * * /usr/local/bin/watchdog.sh >> /var/log/watchdog.log 2>&1
```

### Run security scan after any config change

```bash
security-scan.sh
# Target: VPS 100/100, Mac Mini 85/100 (DM channels open is deliberate)
```

---

## Step 7: Validate Everything

Run through this checklist before declaring an agent "in production":

- [ ] `openclaw doctor --fix` returns clean
- [ ] `curl http://127.0.0.1:<port>/health` returns `{"ok":true}`
- [ ] Agent responds to a test message in its channel
- [ ] SOUL.md is customized (not the default template)
- [ ] Anti-injection section is present in SOUL.md
- [ ] Confidence scoring section is present
- [ ] Heartbeat is configured and running
- [ ] LaunchDaemon (macOS) or cron @reboot (Linux) survives a reboot test
- [ ] Brain symlink is working (`brain_search` returns results)
- [ ] Watchdog is monitoring this agent
- [ ] Security scan passes

---

## Common First-Day Failures

| Symptom | Cause | Fix |
|---|---|---|
| Gateway won't start | Invalid key in openclaw.json | `openclaw doctor --fix` |
| Agent responds but with wrong model | Stale session override in sessions.json | Delete sessions.json, restart |
| Agent hangs on every tool call | `permissionMode: "approve-reads"` in headless mode | Change to `approve-all` |
| `npm: command not found` with sudo | sudo doesn't inherit PATH on macOS | `sudo /opt/homebrew/bin/npm...` |
| Agent can't find SOUL.md | HOME not set correctly | Explicit HOME in LaunchDaemon env vars |
| Brain search returns nothing | Symlink points to wrong directory | Verify `ls -la brain/` shows correct target |
| Health endpoint returns 401 | Auth mode is token-based | Pass `Authorization: Bearer <token>` header |
| Port already in use | Another agent on same port | Check ports with `lsof -i :<port>`, assign unique port |

---

*Next: [Chapter 12 — ROI: The Honest Math →](12-roi.md)*
