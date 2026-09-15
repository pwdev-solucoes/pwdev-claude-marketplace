#!/usr/bin/env python3
"""Read-only comparison of task Markdown contracts and JSON projections.

This module intentionally never selects an authority and never writes either
source.  It is suitable for displaying a proposed synchronization plan.
"""
from __future__ import annotations
import argparse, hashlib, json, re, os, tempfile
from pathlib import Path
from typing import Any

CONFIRMATION_PREFIX = "CONFIRM-SDD-SYNC"
CLASSIFICATIONS = ("no_change", "markdown_only", "json_only", "identity_changed",
                   "status_divergence", "malformed_markdown", "malformed_json")

def _confined(path: Path, root: Path) -> None:
    try: path.resolve(strict=False).relative_to(root.resolve(strict=True))
    except (OSError, ValueError) as exc: raise ValueError("path must be inside repository root") from exc

def _frontmatter(text: str) -> dict[str, Any]:
    from sdd_okf import parse_frontmatter
    meta, _ = parse_frontmatter(text)
    task = (meta or {}).get("task")
    if not isinstance(task, dict) or not isinstance(task.get("id"), str):
        raise ValueError("missing task frontmatter")
    return task

def _markdown(root: Path) -> dict[str, dict[str, Any]]:
    if root.is_symlink(): raise ValueError("markdown root must not be a symlink")
    result = {}
    for path in sorted(root.glob("task-*.md")):
        if path.is_symlink(): raise ValueError(f"markdown file must not be a symlink: {path.name}")
        task = _frontmatter(path.read_text(encoding="utf-8"))
        tid = task["id"]
        if tid in result: raise ValueError(f"duplicate task id: {tid}")
        result[tid] = {"task": task, "path": path.as_posix()}
    return result

def _json(path: Path) -> dict[str, dict[str, Any]]:
    if path.is_symlink(): raise ValueError("state file must not be a symlink")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("tasks"), list): raise ValueError("tasks must be an array")
    result = {}
    for task in data["tasks"]:
        if not isinstance(task, dict) or not isinstance(task.get("id"), str): raise ValueError("invalid task entry")
        if task["id"] in result: raise ValueError(f"duplicate task id: {task['id']}")
        result[task["id"]] = task
    return result

def _identity(task: dict[str, Any]) -> tuple[Any, ...]:
    return (task.get("id"), tuple(task.get("dependencies", [])), tuple(task.get("acceptance_criteria", [])))

def _identity_changed(markdown: dict[str, Any], projection: dict[str, Any]) -> bool:
    # A title absent from older Markdown contracts is not an identity change.
    titles_differ = "title" in markdown and "title" in projection and markdown["title"] != projection["title"]
    return titles_differ or _identity(markdown) != _identity(projection)

def _repository(md_root: Path, root: Path | str | None) -> Path:
    # Conventional layout: <repository>/tasks/prd-<slug>.
    return Path(root).resolve() if root else md_root.resolve().parents[1]

def plan_token(fingerprints: dict[str, Any]) -> str:
    """Bind the human confirmation to the exact inputs the plan was built from."""
    digest = hashlib.sha256(json.dumps(fingerprints, sort_keys=True).encode()).hexdigest()[:12]
    return f"{CONFIRMATION_PREFIX}-{digest}"

def _digest(path: Path) -> str:
    digest = hashlib.sha256()
    if path.is_dir():
        for child in sorted(path.rglob("*")):
            if child.is_file() and not child.is_symlink():
                digest.update(child.relative_to(path).as_posix().encode())
                digest.update(child.read_bytes())
    else:
        digest.update(path.read_bytes())
    return digest.hexdigest()

def _yaml_scalar(value: Any) -> str:
    if isinstance(value, bool): return "true" if value else "false"
    if value is None: return "null"
    if isinstance(value, (list, dict)): return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return json.dumps(str(value), ensure_ascii=False)

