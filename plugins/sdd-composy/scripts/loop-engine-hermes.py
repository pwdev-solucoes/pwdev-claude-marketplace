#!/usr/bin/env python3
"""Hermes runtime adapter for the SDD loop."""
from __future__ import annotations
import json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from loop_engine_common import (RESULT_KEYS, STATUSES, VERDICTS, RuntimeError_, authorized, loads_json,  # noqa: E402,F401
                                require_stage, stage_prompt, run_process, validate_result)

def build_command(stage_contract: dict, root: Path) -> list[str]:
    require_stage(stage_contract)
    if not authorized(stage_contract):
        raise RuntimeError_("Hermes automation requires isolation or automation consent")
    prompt = stage_prompt(stage_contract)
    return ["hermes", "-z", prompt, "--in", str(Path(root))]

def run(stage_contract: dict, root: Path, *, timeout: float = 300, executable: str | None = None,
        loop_root: Path | None = None) -> dict:
    command = build_command(stage_contract, Path(root))
    if executable: command[0] = executable
    value = loads_json(run_process(command, Path(root), timeout))
    return validate_result(value, stage_contract["stage"], root=Path(root), loop_root=loop_root,
                           stage_contract=stage_contract)

if __name__ == "__main__":
    print(json.dumps({"error": "use the adapter API"}, sort_keys=True)); sys.exit(2)
