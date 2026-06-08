# 30-Day Deployment Calendar

## Week 1: Foundation (Days 1-7)

### Day 1-2: Infrastructure
- [ ] Provision VPS (Hetzner recommended, €15/mo, EU region)
- [ ] Install OpenClaw (`npm i -g openclaw@beta`)
- [ ] Configure first agent (Strategy Hub) with your LLM API key
- [ ] Test: send a message, get a response
- [ ] Set up Tailscale on VPS + your laptop

### Day 3-4: Knowledge Base
- [ ] Create Context Tree structure: `brain/knowledge/{your-brand}/{finance,operations,team,marketing,strategy}` + `platform/{agents,auth,config}`
- [ ] Populate Day 1 essentials: products.md, policies.md, org-chart.md
- [ ] Write MEMORY.md (executive summary — see template)
- [ ] Generate initial `_index.md` files (use `generate-index.sh`)
- [ ] Test: `brain_search` finds your product info

### Day 5-7: Second Agent + Channel
- [ ] Deploy CS Agent (highest-impact first)
- [ ] Connect to your CS channel (Slack, WhatsApp, or email)
- [ ] Load: FAQ, return policy, shipping times, brand voice guidelines
- [ ] Enter **shadow mode**: agent drafts, human sends
- [ ] Review first 20 drafts for quality

## Week 2: Expand (Days 8-14)

### Day 8-9: Finance Agent
- [ ] Deploy Finance Agent
- [ ] Connect: Holded/Xero/QuickBooks API + Shopify
- [ ] Configure: weekly P&L template, AR thresholds
- [ ] First run: generate this week's P&L
- [ ] Review accuracy against manual P&L

### Day 10-11: Secondary Host (Optional)
- [ ] If running 4+ agents: set up Mac Mini or second VPS
- [ ] Install Tailscale, connect to mesh
- [ ] Deploy domain agents on secondary host
- [ ] Set up brain-sync (rsync every 30 min)
- [ ] Set up LaunchDaemons (use templates in `templates/launch-daemons/`)

### Day 12-14: Marketing + Retail
- [ ] Deploy Marketing Agent (connect Klaviyo, Meta Ads, GA4)
- [ ] Deploy Retail Agent if you have physical stores (connect TC Analytics, POS)
- [ ] Configure crons: daily revenue snapshot, retail report
- [ ] All agents in **shadow mode** — human reviews everything

## Week 3: Integrate (Days 15-21)

### Day 15-16: MCP Server
- [ ] Deploy MCP server (use `mcp-server.py` template)
- [ ] Configure Cloudflare Tunnel for public HTTPS
- [ ] Test: Claude Desktop connects to MCP with all tools
- [ ] Onboard 1-2 team members to Claude Desktop

### Day 17-18: Merchandising + HR
- [ ] Deploy Merch Agent (Stockagile, Shopify inventory)
- [ ] Deploy HR Agent (Holded leaves, Notion, Payhawk)
- [ ] Configure: sell-through thresholds, absence tracking

### Day 19-21: Automation
- [ ] Set up all crons (see `cron-definitions.md`)
- [ ] CS ticket monitoring (every 15 min)
- [ ] Inventory monitoring (every 30 min)
- [ ] Knowledge Mining (daily)
- [ ] Brain sync health check (every 2 hours)
- [ ] Deploy openclaw-ops toolkit (heal, watchdog, security-scan)

## Week 4: Graduate (Days 22-30)

### Day 22-24: Graduated Autonomy
- [ ] CS Agent: promote WISMO + tracking queries to auto-resolve (>95% confidence)
- [ ] Finance Agent: auto-deliver weekly P&L (no human review)
- [ ] Retail Agent: auto-publish daily reports
- [ ] Monitor: review confidence scores and escalation rates daily

### Day 25-27: Cross-Agent Coordination
- [ ] Configure Strategy Hub as orchestrator
- [ ] Test: morning briefing pulls from all agents
- [ ] Test: CS pattern → Merch agent notification
- [ ] Test: inventory alert → Retail agent transfer recommendation

### Day 28-30: Production Hardening
- [ ] Run `security-scan.sh` — fix any findings
- [ ] Verify all agents survive a reboot (test by rebooting each host)
- [ ] Set up audit logging (JSONL format)
- [ ] Document your deployment: agents, ports, API keys, cron schedule
- [ ] Baseline metrics: autonomy rate, escalation rate, hours saved estimate
- [ ] 🎉 You're in production

## Post-30 Days: Compound

### Month 2
- [ ] Expand CS autonomy to returns + exchanges (80-95% confidence)
- [ ] Add Knowledge Mining patterns to brain weekly
- [ ] First Pattern Library extraction
- [ ] Onboard full team to Claude Desktop via MCP

### Month 3
- [ ] Target: 65% autonomous operations
- [ ] Fine-tune confidence thresholds based on data
- [ ] Add advanced capabilities as needed (Invoice Pipeline, Copy Engine, etc.)
- [ ] First quarterly knowledge audit

### Month 6
- [ ] Target: 82% autonomous operations
- [ ] The system should now feel like a team member, not a tool
- [ ] Knowledge base should have 200+ documents
- [ ] Every weekly review should surface at least one insight you didn't ask for
