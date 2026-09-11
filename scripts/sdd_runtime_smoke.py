#!/usr/bin/env python3
"""Offline and explicitly gated real-runtime acceptance harness for SDD Composy."""

from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import tempfile
import time
import sys
from typing import Any, Callable, Dict, Iterator, List, Optional, Sequence


RUNTIMES = ("hermes", "codex", "claude")
LANGUAGES = ("pt-BR", "en-US")
OFFLINE_SCENARIOS = ("read-only", "lifecycle", "fleet", "handoff", "evidence", "compose")
STATUSES = {"PASS", "FAIL", "BLOCKED", "NOT_RUN"}
DEFAULT_TIMEOUT = 300
DEFAULT_MAX_CALLS = 28


class SmokeBlocked(RuntimeError):
    """A prerequisite is absent; this is not evidence of a passing scenario."""


class InvocationBudget:
    def __init__(self, limit: int = DEFAULT_MAX_CALLS):
        if not 1 <= limit <= DEFAULT_MAX_CALLS:
            raise ValueError("max calls per runtime must be between 1 and 28")
        self.limit = limit
        self.counts = {runtime: 0 for runtime in RUNTIMES}

    def consume(self, runtime: str) -> None:
        if runtime not in self.counts:
            raise ValueError(f"unknown runtime: {runtime}")
        if self.counts[runtime] >= self.limit:
            raise SmokeBlocked(f"{runtime} call budget of {self.limit} reached")
        self.counts[runtime] += 1


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def tree_fingerprint(root: Path) -> str:
    _reject_symlink_ancestors(root)
    _reject_symlink_tree(root)
    digest = hashlib.sha256()
    for path in sorted(candidate for candidate in root.rglob("*") if candidate.is_file()):
        digest.update(path.relative_to(root).as_posix().encode())
        digest.update(b"\0")
        digest.update(sha256_path(path).encode())
        digest.update(b"\n")
    return digest.hexdigest()


def sanitize(value: str) -> str:
    value = re.sub(r"(?i)\b(token|password|secret|api[_-]?key)\s*[=:]\s*[^\s]+",
                   r"\1=[REDACTED]", value)
    value = re.sub(r"(?i)\bAuthorization:\s*Bearer\s+[^\s]+",
                   "Authorization: Bearer [REDACTED]", value)
    return re.sub(r"/(?:Users|home)/[^/\s]+", "/[USER]", value)


def run_process(command: Sequence[str], cwd: Path, timeout: float = DEFAULT_TIMEOUT) -> Dict[str, Any]:
    started = time.monotonic()
    process = subprocess.Popen(list(command), cwd=str(cwd), text=True,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               start_new_session=True)
    try:
        stdout, stderr = process.communicate(timeout=timeout)
        return {"status": "PASS" if process.returncode == 0 else "FAIL",
                "reason": None if process.returncode == 0 else "nonzero exit",
                "exit_code": process.returncode,
                "duration_seconds": round(time.monotonic() - started, 6),
                "stdout": sanitize(stdout), "stderr": sanitize(stderr)}
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGTERM)
        try:
            stdout, stderr = process.communicate(timeout=1)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            stdout, stderr = process.communicate()
        return {"status": "BLOCKED", "reason": "timeout", "exit_code": None,
                "duration_seconds": round(time.monotonic() - started, 6),
                "stdout": sanitize(stdout), "stderr": sanitize(stderr)}


def _secret_name(name: str) -> bool:
    lower = name.lower()
    # Samples/examples are documentation, not credentials. Everything else in
    # the common credential/key/certificate families is excluded fail-closed.
    if any(marker in lower for marker in (".example.", ".sample.", "-example.", "-sample.")):
        return False
    stem = Path(lower).stem
    return (lower.startswith(".env") or any(word in stem for word in
            ("credential", "secret", "token", "auth", "keystore", "truststore",
             "private-key", "private_key", "privatekey"))
            or lower.startswith("id_")
            or lower in {"id_rsa", "id_dsa"}
            or "private" in stem or Path(lower).suffix in {".key", ".pem", ".p12", ".pfx", ".crt", ".cer", ".cert", ".jks", ".der", ".ckey"})


def _reject_symlink_tree(root: Path) -> None:
    if root.is_symlink():
        raise SmokeBlocked(f"symlink is forbidden: {root}")
    for path in root.rglob("*"):
        if path.is_symlink():
            raise SmokeBlocked(f"symlink is forbidden: {path}")


