#!/usr/bin/env python3
"""Hermes runtime adapter for the SDD loop."""
from __future__ import annotations
import datetime as dt, hashlib, json, os, subprocess, sys, time
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

def _verify_command_record(value: dict, root: Path, stage_contract: dict, now: float | None) -> None:
    try:
        task_id = stage_contract["task_id"]
        loops = root / ".planning/sdd-composy/loops"
        if root.is_symlink() or loops.is_symlink() or not loops.is_dir(): raise ValueError
        matches = []
        for path in loops.iterdir():
            if path.is_symlink() or not path.is_file(): continue
            loop = json.loads(path.read_text(encoding="utf-8"))
            if loop.get("task_id") == task_id and loop.get("status") == "running": matches.append(loop)
        if len(matches) != 1: raise ValueError
        loop = matches[0]
        review = next(item for item in loop.get("stages", ()) if item.get("name") == "REVIEW")
        baseline = dt.datetime.fromisoformat(review["published_at"].replace("Z", "+00:00")).timestamp()
        reference = value["evidence"]["command_record"]
        relative = Path(reference["path"])
        if not relative.parts or relative.is_absolute() or ".." in relative.parts: raise ValueError
        path = root
        for part in relative.parts:
            path = path / part
            if path.is_symlink(): raise ValueError
        if not path.is_file(): raise ValueError
        raw = path.read_bytes()
        if hashlib.sha256(raw).hexdigest() != reference.get("sha256"): raise ValueError
        record = json.loads(raw)
        if record.get("task_id") != task_id or record.get("loop_id") != loop.get("id"): raise ValueError
        if record.get("status") != "passed" or type(record.get("exit_code")) is not int or record["exit_code"] != 0 or not record.get("command"): raise ValueError
        stdout, stderr = record.get("stdout"), record.get("stderr")
        if not isinstance(stdout, str) or not isinstance(stderr, str) or record.get("sha256") != hashlib.sha256((stdout + "\n" + stderr).encode()).hexdigest(): raise ValueError
        started, ended = record.get("started_at"), record.get("ended_at")
        deadline = (time.time() if now is None else now) + 1
        if any(type(item) not in (int, float) for item in (started, ended)) or not baseline <= started <= ended < deadline: raise ValueError
    except (KeyError, OSError, TypeError, ValueError, StopIteration, json.JSONDecodeError) as exc:
        raise RuntimeError_("successful VERIFY requires real command evidence") from exc

def validate_result(value: object, requested_stage: str | None = None, *, root: Path | None = None,
                    stage_contract: dict | None = None, now: float | None = None) -> dict:
    if not isinstance(value, dict) or set(value) != set(RESULT_KEYS):
        raise RuntimeError_("invalid loop result schema")
    if not isinstance(value["stage"], str) or not value["stage"].strip(): raise RuntimeError_("invalid result stage")
    if value["status"] not in STATUSES: raise RuntimeError_("invalid result status")
    if not isinstance(value["message"], str) or not value["message"].strip(): raise RuntimeError_("invalid result message")
    if value["verdict"] not in VERDICTS: raise RuntimeError_("invalid result verdict")
    if not isinstance(value["evidence"], dict): raise RuntimeError_("invalid result evidence")
    if requested_stage is not None and value["stage"] != requested_stage:
        raise RuntimeError_("result does not match requested stage")
    if value["stage"] == "VERIFY" and value["status"] == "completed":
        if root is None or stage_contract is None: raise RuntimeError_("successful VERIFY requires real command evidence")
        _verify_command_record(value, Path(root), stage_contract, now)
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
    return validate_result(value, stage_contract["stage"], root=Path(root), stage_contract=stage_contract)

if __name__ == "__main__":
    print(json.dumps({"error": "use the adapter API"}, sort_keys=True)); sys.exit(2)
