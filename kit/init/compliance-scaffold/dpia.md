# Data Protection Impact Assessment (DPIA)
## [YOUR BRAND] AI Swarm — Multi-Agent Operations System

*Document: DPIA-[YOUR BRAND]-2026-001*
*Created: 11 April 2026*
*Controller: [YOUR COMPANY] (CIF: [YOUR CIF])*
*DPO Contact: [CEO EMAIL]*
*Next Review: 11 April 2027*

---

## 1. Description of Processing

### 1.1 System Overview
Multi-agent AI system composed of 7 specialized agents + 1 founder interface, processing operational data across customer service, finance, marketing, retail, merchandising, and HR domains. Agents run on OpenClaw runtime, hosted on EU infrastructure, using LLM APIs (Anthropic Claude, OpenAI GPT-5.4) for inference.

### 1.2 Agents and Their Data Access

| Agent | Personal Data Processed | Purpose | Volume |
|---|---|---|---|
| CS Agent | Customer names, emails, order history, complaint content | Draft CS responses, ticket triage, pattern detection | ~50 tickets/day |
| Finance Agent | Employee names (payroll), supplier names, invoice data | P&L reports, AR tracking, invoice reconciliation | ~20 invoices/month |
| Marketing Agent | Customer email addresses (via Klaviyo segments), campaign engagement data | Campaign analysis, segmentation, attribution | ~15K email profiles |
| Retail Agent | Aggregated foot traffic (no PII), POS transaction data (no card data) | Store reports, staffing recommendations | ~500 transactions/day |
| Merch Agent | Wholesale partner contact names, order data | Sell-through analysis, wholesale ops | ~30 B2B accounts |
| Strategy Agent | Cross-domain summaries (derived, not raw PII) | Morning briefings, coordination | Aggregated data only |
| HR Agent | Employee names, absence dates, vacation balances, department, payroll changes | Absence reports, payroll prep, vacation tracking | 44 employees |
| Claude Code | All of the above (founder interface) | On-demand queries across all domains | Ad-hoc |

### 1.3 Data Sources

| Source System | Data Type | Access Mode |
|---|---|---|
| Shopify | Orders, customers, products, inventory | API (read + limited write) |
| Richpanel | CS tickets, customer conversations | API (read + draft write) |
| Klaviyo | Email profiles, campaign data, segments | API (read + limited write) |
| Holded | Invoices, contacts, treasury, employee records | API (read) |
| Holded Leaves | Employee absences, vacation balances | Web scraper (read-only) |
| Payhawk | Expenses, corporate cards, bank statements | API (read) |
| Stockagile | Inventory, warehouse stock, wholesale orders | API (read + write) |
| Google Workspace | Gmail, Calendar, Drive, Sheets | API via Domain-Wide Delegation |
| Notion | HR databases, onboarding checklists, policies | API (read + write) |
| TC Analytics | Foot traffic (aggregated, no PII) | Scraper (read) |
| Meta Ads | Campaign performance (aggregated, no PII) | API (read) |
| GA4 | Web analytics (aggregated, no PII) | API (read) |

### 1.4 Data Flow

```
Source Systems → MCP Server (VPS, Germany) → Agent Processing → Output
                                                    ↓
                                           Brain (knowledge base)
                                           Memory (daily logs)
                                           Audit (JSONL logs)
```

All data stays within EU infrastructure. LLM API calls transmit prompts to Anthropic (US) and OpenAI (US) servers — these are processed under API terms (no training, no retention beyond request processing).

## 2. Legal Basis (GDPR Article 6)

| Data Category | Legal Basis | Justification |
|---|---|---|
| Customer data (orders, tickets) | Art. 6(1)(b) — Contract performance | Processing orders and handling support requests |
| Customer email profiles | Art. 6(1)(f) — Legitimate interest | Marketing optimization (with opt-out via Klaviyo) |
| Employee data (HR) | Art. 6(1)(b) — Employment contract | Payroll processing, absence management |
| Employee data (monitoring) | N/A — **not performed** | HR agent explicitly prohibited from performance monitoring |
| Supplier/partner data | Art. 6(1)(f) — Legitimate interest | Invoice processing, wholesale operations |
| Aggregated analytics | N/A — no PII | Store traffic, campaign metrics |

## 3. Necessity and Proportionality

### 3.1 Why AI Agents vs Manual Processing?
- 44-person company growing 50%+ annually with operational bottleneck
- AI agents automate 62 hours/week of repetitive operational work
- Human oversight maintained via graduated autonomy (confidence scoring)
- Alternative: hire 3-4 additional operational staff at ~€150K/year

