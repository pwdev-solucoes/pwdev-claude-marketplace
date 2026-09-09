#!/usr/bin/env python3
"""The single, runtime-neutral language preference contract for SDD Composy."""
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any

SUPPORTED_LANGUAGES = ("pt-BR", "en-US")
NOT_INITIALIZED = {"status": "not_initialized", "next_action": "run_init"}


def _root(value: str | os.PathLike[str]) -> Path:
    root = Path(value).expanduser()
    if not root.is_absolute():
        root = Path.cwd() / root
    if root.is_symlink() or not root.is_dir():
        raise ValueError("repository root must be a real directory")
    return root.resolve(strict=False)


def preference_path(root: str | os.PathLike[str]) -> Path:
    """Return the confined preference file (without creating it)."""
    cursor = _root(root)
    for part in (".planning", "sdd-composy", "config.json"):
        cursor = cursor / part
        if cursor.is_symlink():
            raise ValueError("language preference path is unsafe")
    return cursor


def _read(path: Path) -> dict[str, Any] | None:
    if path.is_symlink():
        raise ValueError("language preference path is unsafe")
    if not path.exists():
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("invalid language configuration; preserve and repair config.json") from exc
    if not isinstance(value, dict):
        raise ValueError("language configuration must be an object")
    return value


def persist_language(root: str | os.PathLike[str], language: str) -> dict[str, Any]:
    """Atomically persist a validated language while preserving config keys."""
    if language not in SUPPORTED_LANGUAGES:
        raise ValueError("language must be exactly pt-BR or en-US")
    target = preference_path(root)
    parent = target.parent
    root_path = _root(root)
    for directory in (root_path / ".planning", parent):
        if directory.is_symlink():
            raise ValueError("language preference path is unsafe")
    if target.is_symlink():
        raise ValueError("language preference file is unsafe")
    if parent.is_symlink() or (parent.exists() and not parent.is_dir()):
        raise ValueError("language preference directory is unsafe")
    parent.mkdir(parents=True, exist_ok=True)
    current = _read(target) or {}
    current["language"] = language
    fd, temporary = tempfile.mkstemp(prefix=".config.", dir=str(parent), text=True)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as handle:
            json.dump(current, handle, ensure_ascii=False, sort_keys=True, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, target)
    finally:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
    return {"language": language, "source": "explicit"}


def resolve_language(root: str | os.PathLike[str], explicit: str | None = None,
                     *, init: bool = False) -> dict[str, Any]:
    """Resolve language; only ``init=True`` may return a choice prompt."""
    stored_config = _read(preference_path(root))
    if explicit is not None and init:
        if explicit not in SUPPORTED_LANGUAGES:
            return {"status": "invalid_language", "allowed": list(SUPPORTED_LANGUAGES),
                    "language": explicit}
        return {"language": explicit, "source": "explicit"}
    stored = stored_config.get("language") if stored_config else None
    if stored in SUPPORTED_LANGUAGES:
        return {"language": stored, "source": "persisted"}
    return {"choices": list(SUPPORTED_LANGUAGES)} if init else dict(NOT_INITIALIZED)


def language(root: str | os.PathLike[str], explicit: str | None = None,
             *, init: bool = False) -> dict[str, Any]:
    """Compatibility alias used by adapters."""
    return resolve_language(root, explicit, init=init)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("root")
    parser.add_argument("--lang", choices=SUPPORTED_LANGUAGES)
    parser.add_argument("--init", action="store_true")
    args = parser.parse_args()
    print(json.dumps(resolve_language(args.root, args.lang, init=args.init), ensure_ascii=False, sort_keys=True))
