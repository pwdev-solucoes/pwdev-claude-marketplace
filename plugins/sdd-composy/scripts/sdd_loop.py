#!/usr/bin/env python3
"""Provider-neutral, bounded autonomous loop state machine."""
from __future__ import annotations
import argparse, datetime as dt, hashlib, json, os, re, tempfile
from pathlib import Path

TASK_ID = re.compile(r"^TASK-[0-9]{3,}$")
LOOP_ID = re.compile(r"^[A-Za-z][A-Za-z0-9._-]*$")
TERMINAL = {"completed", "iteration_cap", "missing_progress", "scope_expansion",
            "architectural_ambiguity", "destructive_action", "external_authorization",
            "environment_failure", "cancelled", "destructive_request", "scope_drift",
            "new_architecture", "repeated_environment_failure", "third_rejection",
            "identical_diff", "identical_failure"}
STAGES = {"pending", "running", *TERMINAL}
LOOP_STAGES = ("EXECUTE", "QA", "EVIDENCE", "REVIEW", "VERIFY")
SUCCESS_EVIDENCE = {"passed", "approved", "complete", "ok"}
_PROGRESS_FIELDS = ("diff", "failure", "scope", "architecture", "environment", "verdict")

class LoopError(ValueError): pass

def _now(): return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
def _digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

def progress_fingerprint(snapshot):
    """Return a stable identity for the material outcome of one iteration.

    Timestamps, messages, and other presentation metadata are intentionally not
    part of the identity: changing those is not progress.
    """
    if not isinstance(snapshot, dict):
        raise LoopError("iteration snapshot must be an object")
    return _digest({key: snapshot.get(key) for key in _PROGRESS_FIELDS})

def correction_decision(previous, current, *, rejection_count=0):
    """Classify whether a correction is safe, or stop with one exact reason."""
    if not isinstance(previous, dict) or not isinstance(current, dict):
        raise LoopError("iteration snapshots must be objects")
    if isinstance(rejection_count, bool) or not isinstance(rejection_count, int) or rejection_count < 0:
        raise LoopError("rejection_count must be a non-negative integer")
    # Safety and contract guards take precedence over any apparent progress.
    if current.get("destructive") or current.get("destructive_request"):
        return {"status": "needs_human", "reason": "destructive_request"}
    if current.get("scope_changed") or current.get("scope_drift"):
        return {"status": "needs_human", "reason": "scope_drift"}
    if current.get("architecture_changed") or current.get("new_architecture"):
        return {"status": "needs_human", "reason": "new_architecture"}
    if current.get("environment_failure") and previous.get("environment_failure") and current.get("environment") == previous.get("environment"):
        return {"status": "needs_human", "reason": "repeated_environment_failure"}
    if current.get("verdict", "").lower() == "rejected" and rejection_count >= 2:
        return {"status": "needs_human", "reason": "third_rejection"}
    if current.get("diff") == previous.get("diff") and current.get("diff") is not None:
        return {"status": "needs_human", "reason": "identical_diff"}
    if current.get("failure") == previous.get("failure") and current.get("failure") is not None:
        return {"status": "needs_human", "reason": "identical_failure"}
    return {"status": "correction", "reason": "progress"}
def _stamp(value):
    if not isinstance(value, str): raise LoopError("timestamp must be RFC3339")
    try: dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc: raise LoopError("timestamp must be RFC3339") from exc

def validate(data):
    if not isinstance(data, dict) or data.get("schema_version") != "1": raise LoopError("invalid loop schema")
    if not isinstance(data.get("id"), str) or not LOOP_ID.fullmatch(data["id"]): raise LoopError("invalid loop id")
    if not isinstance(data.get("task_id"), str) or not TASK_ID.fullmatch(data["task_id"]): raise LoopError("invalid task id")
    if data.get("status") not in STAGES: raise LoopError("invalid loop status")
    cap, iteration = data.get("max_iterations"), data.get("iteration")
    if not isinstance(cap, int) or isinstance(cap, bool) or cap not in (1, 2, 3): raise LoopError("max_iterations must be 1, 2, or 3")
    if not isinstance(iteration, int) or isinstance(iteration, bool) or iteration < 0 or iteration > cap: raise LoopError("invalid iteration")
    for key in ("started_at", "updated_at"): _stamp(data.get(key))
    if data["status"] in TERMINAL:
        if not isinstance(data.get("stop_reason"), str) or not data["stop_reason"].strip(): raise LoopError("terminal loop requires stop_reason")
        _stamp(data.get("finished_at"))
    return data