### 3.2 Data Minimization
- Each agent only accesses data relevant to its domain (principle of least privilege)
- Finance agent cannot access CS tickets; CS agent cannot access salary data
- API keys are domain-scoped; no agent has unrestricted access
- Aggregated data preferred over individual records where possible

### 3.3 Storage Limitation
| Data Type | Retention | Location |
|---|---|---|
| Agent memory logs | 90 days rolling | VPS (Germany) |
| Brain knowledge base | Indefinite (operational knowledge) | VPS + Mac Mini (synced) |
| Audit logs (JSONL) | 90 days, then archived | VPS |
| LLM conversation context | Session-only (cleared on compaction) | VPS + Mac Mini |
| Customer data in source systems | Per source system policy | Shopify/Klaviyo/Holded clouds |

## 4. Risk Assessment

| # | Risk | Likelihood | Impact | Residual Risk |
|---|---|---|---|---|
| R1 | CS agent sends incorrect information to customer | Medium | Low | **Low** — human reviews all drafts before sending |
| R2 | HR agent exposes salary data | Low | High | **Low** — salary access restricted to CEO only in SOUL.md |
| R3 | Agent follows injected instructions from customer message | Low | Medium | **Low** — anti-prompt-injection in all SOULs |
| R4 | Employee data leaked via brain sync | Very Low | High | **Very Low** — brain syncs only .md files, salary data in Holded not brain |
| R5 | LLM provider uses company data for training | Very Low | High | **Very Low** — API terms prohibit training; no consumer products used |
| R6 | Agent makes biased employment decision | N/A | N/A | **N/A** — HR agent prohibited from employment decisions (EU AI Act guardrails) |
| R7 | Data breach via VPS/Mac Mini compromise | Low | High | **Low** — Tailscale mesh (encrypted), loopback gateway binding, UFW firewall |
| R8 | Unauthorized employee accesses agent data | Low | Medium | **Low** — OS-level user separation on Mac Mini, brain access via MCP auth |

## 5. Mitigation Measures

### Technical
- [x] EU data residency (Hetzner Germany + Mac Mini Spain)
- [x] Tailscale encrypted mesh networking (zero open ports)
- [x] Gateway loopback binding (no direct external access)
- [x] OS-level user separation per agent on Mac Mini
- [x] API-only LLM usage (no training on data)
- [x] Anti-prompt-injection in all agent SOULs
- [x] JSONL audit logging with 90-day retention

### Organizational
- [x] Human manager assigned to each agent
- [x] Graduated autonomy (confidence scoring)
- [x] Shadow mode for new agent deployments
- [x] Quarterly compliance review scheduled
- [x] Incident reporting procedure documented
- [x] HR agent explicitly prohibited from employment decisions

### Contractual
- [x] Anthropic API terms reviewed — no data training, no retention
- [x] OpenAI API terms reviewed — no data training, no retention
- [x] Shopify/Klaviyo/Holded DPAs in place (standard SaaS agreements)

## 6. Data Subject Rights

| Right | How Exercised | Process |
|---|---|---|
| Access (Art. 15) | Customer/employee requests via email | Diego reviews, exports relevant data from source systems |
| Rectification (Art. 16) | Request to correct data | Updated in source system; brain knowledge updated accordingly |
| Erasure (Art. 17) | Request to delete data | Deleted from source system + brain search for references |
| Restriction (Art. 18) | Request to limit processing | Agent access to specific data restricted via tool permissions |
| Portability (Art. 20) | Request for data export | Export from Shopify/Klaviyo/Holded in standard formats |
| Objection (Art. 21) | Objection to AI processing | Agent processing paused for that individual; manual handling |

## 7. Consultation

This DPIA was prepared by the AI swarm (Claude Code) based on the actual system architecture and reviewed by:

- **[CEO NAME]** (CEO & Controller) — [  ] Reviewed: ____/____/2026
- **Legal Counsel** ([LEGAL COUNSEL]) — [  ] Reviewed: ____/____/2026

## 8. Review Schedule

| Review | Date | Scope |
|---|---|---|
| Initial DPIA | 11 April 2026 | Full assessment (this document) |
| Q3 2026 review | July 2026 | Pre-enforcement check (EU AI Act Aug 2) |
| Annual review | April 2027 | Full reassessment |
| Ad-hoc review | As needed | When new agent deployed or capabilities change |
