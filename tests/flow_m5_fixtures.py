import json
import hashlib
import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional


def init_repository(root: Path) -> Path:
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    subprocess.run(["git", "-C", str(root), "config", "user.name", "Flow Test"], check=True)
    subprocess.run(
        ["git", "-C", str(root), "config", "user.email", "flow@example.invalid"],
        check=True,
    )
    (root / "README.md").write_text("# Fixture\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(root), "add", "README.md"], check=True)
    subprocess.run(["git", "-C", str(root), "commit", "-qm", "fixture"], check=True)
    return root


def create_approved_phase(repo: Path, slug: str, tracked: bool) -> None:
    phase = repo / ".planning" / "flow" / "phases" / slug
    phase.mkdir(parents=True, exist_ok=True)
    (phase / "spec.md").write_text(
        "# Demo specification\n\n"
        "- Status: APPROVED\n"
        "- Objective: exercise the fleet fixture\n",
        encoding="utf-8",
    )
    (phase / "decisions.md").write_text(
        "# Demo decisions\n\n"
        "- Status: APPROVED\n"
        "- Decision: keep fixture behavior isolated\n",
        encoding="utf-8",
    )
    if tracked:
        subprocess.run(
            [
                "git",
                "-C",
                str(repo),
                "add",
                ".planning/flow/phases/" + slug + "/spec.md",
                ".planning/flow/phases/" + slug + "/decisions.md",
            ],
            check=True,
        )
        subprocess.run(
            [
                "git",
                "-C",
                str(repo),
                "commit",
                "-qm",
                "fixture: approve " + slug,
            ],
            check=True,
        )


def write_executable(path: Path, body: str) -> None:
    path.write_text("#!/bin/sh\nset -eu\n" + body + "\n", encoding="utf-8")
    path.chmod(0o755)


def create_fleet_worktree(repository: Path, slug: str, worktree: Path) -> Path:
    create_approved_phase(repository, slug, tracked=True)
    ignore = repository / ".gitignore"
    ignore.write_text(
        ".planning/flow/fleet-status.json\n",
        encoding="utf-8",
    )
    subprocess.run(["git", "-C", str(repository), "add", ".gitignore"], check=True)
    subprocess.run(
        ["git", "-C", str(repository), "commit", "-qm", "fixture: ignore fleet status"],
        check=True,
    )
    subprocess.run(
        [
            "git",
            "-C",
            str(repository),
            "worktree",
            "add",
            "-q",
            "-b",
            f"flow-fleet/{slug}",
            str(worktree),
        ],
        check=True,
    )
    return worktree.resolve()


def write_registered_fleet_member(
    repository: Path,
    slug: str,
    worktree: Path,
    *,
    status: str = "ACTIVE",
) -> Path:
    canonical_worktree = worktree.resolve()
    member = repository.resolve() / ".planning" / "flow" / "fleet" / f"{slug}.json"
    member.parent.mkdir(parents=True, exist_ok=True)
    member.write_text(
        json.dumps(
            {
                "slug": slug,
                "branch": f"flow-fleet/{slug}",
                "worktree_path": str(canonical_worktree),
                "app_port": 3000,
                "db_port": 5432,
                "port_index": 0,
                "project_name": f"flow-fleet-{slug}",
                "tmux_window": f"pwdev-flow-fleet:{slug}",
                "compose_file": "docker-compose.flow-fleet.yml",
                "status": status,
                "created_at": "2026-08-16T00:00:00Z",
                "updated_at": "2026-08-16T00:00:00Z",
                "worktree_created": True,
                "docker_attempted": True,
                "tmux_attempted": True,
                "spec_sha256": hashlib.sha256(
                    (canonical_worktree / ".planning" / "flow" / "phases" / slug / "spec.md").read_bytes()
                ).hexdigest(),
                "decisions_sha256": hashlib.sha256(
                    (
                        canonical_worktree
                        / ".planning"
                        / "flow"
                        / "phases"
                        / slug
                        / "decisions.md"
                    ).read_bytes()
                ).hexdigest(),
                "initiating_root": str(repository.resolve()),
                "base_branch": subprocess.run(
                    ["git", "-C", str(repository), "symbolic-ref", "--quiet", "--short", "HEAD"],
                    check=True,
                    capture_output=True,
                    text=True,
                ).stdout.strip(),
                "base_commit": subprocess.run(
                    ["git", "-C", str(repository), "rev-parse", "HEAD"],
                    check=True,
                    capture_output=True,
                    text=True,
                ).stdout.strip(),
            }
        )
        + "\n",
        encoding="utf-8",
    )
    return member


def create_closed_command_path(root: Path, commands: tuple[str, ...]) -> Path:
    fake_bin = root / "bin"
    fake_bin.mkdir()
    for command in commands:
        executable = shutil.which(command)
        if executable is None:
            raise AssertionError(f"{command} is required for the fleet runner tests")
        write_executable(fake_bin / command, f'exec "{executable}" "$@"')
    return fake_bin


def write_fake_codex(path: Path) -> None:
    path.write_text(
        """#!/usr/bin/python3
import json
import os
import re
import signal
import subprocess
import sys
import time
from pathlib import Path

arguments = sys.argv[1:]
log_directory = Path(os.environ["FLOW_FAKE_CODEX_ARGS"])
log_directory.mkdir(parents=True, exist_ok=True)
counter_path = Path(os.environ["FLOW_FAKE_CODEX_COUNTER"])
call_number = int(counter_path.read_text(encoding="utf-8") or "0") + 1 if counter_path.exists() else 1
counter_path.write_text(str(call_number), encoding="utf-8")
(log_directory / f"{call_number:02d}.txt").write_text(
    "".join(f"{argument}\\n" for argument in arguments),
    encoding="utf-8",
)

orphan_call = os.environ.get("FLOW_FAKE_ORPHAN_CALL", "")
if orphan_call == str(call_number):
    orphan_code = (
        "import os,signal,time; from pathlib import Path; "
        "signal.signal(signal.SIGHUP, signal.SIG_IGN); "
        "signal.signal(signal.SIGTERM, signal.SIG_IGN); "
        "Path(os.environ['FLOW_FAKE_ORPHAN_PID']).write_text(str(os.getpid())); "
        "Path(os.environ['FLOW_FAKE_ORPHAN_READY']).write_text('ready'); "
        "time.sleep(120)"
    )
    subprocess.Popen([sys.executable, "-c", orphan_code])
    orphan_ready = Path(os.environ["FLOW_FAKE_ORPHAN_READY"])
    orphan_deadline = time.monotonic() + 5
    while not orphan_ready.exists() and time.monotonic() < orphan_deadline:
        time.sleep(0.01)
    if not orphan_ready.exists():
        raise SystemExit(94)

block_call = os.environ.get("FLOW_FAKE_BLOCK_CALL", "")
if block_call == str(call_number):
    Path(os.environ["FLOW_FAKE_BLOCK_READY"]).write_text("ready\\n", encoding="utf-8")
    release = Path(os.environ["FLOW_FAKE_BLOCK_RELEASE"])
    while not release.exists():
        time.sleep(0.01)

exit_call = os.environ.get("FLOW_FAKE_CODEX_EXIT_CALL", "")
if exit_call == str(call_number):
    raise SystemExit(int(os.environ.get("FLOW_FAKE_CODEX_EXIT_CODE", "17")))

result_index = arguments.index("--output-last-message") + 1
result_path = Path(arguments[result_index])
sequence = Path(os.environ["FLOW_FAKE_CODEX_SEQUENCE"]).read_text(encoding="utf-8").splitlines()
if call_number > len(sequence):
    raise SystemExit(91)
result_path.parent.mkdir(parents=True, exist_ok=True)
result_path.write_text(sequence[call_number - 1] + "\\n", encoding="utf-8")

prompt = arguments[-1]
match = re.search(r"FLOW_FLEET_STAGE=([a-z-]+)", prompt)
if not match:
    raise SystemExit(92)
stage = match.group(1)
skip_stage = os.environ.get("FLOW_FAKE_SKIP_ARTIFACT_STAGE", "")
skip_calls = {value for value in os.environ.get("FLOW_FAKE_SKIP_ARTIFACT_CALLS", "").split(",") if value}
if stage != skip_stage and str(call_number) not in skip_calls:
    worktree = Path(arguments[arguments.index("--cd") + 1])
    slug_match = re.search(r"FLOW_FLEET_SLUG=([a-z0-9-]+)", prompt)
    if not slug_match:
        raise SystemExit(93)
    phase = worktree / ".planning" / "flow" / "phases" / slug_match.group(1)
    artifacts = {
        "plan": phase / "plans" / "01-fleet-plan.md",
        "execute": phase / "execution" / "01-summary.md",
        "review": phase / "review" / "code-review.md",
        "verify": phase / "verify" / f"verify-{call_number:02d}.md",
        "execute-fix": phase / "execution" / f"fix-{call_number:02d}-summary.md",
        "review-fix": phase / "review" / f"fix-{call_number:02d}.md",
    }
    artifact = artifacts[stage]
    artifact.parent.mkdir(parents=True, exist_ok=True)
    artifact.write_text(f"# Fixture {stage} {call_number}\\n", encoding="utf-8")

branch_change_call = os.environ.get("FLOW_FAKE_BRANCH_CHANGE_CALL", "")
if branch_change_call == str(call_number):
    subprocess.run(
        ["git", "-C", str(worktree), "switch", "-q", "-c", f"fixture-branch-{call_number}"],
        check=True,
    )

print(json.dumps({"event": "fake-codex", "stage": stage}))
""",
        encoding="utf-8",
    )
    path.chmod(0o755)


def run_shell(
    script: Path,
    repository: Path,
    *args: str,
    env: Optional[dict[str, str]] = None,
) -> subprocess.CompletedProcess[str]:
    supplied_environment = {} if env is None else dict(env)
    clean_environment = supplied_environment.pop("FLOW_CLEAN_ENV", "") == "1"
    environment = {} if clean_environment else os.environ.copy()
    environment.update(supplied_environment)
    environment["LC_ALL"] = "C"
    return subprocess.run(
        ["/bin/bash", str(script), *args],
        cwd=repository,
        env=environment,
        check=False,
        capture_output=True,
        text=True,
    )
