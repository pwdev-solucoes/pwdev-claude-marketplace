#!/usr/bin/env python3
"""Import, inspect, and safely advance the durable task projection."""
from __future__ import annotations

import argparse, copy, datetime as dt, json, os, re, tempfile
from pathlib import Path
from typing import Any

from sdd_okf import parse_frontmatter

TASK_ID = re.compile(r"^TASK-[0-9]{3,}$")
SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
CRITERION = re.compile(r"^CA-[0-9]{3,}$")
RFC3339 = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$")
STATES = {"pending", "ready", "running", "qa_required", "evidence_required",
          "review_required", "verify_required", "complete", "blocked", "rejected", "skipped"}

class TaskError(ValueError): pass

def _safe_rel(value: str) -> bool:
    return isinstance(value, str) and bool(value) and not value.startswith(("/", "\\")) and "\\" not in value and all(p not in ("", ".", "..") for p in value.split("/"))

def validate(data: dict[str, Any], root: Path | None = None) -> None:
    if not isinstance(data, dict) or data.get("schema_version") != "1": raise TaskError("schema_version must be '1'")
    slug = data.get("prd_slug")
    if not isinstance(slug, str) or not SLUG.fullmatch(slug): raise TaskError("invalid prd_slug")
    stamp = data.get("updated_at")
    if not isinstance(stamp, str) or not RFC3339.fullmatch(stamp): raise TaskError("updated_at must be RFC3339 date-time")
    try: dt.datetime.fromisoformat(stamp.replace("Z", "+00:00"))
    except ValueError as exc: raise TaskError("updated_at must be ISO-8601 date-time") from exc
    tasks = data.get("tasks")
    if not isinstance(tasks, list): raise TaskError("tasks must be an array")
    ids = set()
    for task in tasks:
        if not isinstance(task, dict): raise TaskError("task must be an object")
        for key in ("id", "title", "state", "dependencies", "acceptance_criteria", "verification_commands", "allowed_paths", "evidence_required"):
            if key not in task: raise TaskError(f"task missing {key}")
        tid = task["id"]
        if not isinstance(tid, str) or not TASK_ID.fullmatch(tid) or tid in ids: raise TaskError(f"invalid or duplicate task id: {tid}")
        ids.add(tid)
        if not isinstance(task["title"], str) or not task["title"] or not isinstance(task["state"], str) or task["state"] not in STATES: raise TaskError(f"invalid task {tid}")
        if not isinstance(task["dependencies"], list) or len(set(task["dependencies"])) != len(task["dependencies"]): raise TaskError(f"invalid dependencies: {tid}")
        if not all(isinstance(x, str) and TASK_ID.fullmatch(x) for x in task["dependencies"]): raise TaskError(f"invalid dependency: {tid}")
        if not isinstance(task["acceptance_criteria"], list) or not task["acceptance_criteria"] or not all(isinstance(x,str) and CRITERION.fullmatch(x) for x in task["acceptance_criteria"]): raise TaskError(f"invalid acceptance criteria: {tid}")
        if not isinstance(task["verification_commands"], list) or not task["verification_commands"] or not all(isinstance(x,str) and x for x in task["verification_commands"]): raise TaskError(f"invalid verification commands: {tid}")
        if not isinstance(task["allowed_paths"], list) or not task["allowed_paths"] or not all(_safe_rel(x) for x in task["allowed_paths"]): raise TaskError(f"unsafe allowed path: {tid}")
        if not isinstance(task["evidence_required"], bool): raise TaskError(f"evidence_required must be boolean: {tid}")
        if task["state"] == "skipped" and not isinstance(task.get("justification"), str): raise TaskError(f"skipped task requires justification: {tid}")
    for task in tasks:
        if any(dep not in ids for dep in task["dependencies"]): raise TaskError(f"unknown dependency: {task['id']}")
    # A dependency graph must be acyclic; report the offending task rather than
    # allowing an impossible ready queue to be published.
    graph = {t["id"]: t["dependencies"] for t in tasks}; visiting, visited = set(), set()
    def visit(tid: str) -> None:
        if tid in visiting: raise TaskError(f"dependency cycle involving {tid}")
        if tid in visited: return
        visiting.add(tid)
        for dep in graph[tid]: visit(dep)
        visiting.remove(tid); visited.add(tid)
    for tid in graph: visit(tid)

