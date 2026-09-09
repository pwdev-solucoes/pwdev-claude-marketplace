#!/usr/bin/env python3
"""Hermes runtime adapter for the SDD loop."""
from __future__ import annotations
import json, os, subprocess, sys
from pathlib import Path

RESULT_KEYS = ("stage", "status", "message", "verdict", "evidence")
STATUSES = {"completed", "failed", "blocked", "needs_human"}
VERDICTS = {"passed", "approved", "rejected", "blocked", "needs_human"}

class RuntimeError_(ValueError): pass

def _authorized(stage_contract: dict) -> bool:
    return stage_contract.get("isolation_confirmed") is True or stage_contract.get("automation_consent") is True

def build_command(stage_contract: dict, root: Path) -> list[str]:
    if not isinstance(stage_contract, dict) or not isinstance(stage_contract.get("stage"), str) or not stage_contract["stage"].strip():
        raise RuntimeError_("stage contract requires stage")
    if not _authorized(stage_contract):
        raise RuntimeError_("Hermes automation requires isolation or automation consent")
    payload = json.dumps(stage_contract, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    prompt = ("Execute only this SDD LOOP stage contract and return exactly one JSON object "
              "with keys stage,status,message,verdict,evidence: " + payload)
    return ["hermes", "-z", prompt, "--in", str(Path(root))]

def validate_result(value: object, requested_stage: str | None = None) -> dict:
    if not isinstance(value, dict) or set(value) != set(RESULT_KEYS):
        raise RuntimeError_("invalid loop result schema")
    if not isinstance(value["stage"], str) or not value["stage"].strip(): raise RuntimeError_("invalid result stage")
    if value["status"] not in STATUSES: raise RuntimeError_("invalid result status")
    if not isinstance(value["message"], str) or not value["message"].strip(): raise RuntimeError_("invalid result message")
    if value["verdict"] not in VERDICTS: raise RuntimeError_("invalid result verdict")
    if not isinstance(value["evidence"], dict): raise RuntimeError_("invalid result evidence")
    if requested_stage is not None and value["stage"] != requested_stage:
        raise RuntimeError_("result does not match requested stage")
    if value["stage"] == "verify" and value["status"] == "completed":
        record = value["evidence"].get("command_record")
        if not isinstance(record, dict) or record.get("exit_code") != 0 or record.get("status") not in {"passed", "success"} or not isinstance(record.get("command"), list) or not record["command"]:
            raise RuntimeError_("successful VERIFY requires real command evidence")
    return value

def run(stage_contract: dict, root: Path, *, timeout: float = 300, executable: str | None = None) -> dict:
    command = build_command(stage_contract, Path(root))
    if executable: command[0] = executable
    env = {"PATH": os.environ.get("PATH", ""), "LC_ALL": "C", "LANG": "C"}
    try:
        completed = subprocess.run(command, cwd=str(root), env=env, text=True, capture_output=True, timeout=timeout, check=False)
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError_("runtime timeout") from exc
    except OSError as exc:
        raise RuntimeError_(f"runtime unavailable: {exc}") from exc
    if completed.returncode != 0: raise RuntimeError_(f"runtime exited with status {completed.returncode}")
    try: value = json.loads(completed.stdout)
    except (TypeError, ValueError) as exc: raise RuntimeError_("runtime returned malformed JSON") from exc
    return validate_result(value, stage_contract["stage"])

if __name__ == "__main__":
    print(json.dumps({"error": "use the adapter API"}, sort_keys=True)); sys.exit(2)
