# Shared Brain Setup — Multi-Agent Knowledge Sync

## Architecture

```
Hub Agent (Server A)                    Other Agents (Server B)
┌─────────────────────┐                ┌──────────────────────┐
│ brain/knowledge/    │  rsync --del   │ /shared/brain/       │
│   (source of truth) │ ──────────────►│   knowledge/         │
│                     │                │                      │
│ Knowledge Mining    │                │ Agent 1: brain/ →    │
│ runs here           │                │   /shared/brain/     │
└─────────────────────┘                │ Agent 2: brain/ →    │
                                       │   /shared/brain/     │
                                       │ Agent 3: brain/ →    │
                                       │   /shared/brain/     │
                                       └──────────────────────┘
```

## Setup Steps

### 1. Choose Your Source of Truth

Your hub agent's `brain/knowledge/` is the canonical source. All changes go here first.

### 2. Create Shared Directory (on agent server)

```bash
# On the machine running your other agents
sudo mkdir -p /Users/Shared/brand-brain/knowledge
sudo chown -R root:staff /Users/Shared/brand-brain
sudo chmod -R 755 /Users/Shared/brand-brain
```

### 3. Initial Sync

```bash
# From hub server
rsync -avz --delete \
  /path/to/hub/brain/knowledge/ \
  user@agent-server:/Users/Shared/brand-brain/knowledge/
```

### 4. Create Symlinks for Each Agent

```bash
# On agent server, for each agent
ln -s /Users/Shared/brand-brain /Users/agent-name/workspace/brain
```

Verify:
```bash
ls /Users/agent-name/workspace/brain/knowledge/
# Should show the Context Tree
```

### 5. Automate Sync

Add to your Knowledge Mining cron or create a separate sync job:

```bash
# Runs after knowledge mining completes
# Option A: SSH + rsync
rsync -avz --delete \
  /hub/brain/knowledge/ \
  user@agent-server:/Users/Shared/brand-brain/knowledge/

# Option B: If on same machine, just use the symlink (no sync needed)
```

## Single-Machine Setup

If all agents run on the same machine, skip rsync entirely:

```bash
# All agents point to the same directory
mkdir -p /shared/brain/knowledge
# For each agent workspace:
ln -s /shared/brain /path/to/agent/workspace/brain
```

Changes by any agent are instantly visible to all others.

## Permissions

- Shared brain directory: `755` (readable by all agents)
- Individual agents should only WRITE to their own domain areas
- Hub agent has write access to everything
- Use filesystem permissions to enforce if needed

## Troubleshooting

**Symlink not working?**
- Check: `readlink /path/to/agent/workspace/brain` — should show the shared path
- Verify the target exists: `ls /Users/Shared/brand-brain/knowledge/`

**Files not syncing?**
- Test rsync manually first: `rsync -avz --dry-run source/ dest/`
- Check SSH key access: `ssh user@server "echo ok"`
- Verify `--delete` flag is included (removes stale files)

**Agent can't read knowledge?**
- Check directory permissions: `ls -la /Users/Shared/brand-brain/`
- Agent user needs read access to the shared directory