def _reject_symlink_ancestors(path: Path) -> None:
    absolute = path.absolute()
    current = Path(absolute.anchor)
    for part in absolute.parts[1:]:
        current = current / part
        if current.is_symlink() and current not in {Path("/var"), Path("/tmp")}:
            raise SmokeBlocked(f"symlink path component is forbidden: {current}")
        if not current.exists():
            break


def _ignore_copy(_directory: str, names: List[str]) -> set:
    excluded = {".git", ".planning", ".worktrees", "fleet-logs", "fleet-results", "__pycache__"}
    return {name for name in names if name in excluded or _secret_name(name)}


@contextmanager
def isolated_fixture(plugin_root: Path, base_dir: Optional[Path] = None) -> Iterator[Path]:
    _reject_symlink_ancestors(plugin_root)
    if base_dir is not None:
        _reject_symlink_ancestors(base_dir)
    _reject_symlink_tree(plugin_root)
    root = Path(tempfile.mkdtemp(prefix="sdd-runtime-smoke-", dir=str(base_dir) if base_dir else None))
    try:
        shutil.copytree(plugin_root.resolve(), root / "plugin", ignore=_ignore_copy)
        (root / "src").mkdir()
        (root / "tests").mkdir()
        (root / "README.md").write_text("# SDD runtime smoke fixture\n", encoding="utf-8")
        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
        subprocess.run(["git", "add", "."], cwd=root, check=True)
        subprocess.run(["git", "-c", "user.name=SDD Smoke", "-c",
                        "user.email=sdd-smoke.invalid", "commit", "-qm", "fixture baseline"],
                       cwd=root, check=True)
        yield root
    finally:
        if root.exists():
            shutil.rmtree(root)


def validate_fixture_approval(approval: Dict[str, Any]) -> None:
    if (approval.get("status") != "APPROVED" or approval.get("synthetic") is not True
            or approval.get("scope") != "task-08-runtime-smoke"):
        raise SmokeBlocked("fixture contains invented approval without synthetic test scope")


def _selection(value: str, all_value: str, choices: Sequence[str]) -> Sequence[str]:
    return choices if value == all_value else (value,)


