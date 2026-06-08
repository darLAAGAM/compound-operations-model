# Chapter 9c: Agent — HR & People Operations (HR Agent)

## Why AI for HR?

Here's a dirty secret about companies doing €2-10M in revenue: **most of them have zero HR processes.** Everything is ad-hoc — vacations tracked in a shared calendar (maybe), payroll prep done in a panic on the 20th of each month, onboarding that consists of "here's your laptop, ask someone if you have questions."

Sound familiar? This was the brand as it scaled to ~40-person team. No formal HR department. No HRIS. No consistent processes.

The typical solution: hire an HR manager (€45-60K/year) or outsource to an HR consultancy (€1-2K/month for basic coverage). The solution: **HR Agent, an AI HR agent that handles 80% of the HR function for €0 incremental cost** — running on the same infrastructure as the other 8 agents.

## What HR Agent Does

### 1. Onboarding & Offboarding
When a new employee joins, HR Agent:
- Creates their profile in the team database (Notion)
- Generates an onboarding checklist tailored to their role
- Sends welcome pack with links to policies, clock-in tutorials, and the org chart
- Schedules 30/60/90-day check-in reminders
- Coordinates with the external payroll agency (gestoría) for social security enrollment

For offboarding: reverse checklist — access revocation list, knowledge transfer documentation, payroll agency notification.

### 2. Vacation & Leave Management
The complete lifecycle:
1. Employee requests via Slack DM or #hr channel
2. HR Agent checks their balance in Holded (the payroll system)
3. Verifies no conflicts (max 2 people out per department)
4. If OK → creates entry in the absence calendar, flags for CEO approval
5. Once approved → updates calendar, notifies employee, creates Google Calendar event

**Confidence level:** 92% autonomous on standard requests. Escalates unusual cases (extended leave, sick leave documentation, legal questions).

### 3. Monthly Payroll Preparation
On the 20th of every month, HR Agent:
1. Reviews the team database for changes (new hires, departures, salary changes)
2. Checks Holded for absence incidents (sick leave, special permits)
3. Compiles a "monthly newsletter" for the external payroll agency:
   - New hires: name, ID number, start date, salary, payment schedule
   - Departures: name, effective date, reason
   - Incidents: sick leave, special permits, overtime
4. Creates an email draft for CEO review — **never sends directly**

### 4. Employee Handbook & Policies
HR Agent maintains a living policy database in Notion covering:
- Vacation policy (30 calendar days per local labor regulations)
- Clock-in procedures (mandatory under local labor law)
- Expense policy (Payhawk card usage, travel booking)
- Employee discount policy
- AI usage policy
- Travel and expense reimbursement
- Marriage leave

When employees ask "how do I file an expense?" or "what's our vacation policy?" — HR Agent answers with the exact policy and links to the relevant Notion page.

### 5. Expense Monitoring
Monthly report via Payhawk API:
- Categorized by type (office, travel, software, retail operations)
- Month-over-month comparison
- Flagging unusual expenses or missing receipts
- Summary sent to #hr and Finance (Finance Agent)

### 6. Org Chart & Team Database
Maintains a single source of truth for:
- all employees across HQ, retail, and remote
- Department structure, reporting lines
- Contact information (phones, personal emails)
- Contract details (start date, position, salary tier)
- Employment status tracking

## The SOUL.md

```
# SOUL.md — HR Agent (HR Agent)

## Identity
- Name: HR Agent
- Role: HR Manager AI
- Personality: Professional, empathetic, precise with regulations
- Tone: Warm but formal. Always addresses by first name.

## Hard Rules
1. NEVER send emails directly — only drafts for CEO review
2. NEVER approve vacations without CEO confirmation
3. NEVER share salary data with anyone except CEO
4. NEVER handle social security enrollment — that's the external agency
5. ALWAYS escalate labor conflicts or sensitive situations to CEO
6. Sensitive data (salaries, ID numbers) never in public Slack channels
```

## Integration Stack

| System | Access | What It Provides |
|--------|--------|-----------------|
| **Notion** | Read/Write | Team database, policies, onboarding checklists, absence calendar |
| **Holded** | Read | Employee data, leave balances, payroll info |
| **Payhawk** | Read | Expense data, card management, receipt tracking |
| **Google Workspace** | Draft | Email drafts for payroll agency, calendar events |
| **Slack** | Read/Write | #hr channel, direct messages, announcements |
| **Brain** | Read/Write | HR knowledge, procedures, templates |

## Automated Schedules

| When | What | Where |
|------|------|-------|
| Daily 9:00 AM | Today's absences announcement | #general |
| Monday 9:30 AM | Pending vacation requests summary | #hr |
| 20th of month | Payroll prep draft | DM to CEO |
| 1st of month | Monthly expense report | #hr |
| Quarterly | Salary review reminders | DM to CEO |

## ROI

| Metric | Before HR Agent | After | Impact |
|--------|-----------------|-------|--------|
| HR processes documented | 0 | 12 policies | From chaos to structure |
| Payroll prep time | 4-6 hours/month | 30 minutes review | -90% CEO time |
| Vacation request cycle | 1-3 days (forgot) | 2 hours | Employee satisfaction |
| Policy questions | "Ask a colleague" | Instant, 24/7 | Self-service HR |
| Onboarding completeness | ~40% (ad-hoc) | 95% (checklist) | Better first impressions |
| Annual cost | €0 (no HR) or €50K (hire) | €0 incremental | Pure upside |

## Why Not Just Hire an HR Person?

At 35 employees, you arguably should. But consider:
- An HR manager costs €45-60K/year fully loaded
- They work 40 hours/week, take vacation, get sick
- They need 2-3 months to understand your company
- Most of their time goes to **repetitive administrative tasks** that AI handles perfectly

HR Agent handles the repetitive 80% (vacation tracking, payroll prep, policy questions, expense reports, onboarding checklists). The remaining 20% — labor negotiations, terminations, culture building — still needs a human. In most cases, that human is the CEO spending 2-3 hours/week on HR decisions, reviewing HR Agent's drafts.

**The real unlock:** Going from zero HR processes to full HR coverage in a single deployment. For a growing brand, the alternative isn't "HR person vs. AI" — it's "some HR coverage vs. no HR coverage at all."

## Technical Notes

> **Current status (April 2026):** No OpenClaw gateway. Runs via internal scripts only. UID 506. All scheduling and integrations are handled through shell scripts and cron jobs on the secondary compute node, bypassing the standard OpenClaw gateway pattern used by the other agents.

## Implementation Checklist

- [x] Create team database in Notion with all employees
- [x] Create policy database with company handbook
- [x] Create onboarding checklist templates
- [x] Set up absence calendar synced with Holded
- [x] Configure Payhawk API access for expense monitoring
- [x] Write SOUL.md with HR protocols and hard rules
- [x] Deploy on dedicated compute node
- [x] Create Slack app and channel (#hr)
- [x] First payroll prep cycle test

---

*Next: [Chapter 10 — The Technology Stack →](10-stack.md)*
