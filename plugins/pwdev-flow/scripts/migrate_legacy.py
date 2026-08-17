#!/usr/bin/env python3
"""Plan or apply a non-destructive PWDEV Code configuration migration."""

from __future__ import annotations

import argparse
import json
import re
import sys
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SOURCE_PATH = Path(".planning/config.json")
TARGET_PATH = Path(".planning/flow/config.json")
SAFE_LEGACY_FIELDS = ("default_intensity", "branch_strategy", "commit_convention")
CONSUMED_FIELDS = {"lang", "audit", "type", "framework", "version"}
SECRET_KEY_RE = re.compile(
    r"(?:^|_)(?:secret|token|password|credential|private_key|api_key)(?:$|_)",
    re.IGNORECASE,
)


class MigrationError(Exception):
    """Expected migration validation failure."""


def emit(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))


def load_legacy(root: Path) -> dict[str, Any]:
    path = root / SOURCE_PATH
    if not path.is_file():
        raise MigrationError("Legacy config was not found")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise MigrationError("Legacy config must be valid JSON") from error
    if not isinstance(payload, dict):
        raise MigrationError("Legacy config must contain a JSON object")
    return payload


def safe_string(value: Any) -> str | None:
    return value.strip() if isinstance(value, str) and value.strip() else None


def build_mapping(legacy: dict[str, Any], runtime: str = "codex") -> tuple[dict[str, Any], list[str]]:
    language = legacy.get("lang") if legacy.get("lang") in {"pt-BR", "en"} else "pt-BR"
    mapped: dict[str, Any] = {
        "schema_version": 1,
        "language": language,
        # Which adapter performed the migration. Hardcoding codex here made a
        # Claude-initiated migration stamp the wrong runtime.
        "runtime": runtime,
        "auto_commit": False,
        "audit": legacy.get("audit") is True,
    }
    repository_type = safe_string(legacy.get("type"))
    if repository_type:
        mapped["repository_type"] = repository_type

    preserved = {
        field: deepcopy(legacy[field])
        for field in SAFE_LEGACY_FIELDS
        if field in legacy and not SECRET_KEY_RE.search(field)
    }
    if preserved:
        mapped["legacy"] = preserved

    migration: dict[str, Any] = {"source": SOURCE_PATH.as_posix()}
    framework = safe_string(legacy.get("framework"))
    version = safe_string(legacy.get("version"))
    if framework:
        migration["framework"] = framework
    if version:
        migration["version"] = version
    mapped["migration"] = migration

    copied_fields = CONSUMED_FIELDS | set(SAFE_LEGACY_FIELDS)
    excluded = sorted(key for key in legacy if key not in copied_fields)
    return mapped, excluded


def plan(root: Path, runtime: str = "codex") -> tuple[dict[str, Any], list[str]]:
    legacy = load_legacy(root)
    mapped, excluded = build_mapping(legacy, runtime)
    emit(
        {
            "excluded": excluded,
            "mapped": mapped,
            "source": SOURCE_PATH.as_posix(),
            "target": TARGET_PATH.as_posix(),
            "target_exists": (root / TARGET_PATH).exists(),
        }
    )
    return mapped, excluded


def apply(root: Path, runtime: str = "codex") -> int:
    legacy = load_legacy(root)
    mapped, excluded = build_mapping(legacy, runtime)
    target = root / TARGET_PATH
    if target.exists():
        raise FileExistsError("Flow config already exists; migration will not overwrite it")

    migrated = deepcopy(mapped)
    migrated["migration"]["migrated_at"] = (
        datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    )
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("x", encoding="utf-8") as handle:
        json.dump(migrated, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")

    emit(
        {
            "applied": True,
            "excluded": excluded,
            "source": SOURCE_PATH.as_posix(),
            "source_preserved": True,
            "target": TARGET_PATH.as_posix(),
        }
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Migrate PWDEV Code config to PWDEV Flow")
    parser.add_argument("--root", required=True, help="Repository root")
    parser.add_argument(
        "--runtime",
        choices=("codex", "claude"),
        default="codex",
        help="Adapter performing the migration; recorded in the Flow config",
    )
    parser.add_argument("command", choices=("plan", "apply"))
    return parser


def main() -> int:
    arguments = build_parser().parse_args()
    root = Path(arguments.root).expanduser().resolve()
    if not root.is_dir():
        emit({"error": "repository_root_not_found"})
        return 2
    try:
        if arguments.command == "plan":
            plan(root, arguments.runtime)
            return 0
        return apply(root, arguments.runtime)
    except FileExistsError as error:
        emit({"error": str(error)})
        return 3
    except MigrationError as error:
        emit({"error": str(error)})
        return 2
    except OSError as error:
        # Permissions, ENOSPC and friends must still leave the structured
        # contract the callers parse, not a bare traceback.
        emit({"error": f"migration io failure: {error.strerror or error}"})
        return 2


if __name__ == "__main__":
    sys.exit(main())