def _replace_task(text: str, task: dict[str, Any]) -> str:
    m = re.match(r"^(---\r?\n)([\s\S]*?)(\r?\n---\r?\n?)([\s\S]*)$", text)
    if not m: raise ValueError("missing frontmatter")
    lines = ["task:"]
    for key in sorted(task): lines.append(f"  {key}: {_yaml_scalar(task[key])}")
    raw = m.group(2)
    match = re.search(r"(?m)^task:\n(?:^[ \t]+.*\n?)*", raw)
    if match: raw = raw[:match.start()] + "\n".join(lines) + "\n" + raw[match.end():]
    else: raw = raw.rstrip() + "\n" + "\n".join(lines) + "\n"
    return m.group(1) + raw.rstrip("\n") + m.group(3) + m.group(4)

def _new_markdown(task: dict[str, Any]) -> str:
    lines = ["---", "type: TASK", 'okf_version: "0.2"', "task:"]
    for key in sorted(task): lines.append(f"  {key}: {_yaml_scalar(task[key])}")
    return "\n".join(lines) + "\n---\n\n# " + str(task.get("id", "TASK")) + "\n"

def inspect(markdown_root: Path | str, state_path: Path | str, *, root: Path | str | None = None) -> dict[str, Any]:
    md_root, state = Path(markdown_root), Path(state_path)
    if md_root.is_symlink() or state.is_symlink():
        raise ValueError("repository inputs must not be symlinks")
    if root is not None and Path(root).is_symlink():
        raise ValueError("repository root must not be a symlink")
    repository = _repository(md_root, root)
    _confined(md_root, repository); _confined(state, repository)
    try: md = _markdown(md_root); md_error = None
    except (OSError, UnicodeError, ValueError) as exc: md, md_error = {}, str(exc)
    try: js = _json(state); js_error = None
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as exc: js, js_error = {}, str(exc)
    if md_error or js_error:
        errors = {"markdown": md_error, "json": js_error}
        items = ([{"id": "*", "classification": "malformed_markdown"}] if md_error else [])
        items += ([{"id": "*", "classification": "malformed_json"}] if js_error else [])
        fingerprints = {"markdown": _digest(md_root) if not md_error else None, "json": _digest(state) if not js_error else None}
        return {"schema": "sdd-composy.sync", "read_only": True, "items": items, "errors": errors,
                "confirmation_token": plan_token(fingerprints), "fingerprints": fingerprints}
    items = []
    for tid in sorted(set(md) | set(js)):
        if tid not in js: classification = "markdown_only"
        elif tid not in md: classification = "json_only"
        elif _identity_changed(md[tid]["task"], js[tid]): classification = "identity_changed"
        elif md[tid]["task"].get("state") != js[tid].get("state"): classification = "status_divergence"
        else: classification = "no_change"
        items.append({"id": tid, "classification": classification, "markdown": md.get(tid, {}).get("path")})
    fingerprints = {"markdown": {p: _digest(Path(v["path"])) for p, v in md.items()}, "json": _digest(state)}
    return {"schema": "sdd-composy.sync", "read_only": True, "items": items, "errors": {},
            "confirmation_token": plan_token(fingerprints), "fingerprints": fingerprints}

def plan(report: dict[str, Any]) -> dict[str, Any]:
    """Return a deterministic plan; no operation is executable by this API."""
    items = sorted(report.get("items", []), key=lambda x: (x.get("id", ""), x.get("classification", "")))
    fingerprints = report.get("fingerprints", {})
    return {"schema": "sdd-composy.sync-plan", "read_only": True, "operations": [], "items": items, "errors": report.get("errors", {}),
            "confirmation_token": plan_token(fingerprints), "fingerprints": fingerprints}

def _atomic_write(path: Path, data: bytes) -> None:
    if path.is_symlink(): raise ValueError("destination must not be a symlink")
    fd, name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "wb") as handle: handle.write(data); handle.flush(); os.fsync(handle.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name): os.unlink(name)