def ready_tasks(data: dict[str, Any]) -> list[dict[str, Any]]:
    validate(data)
    by_id = {t["id"]: t for t in data["tasks"]}
    return [t for t in data["tasks"] if t["state"] in {"pending", "rejected"}
            and all(by_id[d]["state"] == "complete" for d in t["dependencies"])]

def _task(data: dict[str, Any], task_id: str) -> dict[str, Any]:
    for task in data["tasks"]:
        if task["id"] == task_id: return task
    raise TaskError(f"unknown task: {task_id}")

def _evidence_time(value: Any) -> dt.datetime:
    if not isinstance(value, str) or not RFC3339.fullmatch(value):
        raise TaskError("evidence timestamp must be RFC3339 date-time")
    try:
        stamp = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise TaskError("evidence timestamp must be ISO-8601 date-time") from exc
    if stamp.tzinfo is None:
        raise TaskError("evidence timestamp must include timezone")
    return stamp

def _record(task: dict[str, Any], name: str, now: dt.datetime) -> dict[str, Any]:
    evidence = task.get("evidence")
    record = evidence.get(name) if isinstance(evidence, dict) else None
    if not isinstance(record, dict):
        raise TaskError(f"missing {name} evidence")
    stamp = _evidence_time(record.get("timestamp"))
    baseline_value = task.get("_state_updated_at", task.get("updated_at"))
    baseline = _evidence_time(baseline_value) if isinstance(baseline_value, str) else None
    if stamp > now or (baseline is not None and stamp < baseline):
        raise TaskError(f"stale {name} evidence")
    return record

def _evidence_ok(task: dict[str, Any], now: dt.datetime) -> None:
    tests = _record(task, "tests", now)
    if tests.get("status") not in {"passed", "pass", "ok"} or tests.get("tests_passed") is False:
        raise TaskError("tests evidence is not passing")
    qa = _record(task, "qa", now)
    if qa.get("status") in {"blocked", "failed", "rejected"} or qa.get("blocking") is True or qa.get("qa_passed") is False:
        raise TaskError("QA evidence is blocking")
    review = _record(task, "review", now)
    if review.get("status") not in {"approved", "passed", "pass", "ok"} or review.get("review_approved") is False:
        raise TaskError("review evidence is not approved")
    verify = _record(task, "verify", now)
    if verify.get("status") not in {"approved", "passed", "pass", "ok"} or verify.get("verify_approved") is False:
        raise TaskError("verification evidence is not approved")
    trace = _record(task, "trace", now)
    if trace.get("status") not in {"consistent", "approved", "passed", "pass", "ok"} or trace.get("trace_consistent") is False:
        raise TaskError("trace evidence is inconsistent")

