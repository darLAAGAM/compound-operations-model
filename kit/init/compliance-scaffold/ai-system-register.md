# AI System Register — [YOUR COMPANY]
## EU AI Act Article 26 — Deployer Documentation

*Document: REG-[YOUR BRAND]-AI-2026-001*
*Created: 11 April 2026*
*Organization: [YOUR COMPANY]*
*Responsible: [CEO NAME], CEO*
*Contact: [CEO EMAIL]*

---

## Overview

[YOUR COMPANY] operates a multi-agent AI system ("OperAI Swarm") for internal business operations. The system consists of 7 specialized AI agents plus a founder command interface, connected to 16 business systems via 44 MCP tools. The system is deployed on EU-hosted infrastructure and has been in production since October 2025.

**This register lists all AI systems deployed by [YOUR COMPANY], their intended purpose, risk classification under the EU AI Act, and the human oversight measures in place.**

---

## AI Systems Deployed

### System 1: Strategy Agent (Strategy Agent)

| Field | Value |
|---|---|
| **System ID** | [YOUR BRAND]-AI-001 |
| **Intended Purpose** | Central coordination of all agents, morning briefings, competitive intelligence, knowledge mining, CEO personal assistant |
| **Risk Classification** | Minimal risk |
| **Justification** | Internal coordination and synthesis. No decisions about natural persons. No external-facing output. |
| **Provider** | OpenAI (GPT-5.4 via ChatGPT OAuth) |
| **Deployer** | [YOUR COMPANY] |
| **Host** | Hetzner VPS, Germany (EU) |
| **Human Oversight** | [CEO NAME] (CEO). Reviews all strategic recommendations. |
| **Autonomy Level** | 90% autonomous for coordination; strategic decisions always reviewed |
| **Data Processed** | Aggregated cross-domain summaries. No raw PII. |
| **Deployment Date** | October 2025 |
| **Last Review** | April 2026 |

### System 2: Customer Service Agent (CS Agent)

| Field | Value |
|---|---|
| **System ID** | [YOUR BRAND]-AI-002 |
| **Intended Purpose** | CS ticket triage, draft response generation, complaint pattern detection |
| **Risk Classification** | **Limited risk** |
| **Justification** | Interacts indirectly with customers (drafts reviewed by human before sending). Article 50 transparency required. |
| **Provider** | Anthropic (Claude Sonnet 4) |
| **Deployer** | [YOUR COMPANY] |
| **Host** | Mac Mini M4, Spain (EU) |
| **Human Oversight** | [CS LEAD] (CS Lead). Reviews and sends all customer-facing drafts. |
| **Autonomy Level** | 60% auto-resolved (WISMO, tracking); 40% requires human review |
| **Transparency Measure** | Email footer: "This response was prepared with AI assistance and reviewed by our team." |
| **Data Processed** | Customer names, emails, order numbers, complaint content |
| **Deployment Date** | February 2026 |
| **Last Review** | April 2026 |

### System 3: Finance Agent (Finance Agent)

| Field | Value |
|---|---|
| **System ID** | [YOUR BRAND]-AI-003 |
| **Intended Purpose** | Weekly P&L generation, AR tracking, invoice reconciliation, cash position monitoring |
| **Risk Classification** | Minimal risk |
| **Justification** | Financial reporting and analysis. No decisions about natural persons' access to financial services. |
| **Provider** | OpenAI (GPT-5.4 via ChatGPT OAuth) |
| **Host** | Mac Mini M4, Spain (EU) |
| **Human Oversight** | [FINANCE MANAGER] (Finance Manager). Reviews all reports. |
| **Autonomy Level** | Reports auto-generated; anomalies flagged for human review |
| **Data Processed** | Invoice data, revenue figures, expense data. Employee names in payroll context. |
| **Deployment Date** | February 2026 |
| **Last Review** | April 2026 |

### System 4: Digital Marketing Agent (Marketing Agent)

| Field | Value |
|---|---|
| **System ID** | [YOUR BRAND]-AI-004 |
| **Intended Purpose** | Campaign analysis, email segmentation, SEO opportunities, ads audit, GEO optimization |
| **Risk Classification** | Minimal risk |
| **Justification** | Marketing analytics and optimization. No targeting of vulnerable groups. No individual-level profiling for discrimination. |
| **Provider** | OpenAI (GPT-5.4 via ChatGPT OAuth) |
| **Host** | Mac Mini M4, Spain (EU) |
| **Human Oversight** | [ECOMMERCE LEAD] (Ecommerce Lead). Approves campaign changes. |
| **Autonomy Level** | Analysis autonomous; execution requires human approval |
| **Data Processed** | Aggregated campaign metrics, email segment data (via Klaviyo). |
| **Deployment Date** | February 2026 |
| **Last Review** | April 2026 |

### System 5: Retail Agent (Retail Agent)

