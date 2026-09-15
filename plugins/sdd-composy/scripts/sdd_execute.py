"""Deterministic execution-contract boundary for sdd-execute."""
import hashlib, posixpath, re, subprocess, time
from pathlib import Path
SECRET = re.compile(r'(?i)(password|token|secret|api[_-]?key)(?:\s*[=:]\s*|\s*"\s*:\s*")([^,\s}\"]+)')
def _sanitize(v): return SECRET.sub(lambda m: m.group(1)+"=[REDACTED]", v)
def _base(t, outcome, transition, reason=None, next_action=None, **extra):
    out={"task_id":t.get("id"),"changed_paths":list(t.get("changed_paths",[])),"environment_ownership":t.get("environment_ownership","environment_unknown"),"cleanup_status":t.get("cleanup_status","pending"),"evidence_manifest":[],"outcome":outcome,"transition":transition,"next_action":next_action}
    if reason: out["reason"]=reason
    out.update(extra); return out
def _dependency_states(task, tasks):
    """Resolve dependency IDs (the schema shape) against the projection; legacy dicts carry their state."""
    by_id = {t.get("id"): t for t in (tasks or ()) if isinstance(t, dict)}
    for dependency in task.get("dependencies", []):
        yield dependency.get("state") if isinstance(dependency, dict) else by_id.get(dependency, {}).get("state")
def _within(path, allowed):
    normalized = posixpath.normpath(path)
    if normalized.startswith("../") or normalized in ("..", ".") or posixpath.isabs(normalized): return False
    return any(normalized == a.rstrip("/") or normalized.startswith(a.rstrip("/") + "/") for a in allowed)
def preflight(task, *, tasks=None, red_evidence=False, changed_paths=(), environment="environment_owned", human_approved=False):
    t=dict(task); t["changed_paths"]=list(changed_paths); t["environment_ownership"]=environment
    if t.get("state")!="ready": return _base(t,"blocked","blocked","not_ready","move task to ready")
    if not human_approved: return _base(t,"blocked","blocked","human_approval_missing","obtain explicit human approval")
    if any(state!="complete" for state in _dependency_states(t, tasks)): return _base(t,"blocked","blocked","dependency_missing","complete dependencies")
    if not red_evidence: return _base(t,"blocked","blocked","tdd_missing","record failing test evidence")
    if environment=="environment_unknown": return _base(t,"blocked","blocked","environment_unknown","declare environment ownership")
    outside=[p for p in changed_paths if not _within(p, t.get("allowed_paths",()))]
    if outside: return _base(t,"rejected","rejected","path_violation","change only approved paths",paths=outside)
    return _base(t,"ready","running",next_action="execute declared commands")
def run_command(command, *, cwd, runner=subprocess.run, evidence_path="evidence/command.json"):
    path=Path(evidence_path)
    if path.is_absolute() or ".." in path.parts or path.is_symlink(): raise ValueError("evidence path must be confined and non-symlink")
    started=time.time()
    try:
        r=runner(command,cwd=str(cwd),capture_output=True,text=True,check=False); out,err=_sanitize(r.stdout),_sanitize(r.stderr); status="passed" if r.returncode==0 else "command_failed"
        return {"command":command,"status":status,"exit_code":r.returncode,"started_at":started,"ended_at":time.time(),"stdout":out,"stderr":err,"sha256":hashlib.sha256((out+"\n"+err).encode()).hexdigest(),"evidence_path":str(path)}
    except FileNotFoundError: return {"command":command,"status":"command_unavailable","exit_code":None,"started_at":started,"ended_at":time.time(),"stdout":"","stderr":"","sha256":hashlib.sha256(b"\n").hexdigest(),"evidence_path":str(path)}
def finish(result, evidence, *, cleanup_status="cleaned"):
    if result["outcome"]!="ready": return result
    if not evidence: return {**result,"outcome":"blocked","transition":"blocked","reason":"evidence_missing","next_action":"run declared verification commands","cleanup_status":cleanup_status}
    failed=next((e for e in evidence if e["status"]!="passed"),None)
    if failed: return {**result,"outcome":"blocked","transition":"blocked","reason":failed["status"],"next_action":"resolve command evidence","evidence_manifest":evidence,"cleanup_status":cleanup_status}
    if cleanup_status!="cleaned": return {**result,"outcome":"blocked","transition":"blocked","reason":"cleanup_failed","next_action":"clean owned services","evidence_manifest":evidence,"cleanup_status":cleanup_status}
    return {**result,"outcome":"success","transition":"qa_required","next_action":"perform QA","evidence_manifest":evidence,"cleanup_status":cleanup_status}
