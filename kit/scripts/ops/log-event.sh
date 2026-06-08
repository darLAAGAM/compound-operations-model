#!/bin/bash
# Usage: log-event.sh "Agent" "Description"
# Appends to activity-log.json, keeps last 100, deduplicates recent

AGENT="$1"
TEXT="$2"
LOG="/root/aurelio-v2/operai/site/activity-log.json"

if [ -z "$AGENT" ] || [ -z "$TEXT" ]; then exit 0; fi

python3 -c "
import json, os
log_file = '$LOG'
events = []
if os.path.exists(log_file):
    with open(log_file) as f:
        try: events = json.load(f)
        except: events = []

# Don't add if same text already in last 5 events (dedup)
recent_texts = [e.get('text','') for e in events[:5]]
new_text = '''$TEXT'''
if new_text in recent_texts:
    exit(0)

events.insert(0, {'agent': '''$AGENT''', 'text': new_text})
events = events[:100]

with open(log_file, 'w') as f:
    json.dump(events, f, indent=2)
" 2>/dev/null
