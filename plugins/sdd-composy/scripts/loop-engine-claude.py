#!/usr/bin/env python3
"""Dedicated, deterministic Claude Code runtime adapter for the SDD loop."""
from __future__ import annotations
import json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from loop_engine_common import (RESULT_KEYS, STATUSES, VERDICTS, RuntimeError_, elevated, loads_json,  # noqa: E402,F401
                                require_stage, run_process, stage_prompt, strip_fence, validate_result)

CORE_ENVELOPE_KEYS = {"type", "subtype", "is_error", "result"}

def build_command(stage_contract: dict, root: Path) -> list[str]:
    require_stage(stage_contract)
    # Headless `claude -p` denies tools that need a prompt: safe mode may edit inside the
    # added directory; only a consented, isolated contract skips permissions entirely.
    permission = ["--dangerously-skip-permissions"] if elevated(stage_contract) else ["--permission-mode", "acceptEdits"]
    return ["claude", "-p", stage_prompt(stage_contract), "--output-format", "json", "--no-session-persistence",
            *permission, "--add-dir", str(Path(root))]

def parse_envelope(value: object) -> dict:
    """Decode Claude's JSON result envelope; its telemetry keys vary by version and are ignored."""
    if not isinstance(value, dict) or not CORE_ENVELOPE_KEYS.issubset(value):
        raise RuntimeError_("invalid Claude result envelope")
    if value["type"] != "result" or value["subtype"] != "success" or value["is_error"] is not False:
        raise RuntimeError_("Claude runtime reported an error")
    result = value["result"]
    if isinstance(result, str):
        try: result = json.loads(strip_fence(result))
        except (TypeError, ValueError) as exc: raise RuntimeError_("Claude result is not JSON") from exc
    return validate_result(result)

def run(stage_contract: dict, root: Path, *, timeout: float = 300, executable: str | None = None,
        loop_root: Path | None = None) -> dict:
    command = build_command(stage_contract, Path(root))
    if executable: command[0] = executable
    value = parse_envelope(loads_json(run_process(command, Path(root), timeout)))
    return validate_result(value, stage_contract["stage"], root=Path(root), loop_root=loop_root,
                           stage_contract=stage_contract)

if __name__ == "__main__":
    print(json.dumps({"error": "use the adapter API"}, sort_keys=True)); sys.exit(2)
