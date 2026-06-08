# Knowledge Mining Cron — Setup Guide

## What It Does

Every day, this cron job reads your latest session log (`memory/YYYY-MM-DD.md`), extracts durable operational knowledge, and routes it to the correct domain folder in your Context Tree. Your knowledge base grows organically from real operations.

## Setup

### 1. Create the Cron Job

In your OpenClaw gateway config or via the cron tool:

```yaml
# Example cron job configuration
name: "Knowledge Mining — Daily Digest"
schedule:
  kind: cron
  expr: "0 7 * * *"           # 7:00 AM daily
  tz: "Europe/Madrid"         # Your timezone
sessionTarget: isolated
payload:
  kind: agentTurn
  message: |
    Knowledge Mining task. Read the most recent file in memory/ directory.
    
    Extract ONLY durable knowledge — things that will still be true next month:
    - New API endpoints or integrations discovered
    - Policy changes or process updates
    - Key business decisions
    - New team members or role changes
    - Lessons learned from failures
    - New operational patterns
    
    DO NOT extract:
    - One-time events or conversations
    - Debugging sessions (unless the fix is reusable)
    - Personal messages or ephemeral context
    
    For each extracted item:
    1. Determine the correct domain folder (e.g., <brand>/operations/, platform/config/)
    2. Either update an existing file or create a new one
    3. Regenerate the _index.md for any modified directory
    
    Report what you mined and where you stored it.
delivery:
  mode: announce
```

### 2. Multi-Agent Sync (Optional)

If you have multiple agents on separate machines, add a sync step after mining:

```bash
# Add to the cron job or run as a separate cron
rsync -avz --delete \
  /path/to/source/brain/knowledge/ \
  user@remote:/path/to/shared/brain/knowledge/
```

### 3. Verify It Works

After the first run, check:
- Were the extracted items accurate and durable?
- Did they land in the right domain folders?
- Were `_index.md` files updated?
- Did other agents pick up the changes?

## Tuning Tips

- **Too noisy?** Tighten the extraction prompt — add "ONLY extract if it changes existing knowledge or adds a new permanent fact"
- **Too quiet?** Loosen the prompt — add "Include notable patterns even if they might be temporary"
- **Wrong domain routing?** Add explicit routing rules: "Anything about returns → `brand/operations/`"
- **Duplicate entries?** Add "Before creating a new file, check if the information already exists in the target domain"

## Cost

~€0.10/day in API tokens (reads one file, writes a few small updates). €3/month for a self-improving knowledge base.
