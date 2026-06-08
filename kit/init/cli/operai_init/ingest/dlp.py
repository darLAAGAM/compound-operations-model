"""DLP engine — deterministic-only (no LLM).

Two stages run in sequence. Anything that fails Stage A (secrets) never hits
the retrieval store. Stage B tokenizes structured PII so the sanitized text
is safe for indexing.

Stage C (NER with spaCy) is explicitly deferred to v0.5 because Codex was
right: spaCy confidence scores are not calibrated enough to be a compliance
control. For v0.4 high-risk unstructured sources (Gmail/Slack/Notion/Drive)
are blocked entirely — only structured low-risk sources ship in this phase.
"""
from __future__ import annotations
import hashlib
import re
from dataclasses import dataclass, field
from typing import Callable, Optional

# ─────────────────────────────────────────────────────────────────────────────
# Stage A — Secret scanning
# ─────────────────────────────────────────────────────────────────────────────

# Each pattern is (name, regex, why). Names go into the audit log.
SECRET_PATTERNS: list[tuple[str, re.Pattern, str]] = [
    ("aws_access_key",    re.compile(r"AKIA[0-9A-Z]{16}"),                         "AWS access key id"),
    ("aws_secret",        re.compile(r"(?i)aws(.{0,20})?['\"][0-9a-zA-Z/+]{40}['\"]"), "AWS secret access key"),
    ("stripe_live",       re.compile(r"sk_live_[0-9a-zA-Z]{24,}"),                 "Stripe live secret"),
    ("stripe_test",       re.compile(r"sk_test_[0-9a-zA-Z]{24,}"),                 "Stripe test secret"),
    ("stripe_restricted", re.compile(r"rk_(live|test)_[0-9a-zA-Z]{24,}"),          "Stripe restricted key"),
    ("github_pat",        re.compile(r"ghp_[0-9a-zA-Z]{36}"),                      "GitHub personal access token"),
    ("github_fine",       re.compile(r"github_pat_[0-9A-Za-z_]{82}"),              "GitHub fine-grained PAT"),
    ("slack_bot",         re.compile(r"xox[baprs]-[0-9a-zA-Z-]{10,}"),             "Slack token"),
    ("google_api",        re.compile(r"AIza[0-9A-Za-z_-]{35}"),                    "Google API key"),
    ("openai",            re.compile(r"sk-(proj-)?[A-Za-z0-9_-]{30,}"),            "OpenAI key"),
    ("anthropic",         re.compile(r"sk-ant-[A-Za-z0-9_-]{40,}"),                "Anthropic key"),
    ("private_key",       re.compile(r"-----BEGIN (RSA |EC |OPENSSH |DSA |)PRIVATE KEY-----"), "private key"),
    ("jwt",               re.compile(r"eyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"), "JWT"),
    ("bearer_plain",      re.compile(r"(?i)(bearer|authorization:)\s+[A-Za-z0-9._~+/=-]{32,}"), "bearer token"),
]


@dataclass
class DLPResult:
    safe_for_retrieval: bool
    sanitized_text:     str
    found_secrets:      list[str]   = field(default_factory=list)
    replacements:       list[tuple[str, str]] = field(default_factory=list)  # (type, canonical_token)


def scan_secrets(text: str) -> list[str]:
    found = []
    for name, pat, _why in SECRET_PATTERNS:
        if pat.search(text):
            found.append(name)
    return found


# ─────────────────────────────────────────────────────────────────────────────
# Stage B — Structured PII
# ─────────────────────────────────────────────────────────────────────────────

EMAIL_RE = re.compile(r"(?<![A-Za-z0-9._+-])([a-zA-Z0-9][a-zA-Z0-9._+-]*?)@([a-zA-Z0-9][-a-zA-Z0-9]*\.[a-zA-Z0-9.-]+)")
E164_RE  = re.compile(r"(?<!\w)(\+[1-9]\d{7,14})(?!\w)")
ES_PHONE_RE = re.compile(r"(?<!\w)((?:\+34|0034|34)?[\s.-]?[6-9]\d{2}[\s.-]?\d{3}[\s.-]?\d{3})(?!\w)")
DNI_RE   = re.compile(r"(?<!\w)(\d{8})([A-HJ-NP-TV-Z])(?!\w)")
NIE_RE   = re.compile(r"(?<!\w)([XYZ])(\d{7})([A-HJ-NP-TV-Z])(?!\w)")
IBAN_RE  = re.compile(r"(?<!\w)([A-Z]{2}\d{2}[A-Z0-9]{4}[\s]?\d{4}[\s]?\d{4}[\s]?\d{4}[\s]?\d{0,4})(?!\w)")
CC_RE    = re.compile(r"(?<!\w)(\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4})(?!\w)")
SHOPIFY_ORDER_RE = re.compile(r"(?<!\w)(#?\d{4,10})(?!\w)")  # refined by context in caller


