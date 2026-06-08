"""assess — classify an employee into M-shaped / T-shaped / frontline + training path.

A lightweight conversational questionnaire (8-10 questions, no LLM needed).
Outputs a role-profile.md file alongside the employee's me.md.

Usage:
    operai-init assess laura
    operai-init assess --team              # show distribution
"""
from __future__ import annotations
import json
import re
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from operai_init import common

_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,40}$")


@dataclass
class AssessmentResult:
    name:          str
    current:       str
    target:        str
    adoption_l:    str
    recommended_domains: list[str]
    next_90_days:  list[str]
    training_budget_eur: int
    assessed_at:   str


# ─────────────────────────────────────────────────────────────────────────────
# Scoring rubric — simple weighted answers
# ─────────────────────────────────────────────────────────────────────────────

# Each question has multiple-choice answers, each mapped to a tuple of scores:
#   (m_score, t_score, frontline_score, l_level_bump)
# Totals are computed at the end and the highest wins.

QUESTIONS = [
    {
        "q": "How many domains do you currently touch regularly? (cs/finance/retail/marketing/merch/ops/hr/wholesale)",
        "choices": [
            ("Just one",                    (0, 3, 1, 0)),
            ("Two",                         (1, 3, 0, 0)),
            ("Three",                       (2, 1, 0, 1)),
            ("Four or more",                (3, 0, 0, 1)),
        ],
    },
    {
        "q": "When an agent makes a mistake you flagged, what do you do?",
        "choices": [
            ("Tell my manager",                             (0, 0, 3, 0)),
            ("Suggest what the fix should be",              (1, 2, 1, 1)),
            ("Edit the SOUL.md or write a new skill",       (3, 3, 0, 2)),
            ("I haven't caught an agent mistake yet",       (0, 0, 2, 0)),
        ],
    },
    {
        "q": "How do you mostly work with the brain?",
        "choices": [
            ("Mostly ask the agent questions",              (0, 0, 3, 1)),
            ("Read docs + write daily notes",               (1, 2, 1, 2)),
            ("Write new docs others rely on",               (2, 3, 0, 2)),
            ("I don't use it much yet",                     (0, 0, 1, 0)),
        ],
    },
    {
        "q": "How many MCP tools (of 44) do you use regularly?",
        "choices": [
            ("0-5 tools",                  (0, 0, 3, 0)),
            ("6-15 tools",                 (1, 2, 1, 1)),
            ("16-30 tools",                (3, 3, 0, 2)),
            ("Almost all",                 (3, 1, 0, 2)),
        ],
    },
    {
        "q": "Have you authored a skill or pattern used by others?",
        "choices": [
            ("No",                         (0, 0, 2, 0)),
            ("One",                        (1, 2, 0, 1)),
            ("Two to five",                (2, 3, 0, 2)),
            ("More than five",             (3, 3, 0, 2)),
        ],
    },
    {
        "q": "What fraction of your weekly time is spent directly with humans (customers, employees, partners)?",
        "choices": [
            ("More than 70%",              (0, 0, 3, 0)),
            ("40-70%",                     (1, 2, 1, 1)),
            ("10-40%",                     (3, 2, 0, 1)),
            ("Less than 10%",              (3, 1, 0, 2)),
        ],
    },
    {
        "q": "If a regulator asked you about GDPR/AI Act compliance, you would:",
        "choices": [
            ("Refer them to someone else",        (0, 0, 2, 0)),
            ("Explain the basics + show DPIA",    (2, 2, 0, 2)),
            ("Walk them through full audit trail",(3, 2, 0, 3)),
            ("Not sure what those are",           (0, 0, 1, 0)),
        ],
    },
    {
        "q": "When a new agent/workflow ships, your default reaction is to:",
        "choices": [
            ("Wait for training",                 (0, 0, 3, 0)),
            ("Try it on one small task",          (1, 1, 2, 1)),
            ("Redesign how my team works",        (3, 2, 0, 2)),
            ("Audit it before anyone uses it",    (2, 3, 0, 2)),
        ],
    },
    {
        "q": "How would your teammates describe your role?",
        "choices": [
            ("I do the work, hands-on",           (0, 1, 3, 0)),
            ("I'm the expert in X",               (1, 3, 0, 1)),
            ("I coordinate across teams",         (3, 1, 0, 2)),
            ("I build systems others use",        (3, 2, 0, 2)),
        ],
    },
    {
        "q": "Which domain are you most interested in deepening?",
        "choices": [
            ("Customer service / CX",             (0, 3, 0, 0)),
            ("Finance / numbers",                 (0, 3, 0, 0)),
            ("Marketing / brand",                 (0, 3, 0, 0)),
            ("Retail / ops",                      (0, 3, 0, 0)),
            ("Multiple — I switch often",         (3, 0, 0, 0)),
            ("I prefer customer-facing work",     (0, 0, 3, 0)),
        ],
        "captures_domain": True,
    },
]


def _domain_from_answer(q_idx: int, choice_idx: int) -> str | None:
    if not QUESTIONS[q_idx].get("captures_domain"):
        return None
    mapping = {0: "cs", 1: "finance", 2: "marketing", 3: "retail", 4: "multi", 5: "frontline"}
    return mapping.get(choice_idx)


