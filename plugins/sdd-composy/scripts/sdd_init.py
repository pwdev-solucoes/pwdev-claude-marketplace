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
    from sdd_localization import render_governance
except ImportError:  # pragma: no cover - direct package loading
    from .sdd_language import resolve_language, persist_language
    from .sdd_localization import render_governance


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


def _template_contents(template_root: Path, variables: dict[str, str], language: str = "en-US") -> dict[str, str]:
    output: dict[str, str] = {}
    for source, destination in TEMPLATE_FILES:
        source_path = template_root / source
        if not source_path.is_file() or source_path.is_symlink():
            raise ValueError(f"missing or unsafe template: {source}")
        output[destination] = source_path.read_text(encoding="utf-8")
    # Translate only plugin-owned template text.  Interpolating afterward is
    # what makes runtime values opaque to localization, even when user content
    # happens to equal one of the static source phrases.
    output = render_governance(output, language)
    for destination, text in output.items():
        for key, value in variables.items():
            text = text.replace("{{" + key + "}}", value)
        if re.search(r"\{\{[A-Z][A-Z0-9_]*\}\}", text):
            raise ValueError(f"unresolved template variable in {destination}")
        output[destination] = text
    return output


def _state(generated_at: str, current: dict[str, Any] | None = None) -> dict[str, Any]:
    result = dict(current or {})
    defaults = {
        "schema_version": "1", "revision": 0, "stage": "INIT",
        "active_prd": None, "active_task": None, "last_gate": None,
        "blockers": [], "loops": [], "fleet": [],
        "trace": {"healthy": True, "source_event_count": 0},
        "updated_at": generated_at, "next_action": "run_map",
    }
    for key, value in defaults.items():
        result.setdefault(key, value)
    return result


