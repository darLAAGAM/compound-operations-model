#!/bin/bash
# deploy-dedup-fleet.sh — Deploy SuperMemory Dedup cron to all agents
# Part of AgentivAI Memory Architecture Kit
#
# Usage: ./deploy-dedup-fleet.sh
# Prerequisites:
#   - SSH access to agent host
#   - Agent gateway ports and tokens known
#   - OPENCLAW_ALLOW_INSECURE_PRIVATE_WS=1 for private networks

set -euo pipefail

# Configuration — edit these for your setup
HOST_IP="100.127.229.52"        # Tailnet IP of agent host
SSH_USER="mafalda"               # SSH user with sudo access
CRON_EXPR="45 3 * * *"          # 03:45 UTC daily
DEDUP_MESSAGE="Execute automated SuperMemory cleanup: Search for duplicate memories with high overlap. Focus on: multiple versions of same facts about people/roles/tools, temporal noise like troubleshooting states, redundant access permission statements. Delete duplicates keeping most informative version. Report stats briefly. Run quietly."

# Agent definitions: name:port:token
AGENTS=(
  "mafalda:18789:mafalda-ops-2026"
  "gala:18790:gala-ops-2026"
  "ferland:18794:ferland-ops-2026"
  "donatello:18795:donatello-ops-2026"
  "olivia:18796:olivia-ops-2026"
)

echo "🧠 AgentivAI SuperMemory Dedup Fleet Deployment"
echo "================================================"
echo "Host: $HOST_IP | Schedule: $CRON_EXPR"
echo ""

for agent_def in "${AGENTS[@]}"; do
  IFS=: read -r AGENT PORT TOKEN <<< "$agent_def"
  echo "→ Deploying to $AGENT (port $PORT)..."
  
  RESULT=$(ssh "$SSH_USER@$HOST_IP" "sudo -u $AGENT bash -l -c '
    cd /Users/$AGENT && HOME=/Users/$AGENT \
    OPENCLAW_ALLOW_INSECURE_PRIVATE_WS=1 \
    OPENCLAW_GATEWAY_URL=ws://$HOST_IP:$PORT \
    /opt/homebrew/bin/openclaw cron add \
      --name \"SuperMemory Dedup\" \
      --cron \"$CRON_EXPR\" \
      --session isolated \
      --message \"$DEDUP_MESSAGE\" \
      --no-deliver \
      --json \
      --token $TOKEN \
      2>&1
  '")
  
  JOB_ID=$(echo "$RESULT" | python3 -c "import json,sys; print(json.load(sys.stdin)['id'])" 2>/dev/null || echo "FAILED")
  
  if [ "$JOB_ID" != "FAILED" ]; then
    echo "  ✅ $AGENT → Job $JOB_ID"
  else
    echo "  ❌ $AGENT → Failed"
    echo "     $RESULT" | head -3
  fi
done

echo ""
echo "🦞 Fleet deployment complete."
echo "First run: $(date -u -d "tomorrow 03:45" '+%Y-%m-%d %H:%M UTC' 2>/dev/null || echo '~03:45 UTC tonight/tomorrow')"
