#!/usr/bin/env python3
"""Portable semantic audit trail for PWDEV Flow."""

from __future__ import annotations

import argparse
import json
import os
import re
import stat
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 1
CONFIG_PATH = Path(".planning/flow/config.json")
EVENTS_PATH = Path(".planning/flow/audit/events.jsonl")
ALLOWED_ACTIONS = {
    "started",
    "completed",
    "failed",
    "gate_approved",
    "gate_rejected",
    "artifact_written",
    "decision_recorded",
    "memory_captured",
    "memory_superseded",
    "simplify_proposed",
    "simplify_applied",
    "archived",
    "migrated",
    "fleet_launched",
    "fleet_stage",
    "fleet_teardown",
    "external_run",
}
SECRET_KEY_RE = re.compile(
    r"(?:^|_)(?:secret|token|password|credential|private_key|api_key)(?:$|_)",
    re.IGNORECASE,
)
MODEL_PROMPT_KEY_RE = re.compile(r"model|prompt", re.IGNORECASE)
SECRET_TARGET_RE = re.compile(
    r"(?:^|/)(?:\.env(?:\.[^/]*)?|credentials?[^/]*|id_rsa[^/]*)$|\.(?:pem|key)$",
    re.IGNORECASE,
)
SKILL_RE = re.compile(r"^flow-[a-z0-9-]+$")


class AuditError(Exception):
    """Expected audit validation failure."""


def safe_directory(root: Path, relative: Path, *, create: bool) -> Path:
    current = root
    for part in relative.parts:
        if part in ("", ".", ".."):
            raise AuditError("Audit path contains an unsafe component")
        candidate = current / part
        try:
            metadata = os.lstat(candidate)
        except FileNotFoundError:
            if not create:
                raise AuditError("Audit directory does not exist")
            os.mkdir(candidate, 0o700)
            metadata = os.lstat(candidate)
        if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISDIR(metadata.st_mode):
            raise AuditError("Audit path contains a symlink or non-directory component")
        resolved = candidate.resolve(strict=True)
        try:
            resolved.relative_to(root)
        except ValueError as error:
            raise AuditError("Audit path escapes the repository root") from error
        current = resolved
    return current


def safe_regular_file(root: Path, relative: Path) -> Path:
    parent = safe_directory(root, relative.parent, create=False)
    path = parent / relative.name
    try:
        metadata = os.lstat(path)
    except FileNotFoundError as error:
        raise AuditError("Audit file does not exist") from error
    if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISREG(metadata.st_mode):
        raise AuditError("Audit file must be a regular non-symlink file")
    return path


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def emit(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))


def load_config(root: Path) -> dict[str, Any]:
    path = root / CONFIG_PATH
    if not path.exists() and not path.is_symlink():
        return {}
    path = safe_regular_file(root, CONFIG_PATH)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise AuditError("Flow audit config must be valid JSON") from error
    if not isinstance(payload, dict):
        raise AuditError("Flow audit config must contain a JSON object")
    return payload


def contains_secret_key(value: Any) -> bool:
    if isinstance(value, dict):
        return any(
            SECRET_KEY_RE.search(str(key)) is not None
            or MODEL_PROMPT_KEY_RE.search(str(key)) is not None
            or contains_secret_key(item)
            for key, item in value.items()
        )
    if isinstance(value, list):
        return any(contains_secret_key(item) for item in value)
    return False


def parse_detail(raw_detail: str) -> dict[str, Any]:
    try:
        detail = json.loads(raw_detail)
    except json.JSONDecodeError as error:
        raise AuditError("Audit detail must be valid JSON") from error
    if not isinstance(detail, dict):
        raise AuditError("Audit detail must be a JSON object")
    if contains_secret_key(detail):
        raise AuditError("Audit detail contains a prohibited secret-like key")
    return detail


def validate_event(event: Any, line_number: int) -> list[str]:
    prefix = f"line {line_number}"
    if not isinstance(event, dict):
        return [f"{prefix}: event must be an object"]

    errors: list[str] = []
    if event.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"{prefix}: unsupported schema_version")
    if not isinstance(event.get("timestamp"), str) or not event["timestamp"]:
        errors.append(f"{prefix}: timestamp must be a non-empty string")
    if event.get("action") not in ALLOWED_ACTIONS:
        errors.append(f"{prefix}: unknown action")
    if not isinstance(event.get("skill"), str) or SKILL_RE.fullmatch(event["skill"]) is None:
        errors.append(f"{prefix}: invalid skill")
    detail = event.get("detail", {})
    if not isinstance(detail, dict):
        errors.append(f"{prefix}: detail must be an object")
    elif contains_secret_key(detail):
        errors.append(f"{prefix}: detail contains a prohibited secret-like key")
    target = event.get("target")
    if target is not None and (
        not isinstance(target, str) or SECRET_TARGET_RE.search(target) is not None
    ):
        errors.append(f"{prefix}: invalid or secret-like target")
    return errors


