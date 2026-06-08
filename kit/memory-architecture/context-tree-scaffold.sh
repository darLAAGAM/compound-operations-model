#!/bin/bash
# AgentivAI — Context Tree Scaffold Generator
# Creates the domain hierarchy for your brand's knowledge base
#
# Usage: ./context-tree-scaffold.sh <brand-name>
# Example: ./context-tree-scaffold.sh mystore

set -e

BRAND="${1:-my-brand}"
BASE="brain/knowledge"

echo "🧠 AgentivAI — Creating Context Tree for: $BRAND"
echo ""

# Create domain structure
mkdir -p "$BASE/$BRAND"/{finance,operations,team,marketing,strategy}
mkdir -p "$BASE/platform"/{agents,auth,setup,config}
mkdir -p "$BASE/personal"
mkdir -p "$BASE/projects"

# Generate starter files
cat > "$BASE/$BRAND/operations/products.md" << 'EOF'
# Product Catalog

<!-- Export from Shopify: Settings → Products → Export CSV, then convert to markdown -->

## How to Populate

1. Export your Shopify product catalog
2. Format as structured markdown with: name, description, price, sizes, materials
3. Group by category
4. Include variant info (colors, sizes available)

## Example Format

### Product Name
- **Price:** €XX
- **Sizes:** XS, S, M, L, XL
- **Materials:** 100% cotton
- **Care:** Machine wash cold
- **SKU prefix:** PRD-001
EOF

cat > "$BASE/$BRAND/operations/policies.md" << 'EOF'
# Policies

## Returns
- Return window: [X] days from delivery
- Condition: unworn, tags attached
- Process: [describe your return process]
- Exceptions: [swimwear, earrings, etc.]
- Refund method: original payment method
- Refund timeline: [X] business days after receipt

## Shipping
- Standard: [X] business days, €[X]
- Express: [X] business days, €[X]
- Free shipping threshold: €[X]
- International: [list countries/zones and pricing]

## Exchanges
- Available: yes/no
- Process: [describe]

## Warranty
- Duration: [X] months
- Covers: manufacturing defects
- Does not cover: normal wear, alterations
EOF

cat > "$BASE/$BRAND/operations/faq.md" << 'EOF'
# Frequently Asked Questions

<!-- Add your top 30 customer questions here -->

## Ordering

**Q: How do I place an order?**
A: [Your answer]

**Q: Can I modify my order after placing it?**
A: [Your answer]

**Q: What payment methods do you accept?**
A: [Your answer]

## Shipping

**Q: Where is my order?**
A: [Your answer with tracking instructions]

**Q: Do you ship internationally?**
A: [Your answer]

## Returns

**Q: How do I return an item?**
A: [Your answer]

**Q: When will I get my refund?**
A: [Your answer]

## Products

**Q: How do your sizes run?**
A: [Your answer with size guide link]

**Q: What materials do you use?**
A: [Your answer]

## Account

**Q: How do I track my order?**
A: [Your answer]
EOF

cat > "$BASE/$BRAND/team/org-chart.md" << 'EOF'
# Team & Escalation Directory

## Leadership
| Name | Role | Email | Handles |
|------|------|-------|---------|
| [CEO] | CEO | | Strategy, major decisions |
| [COO] | COO | | Operations oversight |

## Departments

### Customer Service
- **Lead:** [Name]
- **Escalate to:** [Name] for refunds > €[X], complaints, VIP issues

### Operations / Logistics
- **Lead:** [Name]
- **Escalate to:** [Name] for stockouts, 3PL issues, shipping delays

### Finance
- **Lead:** [Name]
- **Escalate to:** [Name] for invoices, payments, budget questions

### Marketing
- **Lead:** [Name]
- **Escalate to:** [Name] for campaigns, brand voice, PR

## Escalation Rules
1. Agents NEVER respond to customers directly (drafts only)
2. Refunds > €[X] require human approval
3. Legal/compliance questions always escalate to [Name]
4. VIP customers (list) get priority treatment
EOF

cat > "$BASE/$BRAND/marketing/brand-voice.md" << 'EOF'
# Brand Voice Guide

## Tone
- [Describe your brand's personality: friendly, professional, playful, premium, etc.]
- We are: [3-5 adjectives]
- We are NOT: [3-5 adjectives]

## Language Rules
- Use [formal/informal] language
- Address customers as [you/usted/tú]
- Sign off as: [brand name / team member name]
- Emoji usage: [yes/no, which ones]

## Do's
- ✅ [Example of good communication]
- ✅ [Example of good communication]

## Don'ts
- ❌ [Example of bad communication]
- ❌ [Example of bad communication]

## Sample Responses

### Good Response (Order Inquiry)
> "Hi [Name]! Your order #[X] shipped yesterday and should arrive by [date]. Here's your tracking link: [link]. Let me know if you need anything else! 💛"

### Bad Response (Order Inquiry)
> "Your order has been dispatched. Please refer to the tracking number provided in your shipping confirmation email."
EOF

cat > "$BASE/platform/agents/agents.md" << 'EOF'
# Agent Directory

## Agents

| Agent | Role | Model | Human Contact |
|-------|------|-------|---------------|
| Hub (Main) | Orchestration + Strategy | Claude Opus | CEO |
| CS Agent | Customer Service | Claude Sonnet | CS Lead |
| Ops Agent | Inventory & Supply Chain | Claude Sonnet | Ops Manager |
| Finance Agent | Reporting & Analysis | Claude Sonnet | Finance Manager |

## Communication Rules
- Agents communicate through the hub, not directly
- All escalations include: context summary, recommended action, urgency level
- Human contacts receive Slack notifications for escalations

## Channels
- Hub: WhatsApp (founder) + Slack
- CS: Slack only (no direct customer contact)
- Ops: Slack only
- Finance: Slack only
EOF

cat > "$BASE/platform/config/rules.md" << 'EOF'
# Operational Rules & Guardrails

## Safety Rules
1. Never send messages to customers without human approval
2. Never make financial transactions without human approval
3. Never delete data — archive instead
4. Always confirm before bulk operations (> 10 items)

## Knowledge Rules
1. If you don't know, say so — never hallucinate
2. Always cite the source file when referencing policies
3. When policies conflict, escalate to human
4. Update knowledge base when you discover outdated info

## Communication Rules
1. Internal comms in Slack, never email
2. Draft customer responses as internal notes
3. Include order/ticket numbers in every escalation
4. Use the brand voice guide for all customer-facing drafts
EOF

echo ""
echo "✅ Context Tree created at: $BASE/"
echo ""
echo "📁 Structure:"
find "$BASE" -type d | sed 's|[^/]*/|  |g'
echo ""
echo "📝 Next steps:"
echo "  1. Populate the template files with your actual data"
echo "  2. Run: ./generate-indexes.sh  (to create _index.md files)"
echo "  3. Write your MEMORY.md (use memory-md-template.md as guide)"
echo "  4. Install SuperMemory: openclaw extensions install openclaw-supermemory"
