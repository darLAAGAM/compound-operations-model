#!/bin/bash
source /root/.bashrc 2>/dev/null || true
# CS Ticket Auto-Processing — Checks Richpanel for OPEN tickets, sends to Mafalda
# Runs every 15 minutes during business hours (08:00-22:00 CET)
set -euo pipefail

LOG="/tmp/cs-tickets-$(date +%Y-%m-%d).log"
    /root/aurelio-v2/scripts/log-event.sh "Mafalda" "$(/usr/bin/python3 -c "import json,os; q=\"$queue_file\"; print(str(len(json.load(open(q)))) + \" new CS tickets triaged and queued for draft response\" if os.path.exists(q) and os.path.getsize(q)>2 else \"No new tickets\")" 2>/dev/null

python3 << 'PYEOF'
import json, urllib.request, os, datetime

# Get Richpanel API key
RICHPANEL_KEY = os.environ.get("RICHPANEL_API_KEY", "")
if not RICHPANEL_KEY:
    with open("/root/.bashrc") as f:
        for line in f:
            if "RICHPANEL_API_KEY" in line and "export" in line:
                RICHPANEL_KEY = line.split("=", 1)[1].strip().strip('"').strip("'")

if not RICHPANEL_KEY:
    print("No Richpanel API key found")
    exit(1)

# Query open tickets
url = "https://api.richpanel.com/v1/conversations?status=OPEN"
headers = {
    "x-api-key": RICHPANEL_KEY,
    "Content-Type": "application/json"
}

try:
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())
    
    conversations = data.get("data", data.get("conversations", []))
    if isinstance(conversations, dict):
        conversations = conversations.get("data", [])
    
    if not conversations:
        print(f"{datetime.datetime.now()}: No open tickets")
        exit(0)
    
    # Check which tickets are unprocessed (no agent response yet)
    # Save processed ticket IDs to avoid duplicate processing
    processed_file = "/tmp/cs-processed-tickets.json"
    processed = set()
    if os.path.exists(processed_file):
        with open(processed_file) as f:
            processed = set(json.load(f))
    
    new_tickets = []
    for conv in conversations[:30]:  # Max 30 per cycle
        ticket_id = str(conv.get("id", conv.get("_id", "")))
        if ticket_id and ticket_id not in processed:
            new_tickets.append(conv)
            processed.add(ticket_id)
    
    if not new_tickets:
        print(f"{datetime.datetime.now()}: All {len(conversations)} open tickets already processed")
        exit(0)
    
    # Save processed IDs
    with open(processed_file, "w") as f:
        json.dump(list(processed)[-500:], f)  # Keep last 500
    
    print(f"{datetime.datetime.now()}: {len(new_tickets)} new tickets to process")
    
    # For each new ticket, prepare a summary for Mafalda
    # Write to a queue file that will be picked up by agent_send
    queue_file = "/tmp/cs-ticket-queue.json"
    queue = []
    for ticket in new_tickets[:5]:  # Process max 5 per cycle to manage costs
        summary = {
            "id": str(ticket.get("id", ticket.get("_id", ""))),
            "subject": ticket.get("subject", "No subject"),
            "customer": ticket.get("customer", {}).get("email", "unknown"),
            "message": str(ticket.get("messages", [{}])[0].get("text", ""))[:500] if ticket.get("messages") else "No message"
        }
        queue.append(summary)
    
    with open(queue_file, "w") as f:
        json.dump(queue, f)
    
    print(f"Queued {len(queue)} tickets for Mafalda processing")

except Exception as e:
    print(f"Error: {e}")
PYEOF
