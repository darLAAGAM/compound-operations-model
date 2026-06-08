# Chapter 11d: EU AI Act Compliance — What You Actually Need to Do

## Why This Chapter Exists

The EU AI Act (Regulation 2024/1689) becomes fully enforceable on **August 2, 2026**. If you're deploying AI agents in Europe — or serving European customers — this applies to you. Non-compliance penalties: up to 7% of global annual revenue or €35M, whichever is higher.

Most AI vendors either ignore this or drown you in legal jargon. This chapter tells you exactly what you need to do, agent by agent, in plain language.

## The Risk Classification That Actually Matters

The AI Act uses a risk-based approach. Most of your agents will fall into **minimal risk** (no specific obligations) or **limited risk** (transparency only). The only category that triggers serious compliance work is **high-risk** — and most operational agents don't qualify.

### How to Classify Your Agents

| Agent Type | Likely Classification | Key Question |
|---|---|---|
| **CS / Customer Service** | Limited risk | Does it interact with customers? → Transparency required |
| **Finance / Reporting** | Minimal risk | Does it make decisions about people's access to financial services? → If no, minimal risk |
| **Marketing / Analytics** | Minimal risk | Does it target vulnerable groups? → If no, minimal risk |
| **Retail / Inventory** | Minimal risk | Decisions about products and logistics, not people |
| **Merchandising** | Minimal risk | Product analysis, not people analysis |
| **Strategy / Coordination** | Minimal risk | Internal coordination, no external-facing decisions |
| **HR / People Ops** | ⚠️ **Depends on use** | Admin (absences, payroll) = limited risk. Recruitment, evaluation, performance monitoring = **high-risk** |

### The HR Agent Is the Critical One

Under Annex III of the AI Act, these employment-related uses are classified as **high-risk**:

- Screening or evaluating job candidates
- Making hiring or firing decisions
- Monitoring employee performance or productivity
- Evaluating employees for promotion or demotion
- Analyzing employee behavior or emotional state
- Deciding employment terms or conditions

If your HR agent does ANY of the above, you need full high-risk compliance: risk management system, data governance, technical documentation, human oversight, accuracy testing, and incident reporting.

**Our recommendation:** keep your HR agent strictly administrative — absences, payroll prep, vacation balances, policy lookups, expense categorization. These are NOT high-risk. The moment you add candidate screening or performance evaluation, you trigger a completely different compliance regime.

Add this explicit guardrail to your HR agent's SOUL.md:

```markdown
## EU AI Act Compliance

### Prohibited Uses (Annex III High-Risk)
This agent NEVER:
- Screens or evaluates job candidates
- Makes hiring, firing, or promotion decisions
- Monitors employee performance or productivity
- Scores or ranks employees

If asked to perform any of the above, respond:
"This is classified as high-risk under the EU AI Act. I cannot perform
employment-related decisions. Please handle this through your HR team."
```

## What Every Deployment Needs (Regardless of Risk Category)

### 1. Transparency for Customer-Facing Agents (Article 50)

If any agent drafts responses that reach end customers, those customers must know AI was involved. This applies to:

- CS agents drafting email responses
- Chatbots on your website
- AI-generated marketing communications (if personalized)

**The simplest fix:** add a footer to every AI-drafted customer response:

> *"This response was drafted with AI assistance and reviewed by our team."*

Or include it in your email signature template. Either way, the customer must be informed.

### 2. Record-Keeping (Article 12)

Log every agent action with:
- Timestamp
- Which agent acted
- What action was taken
- Confidence score
- Data sources used
- Whether a human reviewed it

The playbook's JSONL audit logging format already covers this:

```json
{"timestamp":"2026-04-11T08:15:00Z","agent":"cs-agent","action":"draft_response","confidence":"94%","data":"order_tracking","human_review":false}
```

### 3. Human Oversight (Article 14)

The confidence scoring framework from this playbook is exactly what the AI Act envisions:

| Confidence | Action | AI Act Alignment |
|---|---|---|
| > 95% | Autonomous | Acceptable for minimal-risk systems |
| 80-95% | Act + flag for review | "Meaningful human oversight" |
| 60-80% | Draft for approval | Full human-in-the-loop |
| < 60% | Escalate | Human takes over |

**Keep this framework.** It's your primary compliance mechanism. Document the thresholds and review them quarterly.

### 4. EU Data Residency

Host your infrastructure in the EU. The reference deployment uses Hetzner (Germany). This isn't strictly required by the AI Act, but it simplifies GDPR compliance and avoids cross-border data transfer headaches.

### 5. API Usage, Not Training

Ensure you're using LLM providers via API (not consumer products). API terms explicitly state your data isn't used for model training. This matters for GDPR's "purpose limitation" principle and for the AI Act's data governance requirements.

## Data Protection Impact Assessment (DPIA)

If your agents process personal data at scale — customer emails, employee records, order history — you likely need a DPIA under GDPR Article 35. This is separate from the AI Act but overlaps.

A DPIA template can live in the open-source repo. The key sections:

