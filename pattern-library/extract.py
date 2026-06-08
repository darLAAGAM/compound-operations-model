#!/usr/bin/env python3
"""
OperAI Pattern Extraction Pipeline

Scans agent memory logs, audit logs, and brain docs to extract 
reusable operational patterns. Runs daily via cron.

Flow:
1. Read recent memory logs (last 7 days)
2. Read audit logs (last 30 days)  
3. Send to LLM for pattern extraction
4. Anonymize extracted patterns
5. Write to pattern library
6. Update stats
"""

import os
import json
import glob
import datetime
import hashlib
import urllib.request

MEMORY_DIR = "/root/aurelio-v2/memory"
AUDIT_DIR = "/root/aurelio-v2/audit-logs"
BRAIN_DIR = "/root/aurelio-v2/brain/knowledge"
PATTERN_DIR = "/root/aurelio-v2/operai/pattern-library/patterns"
STATS_FILE = "/root/aurelio-v2/operai/pattern-library/stats.json"
LOG_FILE = "/tmp/pattern-extraction.log"

# Load API key
API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
if not API_KEY:
    for path in ["/root/.bashrc"]:
        if os.path.exists(path):
            with open(path) as f:
                for line in f:
                    if "ANTHROPIC_API_KEY" in line and "export" in line:
                        API_KEY = line.split("=", 1)[1].strip().strip('"').strip("'")
                        if API_KEY and not API_KEY.startswith("$"):
                            break
                        API_KEY = ""

def log(msg):
    ts = datetime.datetime.now().isoformat()
    with open(LOG_FILE, "a") as f:
        f.write(f"{ts}: {msg}\n")
    print(msg)

def read_recent_memories(days=7):
    """Read memory logs from the last N days"""
    content = []
    today = datetime.date.today()
    for i in range(days):
        d = today - datetime.timedelta(days=i)
        path = os.path.join(MEMORY_DIR, f"{d.isoformat()}.md")
        if os.path.exists(path):
            with open(path) as f:
                content.append(f"## Memory {d.isoformat()}\n{f.read()}")
    return "\n\n".join(content)

def read_audit_logs(days=30):
    """Read audit logs from recent months"""
    content = []
    files = sorted(glob.glob(os.path.join(AUDIT_DIR, "audit-*.jsonl")))
    for fpath in files[-2:]:  # Last 2 months
        with open(fpath) as f:
            lines = f.readlines()[-100:]  # Last 100 entries
            content.extend(lines)
    return "\n".join(content)

def extract_patterns(memory_text, audit_text):
    """Use LLM to extract operational patterns"""
    if not API_KEY:
        log("No API key — skipping LLM extraction")
        return []
    
    prompt = f"""You are an operational patterns analyst for OperAI. 

Analyze the following agent memory logs and audit trails from a consumer brand's AI operations. Extract REUSABLE OPERATIONAL PATTERNS that would help ANY consumer/retail brand.

For each pattern, output in this EXACT YAML format:

```yaml
id: PAT-[DOMAIN]-[NNN]
domain: [one of: customer-service, inventory, finance, marketing, wholesale, retail, merchandising, hr, operations]
type: [one of: resolution-template, threshold, timing, workflow, rule, metric-benchmark]
confidence: [high/medium/low]
title: "[concise title]"
context: "[when/why this pattern applies]"
pattern: "[the actual operational pattern — step by step]"
conditions: ["when to use this"]
anti_patterns: ["what NOT to do"]
metrics: ["measurable outcomes"]
tags: [relevant, keywords]
```

CRITICAL ANONYMIZATION RULES:
- NO brand names, NO employee names, NO locations
- Replace names with roles: "the CS lead", "the finance manager"  
- Use relative metrics only: percentages, ratios, trends
- NO specific revenue figures, NO customer data

Only extract patterns that are GENERALIZABLE — things that would work for any consumer/retail brand running AI agents. Skip brand-specific operational details.

Extract 3-8 patterns maximum. Quality over quantity.

---
MEMORY LOGS:
{memory_text[:15000]}

---
AUDIT TRAIL:
{audit_text[:5000]}
"""

    headers = {
        "Content-Type": "application/json",
        "x-api-key": API_KEY,
        "anthropic-version": "2023-06-01"
    }
    
    body = json.dumps({
        "model": "claude-haiku-4-5-20251001",
        "max_tokens": 4000,
        "messages": [{"role": "user", "content": prompt}]
    }).encode()

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=body, headers=headers, method="POST"
    )
    
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            result = json.loads(resp.read())
            return result["content"][0]["text"]
    except Exception as e:
        log(f"LLM extraction error: {e}")
        return ""

