#!/usr/bin/env python3
"""Dedicated, deterministic Claude Code runtime adapter for the SDD loop."""
from __future__ import annotations
import json, os, subprocess, sys
from pathlib import Path

RESULT_KEYS = ("stage", "status", "message", "verdict", "evidence")
STATUSES = {"completed", "failed", "blocked", "needs_human"}
VERDICTS = {"passed", "approved", "rejected", "blocked", "needs_human"}
class RuntimeError_(ValueError): pass

def build_command(stage_contract: dict, root: Path) -> list[str]:
    if not isinstance(stage_contract, dict) or not stage_contract.get("stage"): raise RuntimeError_("stage contract requires stage")
    root = Path(root)
    payload = json.dumps(stage_contract, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return ["claude", "-p", payload, "--output-format", "json", "--add-dir", str(root)]

def validate_result(value: object) -> dict:
    if not isinstance(value, dict) or set(value) != set(RESULT_KEYS): raise RuntimeError_("invalid loop result schema")
    if not isinstance(value["stage"], str) or not value["stage"].strip(): raise RuntimeError_("invalid result stage")
    if value["status"] not in STATUSES: raise RuntimeError_("invalid result status")
    if not isinstance(value["message"], str) or not value["message"].strip(): raise RuntimeError_("invalid result message")
    if value["verdict"] not in VERDICTS: raise RuntimeError_("invalid result verdict")
    if not isinstance(value["evidence"], dict): raise RuntimeError_("invalid result evidence")
    return value

def parse_envelope(value: object) -> dict:
    """Decode Claude's closed native JSON result envelope."""
    allowed = {"type", "subtype", "is_error", "result", "duration_ms", "duration_api_ms", "num_turns", "session_id", "total_cost_usd"}
    if not isinstance(value, dict) or not {"type", "subtype", "is_error", "result"}.issubset(value) or set(value) - allowed:
        raise RuntimeError_("invalid Claude result envelope")
    if value["type"] != "result" or value["subtype"] != "success" or value["is_error"] is not False:
        raise RuntimeError_("Claude runtime reported an error")
    payload = value["result"]
    if isinstance(payload, str):
        try: payload = json.loads(payload)
        except (TypeError, ValueError) as exc: raise RuntimeError_("Claude result is not JSON") from exc
    return validate_result(payload)

def run(stage_contract: dict, root: Path, *, timeout: float = 300, executable: str | None = None) -> dict:
    command = build_command(stage_contract, Path(root))
    if executable: command[0] = executable
    env = {"PATH": os.environ.get("PATH", ""), "LC_ALL": "C", "LANG": "C"}
    try: completed = subprocess.run(command, cwd=str(root), env=env, text=True, capture_output=True, timeout=timeout, check=False)
    except subprocess.TimeoutExpired as exc: raise RuntimeError_("runtime timeout") from exc
    if completed.returncode != 0: raise RuntimeError_(f"runtime exited with status {completed.returncode}")
    try: value = json.loads(completed.stdout)
    except (TypeError, ValueError) as exc: raise RuntimeError_("runtime returned malformed JSON") from exc
    return parse_envelope(value)

if __name__ == "__main__":
    print(json.dumps({"error": "use the adapter API"}, sort_keys=True)); sys.exit(2)