1. **Description of processing:** what data, what agents, what purpose
2. **Legal basis:** legitimate interest (operational efficiency) or consent
3. **Necessity and proportionality:** why AI agents vs manual processing
4. **Risks to data subjects:** what could go wrong (data leak, incorrect automated response, etc.)
5. **Mitigation measures:** confidence scoring, human review, audit logging, access controls
6. **Retention:** how long data is kept, when it's deleted

## What About the LLM Providers?

The AI Act places obligations on both **providers** (Anthropic, OpenAI, Google) and **deployers** (you). The providers handle:

- Model safety testing and evaluation
- Technical documentation of the model
- Compliance with general-purpose AI model requirements (Article 51-55)

You handle:
- Using the system according to the provider's instructions
- Human oversight and monitoring
- Transparency to end users
- Incident reporting if something goes wrong

**You are a deployer, not a provider.** Your obligations are lighter. But they're not zero.

## The Compliance Checklist

Before August 2, 2026:

- [ ] Classify each agent by risk category (use the table above)
- [ ] Add transparency disclaimers to all customer-facing agent outputs
- [ ] Add explicit "prohibited uses" guardrails to HR agent SOUL.md
- [ ] Verify audit logging is active on all agents (JSONL format)
- [ ] Verify confidence scoring is configured on all agents
- [ ] Verify human oversight is documented (who reviews what, at what threshold)
- [ ] Complete a DPIA for personal data processing
- [ ] Document the "intended purpose" of each agent (SOUL.md serves this role)
- [ ] Establish incident reporting procedure (who to notify if an agent causes harm)
- [ ] Quarterly review calendar set: autonomy rates, escalation patterns, risk classification

## What This Means for Sales

**Compliance is a selling point, not a burden.** When you pitch Compai to a European brand, you can say:

- "Every agent is classified by EU AI Act risk category"
- "Graduated autonomy with confidence scoring — exactly what Article 14 requires"
- "Full audit logging from day one"
- "HR agent has explicit guardrails against high-risk employment uses"
- "EU-hosted infrastructure, API-only LLM usage"

No competitor (Lindy, Artisan, 11x, CEO.ai) documents AI Act compliance in their materials. This is a trust differentiator.

---

*Next: [Chapter 12 — ROI: The Honest Math →](12-roi.md)*

## Ready-Made Templates (In the Repo)

The repo includes three compliance documents ready to fill in:

### 1. DPIA Template (`knowledge-base/dpia-template.md`)
Complete Data Protection Impact Assessment pre-filled with the multi-agent architecture. 8 sections covering:
- System description with per-agent data access table
- 12 data source mappings
- Legal basis per data category
- 8 risk assessments with likelihood × impact scoring
- Technical, organizational, and contractual mitigations
- Data subject rights procedures
- Signature fields for controller + legal counsel
- Review schedule

**Time to complete:** ~2 hours. Fill in your company name, employee count, specific data types, and retention periods.

### 2. AI System Register Template (`knowledge-base/ai-system-register-template.md`)
Formal register of all 8 AI systems with per-agent documentation:
- System ID, intended purpose, risk classification with justification
- Provider, host location, human oversight assignment
- Autonomy level, data processed, prohibited uses
- Consolidated compliance measures table (10 items)

**Time to complete:** ~1 hour. Fill in your team names, system details, and deployment dates.

### 3. EU AI Act Guardrails Templates (`knowledge-base/eu-ai-act-guardrails.md`)
Copy-paste blocks for agent SOUL.md files:
- HR Agent prohibited uses (Annex III)
- CS Agent transparency obligation (Article 50)
- General compliance block (all agents)
- DPIA summary template

**Time to complete:** ~15 minutes per agent. Copy the relevant block into each SOUL.md.

## Implementation Checklist

Complete these before August 2, 2026:

### Week 1: Foundation
- [ ] Classify each agent by risk category (use the table in this chapter)
- [ ] Add anti-prompt-injection block to ALL agent SOULs
- [ ] Add confidence scoring to ALL agent SOULs
- [ ] Verify audit logging is active on all agents

### Week 2: Transparency + HR
- [ ] Add Article 50 transparency disclaimer to CS agent SOUL
- [ ] Configure CS email template with AI disclosure footer
- [ ] Add Annex III prohibited uses block to HR agent SOUL
- [ ] Verify HR agent cannot perform employment decisions

### Week 3: Documentation
- [ ] Complete DPIA template with your company data
- [ ] Complete AI System Register with all deployed systems
- [ ] Document incident reporting procedure (who to notify, how, timeline)
- [ ] Assign human oversight manager to each agent

### Week 4: Verification
- [ ] Run security-scan.sh on all agents
- [ ] Verify all agents survive a reboot test
- [ ] Review autonomy rates and confidence calibration
- [ ] Schedule quarterly compliance review (first: 1 month before Aug 2, 2026)

### Ongoing
- [ ] Quarterly review of autonomy rates, escalation patterns, threshold calibration
- [ ] Annual DPIA reassessment
- [ ] Update AI System Register when new agents deployed or capabilities change
- [ ] Review incident log (any serious incidents → report to supervisory authority)
