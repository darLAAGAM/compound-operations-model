# Production Cron Definitions

All crons that run in the reference deployment. Adapt paths and times to your setup.

## Critical (must-have)

| Cron | Schedule | Agent | What It Does |
|---|---|---|---|
| CS ticket monitor | `*/15 6-20 * * *` | CS Agent | Triage new tickets, draft responses, auto-resolve high-confidence |
| Inventory monitor | `*/30 7-21 * * *` | Merch Agent | Check stock levels, flag low inventory, recommend transfers |
| Brain sync | `*/30 * * * *` | System | Bidirectional rsync between VPS and secondary host |
| Brain sync health | `0 */2 * * *` | System | Verify sync freshness, alert if stale > 2 hours |

## Daily

| Cron | Schedule | Agent | What It Does |
|---|---|---|---|
| Knowledge Mining | `0 6 * * *` | Strategy Hub | Extract patterns from yesterday's memory logs → brain |
| Index generation | `10 6 * * *` | System | Rebuild all _index.md files in the Context Tree |
| Revenue snapshot | `30 6 * * *` | Finance Agent | Morning revenue report posted to Slack |
| Retail daily report | `0 7 * * *` | Retail Agent | Foot traffic + POS summary for both stores |
| Budget tracking | `0 * * * *` | System | Update cost tracking for the current month |

## Weekly

| Cron | Schedule | Agent | What It Does |
|---|---|---|---|
| Weekly P&L | `0 6 * * 1` | Finance Agent | Full P&L compiled and posted to Slack (Monday) |
| Pattern extraction | `0 5 * * 0` | System | Auto-extract anonymized patterns for the pattern library (Sunday) |

## Setup

```bash
# Edit crontab
crontab -e

# Example entries (adapt paths)
*/15 6-20 * * * /path/to/scripts/cs-ticket-monitor.sh >> /var/log/cs-monitor.log 2>&1
*/30 7-21 * * * /path/to/scripts/inventory-monitor.sh >> /var/log/inventory.log 2>&1
*/30 * * * * /path/to/scripts/brain-sync.sh >> /var/log/brain-sync.log 2>&1
0 6 * * * /path/to/scripts/knowledge-mining.sh >> /var/log/knowledge-mining.log 2>&1
```

## Critical Rule

Every cron script MUST start with:
```bash
#!/bin/bash
source /root/.bashrc 2>/dev/null || true
```

Cron jobs run with minimal environment — no PATH, no API tokens, no aliases. Without sourcing .bashrc, every script will fail silently.