def _path(root, loop_id):
    root = Path(root)
    if root.is_symlink(): raise LoopError("repository root symlink is not allowed")
    folder = root
    for component in (".planning", "sdd-composy", "loops"):
        folder = folder / component
        if folder.is_symlink(): raise LoopError("loop state directory symlink is not allowed")
        folder.mkdir(exist_ok=True)
    path = folder / f"{loop_id}.json"
    if path.is_symlink(): raise LoopError("loop state symlink is not allowed")
    return path

def _publish(path, data):
    validate(data)
    if path.is_symlink(): raise LoopError("loop state symlink is not allowed")
    fd, tmp = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(data, stream, indent=2, sort_keys=True); stream.write("\n"); stream.flush(); os.fsync(stream.fileno())
        os.replace(tmp, path)
        try:
            dir_fd = os.open(path.parent, os.O_RDONLY)
            try: os.fsync(dir_fd)
            finally: os.close(dir_fd)
        except (AttributeError, OSError):
            # Directory fsync is unavailable on some platforms; file fsync and
            # atomic rename remain the portable durability floor.
            pass
    finally:
        if os.path.exists(tmp): os.unlink(tmp)
    return data

def start(root, task_id, max_iterations=3, loop_id=None, now=None):
    if not TASK_ID.fullmatch(task_id): raise LoopError("invalid task id")
    if max_iterations not in (1, 2, 3): raise LoopError("max_iterations must be 1, 2, or 3")
    loop_id = loop_id or f"loop-{task_id.lower()}"
    if not LOOP_ID.fullmatch(loop_id): raise LoopError("invalid loop id")
    path = _path(root, loop_id)
    if path.exists(): raise LoopError("loop already exists")
    stamp = now or _now(); data = {"schema_version":"1", "id":loop_id, "task_id":task_id,
        "status":"running", "iteration":0, "max_iterations":max_iterations,
        "started_at":stamp, "updated_at":stamp,
        "stages":[{"name": name, "status":"pending"} for name in LOOP_STAGES]}
    return _publish(path, data)

def _stage_records(data):
    records = data.get("stages")
    if not isinstance(records, list) or len(records) != len(LOOP_STAGES):
        raise LoopError("loop stage state is missing or stale")
    if [r.get("name") for r in records if isinstance(r, dict)] != list(LOOP_STAGES):
        raise LoopError("loop stage order is invalid")
    return records

def publish_stage(root, loop_id, stage, *, artifact, evidence, now=None):
    """Durably publish one stage, including the exact artifact/evidence binding."""
    data = status(root, loop_id)
    if data["status"] != "running": raise LoopError("only running loops can publish stages")
    records = _stage_records(data)
    if stage not in LOOP_STAGES: raise LoopError("invalid loop stage")
    index = LOOP_STAGES.index(stage)
    if any(r.get("status") == "pending" for r in records[:index]):
        raise LoopError("prior loop stage is incomplete")
    if any(r.get("status") == "complete" for r in records[index + 1:]):
        raise LoopError("cannot backfill stage after a later durable publication")
    # Validate already-published records before touching the current record;
    # an externally mutated ledger must fail closed at the write boundary.
    for existing in records[:index]:
        if existing.get("status") == "complete" and (
            "artifact" not in existing or "evidence" not in existing or
            existing.get("artifact_digest") != _digest(existing["artifact"]) or
            existing.get("evidence_digest") != _digest(existing["evidence"]) or
            not isinstance(existing["evidence"], dict) or
            existing["evidence"].get("status") not in SUCCESS_EVIDENCE
        ):
            raise LoopError("stale or unbound prior stage evidence")
    record = records[index]
    if record.get("status") == "complete":
        # Idempotent replay is allowed only when the caller presents the same
        # publication; a different payload indicates stale state.
        if record.get("artifact_digest") != _digest(artifact) or record.get("evidence_digest") != _digest(evidence):
            raise LoopError("stage publication conflicts with durable evidence")
        return data
    if not isinstance(artifact, dict) or not artifact: raise LoopError("stage artifact is required")
    if not isinstance(evidence, dict) or evidence.get("status") not in SUCCESS_EVIDENCE:
        raise LoopError("stage evidence is missing or not successful")
    stamp = now or _now(); _stamp(stamp)
    record.update(status="complete", artifact=artifact, evidence=evidence,
                  artifact_digest=_digest(artifact), evidence_digest=_digest(evidence), published_at=stamp)
    data["updated_at"] = stamp
    _publish(_path(root, loop_id), data)
    return data

