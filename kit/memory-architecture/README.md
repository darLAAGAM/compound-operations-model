# Memory Architecture Kit — AgentivAI

## What's Included

| Asset | Description |
|-------|-------------|
| `context-tree-scaffold.sh` | Creates the full domain hierarchy for your brand |
| `generate-indexes.sh` | Auto-generates `_index.md` files for every directory |
| `memory-md-template.md` | MEMORY.md template — executive context injected every prompt |
| `knowledge-mining-cron.md` | Setup guide for daily automated knowledge distillation |
| `shared-brain-setup.md` | Multi-agent knowledge sync via symlinks + rsync |
| `deploy-dedup-fleet.sh` | Deploy nightly SuperMemory dedup cron to all agents |
| `fix-device-pairing.py` | Fix broken device pairing (Ed25519 key format gotcha) |

## Quick Start

```bash
# 1. Create Context Tree
chmod +x context-tree-scaffold.sh
./context-tree-scaffold.sh my-brand

# 2. Populate template files with your real data
# Edit: brain/knowledge/my-brand/operations/products.md
# Edit: brain/knowledge/my-brand/operations/policies.md
# Edit: brain/knowledge/my-brand/team/org-chart.md
# Edit: brain/knowledge/my-brand/marketing/brand-voice.md

# 3. Generate _index.md files
chmod +x generate-indexes.sh
./generate-indexes.sh

# 4. Copy MEMORY.md template and fill in
cp memory-md-template.md ../../MEMORY.md

# 5. Install SuperMemory
openclaw extensions install openclaw-supermemory
openclaw restart

# 6. Set up Knowledge Mining cron (see knowledge-mining-cron.md)

# 7. If multi-agent: set up shared brain (see shared-brain-setup.md)

# 8. Deploy nightly memory dedup to all agents
chmod +x deploy-dedup-fleet.sh
# Edit agent ports/tokens in the script, then:
./deploy-dedup-fleet.sh

# 9. If device pairing is broken:
sudo python3 fix-device-pairing.py /Users/<agent>/.openclaw
# Then restart the agent gateway
```

## The Three-Layer Stack

```
Layer 3: Working Memory    → memory/YYYY-MM-DD.md (auto, daily)
Layer 2: Semantic Memory   → SuperMemory (auto, per session)
Layer 1: Institutional     → brain/knowledge/ Context Tree (curated + mined)
```

```
Layer 4: Memory Hygiene   → Nightly dedup cron (auto, per agent)
```

**Cost:** ~€3/month (Knowledge Mining + dedup API tokens). Everything else is free.

## Full Documentation

See [Chapter 10b: Memory Architecture](../../playbook/10b-memory-architecture.md) in the AgentivAI Playbook.