def transition(data: dict[str, Any], task_id: str, target: str, *, reason: str | None = None,
               now: dt.datetime | None = None, authority: str | None = None) -> dict[str, Any]:
    validate(data); task = _task(data, task_id); source = task["state"]
    if target not in STATES: raise TaskError(f"invalid target state: {target}")
    allowed = {"pending": {"ready", "skipped"}, "rejected": {"ready", "skipped"}, "ready": {"running", "skipped"},
               "running": {"qa_required", "blocked", "rejected", "skipped"}, "qa_required": {"evidence_required", "review_required", "skipped"},
               "evidence_required": {"review_required", "skipped"}, "review_required": {"verify_required", "rejected", "skipped"},
               "verify_required": {"complete", "rejected", "skipped"}, "blocked": {"ready", "skipped"}, "complete": set(), "skipped": set()}
    if target not in allowed.get(source, set()): raise TaskError(f"illegal transition: {source} -> {target}")
    if target == "ready":
        by_id = {t["id"]: t for t in data["tasks"]}
        if any(by_id[d]["state"] != "complete" for d in task["dependencies"]): raise TaskError("dependencies are not complete")
    if target == "running":
        by_id = {t["id"]: t for t in data["tasks"]}
        if any(by_id[d]["state"] != "complete" for d in task["dependencies"]): raise TaskError("dependencies are not complete")
    if target == "blocked" and not reason: raise TaskError("blocked transition requires reason")
    if target == "rejected" and (not reason or not reason.strip()):
        raise TaskError("rejected transition requires reason")
    stamp = now or dt.datetime.now(dt.timezone.utc)
    if stamp.tzinfo is None: raise TaskError("now must include timezone")
    # The projection timestamp is the freshness baseline; keep it out of the
    # task object so unknown task fields remain untouched.
    task["_state_updated_at"] = data.get("updated_at")
    if target == "evidence_required":
        _record(task, "tests", stamp)
    elif target == "review_required":
        if source == "qa_required" and task.get("evidence_required", True):
            raise TaskError("evidence dossier is required")
        _record(task, "tests", stamp); _record(task, "qa", stamp)
    elif target == "verify_required":
        _record(task, "tests", stamp); _record(task, "qa", stamp); _record(task, "review", stamp)
    elif target == "complete":
        _evidence_ok(task, stamp)
    elif target == "skipped":
        if not reason or not reason.strip(): raise TaskError("skipped transition requires justification")
        if not authority or not authority.strip(): raise TaskError("skipped transition requires human authority")
    task["state"] = target
    if target == "blocked": task["blocked_reason"] = reason
    elif target == "skipped": task["justification"] = reason
    if target == "skipped": task["skip_authority"] = authority
    elif target == "rejected":
        task["rejection_reason"] = reason
        task["rejection_stage"] = source
        task["evidence_invalidated_at"] = stamp.replace(microsecond=0).isoformat().replace("+00:00", "Z")
    elif target == "ready":
        task.pop("rejection_reason", None); task.pop("blocked_reason", None)
    task.pop("_state_updated_at", None)
    data["updated_at"] = stamp.replace(microsecond=0).isoformat().replace("+00:00", "Z")
    validate(data); return data

def integrate_quality_artifacts(data: dict[str, Any], task_id: str,
                                artifacts: dict[str, dict[str, Any]], *,
                                now: dt.datetime | None = None) -> dict[str, Any]:
    """Consume approved QA/review/verdict artifacts through the task gates.

    This is deliberately the only lifecycle bridge for quality reports.  The
    reports never set state directly: each state is reached through
    ``transition`` and therefore retains dependency, freshness, and approval
    guards.  A rejected or unapproved artifact fails closed with no mutation.
    """
    validate(data)
    stamp = now or dt.datetime.now(dt.timezone.utc)
    if stamp.tzinfo is None:
        raise TaskError("now must include timezone")
    if not isinstance(artifacts, dict):
        raise TaskError("quality artifacts must be an object")
    task = _task(data, task_id)
    expected_types = {"qa": "QA_REPORT", "review": "CODE_REVIEW", "verdict": "VERIFICATION_VERDICT"}
    for name in ("qa", "review", "verdict"):
        artifact = artifacts.get(name)
        if not isinstance(artifact, dict):
            raise TaskError(f"missing {name} artifact")
        lifecycle = artifact.get("lifecycle") if isinstance(artifact.get("lifecycle"), dict) else artifact
        status = lifecycle.get("status")
        approval = lifecycle.get("human_approval", artifact.get("human_approval"))
        if artifact.get("type") != expected_types[name]:
            raise TaskError(f"{name} artifact has invalid type")
        verified = artifact.get("verified")
        if not isinstance(verified, list) or not verified or any(not isinstance(actor, dict) or not actor.get("by") for actor in verified):
            raise TaskError(f"{name} artifact is missing a verification actor")
        if status != "APPROVED" or approval != "APPROVED":
            raise TaskError(f"{name} artifact is not approved")
        if name == "verdict" and artifact.get("verdict") != "COMPLETE":
            raise TaskError("verification verdict is not COMPLETE")
    if task["state"] != "running":
        raise TaskError("quality integration requires a running task")
    iso = stamp.replace(microsecond=0).isoformat().replace("+00:00", "Z")
    staged = copy.deepcopy(data)
    task = _task(staged, task_id)
    task.setdefault("evidence", {})
    task["evidence"].update({
        "qa": {"status": "passed", "qa_passed": True, "timestamp": iso},
        "review": {"status": "approved", "review_approved": True, "timestamp": iso},
        "verify": {"status": "approved", "verify_approved": True, "timestamp": iso},
        "trace": {"status": "consistent", "trace_consistent": True, "timestamp": iso},
    })
    transition(staged, task_id, "qa_required", now=stamp)
    transition(staged, task_id, "evidence_required", now=stamp)
    transition(staged, task_id, "review_required", now=stamp)
    transition(staged, task_id, "verify_required", now=stamp)
    transition(staged, task_id, "complete", now=stamp)
    data.clear(); data.update(staged)
    return data