def _valid_state(value: Any) -> bool:
    summary_re = re.compile(r"^[A-Za-z][A-Za-z0-9._-]*$")
    def valid_summary(item: Any) -> bool:
        return (isinstance(item, dict) and isinstance(item.get("id"), str)
                and bool(summary_re.fullmatch(item["id"]))
                and isinstance(item.get("status"), str) and bool(item["status"]))
    def valid_datetime(item: Any) -> bool:
        if not isinstance(item, str): return False
        try:
            _dt.datetime.fromisoformat(item.replace("Z", "+00:00"))
            return bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}T.+(?:Z|[+-]\d{2}:\d{2})", item))
        except ValueError:
            return False
    last_gate = value.get("last_gate") if isinstance(value, dict) else None
    valid_gate = last_gate is None or (isinstance(last_gate, dict)
        and last_gate.get("name") in {"PRD", "STORIES", "TECHSPEC", "TASKS", "COMPLETE"}
        and last_gate.get("status") in {"approved", "rejected"}
        and valid_datetime(last_gate.get("at"))
        and isinstance(last_gate.get("actor_id"), str) and bool(ACTOR_RE.fullmatch(last_gate["actor_id"])))
    return (isinstance(value, dict) and value.get("schema_version") == "1"
            and isinstance(value.get("revision"), int) and not isinstance(value.get("revision"), bool) and value.get("revision", -1) >= 0
            and value.get("stage") in {"INIT", "MAP", "PRD", "STORIES", "TECHSPEC", "TASKS", "EXECUTE", "QA", "EVIDENCE", "REVIEW", "VERIFY", "COMPLETE"}
            and all(key in value for key in ("active_prd", "active_task", "last_gate", "blockers", "loops", "fleet", "trace", "updated_at", "next_action"))
            and (value.get("active_prd") is None or isinstance(value.get("active_prd"), str) and bool(re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", value["active_prd"])))
            and (value.get("active_task") is None or isinstance(value.get("active_task"), str) and bool(re.fullmatch(r"TASK-[0-9]{3,}", value["active_task"])))
            and valid_gate and all(isinstance(value.get(k), list) and all(valid_summary(x) for x in value[k]) for k in ("blockers", "loops", "fleet"))
            and isinstance(value.get("trace"), dict)
            and isinstance(value["trace"].get("healthy"), bool)
            and isinstance(value["trace"].get("source_event_count"), int) and not isinstance(value["trace"].get("source_event_count"), bool)
            and value["trace"]["source_event_count"] >= 0 and valid_datetime(value.get("updated_at"))
            and isinstance(value.get("next_action"), str) and bool(value["next_action"]))


def _has_symlink_ancestor(root: Path, relative: str) -> bool:
    cursor = root
    for component in Path(relative).parts[:-1]:
        cursor = cursor / component
        if cursor.is_symlink():
            return True
    return False


def _atomic_json(path: Path, value: dict[str, Any]) -> None:
    _safe_relative(path.parents[2], str(path.relative_to(path.parents[2])))
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent), text=True)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass


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
    templates = _template_contents(template_root, variables, language)
    targets = dict(templates)
    targets["tasks/index.md"] = _index_text(actor, variables["GENERATED_AT"], language)
    actions: list[dict[str, str]] = []
    conflicts: list[dict[str, str]] = []
    unchanged: list[str] = []
    for relative, content in targets.items():
        path = root / relative
        if _has_symlink_ancestor(root, relative):
            conflicts.append({"path": relative, "reason": "ancestor symlink"})
        elif path.is_symlink():
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
    # Existing compatibility directories are preserved. Missing owned files are
    # planned independently, so their contents are never adopted by existence.
    agents = root / ".agents"
    if agents.is_symlink() or (agents.exists() and not agents.is_dir()):
        conflicts.append({"path": ".agents", "reason": "unsafe path"})
    elif agents.exists():
        unchanged.append(".agents")
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
        if claude.is_dir():
            bridge = claude / "AGENTS.md"
            if bridge.is_symlink() or (bridge.exists() and (not bridge.is_file() or bridge.read_text(encoding="utf-8") != "../AGENTS.md\n")):
                conflicts.append({"path": ".claude/AGENTS.md", "reason": "conflict"})
            elif bridge.exists():
                unchanged.append(".claude/AGENTS.md")
            else:
                actions.append({"path": ".claude/AGENTS.md", "operation": "create"})
        else:
            conflicts.append({"path": ".claude", "reason": "conflict"})
    else:
        actions.append({"path": ".claude", "operation": "symlink", "target": ".agents"})
    compatibility = "symlink" if claude.is_symlink() and os.readlink(claude) == ".agents" else ("existing_directory" if claude.is_dir() else ("conflict" if claude.exists() or claude.is_symlink() else "symlink"))
    plan = {"version": 1, "root": str(root), "actor": actor, "actions": actions, "conflicts": conflicts, "unchanged": unchanged, "claude_compatibility": compatibility}
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
    text = re.sub(r"20\d{2}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:Z|[+-]\d{2}:\d{2})", "<timestamp>", text)
    # The observed source commit changes with every commit; it is not an edit to the file.
    return re.sub(r"`(?:[0-9a-fA-F]{7,64}|uncommitted)`", "`<commit>`", text)