def read_events(root: Path) -> tuple[list[dict[str, Any]], list[str]]:
    path = root / EVENTS_PATH
    if not path.exists() and not path.is_symlink():
        return [], []
    path = safe_regular_file(root, EVENTS_PATH)

    events: list[dict[str, Any]] = []
    errors: list[str] = []
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw_line.strip():
            continue
        try:
            event = json.loads(raw_line)
        except json.JSONDecodeError:
            errors.append(f"line {line_number}: invalid JSON")
            continue
        event_errors = validate_event(event, line_number)
        errors.extend(event_errors)
        if not event_errors:
            events.append(event)
    return events, errors


def append_event(root: Path, event: dict[str, Any]) -> None:
    parent = safe_directory(root, EVENTS_PATH.parent, create=True)
    path = parent / EVENTS_PATH.name
    if path.exists() or path.is_symlink():
        safe_regular_file(root, EVENTS_PATH)
    encoded = (json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8")
    flags = os.O_APPEND | os.O_CREAT | os.O_WRONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags, 0o600)
    except OSError as error:
        raise AuditError("Audit event file could not be opened safely") from error
    try:
        if not stat.S_ISREG(os.fstat(descriptor).st_mode):
            raise AuditError("Audit event destination is not a regular file")
        os.write(descriptor, encoded)
    finally:
        os.close(descriptor)


def record(root: Path, arguments: argparse.Namespace) -> int:
    config = load_config(root)
    if config.get("audit") is not True:
        emit({"reason": "audit_disabled", "recorded": False})
        return 0
    if arguments.action not in ALLOWED_ACTIONS:
        raise AuditError("Unknown audit action")
    if SKILL_RE.fullmatch(arguments.skill) is None:
        raise AuditError("Audit skill must be a flow-* identifier")
    if arguments.target and SECRET_TARGET_RE.search(arguments.target):
        raise AuditError("Audit target is secret-like and cannot be recorded")

    event: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "timestamp": utc_timestamp(),
        "action": arguments.action,
        "skill": arguments.skill,
        "detail": parse_detail(arguments.detail),
    }
    for field in ("phase", "status", "target"):
        value = getattr(arguments, field)
        if value:
            event[field] = value

    errors = validate_event(event, 1)
    if errors:
        raise AuditError(errors[0].split(": ", 1)[-1])
    append_event(root, event)
    emit({"event": event, "recorded": True})
    return 0


def require_valid_events(root: Path) -> list[dict[str, Any]]:
    events, errors = read_events(root)
    if errors:
        raise AuditError("Audit log failed integrity validation")
    return events


def summary(root: Path) -> int:
    events = require_valid_events(root)
    actions = Counter(event["action"] for event in events)
    skills = Counter(event["skill"] for event in events)
    phases = Counter(event["phase"] for event in events if event.get("phase"))
    emit(
        {
            "actions": dict(sorted(actions.items())),
            "first_timestamp": events[0]["timestamp"] if events else None,
            "last_timestamp": events[-1]["timestamp"] if events else None,
            "phases": dict(sorted(phases.items())),
            "skills": dict(sorted(skills.items())),
            "total": len(events),
        }
    )
    return 0


def list_events(root: Path, arguments: argparse.Namespace) -> int:
    events = require_valid_events(root)
    if arguments.action:
        events = [event for event in events if event["action"] == arguments.action]
    emit({"events": events[-arguments.limit :]})
    return 0


def verify(root: Path) -> int:
    events, errors = read_events(root)
    emit({"errors": errors, "total": len(events), "valid": not errors})
    return 0 if not errors else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="PWDEV Flow semantic audit helper")
    parser.add_argument("--root", required=True, help="Repository root")
    subparsers = parser.add_subparsers(dest="command", required=True)

    record_parser = subparsers.add_parser("record")
    record_parser.add_argument("--action", required=True)
    record_parser.add_argument("--skill", required=True)
    record_parser.add_argument("--phase", default="")
    record_parser.add_argument("--status", default="")
    record_parser.add_argument("--target", default="")
    record_parser.add_argument("--detail", default="{}")

    subparsers.add_parser("summary")
    events_parser = subparsers.add_parser("events")
    events_parser.add_argument("--limit", type=int, default=50)
    events_parser.add_argument("--action", choices=sorted(ALLOWED_ACTIONS))
    subparsers.add_parser("verify")
    return parser


def main() -> int:
    arguments = build_parser().parse_args()
    root = Path(arguments.root).expanduser().resolve()
    if not root.is_dir():
        emit({"error": "repository_root_not_found"})
        return 2
    try:
        if arguments.command == "record":
            return record(root, arguments)
        if arguments.command == "summary":
            return summary(root)
        if arguments.command == "events":
            if arguments.limit < 1:
                raise AuditError("Event limit must be positive")
            return list_events(root, arguments)
        return verify(root)
    except AuditError as error:
        emit({"error": str(error)})
        return 2


if __name__ == "__main__":
    sys.exit(main())
