#!/bin/bash
source /root/.bashrc 2>/dev/null || true
# Knowledge Mining Cron — Auto-distill daily memory into brain Context Tree
# Runs daily at 06:00 UTC (08:00 CET)
# Reads today's memory log, extracts durable knowledge, routes to brain

set -euo pipefail

BRAIN_DIR="/root/aurelio-v2/brain/knowledge"
MEMORY_DIR="/root/aurelio-v2/memory"
LOG="/tmp/knowledge-mining-$(date +%Y-%m-%d).log"
TODAY=$(date +%Y-%m-%d)
YESTERDAY=$(date -d "yesterday" +%Y-%m-%d 2>/dev/null || date -v-1d +%Y-%m-%d)

# Find the most recent memory file
MEMORY_FILE=""
for d in "$TODAY" "$YESTERDAY"; do
  if [ -f "$MEMORY_DIR/$d.md" ]; then
    MEMORY_FILE="$MEMORY_DIR/$d.md"
    break
  fi
done

if [ -z "$MEMORY_FILE" ]; then
  echo "$(date): No recent memory file found" >> "$LOG"
  exit 0
fi

echo "$(date): Mining $MEMORY_FILE" >> "$LOG"

# Use the MCP server to ask an agent to extract knowledge
# We use curl to the MCP server's agent_send endpoint
EXTRACTION_PROMPT="Read the following daily memory log and extract ONLY durable knowledge that should be preserved in the brain. Categorize each finding into one of these domains:
- laagam/finance/ — financial decisions, budget changes, pricing
- laagam/operations/ — process changes, tool configs, logistics
- laagam/team/ — org changes, new hires, role updates
- laagam/marketing/ — campaign results, channel changes
- laagam/strategy/ — strategic decisions, competitive intel
- laagam/retail/ — store operations, traffic patterns
- platform/agents/ — agent configs, model changes
- platform/config/ — system changes, cron updates

For each finding, output in this format:
DOMAIN: <domain_path>
FILE: <filename.md>
CONTENT: <the knowledge to store>
---

Only extract DURABLE knowledge (decisions, policies, metrics, configs). Skip ephemeral info (troubleshooting, temporary states). Be selective — only genuinely important findings."

# Read memory content
MEMORY_CONTENT=$(cat "$MEMORY_FILE")

# Save extraction prompt + memory for processing
cat > /tmp/km-prompt.txt << PROMPT_EOF
$EXTRACTION_PROMPT

---
MEMORY LOG ($MEMORY_FILE):
---
$MEMORY_CONTENT
PROMPT_EOF

echo "$(date): Extraction prompt saved. Sending to agent..." >> "$LOG"

# Use Python to call the Anthropic API directly for extraction
python3 << 'PYEOF'
import os, json, re, datetime

BRAIN_DIR = "/root/aurelio-v2/brain/knowledge"
LOG = f"/tmp/knowledge-mining-{datetime.date.today()}.log"

with open("/tmp/km-prompt.txt") as f:
    prompt = f.read()

# Try to use Anthropic API
api_key = os.environ.get("ANTHROPIC_API_KEY", "")
if not api_key:
    # Try to find it
    for path in ["/root/.bashrc", "/root/aurelio-v2/.env"]:
        if os.path.exists(path):
            with open(path) as f:
                for line in f:
                    if "ANTHROPIC_API_KEY" in line and "=" in line:
                        api_key = line.split("=", 1)[1].strip().strip('"').strip("'")
                        if api_key and not api_key.startswith("$"):
                            break
                        api_key = ""

if not api_key:
    with open(LOG, "a") as f:
        f.write(f"{datetime.datetime.now()}: No API key found, using fallback extraction\n")
    
    # Fallback: simple regex extraction of key patterns
    with open("/tmp/km-prompt.txt") as f:
        content = f.read()
    
    # Extract sections that look like decisions or configs
    findings = []
    lines = content.split("\n")
    for i, line in enumerate(lines):
        line_stripped = line.strip()
        if any(kw in line_stripped.lower() for kw in ["decision:", "changed:", "migrated", "deployed", "configured", "updated:", "created:", "installed"]):
            findings.append(line_stripped)
    
    if findings:
        # Write to a catch-all file
        output_path = os.path.join(BRAIN_DIR, "laagam/operations/auto-mined.md")
        existing = ""
        if os.path.exists(output_path):
            with open(output_path) as f:
                existing = f.read()
        
        today = datetime.date.today().isoformat()
        new_section = f"\n## Mined {today}\n" + "\n".join(f"- {f}" for f in findings[:20]) + "\n"
        
        if new_section.strip() not in existing:
            with open(output_path, "a") as f:
                f.write(new_section)
            with open(LOG, "a") as f:
                f.write(f"{datetime.datetime.now()}: Fallback extraction: {len(findings)} findings written to auto-mined.md\n")
    exit(0)

# Use Anthropic API for smart extraction
import urllib.request

headers = {
    "Content-Type": "application/json",
    "x-api-key": api_key,
    "anthropic-version": "2023-06-01"
}

body = json.dumps({
    "model": "claude-haiku-4-5-20251001",
    "max_tokens": 4000,
    "messages": [{"role": "user", "content": prompt}]
}).encode()

req = urllib.request.Request("https://api.anthropic.com/v1/messages", data=body, headers=headers, method="POST")

try:
    with urllib.request.urlopen(req, timeout=60) as resp:
        result = json.loads(resp.read())
        text = result["content"][0]["text"]
except Exception as e:
    with open(LOG, "a") as f:
        f.write(f"{datetime.datetime.now()}: API error: {e}\n")
    exit(1)

# Parse extraction results and write to brain
findings = text.split("---")
count = 0
for finding in findings:
    domain_match = re.search(r"DOMAIN:\s*(.+)", finding)
    file_match = re.search(r"FILE:\s*(.+)", finding)
    content_match = re.search(r"CONTENT:\s*([\s\S]+?)(?=DOMAIN:|FILE:|$)", finding)
    
    if domain_match and file_match and content_match:
        domain = domain_match.group(1).strip().rstrip("/")
        filename = file_match.group(1).strip()
        content = content_match.group(1).strip()
        
        dir_path = os.path.join(BRAIN_DIR, domain)
        os.makedirs(dir_path, exist_ok=True)
        
        file_path = os.path.join(dir_path, filename)
        today = datetime.date.today().isoformat()
        
        if os.path.exists(file_path):
            with open(file_path) as f:
                existing = f.read()
            if content not in existing:
                with open(file_path, "a") as f:
                    f.write(f"\n\n## Update {today}\n{content}\n")
                count += 1
        else:
            with open(file_path, "w") as f:
                f.write(f"# {filename.replace('.md', '').replace('-', ' ').title()}\n\n*Auto-mined {today}*\n\n{content}\n")
            count += 1

with open(LOG, "a") as f:
    f.write(f"{datetime.datetime.now()}: Smart extraction complete. {count} findings written to brain.\n")

print(f"Knowledge Mining complete: {count} findings extracted")
PYEOF

echo "$(date): Mining complete" >> "$LOG"
/root/aurelio-v2/scripts/log-event.sh "Aurelio" "Knowledge Mining complete — durable patterns extracted from daily operations and routed to the brain"