def parse_patterns(raw_text):
    """Parse YAML patterns from LLM output"""
    patterns = []
    current = {}
    current_field = None
    
    for line in raw_text.split("\n"):
        line = line.strip()
        if line.startswith("id:"):
            if current.get("id"):
                patterns.append(current)
            current = {"id": line.split(":", 1)[1].strip()}
            current_field = None
        elif line.startswith("domain:"):
            current["domain"] = line.split(":", 1)[1].strip()
        elif line.startswith("type:"):
            current["type"] = line.split(":", 1)[1].strip()
        elif line.startswith("confidence:"):
            current["confidence"] = line.split(":", 1)[1].strip()
        elif line.startswith("title:"):
            current["title"] = line.split(":", 1)[1].strip().strip('"')
        elif line.startswith("context:"):
            val = line.split(":", 1)[1].strip().strip('"').strip("|")
            current["context"] = val
            current_field = "context"
        elif line.startswith("pattern:"):
            val = line.split(":", 1)[1].strip().strip('"').strip("|")
            current["pattern"] = val
            current_field = "pattern"
        elif line.startswith("conditions:"):
            current["conditions"] = []
            current_field = "conditions"
        elif line.startswith("anti_patterns:"):
            current["anti_patterns"] = []
            current_field = "anti_patterns"
        elif line.startswith("metrics:"):
            current["metrics"] = []
            current_field = "metrics"
        elif line.startswith("tags:"):
            current["tags"] = line.split(":", 1)[1].strip().strip("[]").split(",")
            current["tags"] = [t.strip().strip('"') for t in current["tags"]]
        elif line.startswith("- ") and current_field in ["conditions", "anti_patterns", "metrics"]:
            current.setdefault(current_field, []).append(line[2:].strip().strip('"'))
        elif line and current_field in ["context", "pattern"]:
            current[current_field] = current.get(current_field, "") + " " + line
    
    if current.get("id"):
        patterns.append(current)
    
    return patterns

def save_pattern(pattern):
    """Save a pattern to the library"""
    domain = pattern.get("domain", "operations")
    domain_dir = os.path.join(PATTERN_DIR, domain)
    os.makedirs(domain_dir, exist_ok=True)
    
    # Generate filename from ID
    pat_id = pattern.get("id", f"PAT-{domain[:3].upper()}-{hashlib.md5(pattern.get('title','').encode()).hexdigest()[:6]}")
    filename = f"{pat_id.lower().replace(' ', '-')}.yaml"
    filepath = os.path.join(domain_dir, filename)
    
    # Check if pattern already exists (by title similarity)
    existing_files = glob.glob(os.path.join(domain_dir, "*.yaml"))
    for ef in existing_files:
        with open(ef) as f:
            if pattern.get("title", "")[:50] in f.read():
                log(f"Pattern '{pattern['title'][:50]}' already exists, skipping")
                return False
    
    # Write YAML
    yaml_content = f"""id: {pat_id}
domain: {domain}
type: {pattern.get('type', 'workflow')}
confidence: {pattern.get('confidence', 'medium')}
source_deployments: 1
created: {datetime.date.today().isoformat()}
updated: {datetime.date.today().isoformat()}

title: "{pattern.get('title', 'Untitled')}"

context: |
  {pattern.get('context', '').strip()}

pattern: |
  {pattern.get('pattern', '').strip()}

conditions:
{chr(10).join('  - ' + c for c in pattern.get('conditions', ['General consumer/retail brand']))}

anti_patterns:
{chr(10).join('  - ' + a for a in pattern.get('anti_patterns', ['None documented yet']))}

metrics:
{chr(10).join('  - ' + m for m in pattern.get('metrics', ['To be measured']))}

tags: [{', '.join(pattern.get('tags', [domain]))}]
"""
    
    with open(filepath, "w") as f:
        f.write(yaml_content)
    
    log(f"Saved pattern: {pat_id} → {filepath}")
    return True

def update_stats():
    """Update library statistics"""
    total = 0
    by_domain = {}
    by_confidence = {"high": 0, "medium": 0, "low": 0}
    
    for domain_dir in glob.glob(os.path.join(PATTERN_DIR, "*")):
        if os.path.isdir(domain_dir):
            domain = os.path.basename(domain_dir)
            count = len(glob.glob(os.path.join(domain_dir, "*.yaml")))
            by_domain[domain] = count
            total += count
    
    stats = {
        "total_patterns": total,
        "by_domain": by_domain,
        "by_confidence": by_confidence,
        "last_extraction": datetime.datetime.now().isoformat(),
        "source_deployments": 1
    }
    
    with open(STATS_FILE, "w") as f:
        json.dump(stats, f, indent=2)
    
    return stats

def main():
    log("=== Pattern Extraction Pipeline Started ===")
    
    # 1. Read sources
    memory = read_recent_memories(7)
    audit = read_audit_logs(30)
    log(f"Read {len(memory)} chars of memory, {len(audit)} chars of audit")
    
    if not memory and not audit:
        log("No data to process")
        return
    
    # 2. Extract patterns
    raw = extract_patterns(memory, audit)
    if not raw:
        log("No patterns extracted")
        return
    
    # 3. Parse
    patterns = parse_patterns(raw)
    log(f"Parsed {len(patterns)} patterns")
    
    # 4. Save
    saved = 0
    for p in patterns:
        if save_pattern(p):
            saved += 1
    
    # 5. Update stats
    stats = update_stats()
    log(f"Pipeline complete: {saved} new patterns. Library: {stats['total_patterns']} total.")

if __name__ == "__main__":
    main()
