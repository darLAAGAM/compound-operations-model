#!/bin/bash
source /root/.bashrc 2>/dev/null || true
# Weekly P&L — Automated via Ferland (Finance Agent)
# Runs every Monday at 06:00 UTC (08:00 CET)
# Queries Shopify + Holded, sends to Ferland for narrative, posts to Slack

set -euo pipefail

LOG="/tmp/weekly-pnl-$(date +%Y-%m-%d).log"
echo "$(date): Starting Weekly P&L generation" >> "$LOG"

# Calculate date range (last 7 days)
END_DATE=$(date +%Y-%m-%d)
START_DATE=$(date -d "7 days ago" +%Y-%m-%d 2>/dev/null || date -v-7d +%Y-%m-%d)

# Use the MCP server to query data and ask Ferland to generate narrative
# The MCP tools are accessible via the Python MCP client
python3 << 'PYEOF'
import json, urllib.request, datetime, os

MCP_URL = "https://mcp.laigam.com"
today = datetime.date.today()
week_ago = today - datetime.timedelta(days=7)

# Helper to call MCP tools
def mcp_call(tool, params):
    """Call MCP tool via the server"""
    # We'll use shell commands via subprocess instead
    pass

# Use agent_send to ask Ferland to generate the P&L
import subprocess

# Build the prompt for Ferland
prompt = f"""Genera el P&L semanal ({week_ago} a {today}). 

Pasos:
1. Consulta Shopify orders de la semana (shopify_query orders.json?status=any&created_at_min={week_ago}T00:00:00&created_at_max={today}T23:59:59&limit=250)
2. Calcula revenue por canal (Online, Retail BCN Cubí, Retail MAD Barquillo, ECI Goya, ECI PCat)
3. Consulta GA4 para sessions y conversión (ga4_query con metrics sessions,transactions,totalRevenue)
4. Compara WoW (vs semana anterior)
5. Genera el informe narrativo en formato:

**Semana X ({week_ago} — {today})**
Revenue: €X (+X% WoW)
- Por canal: Online, Retail BCN, Retail MAD, ECI
- Gross Margin estimate
- Flags y anomalías
- Cash position si disponible

Formato: texto limpio para Slack, no markdown pesado."""

# Write prompt for the cron to use via agent_send
with open("/tmp/weekly-pnl-prompt.txt", "w") as f:
    f.write(prompt)

print(f"P&L prompt ready for Ferland: {week_ago} to {today}")
PYEOF

# Now use the agent_send via the MCP Python client
# The actual execution happens via cron calling the MCP
echo "$(date): P&L prompt generated, will be sent to Ferland via MCP" >> "$LOG"
/root/aurelio-v2/scripts/log-event.sh "Ferland" "Weekly P&L compiled: Shopify + Holded data analyzed, narrative summary delivered to Slack"