| Field | Value |
|---|---|
| **System ID** | [YOUR BRAND]-AI-005 |
| **Intended Purpose** | Daily store reports (foot traffic + POS), staffing recommendations, inventory transfer alerts |
| **Risk Classification** | Minimal risk |
| **Justification** | Operational reporting on store performance. Staffing recommendations are advisory only — no employment decisions. |
| **Provider** | OpenAI (GPT-5.4 via ChatGPT OAuth) |
| **Host** | Mac Mini M4, Spain (EU) |
| **Human Oversight** | [RETAIL MANAGER] (Retail Manager). Reviews and acts on recommendations. |
| **Autonomy Level** | Reports auto-published; staffing recommendations require manager approval |
| **Data Processed** | Aggregated foot traffic (no PII), POS transaction totals, inventory levels |
| **Deployment Date** | February 2026 |
| **Last Review** | April 2026 |

### System 6: Merchandising & Wholesale Agent (Merch Agent)

| Field | Value |
|---|---|
| **System ID** | [YOUR BRAND]-AI-006 |
| **Intended Purpose** | Sell-through analysis, size curve audits, markdown candidates, price positioning, wholesale order management |
| **Risk Classification** | Minimal risk |
| **Justification** | Product and inventory analysis. Decisions about products and stock, not about natural persons. |
| **Provider** | OpenAI (GPT-5.4 via ChatGPT OAuth) |
| **Host** | Mac Mini M4, Spain (EU) |
| **Human Oversight** | [BUYER] (Buyer). Reviews all markdown and pricing recommendations. |
| **Autonomy Level** | Analysis autonomous; pricing/markdown decisions require buyer approval |
| **Data Processed** | Product data, inventory levels, wholesale partner names and order data |
| **Deployment Date** | February 2026 |
| **Last Review** | April 2026 |

### System 7: HR & People Agent (HR Agent)

| Field | Value |
|---|---|
| **System ID** | [YOUR BRAND]-AI-007 |
| **Intended Purpose** | Absence tracking, payroll prep, vacation balances, expense categorization, policy lookups |
| **Risk Classification** | **Limited risk (with guardrails)** |
| **Justification** | Administrative HR tasks only. Explicit guardrails prohibit all Annex III high-risk employment uses (recruitment, evaluation, performance monitoring, promotion/termination decisions). |
| **Provider** | Anthropic (Claude Sonnet 4) |
| **Host** | Mac Mini M4, Spain (EU) |
| **Human Oversight** | [CEO NAME] (CEO). Approves all payroll changes and vacation requests. Sole access to salary data. |
| **Autonomy Level** | Read-only queries autonomous; all changes require CEO confirmation |
| **Prohibited Uses** | Candidate screening, hiring/firing decisions, performance monitoring, employee scoring/ranking — per EU AI Act Annex III Section 4 |
| **Data Processed** | Employee names, absence dates, vacation balances, department, payroll changes |
| **Deployment Date** | March 2026 (pre-deployment: scripts only, no OpenClaw gateway) |
| **Last Review** | April 2026 |

### System 8: Founder Command Interface ("Claude Code")

| Field | Value |
|---|---|
| **System ID** | [YOUR BRAND]-AI-008 |
| **Intended Purpose** | Power-user interface for CEO to query all systems, coordinate agents, deploy code, manage operations |
| **Risk Classification** | Minimal risk |
| **Justification** | Single-user tool used exclusively by the CEO. No automated decisions about natural persons. |
| **Provider** | Anthropic (Claude Opus 4.6 via Pro Max subscription) |
| **Host** | CEO MacBook Pro (local) + MCP connection to VPS |
| **Human Oversight** | Direct — CEO is the sole user |
| **Autonomy Level** | Tool-assisted; all actions initiated and approved by the CEO |
| **Data Processed** | All company data (via MCP tools) |
| **Deployment Date** | March 2026 |
| **Last Review** | April 2026 |

---

## Shared Infrastructure

| Component | Details |
|---|---|
| **MCP Server** | 44 tools, SSE endpoint at mcp.[yourdomain].com, Cloudflare Tunnel |
| **Knowledge Base** | 1,341 documents, rsync every 30 min between hosts |
| **Monitoring** | openclaw-ops watchdog (every 5 min), heal.sh, security-scan.sh |
| **Audit Logging** | JSONL format, 90-day retention, per-agent |
| **Networking** | Tailscale encrypted mesh, loopback gateway binding, port forwarders |

## Compliance Measures (All Systems)

| Measure | Status | Reference |
|---|---|---|
| Confidence scoring (graduated autonomy) | ✅ Active on all agents | Article 14 |
| Anti-prompt-injection | ✅ In all SOULs | Article 5 |
| Audit logging | ✅ JSONL per agent | Article 12 |
| Human oversight | ✅ Manager per agent | Article 14 |
| EU data residency | ✅ Hetzner DE + Mac Mini ES | Article 26 |
| API-only LLM usage | ✅ No consumer products | Data governance |
| DPIA completed | ✅ DPIA-[YOUR BRAND]-2026-001 | GDPR Art. 35 |
| Incident reporting procedure | ✅ Documented | Article 26.5 |
| Transparency (CS) | ✅ Email disclaimer | Article 50 |
| HR guardrails (Annex III) | ✅ Prohibited uses in SOUL.md | Annex III Sec. 4 |

---

*This register will be updated whenever a new AI system is deployed or an existing system's capabilities change materially. Next scheduled review: July 2026 (pre-enforcement).*
