"""Google Workspace connector — Service account JSON flow.

For server-side agents, a service account with domain-wide delegation is the
correct pattern. Subject impersonation lets the agent act as a specific user
(e.g. aurelio@brand.com for all agent-initiated Gmail/Drive/Calendar ops).
"""
from __future__ import annotations
import json
import os
from pathlib import Path

from operai_init import common


REQUIRED_SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/documents",
]


def _validate_json(raw: str) -> tuple[bool, dict | str]:
    try:
        obj = json.loads(raw)
    except json.JSONDecodeError as e:
        return False, f"invalid JSON: {e}"
    required = ["type", "client_email", "private_key", "project_id"]
    missing = [k for k in required if k not in obj]
    if missing:
        return False, f"missing keys: {missing}"
    if obj["type"] != "service_account":
        return False, f"expected type='service_account', got '{obj['type']}'"
    return True, obj


def connect(*, home: Path, brand: str) -> None:
    common.info("Google Workspace Service Account setup (10 min)")
    print("""
    1. Open Google Cloud Console → IAM & Admin → Service Accounts
    2. Create service account — name it "operai-swarm"
    3. Enable APIs: Gmail, Drive, Sheets, Calendar, Docs
    4. Create JSON key → download
    5. In Workspace Admin → Security → API controls → Domain-wide delegation:
       Add the service account's Client ID with these scopes:
""")
    for s in REQUIRED_SCOPES:
        print(f"       {s}")
    print("""
    6. Decide which user the agents will impersonate (e.g. operai@yourbrand.com)
""")

    path_in = common.prompt("Path to service account JSON file (or 'paste' to paste inline)")
    if path_in.lower() == "paste":
        print("  Paste the JSON, then press Enter + Ctrl-D:")
        lines: list[str] = []
        try:
            while True:
                lines.append(input())
        except EOFError:
            pass
        raw = "\n".join(lines)
    else:
        p = Path(os.path.expanduser(path_in))
        if not p.exists():
            common.err(f"{p} not found")
            return
        raw = p.read_text()

    ok, parsed = _validate_json(raw)
    if not ok:
        common.err(str(parsed))
        return
    assert isinstance(parsed, dict)

    common.ok(f"Service account: {parsed['client_email']} (project {parsed['project_id']})")

    subject = common.prompt("Email of the user to impersonate (e.g. operai@yourbrand.com)")
    if not subject or "@" not in subject:
        common.warn("No subject provided — agents will only act as the service account itself (limited Gmail/Drive access)")
        subject = ""

    cred_dir = common.credential_path(home, "google-workspace").parent
    sa_path = cred_dir / "google-workspace-sa.json"
    sa_path.write_text(json.dumps(parsed, indent=2))
    os.chmod(sa_path, 0o600)

    saved_path = common.save_credential(home, "google-workspace", {
        "service_account_path": str(sa_path),
        "client_email": parsed["client_email"],
        "project_id":   parsed["project_id"],
        "subject":      subject,
        "scopes":       REQUIRED_SCOPES,
    }, brand=brand)
    common.ok(f"credentials saved to {saved_path}")
    common.info(f"service account key stored at {sa_path}")