# Explicit alias for adapters that describe this operation as applying a gate.
apply_quality_artifacts = integrate_quality_artifacts

def update(path: Path | str, task_id: str, target: str, **kwargs: Any) -> dict[str, Any]:
    data = load(path); transition(data, task_id, target, **kwargs); _atomic_write(Path(path), data); return data

def _atomic_write(path: Path, data: dict[str, Any]) -> None:
    if path.is_symlink(): raise TaskError("output must not be a symlink")
    current = path.parent
    while not current.exists() and current != current.parent: current = current.parent
    if current.is_symlink(): raise TaskError("output ancestor must not be a symlink")
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent), text=True)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2, sort_keys=True); fh.write("\n"); fh.flush(); os.fsync(fh.fileno())
        os.replace(name, path)
    except Exception:
        try: os.unlink(name)
        except OSError: pass
        raise

def _confined(path: Path, root: Path) -> bool:
    try: path.resolve(strict=False).relative_to(root.resolve(strict=True)); return True
    except (OSError, ValueError): return False

def import_tasks(markdown_root: Path | str, output: Path | str, prd_slug: str | None = None, *, root: Path | str | None = None, now: dt.datetime | None = None) -> dict[str, Any]:
    markdown_root, output = Path(markdown_root), Path(output)
    repository = Path(root).resolve(strict=True) if root is not None else markdown_root.resolve(strict=True).parents[1]
    if output.is_symlink() or not _confined(output, repository): raise TaskError("output must be repository-bound and non-symlinked")
    existing = json.loads(output.read_text(encoding="utf-8")) if output.exists() else None
    if existing is not None and (not isinstance(existing, dict) or not isinstance(existing.get("tasks", []), list)):
        raise TaskError("existing task projection is malformed")
    slug = prd_slug or (existing or {}).get("prd_slug") or markdown_root.name.removeprefix("prd-")
    if not SLUG.fullmatch(slug): raise TaskError("invalid prd_slug")
    old = {t.get("id"): t for t in (existing or {}).get("tasks", []) if isinstance(t, dict)}
    tasks = []; divergences = []; seen = set()
    for path in sorted(markdown_root.glob("task-*.md")):
        meta, _ = parse_frontmatter(path.read_text(encoding="utf-8"))
        raw = (meta or {}).get("task")
        if not isinstance(raw, dict): raise TaskError(f"missing task frontmatter: {path}")
        tid = raw.get("id")
        seen.add(tid)
        if tid in old:
            merged = dict(old[tid]); live_state = merged.get("state")
            merged.update(raw)
            if live_state in STATES and raw.get("state") != live_state:
                divergences.append({"task_id": tid, "field": "state", "json": live_state, "markdown": raw.get("state")})
            if live_state in STATES: merged["state"] = live_state
            raw = merged
        elif raw.get("state") != "pending":
            raise TaskError(f"new task cannot be imported in promoted state: {tid}")
        tasks.append(raw)
    tasks.extend(copy.deepcopy(task) for tid, task in old.items() if tid not in seen)
    clock = now or dt.datetime.now(dt.timezone.utc)
    if clock.tzinfo is None: raise TaskError("now must include timezone")
    result = {**(existing or {}), "schema_version": "1", "prd_slug": slug,
              "updated_at": clock.replace(microsecond=0).isoformat().replace("+00:00", "Z"), "tasks": tasks}
    if divergences: result["divergences"] = divergences
    else: result.pop("divergences", None)
    validate(result); _atomic_write(output, result); return result

