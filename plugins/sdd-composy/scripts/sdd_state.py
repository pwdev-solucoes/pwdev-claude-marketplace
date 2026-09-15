#!/usr/bin/env python3
"""Keep `.planning/sdd-composy/state.json` current after INIT.

The mutating CLIs (tasks, loop, trace, fleet) call these helpers after their own durable
write succeeds. An uninitialized repository has no state.json and is left untouched; an
invalid state.json fails closed rather than being repaired.
"""
from __future__ import annotations

import datetime as dt
import fcntl
import json
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Callable

from sdd_init import _atomic_json, _valid_state

TASK_STAGE = {"pending": "TASKS", "ready": "TASKS", "running": "EXECUTE", "qa_required": "QA",
              "evidence_required": "EVIDENCE", "review_required": "REVIEW", "verify_required": "VERIFY",
              "complete": "COMPLETE"}
TASK_NEXT = {"pending": "approve {id} and transition it to ready", "ready": "run sdd-execute on {id}",
             "running": "finish sdd-execute on {id} and request qa_required", "qa_required": "run sdd-qa on {id}",
             "evidence_required": "run sdd-evidence on {id}", "review_required": "run sdd-review on {id}",
             "verify_required": "run sdd-verify on {id}", "complete": "select the next ready task",
             "blocked": "resolve the blocker on {id}, then transition it to ready",
             "rejected": "approve the correction scope for {id}, then transition it to ready",
             "skipped": "select the next ready task"}


class StateError(ValueError):
    pass


def repository_root(path: Path | str) -> Path | None:
    """The repository that owns an operational file below `.planning/sdd-composy/`."""
    resolved = Path(path).absolute()
    for parent in resolved.parents:
        if parent.name == "sdd-composy" and parent.parent.name == ".planning":
            return parent.parent.parent
    return None


def _path(root: Path | str) -> Path:
    base = Path(root)
    for part in (base / ".planning", base / ".planning/sdd-composy"):
        if part.is_symlink(): raise StateError("operational root must not be a symlink")
    path = base / ".planning/sdd-composy/state.json"
    if path.is_symlink(): raise StateError("state.json must not be a symlink")
    return path


@contextmanager
def _locked(path: Path):
    with open(path.parent / ".state.lock", "a+") as handle:
        fcntl.flock(handle, fcntl.LOCK_EX)
        try: yield
        finally: fcntl.flock(handle, fcntl.LOCK_UN)


def _now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def update(root: Path | str | None, change: Callable[[dict[str, Any]], None]) -> dict[str, Any] | None:
    if root is None: return None
    path = _path(root)
    if not path.exists(): return None
    with _locked(path):
        try: state = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc: raise StateError("state.json is unreadable; repair it explicitly") from exc
        if not _valid_state(state): raise StateError("state.json is invalid; repair it explicitly")
        change(state)
        state["revision"] += 1
        state["updated_at"] = _now()
        if not _valid_state(state): raise StateError("state update would publish an invalid state")
        _atomic_json(path, state)
    return state


def _upsert(items: list[dict[str, Any]], entry: dict[str, Any]) -> None:
    for index, item in enumerate(items):
        if item.get("id") == entry["id"]:
            items[index] = entry
            return
    items.append(entry)


def task_changed(root: Path | str | None, prd_slug: str, task: dict[str, Any]) -> dict[str, Any] | None:
    def change(state: dict[str, Any]) -> None:
        task_id, current = task["id"], task["state"]
        state["active_prd"], state["active_task"] = prd_slug, task_id
        if current in TASK_STAGE: state["stage"] = TASK_STAGE[current]
        state["blockers"] = [item for item in state["blockers"] if item.get("id") != task_id]
        if current in {"blocked", "rejected"}:
            reason = task.get("blocked_reason") if current == "blocked" else task.get("rejection_reason")
            state["blockers"].append({"id": task_id, "status": current, "reason": reason or current})
        state["next_action"] = TASK_NEXT[current].format(id=task_id)
    return update(root, change)


def loop_changed(root: Path | str | None, record: dict[str, Any]) -> dict[str, Any] | None:
    def change(state: dict[str, Any]) -> None:
        _upsert(state["loops"], {"id": record["id"], "status": record["status"], "task_id": record["task_id"]})
    return update(root, change)


def trace_changed(root: Path | str | None, report: dict[str, Any]) -> dict[str, Any] | None:
    def change(state: dict[str, Any]) -> None:
        state["trace"] = {"healthy": bool(report.get("ok")), "source_event_count": int(report.get("source_event_count", 0))}
    return update(root, change)


def fleet_changed(root: Path | str | None, member_id: str, status: str, **details: Any) -> dict[str, Any] | None:
    def change(state: dict[str, Any]) -> None:
        _upsert(state["fleet"], {"id": member_id, "status": status, **details})
    return update(root, change)