def _dni_letter_valid(number: str, letter: str) -> bool:
    letters = "TRWAGMYFPDXBNJZSQVHLCKE"
    return letters[int(number) % 23] == letter.upper()


def _iban_valid(iban: str) -> bool:
    iban = re.sub(r"\s", "", iban).upper()
    if len(iban) < 15 or len(iban) > 34:
        return False
    rearranged = iban[4:] + iban[:4]
    digits = "".join(str(int(c, 36)) if c.isalpha() else c for c in rearranged)
    try:
        return int(digits) % 97 == 1
    except ValueError:
        return False


def _luhn_valid(s: str) -> bool:
    digits = re.sub(r"\D", "", s)
    if len(digits) < 13 or len(digits) > 19:
        return False
    total, alt = 0, False
    for d in reversed(digits):
        n = int(d)
        if alt:
            n *= 2
            if n > 9:
                n -= 9
        total += n
        alt = not alt
    return total % 10 == 0


# Subject resolver — callable injected by caller (Ingest pipeline gives it the
# SubjectRegistry.resolve_or_create wrapper). Signature: (alias_type, alias_value) -> subject_id
SubjectResolver = Callable[[str, str], str]


def _tokenize(text: str, resolver: Optional[SubjectResolver]) -> tuple[str, list[tuple[str, str]]]:
    """Replace structured PII with `<type:subject_id>` tokens. Returns sanitized text + replacements."""
    replacements: list[tuple[str, str]] = []

    def _sub(pattern: re.Pattern, alias_type: str, extractor: Callable[[re.Match], Optional[str]]):
        nonlocal text
        def repl(m: re.Match) -> str:
            extracted = extractor(m)
            if extracted is None:
                return m.group(0)
            if resolver:
                try:
                    sid = resolver(alias_type, extracted)
                except Exception:
                    sid = "unresolved"
            else:
                sid = "sid_" + hashlib.sha256(extracted.encode()).hexdigest()[:8]
            token = f"<{alias_type}:{sid}>"
            replacements.append((alias_type, token))
            return token
        text = pattern.sub(repl, text)

    # Order matters — match more specific patterns first.
    _sub(EMAIL_RE,      "email", lambda m: f"{m.group(1)}@{m.group(2)}")
    _sub(DNI_RE,        "dni",   lambda m: m.group(1) + m.group(2) if _dni_letter_valid(m.group(1), m.group(2)) else None)
    _sub(NIE_RE,        "dni",   lambda m: m.group(0) if True else None)  # NIE letter validation similar; accept
    _sub(IBAN_RE,       "iban",  lambda m: re.sub(r"\s", "", m.group(1)).upper() if _iban_valid(m.group(1)) else None)
    _sub(CC_RE,         "cc",    lambda m: re.sub(r"\s|-", "", m.group(1)) if _luhn_valid(m.group(1)) else None)
    _sub(E164_RE,       "phone", lambda m: m.group(1))
    _sub(ES_PHONE_RE,   "phone", lambda m: re.sub(r"[\s.-]", "", m.group(1)))

    return text, replacements


# ─────────────────────────────────────────────────────────────────────────────
# Public entry point
# ─────────────────────────────────────────────────────────────────────────────

def sanitize(text: str, *, resolver: Optional[SubjectResolver] = None) -> DLPResult:
    """Run Stage A (secret scan) + Stage B (PII tokenize). No LLM, no network."""
    secrets_found = scan_secrets(text)
    if secrets_found:
        return DLPResult(
            safe_for_retrieval=False,
            sanitized_text="[redacted — secret detected: " + ",".join(secrets_found) + "]",
            found_secrets=secrets_found,
        )

    sanitized, replacements = _tokenize(text, resolver)
    return DLPResult(
        safe_for_retrieval=True,
        sanitized_text=sanitized,
        replacements=replacements,
    )
