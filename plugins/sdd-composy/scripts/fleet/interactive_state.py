#!/usr/bin/env python3
"""Validated, atomic state transitions for an interactive fleet member."""
from __future__ import annotations

import copy
import datetime as dt
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
    task_id = member.get("task_id")
    if not isinstance(task_id, str) or not TASK_ID.fullmatch(task_id):
        raise InteractiveStateError("invalid task_id")
    owner = member.get("owner")
    if (not isinstance(owner, dict) or owner.get("kind") != "sdd-composy-fleet"
            or owner.get("member_id") != member.get("id")):
        raise InteractiveStateError("invalid member owner")
    interaction = member.get("interaction")
    if not isinstance(interaction, dict):
        raise InteractiveStateError("interaction is required")
    if interaction.get("state") not in STATES:
        raise InteractiveStateError("invalid interaction state")
    _timestamp(interaction.get("started_at")); _timestamp(interaction.get("updated_at"))
    loop = interaction.get("loop")
    if loop is not None:
        if (not isinstance(loop, dict) or set(loop) != {"id", "task_id"}
                or not isinstance(loop.get("id"), str) or not LOOP_ID.fullmatch(loop["id"])
                or loop.get("task_id") != task_id):
            raise InteractiveStateError("invalid loop binding")
    return member


def _safe_path(path: Path) -> Path:
    path = Path(path)
    # The state directory itself must be concrete. System-level aliases such as
    # macOS /var -> /private/var are outside this member publication boundary.
    if path.is_symlink() or path.parent.is_symlink() or not path.is_file():
        raise InteractiveStateError("member path must be a regular file")
    return path


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
    path = Path(path); member = load_member(path); interaction = member["interaction"]
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
    path = Path(path); member = load_member(path)
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
