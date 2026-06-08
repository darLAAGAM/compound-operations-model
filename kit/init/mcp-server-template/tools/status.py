"""status tool — proxies to the operai_init status module."""
from __future__ import annotations
import sys
from pathlib import Path
from typing import Any

from config import OPERAI_HOME, BRAND_SLUG


async def run(*, principal) -> Any:
    # operai_init lives at /opt/operai/services/init/cli/operai_init
    cli_path = OPERAI_HOME / "services" / "init" / "cli"
    if str(cli_path) not in sys.path:
        sys.path.insert(0, str(cli_path))
    try:
        from operai_init import status as status_mod  # type: ignore
        return status_mod.build_report(OPERAI_HOME, BRAND_SLUG)
    except Exception as e:  # noqa: BLE001
        return {"error": f"status unavailable: {e}", "brand": BRAND_SLUG}
