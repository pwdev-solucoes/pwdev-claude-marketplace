"""Provider-neutral contract shared by every SDD LOOP runtime engine.

Each ``loop-engine-<runtime>.py`` owns only its command vector and how its CLI
reports the final message. Result validation, VERIFY command evidence, the
provider environment, consent, and process execution live here once, so the
engines cannot drift apart.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import subprocess
import time
from pathlib import Path

RESULT_KEYS = ("stage", "status", "message", "verdict", "evidence")
# Guard signals the orchestrator reads in correction_decision; engines must let them through.
OPTIONAL_RESULT_KEYS = frozenset({
    "destructive", "destructive_request", "scope_changed", "scope_drift", "architecture_changed",
    "new_architecture", "environment_failure", "environment", "diff", "failure",
})
STATUSES = {"completed", "failed", "blocked", "needs_human"}
VERDICTS = {"passed", "approved", "rejected", "blocked", "needs_human"}
DANGER_MODE = "danger-full-access"

ENV_NAMES = frozenset({
    "PATH", "HOME", "USER", "LOGNAME", "SHELL", "TMPDIR", "TERM", "LANG", "SSH_AUTH_SOCK",
    "HTTP_PROXY", "HTTPS_PROXY", "NO_PROXY", "http_proxy", "https_proxy", "no_proxy",
    "SSL_CERT_FILE", "SSL_CERT_DIR", "NODE_EXTRA_CA_CERTS",
})
ENV_PREFIXES = ("LC_", "XDG_", "ANTHROPIC_", "CLAUDE_", "OPENAI_", "CODEX_", "OPENCODE_", "HERMES_",
                "OPENROUTER_")


class RuntimeError_(ValueError):
    pass


def authorized(stage_contract: dict) -> bool:
    return stage_contract.get("isolation_confirmed") is True or stage_contract.get("automation_consent") is True


def elevated(stage_contract: dict) -> bool:
    """True when the contract asks for unrestricted permissions; fails closed without consent."""
    if stage_contract.get("permission_mode") != DANGER_MODE:
        return False
    if not authorized(stage_contract):
        raise RuntimeError_("unrestricted permissions require isolation or automation consent")
    return True


def require_stage(stage_contract: object) -> dict:
    if not isinstance(stage_contract, dict) or not isinstance(stage_contract.get("stage"), str) \
            or not stage_contract["stage"].strip():
        raise RuntimeError_("stage contract requires stage")
    return stage_contract


def payload(stage_contract: dict) -> str:
    return json.dumps(stage_contract, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def stage_prompt(stage_contract: dict) -> str:
    """The one instruction every provider receives: run this stage, answer in the result contract."""
    return ("Execute only this SDD LOOP stage contract and return exactly one JSON object "
            "with keys stage,status,message,verdict,evidence: " + payload(stage_contract))


def provider_env() -> dict:
    """Keep what a provider needs to authenticate and run; drop everything else."""
    return {key: value for key, value in os.environ.items()
            if key in ENV_NAMES or key.startswith(ENV_PREFIXES) or key.endswith("_API_KEY")}


def run_process(command: list, cwd: Path, timeout: float) -> str:
    try:
        completed = subprocess.run(command, cwd=str(cwd), env=provider_env(), text=True,
                                   capture_output=True, timeout=timeout, check=False)
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError_("runtime timeout") from exc
    except OSError as exc:
        raise RuntimeError_(f"runtime unavailable: {exc}") from exc
    if completed.returncode != 0:
        raise RuntimeError_(f"runtime exited with status {completed.returncode}")
    return completed.stdout


def loads_json(text: object) -> object:
    try:
        return json.loads(text)
    except (TypeError, ValueError) as exc:
        raise RuntimeError_("runtime returned malformed JSON") from exc


def verify_command_record(value: dict, loop_root: Path, stage_contract: dict, now: float | None) -> None:
    """A successful VERIFY must cite a real, hashed command record bound to the running LOOP."""
    try:
        task_id = stage_contract["task_id"]
        loops = loop_root / ".planning/sdd-composy/loops"
        if loop_root.is_symlink() or loops.is_symlink() or not loops.is_dir(): raise ValueError
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
        path = loop_root
        for part in relative.parts:
            path = path / part
            if path.is_symlink(): raise ValueError
        if not path.is_file(): raise ValueError
        raw = path.read_bytes()
        if hashlib.sha256(raw).hexdigest() != reference.get("sha256"): raise ValueError
        record = json.loads(raw)
        if record.get("task_id") != task_id or record.get("loop_id") != loop.get("id"): raise ValueError
        if record.get("status") != "passed" or type(record.get("exit_code")) is not int \
                or record["exit_code"] != 0 or not record.get("command"): raise ValueError
        stdout, stderr = record.get("stdout"), record.get("stderr")
        if not isinstance(stdout, str) or not isinstance(stderr, str) \
                or record.get("sha256") != hashlib.sha256((stdout + "\n" + stderr).encode()).hexdigest():
            raise ValueError
        started, ended = record.get("started_at"), record.get("ended_at")
        deadline = (time.time() if now is None else now) + 1
        if any(type(item) not in (int, float) for item in (started, ended)) \
                or not baseline <= started <= ended < deadline: raise ValueError
    except (KeyError, OSError, TypeError, ValueError, StopIteration, json.JSONDecodeError) as exc:
        raise RuntimeError_("successful VERIFY requires real command evidence") from exc


def validate_result(value: object, requested_stage: str | None = None, *, root: Path | None = None,
                    stage_contract: dict | None = None, now: float | None = None,
                    loop_root: Path | None = None) -> dict:
    if not isinstance(value, dict) or not set(RESULT_KEYS).issubset(value) \
            or not (set(value) - set(RESULT_KEYS)).issubset(OPTIONAL_RESULT_KEYS):
        raise RuntimeError_("invalid loop result schema")
    if not isinstance(value["stage"], str) or not value["stage"].strip(): raise RuntimeError_("invalid result stage")
    if value["status"] not in STATUSES: raise RuntimeError_("invalid result status")
    if not isinstance(value["message"], str) or not value["message"].strip(): raise RuntimeError_("invalid result message")
    if value["verdict"] not in VERDICTS: raise RuntimeError_("invalid result verdict")
    if not isinstance(value["evidence"], dict): raise RuntimeError_("invalid result evidence")
    if requested_stage is not None and value["stage"] != requested_stage:
        raise RuntimeError_("result does not match requested stage")
    if value["stage"] == "VERIFY" and value["status"] == "completed":
        record_root = loop_root if loop_root is not None else root
        if record_root is None or stage_contract is None:
            raise RuntimeError_("successful VERIFY requires real command evidence")
        verify_command_record(value, Path(record_root), stage_contract, now)
    return value


def strip_fence(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = stripped.split("\n", 1)[1] if "\n" in stripped else ""
        if stripped.rstrip().endswith("```"):
            stripped = stripped.rstrip()[:-3]
    return stripped.strip()