def resume(root, loop_id):
    """Validate durable publications and return the exact next stage."""
    data = status(root, loop_id); records = _stage_records(data)
    completed = []
    for index, record in enumerate(records):
        if record.get("status") != "complete":
            if record.get("status") != "pending": raise LoopError("invalid stale stage status")
            if any(other.get("status") == "complete" for other in records[index+1:]):
                raise LoopError("loop stage state is stale or out of order")
            return {"loop_id": loop_id, "task_id": data["task_id"], "next_stage": LOOP_STAGES[index], "completed_stages": completed}
        if "artifact" not in record or "evidence" not in record or record.get("artifact_digest") != _digest(record["artifact"]) or record.get("evidence_digest") != _digest(record["evidence"]):
            raise LoopError("stale or unbound stage evidence")
        if record["evidence"].get("status") not in SUCCESS_EVIDENCE:
            raise LoopError("stage evidence is not successful")
        completed.append(LOOP_STAGES[index])
    return {"loop_id": loop_id, "task_id": data["task_id"], "next_stage": None, "completed_stages": completed}

def status(root, loop_id):
    path = _path(root, loop_id)
    try: data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc: raise LoopError(f"cannot read loop: {exc}") from exc
    return validate(data)

def continue_loop(root, loop_id, outcome="progress", now=None):
    data = status(root, loop_id)
    if data["status"] != "running": raise LoopError("only running loops can continue")
    if outcome not in {"progress", "complete", "missing_progress", "scope_expansion", "architectural_ambiguity", "destructive_action", "external_authorization", "environment_failure", "destructive_request", "scope_drift", "new_architecture", "repeated_environment_failure", "third_rejection", "identical_diff", "identical_failure"}: raise LoopError("invalid loop outcome")
    stamp = now or _now(); data["updated_at"] = stamp
    if outcome == "complete": data.update(status="completed", stop_reason="Completed", finished_at=stamp)
    elif outcome != "progress":
        action = "inspect the recorded stop reason and obtain human direction"
        if outcome == "environment_failure": action = "inspect runtime environment and retry"
        data.update(status=outcome, stop_reason=outcome, next_action=action, finished_at=stamp)
    else:
        data["iteration"] += 1
        if data["iteration"] >= data["max_iterations"]: data.update(status="iteration_cap", stop_reason="Iteration cap reached", finished_at=stamp)
    return _publish(_path(root, loop_id), data)

def cancel(root, loop_id, reason="Cancelled by user", now=None):
    data = status(root, loop_id)
    if data["status"] not in {"pending", "running"}: raise LoopError("only active loops can be cancelled")
    stamp = now or _now(); data.update(status="cancelled", stop_reason=reason, updated_at=stamp, finished_at=stamp)
    return _publish(_path(root, loop_id), data)

