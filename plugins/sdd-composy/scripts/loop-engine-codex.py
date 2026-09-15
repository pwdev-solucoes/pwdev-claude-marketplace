#!/usr/bin/env python3
"""Dedicated, deterministic Codex runtime adapter for the SDD loop."""
from __future__ import annotations
import json, sys, tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from loop_engine_common import (RESULT_KEYS, STATUSES, VERDICTS, RuntimeError_, loads_json, stage_prompt,  # noqa: E402,F401
                                require_stage, run_process, validate_result)

def build_command(stage_contract: dict, root: Path, result_path: Path | None = None) -> list[str]:
    require_stage(stage_contract)
    # Keep this vector literal and provider-specific; callers cannot inject flags.
    command = ["codex", "exec", "--json", "--sandbox", "workspace-write", "--cd", str(Path(root))]
    if result_path is not None:
        command.extend(("--output-last-message", str(result_path)))
    command.append(stage_prompt(stage_contract))
    return command

def run(stage_contract: dict, root: Path, *, timeout: float = 300, executable: str | None = None,
        loop_root: Path | None = None) -> dict:
    with tempfile.TemporaryDirectory(prefix="sdd-codex-result-") as directory:
        result_path = Path(directory) / "final.json"
        command = build_command(stage_contract, Path(root), result_path)
        if executable: command[0] = executable
        run_process(command, Path(root), timeout)
        try: text = result_path.read_text(encoding="utf-8")
        except OSError as exc: raise RuntimeError_("runtime returned malformed JSON") from exc
        value = loads_json(text)
    return validate_result(value, stage_contract["stage"], root=Path(root), loop_root=loop_root,
                           stage_contract=stage_contract)

if __name__ == "__main__":
    print(json.dumps({"error": "use the adapter API"}, sort_keys=True)); sys.exit(2)
