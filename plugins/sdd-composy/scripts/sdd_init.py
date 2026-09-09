#!/usr/bin/env python3
"""Safe, dependency-free SDD Composy repository initialization.

The command is deliberately conservative: it only reads the packaged templates
and a small, allow-listed set of repository metadata, never follows destination
symlinks, and never replaces an existing path.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

try:
    from sdd_language import resolve_language, persist_language
except ImportError:  # pragma: no cover - direct package loading
    from .sdd_language import resolve_language, persist_language


ACTOR_RE = re.compile(r"^[A-Za-z][A-Za-z0-9._-]*:[A-Za-z0-9][A-Za-z0-9._-]*$")
SECRET_NAMES = {".env", ".env.local", ".env.production", ".env.development"}
TEMPLATE_FILES = (
    ("AGENTS.md", "AGENTS.md"),
    ("CLAUDE.md", "CLAUDE.md"),
    ("rules/00-sdd-composy.md", ".agents/rules/00-sdd-composy.md"),
    ("rules/architecture.md", ".agents/rules/architecture.md"),
    ("rules/testing.md", ".agents/rules/testing.md"),
    ("rules/workflow.md", ".agents/rules/workflow.md"),
)


def _utc_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0).isoformat()


def _safe_root(value: str | os.PathLike[str]) -> Path:
    root = Path(value).expanduser()
    if not root.is_absolute():
        root = Path.cwd() / root
    if root.is_symlink():
        raise ValueError("repository root must not be a symlink")
    root = root.resolve(strict=False)
    if not root.is_dir():
        raise ValueError("repository root must be a real directory")
    return root


def _safe_relative(root: Path, relative: str) -> Path:
    if not relative or Path(relative).is_absolute():
        raise ValueError(f"unsafe repository path: {relative!r}")
    candidate = root / relative
    cursor = root
    for component in Path(relative).parts[:-1]:
        cursor = cursor / component
        if cursor.is_symlink():
            raise ValueError(f"unsafe symlink parent: {relative}")
    # Resolve the parent only for validation; do not follow a destination path.
    root_real = root.resolve(strict=False)
    parent = candidate.parent.resolve(strict=False)
    if parent != root_real and root_real not in parent.parents:
        raise ValueError(f"path escapes repository: {relative}")
    if candidate.exists() or candidate.is_symlink():
        if candidate.is_symlink():
            raise ValueError(f"unsafe symlink destination: {relative}")
        if candidate.is_dir():
            raise IsADirectoryError(relative)
    return candidate


def _source_commit(root: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            check=True, capture_output=True, text=True, timeout=5,
        )
        value = result.stdout.strip()
        return value if re.fullmatch(r"[0-9a-fA-F]{7,64}", value) else "uncommitted"
    except (OSError, subprocess.SubprocessError):
        return "uncommitted"


def _template_root(value: str | os.PathLike[str] | None) -> Path:
    root = Path(value) if value else Path(__file__).resolve().parents[1] / "templates"
    root = root.resolve(strict=True)
    if not root.is_dir() or root.is_symlink():
        raise ValueError("template root must be a real directory")
    return root


def _template_contents(template_root: Path, variables: dict[str, str]) -> dict[str, str]:
    output: dict[str, str] = {}
    for source, destination in TEMPLATE_FILES:
        source_path = template_root / source
        if not source_path.is_file() or source_path.is_symlink():
            raise ValueError(f"missing or unsafe template: {source}")
        text = source_path.read_text(encoding="utf-8")
        for key, value in variables.items():
            text = text.replace("{{" + key + "}}", value)
        if re.search(r"\{\{[A-Z][A-Z0-9_]*\}\}", text):
            raise ValueError(f"unresolved template variable in {source}")
        output[destination] = text
    return output


def _index_text(actor: str, generated_at: str, language: str = "en-US") -> str:
    return (
        "---\n"
        "type: Index\n"
        'okf_version: "0.2"\n'
        f"actor_id: {actor}\n"
        f"generated:\n  by: {actor}\n  at: {generated_at}\n"
        + ("---\n\n# Documentos do projeto\n\n" if language == "pt-BR" else "---\n\n# Project documents\n\n")
    )


def run_plan(root: Path, actor: str, template_root: Path, language: str | None = None) -> dict[str, Any]:
    """Resolve init language before inspecting or generating any artifact."""
    resolved = resolve_language(root, language, init=True)
    if "status" in resolved or "choices" in resolved:
        return resolved
    plan = _plan(root, actor, template_root, resolved["language"])
    plan["language"] = resolved["language"]
    plan["language_source"] = resolved.get("source", "persisted")
    plan.pop("plan_token", None)
    plan["plan_token"] = hashlib.sha256(json.dumps(plan, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return plan


def _plan(root: Path, actor: str, template_root: Path, language: str = "en-US") -> dict[str, Any]:
    if not ACTOR_RE.fullmatch(actor):
        raise ValueError("actor must match provider:name (for example agent:sdd-init)")
    # The plan intentionally does not read arbitrary project files. These are
    # the only destinations initialization is permitted to inspect.
    variables = {
        "PROJECT_NAME": root.name,
        "SOURCE_COMMIT": _source_commit(root),
        "GENERATED_AT": _utc_now(),
        "ACTOR_ID": actor,
        "STACK_SUMMARY": "Not mapped yet",
        "COMMANDS": "Run the repository's focused verification command",
    }
    templates = _template_contents(template_root, variables)
    targets = dict(templates)
    targets["tasks/index.md"] = _index_text(actor, variables["GENERATED_AT"], language)
    actions: list[dict[str, str]] = []
    conflicts: list[dict[str, str]] = []
    unchanged: list[str] = []
    for relative, content in targets.items():
        path = root / relative
        if path.is_symlink():
            conflicts.append({"path": relative, "reason": "symlink"})
        elif path.exists():
            if path.is_dir():
                conflicts.append({"path": relative, "reason": "directory"})
            elif _without_timestamps(path.read_text(encoding="utf-8")) == _without_timestamps(content):
                # Timestamped generated files are handled as an existing
                # destination; this preserves idempotence without inspecting
                # arbitrary content.
                unchanged.append(relative)
            else:
                conflicts.append({"path": relative, "reason": "file"})
        else:
            actions.append({"path": relative, "operation": "create"})
    # Existing .agents/.claude are compatibility paths, not files to merge.
    agents = root / ".agents"
    if agents.is_symlink() or (agents.exists() and not agents.is_dir()):
        conflicts.append({"path": ".agents", "reason": "unsafe path"})
    elif agents.exists():
        # A pre-existing empty/foreign .agents directory is a collision. The
        # directory created by this helper is recognized by its complete rules
        # set so that a rerun remains a no-op.
        rules = agents / "rules"
        expected_rules = {name.rsplit("/", 1)[-1] for name, _ in TEMPLATE_FILES if name.startswith("rules/")}
        present_rules = {item.name for item in rules.iterdir()} if rules.is_dir() else set()
        if not rules.is_dir() or not expected_rules.issubset(present_rules):
            conflicts.append({"path": ".agents", "reason": "existing directory"})
    else:
        actions.append({"path": ".agents", "operation": "mkdir"})
    claude = root / ".claude"
    if claude.is_symlink():
        try:
            if os.readlink(claude) != ".agents":
                conflicts.append({"path": ".claude", "reason": "symlink target"})
            else:
                unchanged.append(".claude")
        except OSError:
            conflicts.append({"path": ".claude", "reason": "unreadable symlink"})
    elif claude.exists():
        conflicts.append({"path": ".claude", "reason": "existing path"})
    else:
        actions.append({"path": ".claude", "operation": "symlink", "target": ".agents"})
    plan = {"version": 1, "root": str(root), "actor": actor, "actions": actions, "conflicts": conflicts, "unchanged": unchanged}
    digest = hashlib.sha256(json.dumps(plan, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    plan["plan_token"] = digest
    return plan


def _atomic_create(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() or path.is_symlink():
        raise FileExistsError(str(path))
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent), text=True)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.link(temporary, path)
    finally:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass


def _without_timestamps(text: str) -> str:
    """Compare generated files without making a rerun differ by its clock."""
    return re.sub(r"20\d{2}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:Z|[+-]\d{2}:\d{2})", "<timestamp>", text)


def apply(root: Path, plan: dict[str, Any], template_root: Path) -> dict[str, Any]:
    if 'language' in plan:
        resolved = resolve_language(root, plan['language'], init=True)
        if 'status' in resolved or 'choices' in resolved:
            return resolved
    generated_at = _utc_now()
    variables = {"PROJECT_NAME": root.name, "SOURCE_COMMIT": _source_commit(root), "GENERATED_AT": generated_at, "ACTOR_ID": plan["actor"], "STACK_SUMMARY": "Not mapped yet", "COMMANDS": "Run the repository's focused verification command"}
    contents = _template_contents(template_root, variables)
    contents["tasks/index.md"] = _index_text(plan["actor"], generated_at, plan.get("language", "en-US"))
    blocked = {item["path"] for item in plan["conflicts"]}
    for relative, content in contents.items():
        if relative in blocked or any(relative.startswith(item + "/") for item in blocked):
            continue
        _safe_relative(root, relative)
        path = root / relative
        if path.exists() and path.is_file():
            continue
        _atomic_create(path, content)
    agents = root / ".agents"
    if not agents.exists() and ".agents" not in blocked:
        agents.mkdir()
    rules = agents / "rules"
    if not rules.exists() and ".agents" not in blocked:
        rules.mkdir()
    claude = root / ".claude"
    if not claude.exists() and not claude.is_symlink() and ".claude" not in blocked:
        os.symlink(".agents", claude)
    if "language" in plan:
        persist_language(root, plan["language"])
    return {"ok": True, "created": list(contents) + [".claude"], "actor": plan["actor"]}


def verify(root: Path, actor: str) -> dict[str, Any]:
    required = ["AGENTS.md", "CLAUDE.md", *(f".agents/rules/{name}" for name in ("00-sdd-composy.md", "architecture.md", "testing.md", "workflow.md")), "tasks/index.md"]
    missing = [item for item in required if not (root / item).is_file() or (root / item).is_symlink()]
    index = root / "tasks/index.md"
    index_meta: dict[str, Any] = {}
    if index.is_file() and not index.is_symlink():
        text = index.read_text(encoding="utf-8")
        match = re.match(r"^---\n(.*?)\n---(?:\n|$)", text, flags=re.DOTALL)
        if match:
            for line in match.group(1).splitlines():
                key, separator, value = line.partition(":")
                if separator:
                    index_meta[key.strip()] = value.strip().strip('"')
            generated = re.search(r"^generated:\s*\n((?:^[ \t]+.*(?:\n|$))*)", match.group(1), flags=re.MULTILINE)
            if generated:
                index_meta["generated"] = {}
                for line in generated.group(1).splitlines():
                    key, separator, value = line.strip().partition(":")
                    if separator:
                        index_meta["generated"][key.strip()] = value.strip().strip('"')
    generated = index_meta.get("generated")
    timestamp = generated.get("at", "") if isinstance(generated, dict) else ""
    valid_timestamp = bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:Z|[+-]\d{2}:\d{2})", timestamp))
    valid_index = (index_meta.get("type") == "Index" and index_meta.get("okf_version") == "0.2" and index_meta.get("actor_id") == actor and isinstance(generated, dict) and generated.get("by") == actor and valid_timestamp)
    claude = root / ".claude"
    compatible_link = False
    if claude.is_symlink():
        compatible_link = os.readlink(claude) == ".agents" and claude.resolve(strict=False) == root / ".agents" and (root / ".agents").is_dir()
    return {"ok": not missing and valid_index and compatible_link, "missing": missing, "index_ok": valid_index, "claude_link_ok": compatible_link, "actor": actor}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("inspect", "plan", "apply", "verify"))
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument("--actor", "--actor-id", dest="actor", default="agent:sdd-init")
    parser.add_argument("--template-root")
    parser.add_argument("--plan-token")
    parser.add_argument("--lang", "--language", dest="language")
    args = parser.parse_args(argv)
    try:
        root = _safe_root(args.root)
        template_root = _template_root(args.template_root)
        if args.command == "verify":
            result = verify(root, args.actor)
        else:
            plan = run_plan(root, args.actor, template_root, args.language)
            if "language" not in plan or "status" in plan:
                print(json.dumps(plan, ensure_ascii=False, sort_keys=True))
                return 0 if plan.get("status") != "invalid_language" else 2
            if args.command == "apply":
                if plan["conflicts"] and args.plan_token != plan["plan_token"]:
                    raise ValueError(f"exact plan token required: {plan['plan_token']}")
                result = apply(root, plan, template_root)
            else:
                result = plan
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return 0 if result.get("ok", True) else 1
    except (OSError, ValueError, IsADirectoryError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
