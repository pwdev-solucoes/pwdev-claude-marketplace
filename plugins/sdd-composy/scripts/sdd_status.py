#!/usr/bin/env python3
"""Read-only consolidated status for an SDD Composy repository."""
from __future__ import annotations
import argparse, json
from pathlib import Path
from typing import Any

try:
    from sdd_trace import verify as verify_trace
except ImportError:  # pragma: no cover
    verify_trace = None

def _load(path: Path) -> tuple[Any, str]:
    if path.is_symlink(): return None, "unsafe_symlink"
    if not path.exists(): return None, "missing"
    try: return json.loads(path.read_text(encoding="utf-8")), "valid"
    except (OSError, UnicodeError, json.JSONDecodeError): return None, "malformed"

def _source(value: Any, state: str) -> dict[str, Any]:
    return {"confidence": "high" if state == "valid" else "low", "state": state, "value": value}

def status(root: Path | str, feature: str | None = None, include_tasks: bool = False,
           include_fleet: bool = False) -> dict[str, Any]:
    """Aggregate known state without creating or modifying any path."""
    base = Path(root).absolute()
    op = base / ".planning" / "sdd-composy"
    config, cs = _load(op / "config.json")
    global_state, gs = _load(op / "state.json")
    loops, ls = _records(op / "loops")
    fleet, fs = _fleet_records(op / "fleet")
    trace_path = base / "trace" / "events.jsonl"
    if trace_path.is_symlink():
        tr, ts = {"ok": False, "errors": ["trace target is an unsafe symlink"]}, "unsafe_symlink"
    elif trace_path.exists() and verify_trace:
        try: tr = verify_trace(base); ts = "valid" if tr.get("ok") else "malformed"
        except Exception: tr, ts = {"ok": False, "errors": ["trace unavailable"]}, "malformed"
    else: tr, ts = {"ok": True, "source_event_count": 0}, "missing"
    tasks, task_state = _task_summary(base)
    reasons: list[str] = []
    state_name = "uninitialized"
    next_action = "run sdd-init"
    if any(x in {"malformed", "unsafe_symlink"} for x in (cs, gs, ls, fs, ts, task_state)):
        state_name, next_action = "malformed", "repair the malformed source manually, then rerun sdd-status"
        reasons.append("one or more state sources are malformed")
    elif gs == "valid" and isinstance(global_state, dict):
        state_name = str(global_state.get("stage", "active")).lower()
        next_action = str(global_state.get("next_action") or "inspect the active stage")
        if global_state.get("blockers"):
            state_name, next_action = "blocked", "resolve the recorded blocker before continuing"
            reasons.extend(str(x.get("reason", x.get("id", "blocker"))) for x in global_state["blockers"] if isinstance(x, dict))
        elif global_state.get("active_task") or tasks:
            state_name = "active"
    if tasks:
        md_states = {str(t.get("state")) for t in tasks if isinstance(t, dict)}
        if "blocked" in md_states:
            state_name, next_action = "blocked", "resolve the blocked task and transition it to ready"
        elif "running" in md_states:
            state_name, next_action = "active", "continue the running task"
    running_loops = [x for x in loops if isinstance(x, dict) and x.get("status") == "running"]
    if running_loops:
        state_name, next_action = "looping", "continue the loop or stop it at its configured guard"
    fleet_active = [x for x in fleet if isinstance(x, dict) and x.get("status") in {"running", "pending"}]
    if fleet_active or fleet:
        state_name, next_action = "fleet", "inspect fleet members and collect their results"
    if gs == "valid" and isinstance(global_state, dict) and global_state.get("trace", {}).get("healthy") is False:
        state_name, next_action = "divergent", "verify trace integrity and resolve the reported divergence"
    result = {"schema": "sdd-composy.status", "read_only": True, "status": state_name,
            "next_action": next_action, "reasons": sorted(set(reasons)),
            "sources": {"config": _source(config, cs), "global": _source(global_state, gs),
                        "tasks": _source(tasks, task_state),
                        "trace": _source(tr, ts), "loops": _source(loops, ls), "fleet": _source(fleet, fs)}}
    if feature is not None:
        result["feature"] = feature
    if include_tasks:
        result["task_summary"] = tasks
    if include_fleet:
        result["fleet_summary"] = fleet
    return result

def _records(directory: Path) -> tuple[list[Any], str]:
    if directory.is_symlink(): return [], "unsafe_symlink"
    if not directory.exists(): return [], "missing"
    if not directory.is_dir(): return [], "malformed"
    out = []
    for path in sorted(directory.glob("*.json")):
        value, state = _load(path)
        if state != "valid": return [], state
        out.append(value)
    return out, "valid"

def _fleet_records(directory: Path) -> tuple[list[Any], str]:
    """Read fleet member snapshots without treating fleet IDs as JSON files."""
    if directory.is_symlink(): return [], "unsafe_symlink"
    if not directory.exists(): return [], "missing"
    if not directory.is_dir(): return [], "malformed"
    out = []
    direct, direct_state = _records(directory)
    if direct_state in {"malformed", "unsafe_symlink"}: return [], direct_state
    out.extend(x for x in direct if isinstance(x, dict))
    for fleet_dir in sorted(directory.iterdir()):
        if fleet_dir.is_symlink() or not fleet_dir.is_dir(): continue
        members, state = _records(fleet_dir / "members")
        if state in {"malformed", "unsafe_symlink"}: return [], state
        out.extend(x for x in members if isinstance(x, dict))
    return out, ("valid" if out else "missing")

def _task_summary(root: Path) -> tuple[list[dict[str, Any]], str]:
    out = []
    tasks = root / "tasks"
    if tasks.is_symlink(): return out, "unsafe_symlink"
    if not tasks.exists(): return out, "missing"
    if not tasks.is_dir(): return out, "malformed"
    found = False
    for path in sorted(tasks.rglob("task-*.md")):
        found = True
        if path.is_symlink(): return out, "unsafe_symlink"
        try:
            from sdd_okf import parse_frontmatter
            meta, _ = parse_frontmatter(path.read_text(encoding="utf-8")); task = meta.get("task", {}) if isinstance(meta, dict) else {}
            if not isinstance(meta, dict) or not isinstance(task, dict): return out, "malformed"
            out.append(task)
        except (OSError, UnicodeError, ValueError):
            return out, "malformed"
    return out, ("valid" if found else "missing")

def main() -> int:
    p = argparse.ArgumentParser(); p.add_argument("root"); p.add_argument("--feature")
    p.add_argument("--tasks", action="store_true"); p.add_argument("--fleet", action="store_true")
    p.add_argument("--json", action="store_true")
    a = p.parse_args()
    payload = status(a.root, feature=a.feature, include_tasks=a.tasks, include_fleet=a.fleet)
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=None if a.json else 2)); return 0

if __name__ == "__main__": raise SystemExit(main())