def run_interview(name: str) -> AssessmentResult:
    common.banner(f"Role profile assessment · {name}")
    print("Short conversational assessment (~5 min). 10 questions, one number each.\n")

    m = t = f = 0
    l_total = 0
    domain = None

    for i, q in enumerate(QUESTIONS, 1):
        print(f"{common.BOLD}{i}. {q['q']}{common.RESET}")
        for j, (label, _scores) in enumerate(q["choices"], 1):
            print(f"   {j}. {label}")
        while True:
            try:
                choice = int(input("  > ").strip())
                if 1 <= choice <= len(q["choices"]):
                    break
            except ValueError:
                pass
            common.warn(f"Enter 1-{len(q['choices'])}")
        scores = q["choices"][choice - 1][1]
        m += scores[0]; t += scores[1]; f += scores[2]; l_total += scores[3]
        d = _domain_from_answer(i - 1, choice - 1)
        if d and d not in ("multi", "frontline"):
            domain = d
        print()

    # Classify
    totals = [("M-shaped Supervisor", m), ("T-shaped Specialist", t), ("AI-Empowered Frontline", f)]
    totals.sort(key=lambda x: -x[1])
    current = totals[0][0]
    target = totals[1][0] if totals[0][1] - totals[1][1] < 4 else totals[0][0]

    # Determine L level
    if l_total < 4:      l = "L0"
    elif l_total < 9:    l = "L1"
    elif l_total < 14:   l = "L2"
    else:                l = "L3"

    # Build 90-day plan based on profile
    plan = _ninety_day_plan(current, target, domain, l)

    budget = {"M-shaped Supervisor": 2000, "T-shaped Specialist": 1200, "AI-Empowered Frontline": 500}[current]

    return AssessmentResult(
        name=name,
        current=current,
        target=target,
        adoption_l=l,
        recommended_domains=[domain] if domain else [],
        next_90_days=plan,
        training_budget_eur=budget,
        assessed_at=datetime.now(timezone.utc).isoformat(),
    )


def _ninety_day_plan(current: str, target: str, domain: str | None, l: str) -> list[str]:
    d = domain or "<domain>"
    plans = {
        "AI-Empowered Frontline": [
            f"Month 1: pair with the {d} agent on 20% of your workload; review every draft before ship",
            f"Month 2: write 2 new skills for your role (scripted prompts, FAQ answers)",
            f"Month 3: propose one SOUL.md revision based on edge cases you caught",
        ],
        "T-shaped Specialist": [
            f"Month 1: own SOUL.md revisions for {d} agent end-to-end",
            f"Month 2: author 3 new MCP skills + 2 Pattern Library entries",
            f"Month 3: mentor 2 frontline colleagues; run first quarterly agent review",
        ],
        "M-shaped Supervisor": [
            "Month 1: rotate through all 7 agents; write synthesis of cross-domain patterns",
            "Month 2: own compliance review cycle (DPIA + Register + Annex III)",
            "Month 3: orchestrate a new end-to-end workflow spanning 3+ domains",
        ],
    }
    return plans.get(current, plans["AI-Empowered Frontline"])


def _role_md(r: AssessmentResult) -> str:
    lines = [
        f"# Role Profile — {r.name}",
        "",
        f"*Assessed: {r.assessed_at}*",
        "",
        "## Classification",
        "",
        f"- **Current profile:** {r.current}",
        f"- **Target profile:** {r.target}",
        f"- **Adoption level:** {r.adoption_l}",
        f"- **Recommended domain focus:** {', '.join(r.recommended_domains) or 'multi / tbd'}",
        "",
        "## Next 90 days",
        "",
    ]
    for step in r.next_90_days:
        lines.append(f"- {step}")
    lines.extend([
        "",
        f"## Training budget allocated",
        f"",
        f"€{r.training_budget_eur} / quarter",
        "",
        "## Framework",
        "",
        "See playbook Ch.14 — Team Onboarding for the M/T/frontline model (McKinsey, 2025).",
        "",
        "Re-run this assessment every 6 months via `operai-init assess " + r.name + "`.",
    ])
    return "\n".join(lines) + "\n"


def _team_dir(home: Path, brand: str) -> Path:
    return home / "brain" / "knowledge" / brand / "team"


def run(*, home: Path, brand: str, name: str | None, team: bool) -> None:
    if team:
        _print_team_distribution(home, brand)
        return

    if not name:
        common.err("need a name, or --team to see distribution")
        return

    if not _SLUG_RE.match(name):
        common.err(f"invalid name '{name}' — use lowercase/digits/hyphens")
        return

    result = run_interview(name)

    team_dir = _team_dir(home, brand) / name
    team_dir.mkdir(parents=True, exist_ok=True)
    path = team_dir / "role-profile.md"
    path.write_text(_role_md(result))

    common.banner("Assessment complete")
    print(f"  Current:  {common.BOLD}{result.current}{common.RESET}  ({result.adoption_l})")
    print(f"  Target:   {result.target}")
    print(f"  Budget:   €{result.training_budget_eur}/Q")
    print(f"  Written to: {path}")
    print(f"\n  Next 90 days:")
    for step in result.next_90_days:
        print(f"    • {step}")
    print()


def _print_team_distribution(home: Path, brand: str) -> None:
    team_dir = _team_dir(home, brand)
    if not team_dir.exists():
        common.info("no team assessments yet — run `operai-init assess <name>` per employee")
        return
    counts = {"M-shaped Supervisor": 0, "T-shaped Specialist": 0, "AI-Empowered Frontline": 0, "unclassified": 0}
    total = 0
    for emp_dir in team_dir.iterdir():
        if not emp_dir.is_dir():
            continue
        profile_path = emp_dir / "role-profile.md"
        if not profile_path.exists():
            counts["unclassified"] += 1
            total += 1
            continue
        txt = profile_path.read_text()
        for p in list(counts):
            if f"**Current profile:** {p}" in txt:
                counts[p] += 1
                total += 1
                break
    print(f"\n  Team: {total} members assessed")
    print(f"  ──────────────────────────────")
    for profile, n in counts.items():
        pct = (n / total * 100) if total else 0
        bar = "█" * int(pct / 4)
        print(f"  {profile:<25} {n:>3} ({pct:4.0f}%) {bar}")
    print()
