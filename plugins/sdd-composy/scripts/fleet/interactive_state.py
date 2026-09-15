#!/usr/bin/env python3
"""Validated, atomic state transitions for an interactive fleet member."""
from __future__ import annotations

import copy
import contextlib
import datetime as dt
import fcntl
import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any

STATES = {"starting", "running", "awaiting_human", "completed", "inconclusive", "blocked", "failed"}
TERMINAL = {"completed", "inconclusive", "blocked", "failed"}
TRANSITIONS = {
    "starting": {"running", "blocked", "failed"},
    "running": {"awaiting_human", "completed", "inconclusive", "blocked", "failed"},
    "awaiting_human": {"running", "completed", "inconclusive", "blocked", "failed"},
    "completed": set(), "inconclusive": set(), "blocked": set(), "failed": set(),
}
RFC3339 = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$")
TASK_ID = re.compile(r"^TASK-[0-9]{3,}$")
LOOP_ID = re.compile(r"^[A-Za-z][A-Za-z0-9._-]*$")
MEMBER_ID = LOOP_ID
SHA256 = re.compile(r"^[a-f0-9]{64}$")
MEMBER_STATUS = {"pending", "running", "completed", "failed", "blocked", "cancelled"}
RUNTIMES = {"claude-code", "codex", "hermes", "opencode"}
ACTOR = re.compile(r"^[A-Za-z][A-Za-z0-9._-]*:[A-Za-z0-9][A-Za-z0-9._-]*$")
TERMINAL_STATUS = {"completed", "failed", "blocked", "cancelled"}
UIS = {"cmux", "tmux", "headless"}


class InteractiveStateError(ValueError):
    pass


def _timestamp(value: Any) -> None:
    if not isinstance(value, str) or not RFC3339.fullmatch(value):
        raise InteractiveStateError("timestamp must be RFC3339")
    try:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise InteractiveStateError("timestamp must be valid") from exc
    if parsed.tzinfo is None:
        raise InteractiveStateError("timestamp must include timezone")


def _validate(member: Any) -> dict[str, Any]:
    if not isinstance(member, dict) or member.get("schema_version") != "2":
        raise InteractiveStateError("invalid fleet member")
    required = {"schema_version", "id", "task_id", "status", "runtime", "ui", "branch",
                "worktree_path", "repository_root", "started_at", "updated_at", "owner", "resources"}
    if not required.issubset(member):
        raise InteractiveStateError("fleet member is missing required fields")
    if not isinstance(member["id"], str) or not MEMBER_ID.fullmatch(member["id"]):
        raise InteractiveStateError("invalid member id")
    task_id = member.get("task_id")
    if not isinstance(task_id, str) or not TASK_ID.fullmatch(task_id):
        raise InteractiveStateError("invalid task_id")
    owner = member.get("owner")
    if (not isinstance(owner, dict) or set(owner) != {"kind", "fleet_id", "member_id"}
            or owner.get("kind") != "sdd-composy-fleet"
            or not isinstance(owner.get("fleet_id"), str) or not owner["fleet_id"]
            or owner.get("member_id") != member.get("id")):
        raise InteractiveStateError("invalid member owner")
    if (not isinstance(member["status"], str) or member["status"] not in MEMBER_STATUS
            or not isinstance(member["runtime"], str) or member["runtime"] not in RUNTIMES
            or not isinstance(member["ui"], str) or member["ui"] not in UIS):
        raise InteractiveStateError("invalid member status, runtime, or ui")
    if not isinstance(member["branch"], str) or not member["branch"]:
        raise InteractiveStateError("invalid member branch")
    for key in ("worktree_path", "repository_root"):
        if not isinstance(member[key], str) or len(member[key]) < 2 or not member[key].startswith("/"):
            raise InteractiveStateError(f"invalid {key}")
    _timestamp(member["started_at"]); _timestamp(member["updated_at"])
    resources = member["resources"]
    resource_keys = {"branch", "worktree_path", "port", "compose_project", "compose_file", "compose_allocated"}
    if not isinstance(resources, dict) or not resource_keys.issubset(resources):
        raise InteractiveStateError("invalid member resources")
    if (not isinstance(resources["branch"], str) or not resources["branch"]
            or not isinstance(resources["worktree_path"], str) or len(resources["worktree_path"]) < 2
            or not resources["worktree_path"].startswith("/")
            or isinstance(resources["port"], bool) or not isinstance(resources["port"], int)
            or not 1 <= resources["port"] <= 65535
            or not isinstance(resources["compose_project"], str) or not resources["compose_project"]
            or not _relative(resources["compose_file"])
            or not isinstance(resources["compose_allocated"], bool)):
        raise InteractiveStateError("invalid member resources")
    if "compose_sha256" in resources and (not isinstance(resources["compose_sha256"], str)
                                           or not SHA256.fullmatch(resources["compose_sha256"])):
        raise InteractiveStateError("invalid compose sha256")
    if resources["compose_allocated"] and "compose_sha256" not in resources:
        raise InteractiveStateError("allocated compose requires sha256")
    if member["status"] in {"completed", "failed", "blocked", "cancelled"}:
        if "finished_at" not in member or not _relative(member.get("result_path")):
            raise InteractiveStateError("terminal member is missing completion fields")
        _timestamp(member["finished_at"])
    elif "finished_at" in member:
        _timestamp(member["finished_at"])
    if "result_path" in member and not _relative(member["result_path"]):
        raise InteractiveStateError("invalid result_path")
    if "message" in member and (not isinstance(member["message"], str) or not member["message"]):
        raise InteractiveStateError("invalid message")
    approval = member.get("approval")
    if approval is not None:
        if (not isinstance(approval, dict) or not isinstance(approval.get("by"), str)
                or not ACTOR.fullmatch(approval["by"])):
            raise InteractiveStateError("invalid approval")
        _timestamp(approval.get("at"))
    if "commit" in member and member["commit"] is not None and (
            not isinstance(member["commit"], str) or not re.fullmatch(r"[0-9a-f]{40}", member["commit"])):
        raise InteractiveStateError("invalid commit")
    interaction = member.get("interaction")
    if not isinstance(interaction, dict):
        raise InteractiveStateError("interaction is required")
    if not isinstance(interaction.get("state"), str) or interaction["state"] not in STATES:
        raise InteractiveStateError("invalid interaction state")
    _timestamp(interaction.get("started_at")); _timestamp(interaction.get("updated_at"))
    loop = interaction.get("loop")
    if loop is not None:
        if (not isinstance(loop, dict) or set(loop) != {"id", "task_id"}
                or not isinstance(loop.get("id"), str) or not LOOP_ID.fullmatch(loop["id"])
                or loop.get("task_id") != task_id):
            raise InteractiveStateError("invalid loop binding")
    return member


