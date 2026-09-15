#!/usr/bin/env python3
"""Dedicated, deterministic OpenCode runtime adapter for the SDD loop."""
from __future__ import annotations
import json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from loop_engine_common import (RESULT_KEYS, STATUSES, VERDICTS, RuntimeError_, authorized, elevated,  # noqa: E402,F401
                                require_stage, run_process, stage_prompt, strip_fence, validate_result)

def build_command(stage_contract: dict, root: Path) -> list[str]:
    require_stage(stage_contract)
    if not authorized(stage_contract):
        raise RuntimeError_("OpenCode automation requires isolation or automation consent")
    prompt = stage_prompt(stage_contract)
    # `--auto` approves every permission request; safe mode lets OpenCode reject them.
    auto = ["--auto"] if elevated(stage_contract) else []
    return ["opencode", "run", "--dir", str(Path(root)), "--format", "json", *auto, prompt]

def parse_envelope(text: str) -> dict:
    """Decode `opencode run --format json`: NDJSON events whose text lives in `part.text`.

    The result is the last text part that is a JSON object; the joined text parts are the
    fallback for a JSON object split across parts. Anything else fails closed.
    """
    parts = []
    for line in text.splitlines():
        if not line.strip(): continue
        try: event = json.loads(line)
        except (TypeError, ValueError) as exc: raise RuntimeError_("runtime returned malformed JSON") from exc
        if not isinstance(event, dict): raise RuntimeError_("invalid OpenCode result events")
        part = event.get("part")
        if event.get("type") == "text" and isinstance(part, dict) and isinstance(part.get("text"), str):
            parts.append(part["text"])
    if not parts: raise RuntimeError_("OpenCode result carries no text part")
    for candidate in (parts[-1], "".join(parts)):
        try: value = json.loads(strip_fence(candidate))
        except (TypeError, ValueError): continue
        if isinstance(value, dict): return value
    raise RuntimeError_("OpenCode result is not JSON")

def run(stage_contract: dict, root: Path, *, timeout: float = 300, executable: str | None = None,
        loop_root: Path | None = None) -> dict:
    command = build_command(stage_contract, Path(root))
    if executable: command[0] = executable
    value = parse_envelope(run_process(command, Path(root), timeout))
    return validate_result(value, stage_contract["stage"], root=Path(root), loop_root=loop_root,
                           stage_contract=stage_contract)

if __name__ == "__main__":
    print(json.dumps({"error": "use the adapter API"}, sort_keys=True)); sys.exit(2)