def _load_local(scripts: Path, filename: str, tag: str):
    if str(scripts) not in sys.path:
        sys.path.insert(0, str(scripts))
    spec = importlib.util.spec_from_file_location(f"sdd_smoke_{tag}_{time.time_ns()}", scripts / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _snapshot(root: Path) -> Dict[str, Any]:
    result = {}
    for path in sorted(root.rglob("*")):
        if ".git" in path.parts or path.is_symlink() or not path.is_file():
            continue
        result[path.relative_to(root).as_posix()] = [sha256_path(path), path.stat().st_mode & 0o777]
    return result


def _task_markdown(root: Path) -> Path:
    folder = root / "tasks/prd-smoke"; folder.mkdir(parents=True, exist_ok=True)
    path = folder / "task-001.md"
    path.write_text("""---
type: TASK
task:
  id: TASK-001
  title: Runtime smoke calculator
  state: pending
  dependencies: []
  acceptance_criteria:
    - CA-001
  verification_commands:
    - python3 -m unittest
  allowed_paths:
    - src/calculator.py
  evidence_required: true
---
""", encoding="utf-8")
    return folder


def _offline_lifecycle(root: Path, plugin: Path, language: str) -> Dict[str, Any]:
    scripts = plugin / "scripts"
    init = _load_local(scripts, "sdd_init.py", "init")
    mapper = _load_local(scripts, "sdd_map.py", "map")
    tasks = _load_local(scripts, "sdd_tasks.py", "tasks")
    loop = _load_local(scripts, "sdd_loop.py", "loop")
    execute = _load_local(scripts, "sdd_execute.py", "execute")
    plan = init.run_plan(root, "agent:sdd-runtime-smoke", plugin / "templates", language)
    applied = init.apply(root, plan, plugin / "templates")
    mapped = mapper.build_map(root)
    mapper.write_map(root, mapped)
    task_root = _task_markdown(root)
    projection_path = root / ".planning/sdd-composy/tasks/smoke.json"
    projection_path.parent.mkdir(parents=True, exist_ok=True)
    projection = tasks.import_tasks(task_root, projection_path, root=root)
    next_tasks = tasks.ready_tasks(projection)
    tasks.transition(projection, "TASK-001", "ready")
    loop_state = loop.start(root, "TASK-001", loop_id="loop-smoke")
    for stage in loop.LOOP_STAGES:
        if stage == "VERIFY":
            command = execute.run_command([sys.executable, "-c", "print('verified')"], cwd=root)
            command.update(task_id="TASK-001", loop_id=loop_state["id"])
            raw = json.dumps(command).encode()
            (root / "verify.json").write_bytes(raw)
            evidence = {"status": "passed", "command_record": {
                "path": "verify.json", "sha256": hashlib.sha256(raw).hexdigest()}}
        else:
            evidence = {"status": "passed"}
        loop.publish_stage(root, loop_state["id"], stage, artifact={"stage": stage}, evidence=evidence)
    completed = loop.continue_loop(root, loop_state["id"], outcome="complete")
    return {"passed": bool(applied.get("created")) and bool(mapped) and len(next_tasks) == 1
            and completed["status"] == "completed", "resources": [
                str(projection_path.relative_to(root)), ".planning/sdd-composy/loops/loop-smoke.json",
                "verify.json"], "command": ["sdd-init", "sdd-map", "sdd-tasks import/next", "sdd-loop"]}


def _cleanup_fleet(root: Path, records: List[Dict[str, Any]]) -> None:
    for record in records:
        worktree = Path(record["worktree_path"])
        subprocess.run(["git", "-C", str(root), "worktree", "remove", "--force", str(worktree)],
                       capture_output=True, check=False)
        subprocess.run(["git", "-C", str(root), "branch", "-D", record["branch"]],
                       capture_output=True, check=False)


def _offline_fleet(root: Path, plugin: Path, runtime: str) -> Dict[str, Any]:
    contracts = []
    for task_id, allowed in (("TASK-ADD", "src/addition.py"), ("TASK-SUB", "src/subtraction.py")):
        path = root / f"{task_id}.json"
        path.write_text(json.dumps({"id": task_id, "state": "ready", "dependencies": [],
            "acceptance_criteria": ["CA-001"], "verification_commands": ["true"],
            "allowed_paths": [allowed], "contract_path": str(path)}))
        contracts.append(path)
    base = subprocess.check_output(["git", "-C", str(root), "branch", "--show-current"], text=True).strip()
    requested = "claude" if runtime == "claude" else runtime
    command = [str(plugin / "scripts/fleet/launch.sh"), "--prepare-only", "--runtime", requested,
               "--root", str(root), "--fleet-id", "smoke", "--base-branch", base]
    for contract in contracts:
        command += ["--task", str(contract)]
    result = run_process(command, root)
    members_dir = root / ".planning/sdd-composy/fleet/smoke/members"
    member_paths = sorted(members_dir.glob("*.json"))
    records = [json.loads(path.read_text()) for path in member_paths]
    try:
        actual = records[0]["runtime"]
        requested = "codex" if actual == "hermes" else "hermes"
        fake = root / "mismatch-bin"; fake.mkdir()
        marker = fake / "invoked"
        for name in RUNTIMES:
            binary = fake / name
            binary.write_text(f"#!{sys.executable}\nfrom pathlib import Path\nPath({str(marker)!r}).touch()\nraise SystemExit(91)\n")
            binary.chmod(0o755)
        runner_env = {**os.environ, "PATH": str(fake) + os.pathsep + os.environ.get("PATH", ""),
                      "SDD_FLEET_MEMBER_FILE": str(member_paths[0])}
        runner = [str(plugin / "scripts/fleet/run.sh"), records[0]["slug"], records[0]["worktree_path"]]
        mismatch = subprocess.run(runner, cwd=root, env={**runner_env, "SDD_FLEET_RUNTIME": requested},
                                  text=True, capture_output=True, check=False)
        mismatch_invoked = marker.exists()
        matching = subprocess.run(runner, cwd=root, env={**runner_env, "SDD_FLEET_RUNTIME": actual},
                                  text=True, capture_output=True, check=False)
        passed = result["status"] == "PASS" and len(records) == 2
        passed = passed and len({row["worktree_path"] for row in records}) == 2
        diagnostic = mismatch.stderr
        canonical = "sdd-fleet-run: registered fleet member does not match canonical Git worktree registration\n"
        passed = (passed and mismatch.returncode == 2 and diagnostic == canonical
                  and not mismatch_invoked and canonical not in matching.stderr
                  and matching.returncode == 2
                  and matching.stderr == f"sdd-fleet-run: unsafe phase contract path for {records[0]['slug']}\n"
                  and not marker.exists())
        return {"passed": passed, "resources": [row["worktree_path"] for row in records],
                "command": command, "exit_code": result["exit_code"],
                "mismatch_requested_runtime": requested, "member_runtime": actual,
                "mismatch_diagnostic": diagnostic, "mismatch_stderr": mismatch.stderr,
                "matching_stderr": matching.stderr, "mismatch_provider_invoked": mismatch_invoked}
    finally:
        _cleanup_fleet(root, records)


def _offline_handoff(root: Path, plugin: Path,
                     approval: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    folder = root / ".planning/sdd-composy/handoff"; folder.mkdir(parents=True, exist_ok=True)
    approval = approval or {"status": "APPROVED", "synthetic": True,
                            "scope": "task-08-runtime-smoke"}
    validate_fixture_approval(approval)
    contract = {"task_id": "TASK-008", "gate": "APPROVED", "requirement_id": "RF-010",
                "approval": approval, "evidence": {"durable": True}}
    previous = folder / "seed.json"
    previous.write_text(json.dumps({"result": {"evidence": {"handoff": contract}}}))
    resources = []
    invocations = []
    adapters = ["hermes", "codex", "claude", "hermes"]
    for index, runtime in enumerate(adapters, 1):
        path = folder / f"{index}-{runtime}.json"
        capture = folder / f"{index}-invocation.json"
        executable = folder / f"{index}-{runtime}-fake"
        executable.write_text(f"#!{sys.executable}\n" + '''import json, os, sys
from pathlib import Path
runtime = Path(sys.argv[0]).name.split('-')[1]
args = sys.argv[1:]
if runtime == 'hermes':
    prompt = args[args.index('-z') + 1]
    request = json.loads(prompt[prompt.index('{'):])
elif runtime == 'codex':
    request = json.loads(args[-1])
else:
    request = json.loads(args[args.index('-p') + 1])
previous = Path(request['previous'])
value = json.loads(previous.read_text())['result']['evidence']['handoff']
result = {'stage': request['stage'], 'status': 'completed', 'message': 'offline durable consumer',
          'verdict': 'passed', 'evidence': {'handoff': value}}
Path(request['capture']).write_text(json.dumps({'argv': args, 'cwd': os.getcwd(),
    'runtime': runtime, 'consumed': str(previous)}))
if runtime == 'codex':
    Path(args[args.index('--output-last-message') + 1]).write_text(json.dumps(result))
    print(json.dumps({'type': 'thread.started'}))
elif runtime == 'claude':
    print(json.dumps({'type': 'result', 'subtype': 'success', 'is_error': False,
                      'result': json.dumps(result)}))
else:
    print(json.dumps(result))
''')
        executable.chmod(0o755)
        adapter = _load_local(plugin / "scripts", f"loop-engine-{runtime}.py", runtime)
        result = adapter.run({"stage": "EVIDENCE", "task_id": contract["task_id"],
                              "isolation_confirmed": True, "previous": str(previous),
                              "capture": str(capture)}, root, executable=str(executable))
        invocation = json.loads(capture.read_text())
        if (invocation["runtime"] != runtime or Path(invocation["cwd"]).resolve() != root.resolve()
                or invocation["consumed"] != str(previous)
                or result["evidence"]["handoff"] != contract):
            raise SmokeBlocked("handoff adapter consumption mismatch")
        path.write_text(json.dumps({"runtime": runtime, "result": result}, sort_keys=True))
        previous = path
        invocations.append(invocation)
        resources.append(str(path.relative_to(root)))
    return {"passed": True, "resources": resources, "adapters": adapters,
            "invocations": invocations, "command": ["loop-engine run", *adapters]}


def _offline_evidence(root: Path, plugin: Path) -> Dict[str, Any]:
    evidence = _load_local(plugin / "scripts", "sdd_evidence.py", "evidence")
    trace = _load_local(plugin / "scripts", "sdd_trace.py", "trace")
    status = _load_local(plugin / "scripts", "sdd_status.py", "evidence_status")
    log = root / "run.txt"; log.write_text("ok")
    data = {"prd_slug": "smoke", "task_id": "TASK-008", "entries": [{
        "requirement_id": "RF-010", "story_id": "US-010", "scenario_id": "SC-010",
        "criterion_id": "CA-010", "test_id": "TEST-010", "result": "passed",
        "evidence_type": "log", "path": "run.txt"}]}
    manifest_path = root / "manifest.json"
    manifest = evidence.build(data, root, manifest_path)
    valid = evidence.verify(manifest, root)["ok"]
    log.write_text("tampered")
    tampered = not evidence.verify(manifest, root)["ok"]
    log.unlink()
    absent = not evidence.verify(manifest, root)["ok"]
    stale = dict(manifest); stale["entries"] = [dict(manifest["entries"][0], sha256="0" * 64)]
    stale_detected = not evidence.verify(stale, root)["ok"]
    trace.record(root, {"actor_id": "agent:smoke", "type": "task.started", "stage": "EXECUTE",
                        "task_id": "TASK-008", "data": {}})
    trace.build(root, {"nodes": [{"id": "TASK-008"}], "links": []})
    projection = root / ".planning/sdd-composy/trace/trace.json"
    projection.write_text("{}")
    state_path = root / ".planning/sdd-composy/state.json"
    state_path.write_text(json.dumps({"stage": "EXECUTE", "trace": {"healthy": False}}))
    divergent = status.status(root)["status"] == "divergent"
    return {"passed": valid and tampered and absent and stale_detected and divergent,
            "resources": ["manifest.json", "run.txt", ".planning/sdd-composy/trace/trace.json"],
            "command": ["sdd-evidence build/verify", "sdd-trace/status divergence"]}


def _runtime_version(runtime: str) -> Optional[str]:
    executable = "claude" if runtime == "claude" else runtime
    if not shutil.which(executable):
        return None
    result = run_process([executable, "--version"], Path.cwd(), timeout=10)
    text = (result.get("stdout") or result.get("stderr") or "").splitlines()
    return text[0] if text else None


def _offline_compose(root: Path, plugin: Path) -> Dict[str, Any]:
    fake = root / "bin"; fake.mkdir(); docker = fake / "docker"
    docker.write_text("#!/bin/sh\nexit 0\n"); docker.chmod(0o755)
    cmux_bin = fake / "cmux"
    cmux_bin.write_text("""#!/bin/sh
case "$1" in
  new-workspace) echo '{"workspace_id":"w-smoke"}' ;;
  new-split) echo '{"surface_id":"s-smoke"}' ;;
  list-workspaces) echo '{"workspaces":[{"id":"w-smoke","owner":"sdd-composy","sdd_composy_fleet":"compose-smoke"}]}' ;;
esac
exit 0
""")
    cmux_bin.chmod(0o755)
    contract = root / "compose-task.json"
    contract.write_text(json.dumps({"id": "TASK-COMPOSE", "state": "ready", "dependencies": [],
        "acceptance_criteria": ["CA-001"], "verification_commands": ["true"],
        "allowed_paths": ["src/compose.py"], "contract_path": str(contract)}))
    base = subprocess.check_output(["git", "-C", str(root), "branch", "--show-current"], text=True).strip()
    command = [str(plugin / "scripts/fleet/launch.sh"), "--prepare-only", "--runtime", "codex",
               "--compose", "--root", str(root), "--fleet-id", "compose-smoke",
               "--base-branch", base, "--task", str(contract)]
    env = {**os.environ, "PATH": str(fake) + ":/usr/bin:/bin"}
    result = subprocess.run(command, cwd=root, env=env, text=True, capture_output=True)
    member_path = root / ".planning/sdd-composy/fleet/compose-smoke/members/TASK-COMPOSE.json"
    record = json.loads(member_path.read_text()) if member_path.exists() else {}
    compose = root / record.get("resources", {}).get("compose_file", "missing")
    handle = root / "cmux-handle.json"
    cmux_script = (f'export SDD_CMUX_BIN="{cmux_bin}" SDD_FLEET_ID=compose-smoke; '
                   f'source "{plugin / "scripts/fleet/ui-cmux.sh"}"; '
                   f'fleet_ui_cmux_start "{handle}" "{root}" smoke /usr/bin/true; '
                   f'fleet_ui_cmux_status "{handle}" running green; '
                   f'fleet_ui_cmux_teardown "{handle}"')
    cmux = subprocess.run(["bash", "-c", cmux_script], text=True, capture_output=True)
    try:
        passed = result.returncode == 0 and compose.is_file()
        passed = passed and record["resources"]["compose_sha256"] == sha256_path(compose)
        passed = passed and cmux.returncode == 0 and not handle.exists()
        subprocess.run(["git", "-C", str(root), "checkout", "-qb", "post-merge-smoke"], check=True)
        (root / "post-merge.txt").write_text("preserved")
        subprocess.run(["git", "-C", str(root), "add", "post-merge.txt"], check=True)
        subprocess.run(["git", "-C", str(root), "-c", "user.name=SDD Smoke", "-c",
                        "user.email=sdd-smoke.invalid", "commit", "-qm", "post merge fixture"], check=True)
        subprocess.run(["git", "-C", str(root), "checkout", "-q", base], check=True)
        merged = subprocess.run(["git", "-C", str(root), "-c", "user.name=SDD Smoke", "-c",
                                 "user.email=sdd-smoke.invalid", "merge", "--no-ff", "post-merge-smoke",
                                 "-m", "fixture merge"], capture_output=True)
        passed = passed and merged.returncode == 0 and (root / "post-merge.txt").read_text() == "preserved"
        return {"passed": passed, "resources": [str(compose.relative_to(root)), "cmux:w-smoke"],
                "command": command, "exit_code": result.returncode}
    finally:
        if record:
            _cleanup_fleet(root, [record])


def _offline_check(root: Path, plugin_root: Path, runtime: str, language: str,
                   scenario: str) -> Dict[str, Any]:
    started = time.monotonic()
    if scenario == "read-only":
        status = _load_local(plugin_root / "scripts", "sdd_status.py", "status")
        (root / "project.sentinel").write_bytes(b"project-sentinel")
        (root / "ui.sentinel").write_bytes(b"ui-sentinel")
        before = _snapshot(root)
        result = status.status(root, include_tasks=True, include_fleet=True)
        passed = result["read_only"] is True and _snapshot(root) == before
        outcome = {"passed": passed, "resources": ["project.sentinel", "ui.sentinel"],
                   "command": ["sdd-status", "--tasks", "--fleet"]}
    elif scenario == "lifecycle":
        outcome = _offline_lifecycle(root, plugin_root, language)
    elif scenario == "fleet":
        outcome = _offline_fleet(root, plugin_root, runtime)
    elif scenario == "handoff":
        outcome = _offline_handoff(root, plugin_root)
    elif scenario == "evidence":
        outcome = _offline_evidence(root, plugin_root)
    elif scenario == "compose":
        outcome = _offline_compose(root, plugin_root)
    else:
        outcome = {"passed": False, "resources": [], "command": []}
    payload = json.dumps(outcome, sort_keys=True, default=str).encode()
    return {"status": "PASS" if outcome["passed"] else "FAIL",
            "reason": None if outcome["passed"] else f"offline behavior failed for {scenario}",
            "exit_code": outcome.get("exit_code", 0),
            "duration_seconds": round(time.monotonic() - started, 6),
            "result_sha256": hashlib.sha256(payload).hexdigest(),
            "resources": outcome["resources"], "command": outcome["command"],
            "worktree": str(root), "version": _runtime_version(runtime),
            "provider": "offline-fixture", "model": None}


def _record(runtime: str, language: str, scenario: str, status: str,
            started_at: str, reason: Optional[str], plugin_hash: str,
            exit_code: Optional[int] = None, **measurements: Any) -> Dict[str, Any]:
    if status not in STATUSES:
        raise ValueError(f"invalid status: {status}")
    record = {"runtime": runtime, "version": None, "provider": None, "model": None,
            "language": language, "scenario": scenario, "status": status, "reason": reason,
            "started_at": started_at, "ended_at": utc_now(), "duration_seconds": None,
            "exit_code": exit_code, "plugin_sha256": plugin_hash, "result_sha256": None,
            "command": None, "resources": [], "usage": None, "task_id": "TASK-008",
            "worktree": None}
    for key in ("version", "provider", "model", "duration_seconds", "result_sha256",
                "command", "resources", "usage", "task_id", "worktree"):
        if key in measurements:
            record[key] = measurements[key]
    return record


def write_summary(output: Path, summary: Dict[str, Any]) -> None:
    _reject_symlink_ancestors(output)
    output.mkdir(parents=True, exist_ok=True)
    if output.is_symlink():
        raise SmokeBlocked("output directory may not be a symlink")
    target = output / "summary.json"
    handle, temporary_name = tempfile.mkstemp(prefix=".summary.", suffix=".tmp", dir=output)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(handle, "w", encoding="utf-8") as stream:
            json.dump(summary, stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, target)
    finally:
        if temporary.exists():
            temporary.unlink()


def run_acceptance(*, mode: str, runtime: str, language: str, scenario: str,
                   output: Path, plugin_root: Path,
                   provider_launcher: Optional[Callable[..., Dict[str, Any]]] = None,
                   max_calls_per_runtime: int = DEFAULT_MAX_CALLS,
                   fleet_acknowledged: bool = False) -> Dict[str, Any]:
    runtimes = _selection(runtime, "all", RUNTIMES)
    languages = _selection(language, "both", LANGUAGES)
    scenarios = OFFLINE_SCENARIOS if scenario == "all" else (scenario,)
    budget = InvocationBudget(max_calls_per_runtime)
    plugin_hash = tree_fingerprint(plugin_root)
    records = []
    for selected_runtime in runtimes:
        for selected_language in languages:
            for selected_scenario in scenarios:
                started_at = utc_now()
                if mode == "offline":
                    with isolated_fixture(plugin_root) as fixture:
                        outcome = _offline_check(fixture, fixture / "plugin", selected_runtime,
                                                 selected_language, selected_scenario)
                elif selected_scenario == "fleet" and not fleet_acknowledged:
                    outcome = {"status": "BLOCKED",
                               "reason": "external fleet acknowledgement is required"}
                elif provider_launcher is None:
                    outcome = {"status": "NOT_RUN",
                               "reason": "real provider launcher is unavailable in this phase"}
                else:
                    budget.consume(selected_runtime)
                    outcome = provider_launcher(runtime=selected_runtime,
                                                language=selected_language,
                                                scenario=selected_scenario,
                                                timeout=DEFAULT_TIMEOUT)
                records.append(_record(selected_runtime, selected_language, selected_scenario,
                                       outcome["status"], started_at, outcome.get("reason"),
                                       plugin_hash, outcome.get("exit_code"),
                                       **{key: value for key, value in outcome.items()
                                          if key not in {"status", "reason", "exit_code"}}))
    verdict = "PASS" if records and all(row["status"] == "PASS" for row in records) else (
        "FAIL" if any(row["status"] == "FAIL" for row in records) else "BLOCKED")
    summary = {"schema_version": 1, "mode": mode, "verdict": verdict,
               "started_at": records[0]["started_at"] if records else utc_now(),
               "ended_at": utc_now(), "plugin_sha256": plugin_hash,
               "provider_calls": budget.counts, "max_calls_per_runtime": max_calls_per_runtime,
               "timeout_seconds": DEFAULT_TIMEOUT, "usage": None, "scenarios": records}
    write_summary(output, summary)
    return summary


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("offline", "real"), required=True)
    parser.add_argument("--runtime", choices=(*RUNTIMES, "all"), required=True)
    parser.add_argument("--language", choices=(*LANGUAGES, "both"), required=True)
    parser.add_argument("--scenario", choices=("read-only", "lifecycle", "fleet", "all"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--max-calls-per-runtime", type=int, default=DEFAULT_MAX_CALLS)
    parser.add_argument("--provider-entry-point", choices=("production",))
    parser.add_argument("--acknowledge-real-fleet", action="store_true")
    return parser.parse_args(argv)


def production_provider_launcher(**_request: Any) -> Dict[str, Any]:
    """Explicit real entry point; callers reach it only after the external gate.

    Provider-specific invocation is deliberately a separately reviewed phase. Until that phase
    installs the validated adapter request, this entry point records NOT_RUN rather than guessing.
    """
    return {"status": "NOT_RUN", "reason": "production provider adapter is not enabled",
            "exit_code": None, "duration_seconds": 0.0, "result_sha256": None,
            "resources": [], "command": None}


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    root = Path(__file__).resolve().parents[1]
    launcher = production_provider_launcher if args.provider_entry_point == "production" else None
    summary = run_acceptance(mode=args.mode, runtime=args.runtime, language=args.language,
                             scenario=args.scenario, output=args.output,
                             plugin_root=root / "plugins/sdd-composy",
                             provider_launcher=launcher,
                             max_calls_per_runtime=args.max_calls_per_runtime,
                             fleet_acknowledged=args.acknowledge_real_fleet)
    print(json.dumps({"verdict": summary["verdict"],
                      "output": str(args.output / "summary.json")}))
    return 0 if summary["verdict"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