def load(path: Path | str) -> dict[str, Any]:
    data = json.loads(Path(path).read_text(encoding="utf-8")); validate(data); return data

def verify(data: dict[str, Any], *, now: dt.datetime | None = None) -> dict[str, Any]:
    """Read-only completion gate report; never changes *data*."""
    validate(data)
    stamp = now or dt.datetime.now(dt.timezone.utc)
    if stamp.tzinfo is None: raise TaskError("now must include timezone")
    checks = []
    for task in data["tasks"]:
        result = {"id": task["id"], "state": task["state"], "completion_permitted": False}
        if task["state"] == "complete":
            result["completion_permitted"] = True
            result["status"] = "complete"
        elif task["state"] == "verify_required":
            try:
                _evidence_ok(task, stamp)
            except TaskError as exc:
                result["status"] = "blocked"
                result["error"] = str(exc)
            else:
                result["completion_permitted"] = True
                result["status"] = "ready_for_complete"
        else:
            result["status"] = "not_at_completion_gate"
        checks.append(result)
    checks.sort(key=lambda item: item["id"])
    permitted = all(item["completion_permitted"] for item in checks if item["state"] == "verify_required")
    return {"ok": permitted, "prd_slug": data["prd_slug"], "completion_permitted": permitted, "checks": checks}

def main() -> int:
    p=argparse.ArgumentParser(); sub=p.add_subparsers(dest="cmd", required=True)
    q=sub.add_parser("import"); q.add_argument("markdown_root"); q.add_argument("output"); q.add_argument("--prd-slug"); q.add_argument("--root")
    q=sub.add_parser("list"); q.add_argument("state")
    q=sub.add_parser("show"); q.add_argument("state"); q.add_argument("task_id")
    q=sub.add_parser("next"); q.add_argument("state")
    q=sub.add_parser("verify"); q.add_argument("state")
    for name in ("start", "block", "transition"):
        q=sub.add_parser(name); q.add_argument("state"); q.add_argument("task_id")
        if name == "transition": q.add_argument("target")
        if name == "block": q.add_argument("reason")
    a=p.parse_args()
    try:
        if a.cmd == "import": out=import_tasks(a.markdown_root,a.output,a.prd_slug,root=a.root); print(json.dumps(out,ensure_ascii=False,sort_keys=True,indent=2))
        else:
            data=load(a.state)
            if a.cmd == "list": value=data["tasks"]
            elif a.cmd == "next": value=ready_tasks(data)
            elif a.cmd == "verify":
                value=verify(data)
                print(json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2))
                return 0 if value["ok"] else 2
            elif a.cmd in {"start", "block", "transition"}:
                target = "running" if a.cmd == "start" else ("blocked" if a.cmd == "block" else a.target)
                kwargs = {"reason": a.reason} if a.cmd == "block" else {}
                value=update(a.state, a.task_id, target, **kwargs)
            else: value=next(t for t in data["tasks"] if t["id"]==a.task_id)
            print(json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2))
        return 0
    except (OSError, ValueError, StopIteration) as exc: print(json.dumps({"ok":False,"error":str(exc)})); return 2
if __name__ == "__main__": raise SystemExit(main())