def orchestrate(root, task_id, engine, *, loop_id=None, max_iterations=3,
                human_approved=False, task_publish=None, trace_publish=None,
                cancel_check=None, now=None):
    """Run the five canonical stages through a validated runtime engine.

    ``engine`` receives a stage contract and returns the runtime result contract.
    Publication is performed only after the result is validated and successful;
    optional publishers receive the task/trace event and are never used to
    decide lifecycle state.  This keeps provider policy out of the core loop.
    """
    if not human_approved:
        raise LoopError("human approval is required")
    if loop_id:
        try:
            data = status(root, loop_id)
            if data["task_id"] != task_id: raise LoopError("loop task does not match requested task")
            if data["status"] != "running": return data
        except LoopError as exc:
            if "cannot read loop" not in str(exc):
                raise
            data = start(root, task_id, max_iterations=max_iterations, loop_id=loop_id, now=now)
    else:
        data = start(root, task_id, max_iterations=max_iterations, now=now)
    loop_id = data["id"]
    previous = None
    rejections = 0
    while True:
        if cancel_check and cancel_check():
            return cancel(root, loop_id, now=now)
        resume_state = resume(root, loop_id)
        stage = resume_state["next_stage"]
        if stage is None:
            return continue_loop(root, loop_id, outcome="complete", now=now)
        contract = {"stage": stage, "task_id": task_id, "iteration": data["iteration"] + 1}
        try:
            result = engine(contract)
        except Exception as exc:
            return continue_loop(root, loop_id, outcome="environment_failure", now=now)
        allowed = {"stage", "status", "message", "verdict", "evidence", "destructive", "destructive_request", "scope_changed", "scope_drift", "architecture_changed", "new_architecture", "environment_failure", "environment", "diff", "failure"}
        if not isinstance(result, dict) or not {"stage", "status", "message", "verdict", "evidence"}.issubset(result) or not set(result).issubset(allowed):
            raise LoopError("runtime engine returned invalid result contract")
        if result["stage"] != stage:
            raise LoopError("runtime result stage does not match requested stage")
        successful = result["status"] == "completed" and result["verdict"] in {"passed", "approved", "complete", "ok"}
        if successful:
            evidence = dict(result["evidence"])
            evidence.setdefault("status", "passed")
            publish_stage(root, loop_id, stage, artifact=result, evidence=evidence, now=now)
            event = {"task_id": task_id, "stage": stage, "result": result,
                     "iteration": data["iteration"] + 1}
            if task_publish: task_publish(event)
            if trace_publish: trace_publish(event)
            previous = result
            continue
        rejections += 1
        # `correction_decision` receives the number of rejected results before
        # the current one.  This keeps rejection_count=2 as the third-result
        # boundary while allowing the first two rejected results to request a
        # bounded correction.
        decision = correction_decision(previous or {}, result, rejection_count=rejections - 1)
        if decision["status"] == "needs_human":
            return continue_loop(root, loop_id, outcome=decision["reason"], now=now)
        if data["iteration"] + 1 >= max_iterations:
            return continue_loop(root, loop_id, outcome="progress", now=now)
        data = continue_loop(root, loop_id, outcome="progress", now=now)
        # A correction begins a fresh stage sequence; prior successful work is
        # retained in publications only within the iteration result, not reused.
        data["stages"] = [{"name": name, "status": "pending"} for name in LOOP_STAGES]
        _publish(_path(root, loop_id), data)
        previous = result

def main():
    p=argparse.ArgumentParser(); p.add_argument("--root", type=Path, default=Path.cwd()); sub=p.add_subparsers(dest="op", required=True)
    s=sub.add_parser("start"); s.add_argument("task_id"); s.add_argument("--max-iterations", type=int, default=3); s.add_argument("--loop-id")
    for name in ("status", "cancel"): sub.add_parser(name).add_argument("loop_id")
    c=sub.add_parser("continue"); c.add_argument("loop_id"); c.add_argument("--outcome", default="progress")
    args=p.parse_args()
    try:
        result = start(args.root,args.task_id,args.max_iterations,args.loop_id) if args.op=="start" else status(args.root,args.loop_id) if args.op=="status" else continue_loop(args.root,args.loop_id,args.outcome) if args.op=="continue" else cancel(args.root,args.loop_id)
        print(json.dumps(result, sort_keys=True)); return 0
    except LoopError as exc: print(json.dumps({"error":str(exc)}, sort_keys=True)); return 2
if __name__ == "__main__": raise SystemExit(main())