def apply(markdown_root: Path | str, state_path: Path | str, sync_plan: dict[str, Any], *, authority: str,
          confirmation_token: str, root: Path | str | None = None) -> dict[str, Any]:
    """Apply one explicit authority after revalidating the read-only plan."""
    if authority not in ("markdown", "json"): raise ValueError("authority must be markdown or json")
    if sync_plan.get("schema") != "sdd-composy.sync-plan" or sync_plan.get("read_only") is not True: raise ValueError("invalid synchronization plan")
    if confirmation_token != plan_token(sync_plan.get("fingerprints", {})): raise ValueError("invalid confirmation token")
    md_root, state = Path(markdown_root), Path(state_path)
    repository = _repository(md_root, root)
    _confined(md_root, repository); _confined(state, repository)
    current = inspect(md_root, state, root=repository)
    if current.get("fingerprints") != sync_plan.get("fingerprints"): raise ValueError("stale synchronization plan")
    if current.get("errors"): raise ValueError("cannot apply malformed synchronization inputs")
    md = _markdown(md_root); js = _json(state)
    if authority == "markdown":
        import sdd_tasks
        # Lifecycle state is operational truth: Markdown may carry intent, never a state move.
        moved = sorted(tid for tid, record in md.items() if tid in js and record["task"].get("state") != js[tid].get("state"))
        if moved:
            raise ValueError("state divergence must be resolved with sdd_tasks transition or json authority: " + ", ".join(moved))
        merged = json.loads(state.read_text(encoding="utf-8"))
        by_id = {t["id"]: t for t in merged["tasks"]}
        for tid, record in md.items(): by_id[tid] = {**by_id.get(tid, {}), **record["task"]}
        merged["tasks"] = [by_id[k] for k in sorted(by_id)]
        sdd_tasks.validate(merged)
        _atomic_write(state, (json.dumps(merged, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode())
    else:
        for tid, task in js.items():
            if tid in md:
                destination = Path(md[tid]["path"])
                _atomic_write(destination, _replace_task(destination.read_text(encoding="utf-8"), task).encode())
            else:
                # JSON-only records receive a deterministic, repository-local contract.
                destination = md_root / (tid.lower() + ".md")
                if destination.exists() or destination.is_symlink(): raise ValueError("destination already exists or is a symlink")
                _atomic_write(destination, _new_markdown(task).encode())
    verified = inspect(md_root, state, root=repository)
    if any(i["classification"] != "no_change" for i in verified["items"]): raise ValueError("post-apply verification failed")
    return {"schema": "sdd-composy.sync-apply", "applied": True, "authority": authority, "verified": True}

def main() -> int:
    p = argparse.ArgumentParser(); sub = p.add_subparsers(dest="command", required=True)
    for name in ("inspect", "plan"):
        q = sub.add_parser(name); q.add_argument("markdown_root"); q.add_argument("state"); q.add_argument("--root")
    a = sub.add_parser("apply")
    a.add_argument("markdown_root"); a.add_argument("state"); a.add_argument("plan")
    a.add_argument("--root"); a.add_argument("--authority", required=True, choices=("markdown", "json"))
    a.add_argument("--confirmation-token", required=True)
    args = p.parse_args()
    try:
        if args.command == "apply":
            with Path(args.plan).open(encoding="utf-8") as handle:
                sync_plan = json.load(handle)
            result = apply(args.markdown_root, args.state, sync_plan,
                           authority=args.authority,
                           confirmation_token=args.confirmation_token,
                           root=args.root)
        else:
            report = inspect(args.markdown_root, args.state, root=args.root)
            result = report if args.command == "inspect" else plan(report)
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as exc:
        p.error(str(exc))
    print(json.dumps(result, indent=2, sort_keys=True)); return 0
if __name__ == "__main__": raise SystemExit(main())