def _relative(value: Any) -> bool:
    return (isinstance(value, str) and bool(value) and not value.startswith("/")
            and all(part != ".." for part in value.split("/")))


def _safe_path(path: Path) -> Path:
    path = Path(path).absolute()
    if path.is_symlink() or any(parent.is_symlink() for parent in path.parents) or not path.is_file():
        raise InteractiveStateError("member path must be a regular file")
    return path


@contextlib.contextmanager
def _locked_member(path: Path):
    path = _safe_path(path)
    lock_path = path.with_name(f".{path.name}.lock")
    if lock_path.is_symlink():
        raise InteractiveStateError("member lock must not be a symlink")
    flags = os.O_RDWR | os.O_CREAT
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(lock_path, flags, 0o600)
    except OSError as exc:
        raise InteractiveStateError(f"cannot open member lock: {exc}") from exc
    try:
        fcntl.flock(descriptor, fcntl.LOCK_EX)
        yield path, load_member(path)
    finally:
        fcntl.flock(descriptor, fcntl.LOCK_UN)
        os.close(descriptor)


def load_member(path: str | os.PathLike[str]) -> dict[str, Any]:
    path = _safe_path(Path(path))
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise InteractiveStateError(f"cannot load member: {exc}") from exc
    return _validate(value)


def _publish(path: Path, member: dict[str, Any]) -> dict[str, Any]:
    _validate(member)
    payload = (json.dumps(member, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(payload); stream.flush(); os.fsync(stream.fileno())
        os.replace(temporary, path)
    except BaseException:
        try: os.unlink(temporary)
        except FileNotFoundError: pass
        raise
    return member


def transition(path: str | os.PathLike[str], expected: str, target: str,
               patch: dict[str, Any], now: str) -> dict[str, Any]:
    with _locked_member(Path(path)) as (path, member):
        interaction = member["interaction"]
        if expected not in STATES or interaction["state"] != expected:
            raise InteractiveStateError("unexpected interaction state")
        if target not in TRANSITIONS[expected]:
            raise InteractiveStateError(f"invalid transition: {expected} -> {target}")
        if not isinstance(patch, dict):
            raise InteractiveStateError("patch must be an object")
        if {"state", "started_at", "updated_at", "loop"}.intersection(patch):
            raise InteractiveStateError("patch contains managed fields")
        _timestamp(now)
        updated = copy.deepcopy(member)
        updated["interaction"].update(copy.deepcopy(patch))
        updated["interaction"]["state"] = target
        updated["interaction"]["updated_at"] = now
        return _publish(path, updated)


def bind_loop(path: str | os.PathLike[str], loop_id: str, task_id: str, now: str) -> dict[str, Any]:
    with _locked_member(Path(path)) as (path, member):
        if task_id != member["task_id"]:
            raise InteractiveStateError("loop task does not match member task")
        if not isinstance(loop_id, str) or not LOOP_ID.fullmatch(loop_id):
            raise InteractiveStateError("invalid loop id")
        if "loop" in member["interaction"]:
            raise InteractiveStateError("member already has a loop binding")
        _timestamp(now)
        updated = copy.deepcopy(member)
        updated["interaction"]["loop"] = {"id": loop_id, "task_id": task_id}
        updated["interaction"]["updated_at"] = now
        return _publish(path, updated)


def finish(path: str | os.PathLike[str], status: str, *, result_path: str, message: str,
           commit: str | None, now: str) -> dict[str, Any]:
    """Publish a runner's terminal member status with its result evidence, exactly once."""
    with _locked_member(Path(path)) as (path, member):
        if status not in TERMINAL_STATUS:
            raise InteractiveStateError("finish requires a terminal status")
        if member["status"] not in {"pending", "running"}:
            raise InteractiveStateError("member is already terminal")
        _timestamp(now)
        updated = copy.deepcopy(member)
        updated.update(status=status, result_path=result_path, finished_at=now, updated_at=now,
                       message=message, commit=commit)
        return _publish(path, updated)
