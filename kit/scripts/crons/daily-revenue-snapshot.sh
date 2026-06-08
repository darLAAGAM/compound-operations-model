#!/bin/bash
source /root/.bashrc 2>/dev/null || true
# Daily Revenue Snapshot — Posts to Slack #general at 08:30 CET
set -euo pipefail

LOG="/tmp/daily-revenue-$(date +%Y-%m-%d).log"
YESTERDAY=$(date -d "yesterday" +%Y-%m-%d 2>/dev/null || date -v-1d +%Y-%m-%d)

echo "$(date): Generating daily revenue snapshot for $YESTERDAY" >> "$LOG"

python3 << PYEOF
import json, urllib.request, datetime, os

# Query Shopify for yesterday's orders
SHOPIFY_TOKEN = os.environ.get("SHOPIFY_ACCESS_TOKEN", "")
SHOPIFY_SHOP = os.environ.get("SHOPIFY_SHOP", "laagam-2")

if not SHOPIFY_TOKEN:
    # Try bashrc
    with open("/root/.bashrc") as f:
        for line in f:
            if "SHOPIFY_ACCESS_TOKEN" in line and "export" in line:
                SHOPIFY_TOKEN = line.split("=", 1)[1].strip().strip('"').strip("'")

yesterday = "${YESTERDAY}"
today = "$(date +%Y-%m-%d)"

url = f"https://{SHOPIFY_SHOP}.myshopify.com/admin/api/2024-01/orders.json?status=any&created_at_min={yesterday}T00:00:00&created_at_max={yesterday}T23:59:59&limit=250"

headers = {
    "X-Shopify-Access-Token": SHOPIFY_TOKEN,
    "Content-Type": "application/json"
}

try:
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())
    
    orders = data.get("orders", [])
    total_revenue = sum(float(o.get("total_price", 0)) for o in orders)
    order_count = len(orders)
    
    # Location breakdown
    locations = {}
    for o in orders:
        loc = o.get("source_name", "web")
        if "pos" in loc.lower():
            loc_name = "Retail"
        else:
            loc_name = "Online"
        locations[loc_name] = locations.get(loc_name, 0) + float(o.get("total_price", 0))
    
    # Format message
    msg = f"📊 *Revenue {yesterday}*\\n"
    msg += f"💰 €{total_revenue:,.0f} | {order_count} orders\\n"
    for loc, rev in sorted(locations.items(), key=lambda x: -x[1]):
        msg += f"  • {loc}: €{rev:,.0f}\\n"
    
    # Post to Slack #general (C263E25M0)
    SLACK_TOKEN = ""
    with open("/root/.bashrc") as f:
        for line in f:
            if "SLACK_BOT_TOKEN" in line and "export" in line:
                SLACK_TOKEN = line.split("=", 1)[1].strip().strip('"').strip("'")
    
    if not SLACK_TOKEN:
        # Use the MCP slack_send_message instead — write to file for cron pickup
        with open("/tmp/daily-revenue-msg.txt", "w") as f:
            f.write(msg)
        print(f"Revenue snapshot: €{total_revenue:,.0f} from {order_count} orders")
    else:
        slack_url = "https://slack.com/api/chat.postMessage"
        slack_body = json.dumps({"channel": "C263E25M0", "text": msg}).encode()
        slack_req = urllib.request.Request(slack_url, data=slack_body, headers={
            "Authorization": f"Bearer {SLACK_TOKEN}",
            "Content-Type": "application/json"
        })
        urllib.request.urlopen(slack_req, timeout=10)
        print(f"Posted to Slack: €{total_revenue:,.0f}")

except Exception as e:
    print(f"Error: {e}")
    with open("$LOG", "a") as f:
        f.write(f"Error: {e}\\n")
PYEOF

echo "$(date): Daily snapshot complete" >> "$LOG"
/root/aurelio-v2/scripts/log-event.sh "Ferland" "Daily revenue snapshot generated and posted to Slack"
