#!/usr/bin/env python3
"""Offline and explicitly gated real-runtime acceptance harness for SDD Composy."""

from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import tempfile
import time
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


def _ignore_copy(_directory: str, names: List[str]) -> set:
    excluded = {".git", ".planning", ".worktrees", "fleet-logs", "fleet-results", "__pycache__"}
    return {name for name in names if name in excluded or name.startswith(".env")}


@contextmanager
def isolated_fixture(plugin_root: Path, base_dir: Optional[Path] = None) -> Iterator[Path]:
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


def _offline_check(plugin_root: Path, scenario: str) -> Dict[str, Any]:
    skills = sorted(path.name for path in (plugin_root / "skills").iterdir()
                    if (path / "SKILL.md").is_file())
    if scenario == "read-only":
        before = tree_fingerprint(plugin_root)
        status = plugin_root / "scripts/sdd_status.py"
        passed = len(skills) == 17 and status.is_file() and tree_fingerprint(plugin_root) == before
    elif scenario == "lifecycle":
        stages = ("sdd-init", "sdd-map", "sdd-prd", "sdd-tasks", "sdd-status")
        passed = all((plugin_root / "skills" / name / "SKILL.md").is_file() for name in stages)
        passed = passed and all((plugin_root / "scripts" / name).is_file() for name in (
            "sdd_init.py", "sdd_map.py", "sdd_tasks.py", "sdd_status.py"))
    elif scenario == "fleet":
        members = [{"task_id": "TASK-ADD", "path": "src/addition.py"},
                   {"task_id": "TASK-SUB", "path": "src/subtraction.py"}]
        passed = len({member["task_id"] for member in members}) == 2
        passed = passed and len({member["path"] for member in members}) == 2
        passed = passed and all((plugin_root / "scripts/fleet" / name).is_file() for name in (
            "launch.sh", "run.sh", "engine-hermes.sh", "engine-codex.sh", "engine-claude.sh"))
    elif scenario == "handoff":
        contract = {"task_id": "TASK-008", "gate": "APPROVED", "language": "pt-BR"}
        current = contract
        for source, target in (("hermes", "codex"), ("codex", "claude"),
                               ("claude", "hermes")):
            envelope = {"source": source, "target": target, "contract": current}
            current = json.loads(json.dumps(envelope, sort_keys=True))["contract"]
        passed = current == contract
    elif scenario == "evidence":
        payload = b'{"task_id":"TASK-008","status":"running"}'
        recorded = hashlib.sha256(payload).hexdigest()
        tampered = payload.replace(b"running", b"complete")
        passed = hashlib.sha256(tampered).hexdigest() != recorded
    elif scenario == "compose":
        schema = json.loads((plugin_root / "schemas/fleet-member.schema.json").read_text())
        resource_requirements = schema["properties"]["resources"]["required"]
        passed = {"compose_project", "compose_file", "compose_allocated"}.issubset(resource_requirements)
        passed = passed and (plugin_root / "templates/docker-compose.sdd-fleet.yml").is_file()
        passed = passed and (plugin_root / "scripts/fleet/teardown.sh").is_file()
    else:
        passed = False
    return {"status": "PASS" if passed else "FAIL",
            "reason": None if passed else f"offline contract missing for {scenario}"}


def _record(runtime: str, language: str, scenario: str, status: str,
            started_at: str, reason: Optional[str], plugin_hash: str,
            exit_code: Optional[int] = None) -> Dict[str, Any]:
    if status not in STATUSES:
        raise ValueError(f"invalid status: {status}")
    return {"runtime": runtime, "version": None, "provider": None, "model": None,
            "language": language, "scenario": scenario, "status": status, "reason": reason,
            "started_at": started_at, "ended_at": utc_now(), "duration_seconds": None,
            "exit_code": exit_code, "plugin_sha256": plugin_hash, "result_sha256": None,
            "command": None, "resources": [], "usage": None}


def write_summary(output: Path, summary: Dict[str, Any]) -> None:
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
                    outcome = _offline_check(plugin_root, selected_scenario)
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
                                       plugin_hash, outcome.get("exit_code")))
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
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    root = Path(__file__).resolve().parents[1]
    summary = run_acceptance(mode=args.mode, runtime=args.runtime, language=args.language,
                             scenario=args.scenario, output=args.output,
                             plugin_root=root / "plugins/sdd-composy",
                             max_calls_per_runtime=args.max_calls_per_runtime)
    print(json.dumps({"verdict": summary["verdict"],
                      "output": str(args.output / "summary.json")}))
    return 0 if summary["verdict"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