def apply(root: Path, plan: dict[str, Any], template_root: Path) -> dict[str, Any]:
    if 'language' in plan:
        resolved = resolve_language(root, plan['language'], init=True)
        if 'status' in resolved or 'choices' in resolved:
            return resolved
    generated_at = _utc_now()
    # State is operational authority, so validate it before publishing any
    # generated artifact.  A malformed existing state must be preserved for
    # explicit repair and must not leave an otherwise half-initialized tree.
    state_path = root / ".planning/sdd-composy/state.json"
    _safe_relative(root, ".planning/sdd-composy/state.json")
    state_existed = state_path.exists()
    current = None
    if state_existed:
        try:
            current = json.loads(state_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError("invalid state; preserve and repair state.json") from exc
        if not _valid_state(current):
            raise ValueError("invalid state; preserve and repair state.json")
    new_state = _state(generated_at, current)
    if not _valid_state(new_state):
        raise ValueError("generated INIT state is invalid")

    variables = {"PROJECT_NAME": root.name, "SOURCE_COMMIT": _source_commit(root), "GENERATED_AT": generated_at, "ACTOR_ID": plan["actor"], "STACK_SUMMARY": "Not mapped yet", "COMMANDS": "Run the repository's focused verification command"}
    contents = _template_contents(template_root, variables, plan.get("language", "en-US"))
    contents["tasks/index.md"] = _index_text(plan["actor"], generated_at, plan.get("language", "en-US"))
    blocked = {item["path"] for item in plan["conflicts"]}
    # A user-owned regular file is preserved and does not block INIT; unsafe paths do.
    preserved = sorted(item["path"] for item in plan["conflicts"] if item.get("reason") == "file")
    blocking = [item for item in plan["conflicts"] if item.get("reason") != "file"]
    created: list[str] = []
    candidates = [relative for relative in contents
                  if relative not in blocked and not any(relative.startswith(item + "/") for item in blocked if item != ".agents")
                  and not (root / relative).is_file()]
    claude = root / ".claude"
    compatibility_target = None
    if not claude.exists() and not claude.is_symlink() and ".claude" not in blocked:
        compatibility_target = ".claude"
    elif not claude.is_symlink() and claude.is_dir() and ".claude/AGENTS.md" not in blocked:
        bridge = claude / "AGENTS.md"
        if not bridge.exists() and not bridge.is_symlink():
            compatibility_target = ".claude/AGENTS.md"
    config_path = root / ".planning/sdd-composy/config.json"
    config_existed = config_path.exists()
    planned = list(candidates)
    if compatibility_target:
        planned.append(compatibility_target)
    if "language" in plan and not config_existed:
        planned.append(".planning/sdd-composy/config.json")
    if not state_existed and not blocking:
        planned.append(".planning/sdd-composy/state.json")
    try:
        for relative in candidates:
            _safe_relative(root, relative)
            _atomic_create(root / relative, contents[relative])
            created.append(relative)
        agents = root / ".agents"
        if not agents.exists() and ".agents" not in blocked:
            agents.mkdir()
        rules = agents / "rules"
        if not agents.is_symlink() and ".agents" not in blocked and not rules.exists():
            rules.mkdir(parents=True)
        if compatibility_target == ".claude":
            os.symlink(".agents", claude)
            created.append(".claude")
        elif compatibility_target == ".claude/AGENTS.md":
            bridge = claude / "AGENTS.md"
            _atomic_create(bridge, "../AGENTS.md\n")
            created.append(".claude/AGENTS.md")
        if "language" in plan:
            persist_language(root, plan["language"])
            if not config_existed:
                created.append(".planning/sdd-composy/config.json")
        # INIT is authoritative only after every required artifact was generated.
        if not state_existed and not blocking:
            _atomic_json(state_path, new_state)
            created.append(".planning/sdd-composy/state.json")
    except (OSError, ValueError) as exc:
        return {"ok": False, "created": created,
                "pending": [relative for relative in planned if relative not in created],
                "conflicts": plan["conflicts"], "actor": plan["actor"], "error": str(exc)}
    return {"ok": not blocking, "created": created, "conflicts": plan["conflicts"], "preserved": preserved,
            "actor": plan["actor"]}


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
    compatibility = "conflict"
    if claude.is_symlink():
        compatible_link = os.readlink(claude) == ".agents" and claude.resolve(strict=False) == root / ".agents" and (root / ".agents").is_dir()
        compatibility = "symlink" if compatible_link else "conflict"
    elif claude.is_dir():
        bridge = claude / "AGENTS.md"
        compatibility = "existing_directory" if bridge.is_file() and not bridge.is_symlink() and bridge.read_text(encoding="utf-8") == "../AGENTS.md\n" else "conflict"
    try:
        language_result = resolve_language(root)
        language_ok = language_result.get("language") in {"pt-BR", "en-US"}
    except ValueError:
        language_ok = False
    state_path = root / ".planning/sdd-composy/state.json"
    state_ok = False
    if state_path.is_file() and not state_path.is_symlink():
        try:
            state_ok = _valid_state(json.loads(state_path.read_text(encoding="utf-8")))
        except (OSError, UnicodeError, json.JSONDecodeError):
            state_ok = False
    compatibility_ok = compatible_link or compatibility == "existing_directory"
    result = {"ok": not missing and valid_index and compatibility_ok and language_ok and state_ok,
              "missing": missing, "index_ok": valid_index, "claude_link_ok": compatible_link,
              "claude_compatibility": compatibility, "language_ok": language_ok,
              "state_ok": state_ok, "actor": actor}
    if not state_ok:
        result["next_action"] = "reconcile_init_state"
    return result


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
                    raise ValueError("exact plan_token from the reviewed plan is required to apply a plan with conflicts")
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
