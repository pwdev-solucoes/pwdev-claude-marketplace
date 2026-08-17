import json
import os
import shutil
import signal
import subprocess
import tempfile
import time
import unittest
from pathlib import Path
from typing import Union

from tests.flow_m5_fixtures import (
    create_closed_command_path,
    create_fleet_worktree,
    init_repository,
    run_shell,
    write_fake_codex,
    write_executable,
    write_registered_fleet_member,
)


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "plugins" / "pwdev-flow" / "scripts" / "fleet-run.sh"
DASHBOARD = ROOT / "plugins" / "pwdev-flow" / "scripts" / "fleet-dashboard.sh"
SCHEMA = ROOT / "plugins" / "pwdev-flow" / "templates" / "fleet-result.schema.json"
SAFE_COMMANDS = (
    "awk",
    "date",
    "git",
    "jq",
    "mkdir",
    "mktemp",
    "mv",
    "python3",
    "rm",
    "rmdir",
    "shasum",
    "sleep",
)


def stage_result(
    stage: str,
    *,
    status: str = "OK",
    message: str = "fixture stage complete",
    verdict: str = "NONE",
) -> dict[str, str]:
    return {"stage": stage, "status": status, "message": message, "verdict": verdict}


class FleetRunnerContractTest(unittest.TestCase):
    def runner_fixture(
        self,
        root: Path,
        sequence: list[Union[dict[str, str], str]],
        *,
        skip_artifact_stage: str = "",
        skip_artifact_calls: str = "",
    ) -> tuple[Path, Path, dict[str, str]]:
        repository = init_repository(root / "repo")
        worktree = create_fleet_worktree(repository, "demo", root / "repo-fleet-demo")
        write_registered_fleet_member(repository, "demo", worktree)
        fake_bin = create_closed_command_path(root, SAFE_COMMANDS)
        write_fake_codex(fake_bin / "codex")
        sequence_path = root / "codex-results.jsonl"
        sequence_path.write_text(
            "\n".join(item if isinstance(item, str) else json.dumps(item) for item in sequence)
            + "\n",
            encoding="utf-8",
        )
        environment = {
            "FLOW_CLEAN_ENV": "1",
            "PATH": str(fake_bin),
            "FLOW_FAKE_CODEX_ARGS": str(root / "codex-arguments"),
            "FLOW_FAKE_CODEX_COUNTER": str(root / "codex-counter"),
            "FLOW_FAKE_CODEX_SEQUENCE": str(sequence_path),
            "FLOW_FAKE_SKIP_ARTIFACT_STAGE": skip_artifact_stage,
            "FLOW_FAKE_SKIP_ARTIFACT_CALLS": skip_artifact_calls,
        }
        return repository, worktree, environment

    def run_fleet(
        self,
        repository: Path,
        worktree: Path,
        environment: dict[str, str],
    ) -> subprocess.CompletedProcess[str]:
        return run_shell(RUNNER, repository, "demo", str(worktree), env=environment)

    def argument_calls(self, root: Path) -> list[list[str]]:
        return [
            path.read_text(encoding="utf-8").splitlines()
            for path in sorted((root / "codex-arguments").glob("*.txt"))
        ]

    def assert_structured_dangerous_call(self, arguments: list[str], worktree: Path) -> None:
        self.assertEqual(len(arguments), 10)
        self.assertEqual(arguments[0], "exec")
        self.assertEqual(arguments[1], "--dangerously-bypass-approvals-and-sandbox")
        self.assertEqual(arguments[2], "--ephemeral")
        self.assertEqual(arguments[3:5], ["--cd", str(worktree)])
        self.assertEqual(arguments[5:7], ["--output-schema", str(SCHEMA)])
        self.assertEqual(arguments[7], "--output-last-message")
        self.assertTrue(arguments[8].startswith(str(worktree / ".planning/flow/fleet-results")))
        for flag in (
            "--dangerously-bypass-approvals-and-sandbox",
            "--ephemeral",
            "--cd",
            "--output-schema",
            "--output-last-message",
        ):
            self.assertEqual(arguments.count(flag), 1)

    def read_status(self, worktree: Path) -> dict[str, str]:
        return json.loads(
            (worktree / ".planning" / "flow" / "fleet-status.json").read_text(
                encoding="utf-8"
            )
        )

    def commit_count(self, worktree: Path) -> int:
        return int(
            subprocess.run(
                ["git", "-C", str(worktree), "rev-list", "--count", "HEAD"],
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
        )

    def seed_stale_artifact(self, worktree: Path, relative: str) -> None:
        artifact = worktree / relative
        artifact.parent.mkdir(parents=True, exist_ok=True)
        artifact.write_text("# stale fixture\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(worktree), "add", relative], check=True)
        subprocess.run(
            ["git", "-C", str(worktree), "commit", "-qm", "fixture: stale artifact"],
            check=True,
        )

    def install_mv_failures(
        self,
        root: Path,
        environment: dict[str, str],
        *,
        status_fail_at: int = 0,
        result_publish_failure: bool = False,
    ) -> None:
        actual_mv = shutil.which("mv")
        self.assertIsNotNone(actual_mv)
        environment.update(
            {
                "FLOW_FAKE_STATUS_MV_COUNT": str(root / "status-mv-count"),
                "FLOW_FAKE_STATUS_MV_FAIL_AT": str(status_fail_at),
                "FLOW_FAKE_RESULT_MV_FAIL": "1" if result_publish_failure else "0",
                "FLOW_FAKE_RESULT_MV_SENTINEL": str(root / "result-mv-failure-reached"),
            }
        )
        write_executable(
            root / "bin" / "mv",
            'case "${1:-}" in\n'
            '  */fleet-results/.*.json.*)\n'
            '    if [ "$FLOW_FAKE_RESULT_MV_FAIL" = 1 ]; then : > "$FLOW_FAKE_RESULT_MV_SENTINEL"; exit 43; fi ;;\n'
            '  */.planning/flow/.fleet-status.json.*)\n'
            '    count=0; if [ -f "$FLOW_FAKE_STATUS_MV_COUNT" ]; then IFS= read -r count < "$FLOW_FAKE_STATUS_MV_COUNT"; fi\n'
            '    count=$((count + 1)); printf "%s\\n" "$count" > "$FLOW_FAKE_STATUS_MV_COUNT"\n'
            '    [ "$count" = "$FLOW_FAKE_STATUS_MV_FAIL_AT" ] && exit 44 ;;\n'
            'esac\n'
            f'exec "{actual_mv}" "$@"',
        )

    def success_sequence(self) -> list[dict[str, str]]:
        return [
            stage_result("plan"),
            stage_result("execute"),
            stage_result("review"),
            stage_result("verify", verdict="APPROVED"),
        ]

    def test_symlinked_runner_parent_and_member_are_rejected_before_codex(self) -> None:
        for target in ("log-parent", "central-member"):
            with self.subTest(target=target), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                repository, worktree, environment = self.runner_fixture(
                    root, self.success_sequence()
                )
                outside = root / "outside"
                outside.mkdir()
                sentinel = outside / "sentinel.txt"
                sentinel.write_bytes(b"outside-bytes\n")
                if target == "log-parent":
                    (worktree / ".planning" / "flow" / "fleet-logs").symlink_to(
                        outside, target_is_directory=True
                    )
                else:
                    member = repository / ".planning" / "flow" / "fleet" / "demo.json"
                    outside_member = outside / "member.json"
                    member.rename(outside_member)
                    member.symlink_to(outside_member)

                result = self.run_fleet(repository, worktree, environment)

                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertEqual(sentinel.read_bytes(), b"outside-bytes\n")
                self.assertFalse((root / "codex-counter").exists())
                self.assertFalse((root / "codex-arguments").exists())

    def test_success_runs_four_stages_with_dangerous_ephemeral_structured_args(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository, worktree, environment = self.runner_fixture(root, self.success_sequence())

            result = self.run_fleet(repository, worktree, environment)

            self.assertEqual(result.returncode, 0, result.stderr)
            calls = self.argument_calls(root)
            self.assertEqual(len(calls), 4)
            for arguments in calls:
                self.assert_structured_dangerous_call(arguments, worktree)
            prompts = [arguments[-1] for arguments in calls]
            self.assertEqual(
                [next(skill for skill in ("$flow-plan", "$flow-execute", "$flow-review", "$flow-verify") if skill in prompt) for prompt in prompts],
                ["$flow-plan", "$flow-execute", "$flow-review", "$flow-verify"],
            )

    def test_runner_emits_sanitized_stage_audit_only_after_published_outcomes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository, worktree, environment = self.runner_fixture(
                root, self.success_sequence()
            )
            config = repository / ".planning" / "flow" / "config.json"
            config.write_text(json.dumps({"audit": True}), encoding="utf-8")

            result = self.run_fleet(repository, worktree, environment)

            self.assertEqual(result.returncode, 0, result.stderr)
            audit_file = repository / ".planning" / "flow" / "audit" / "events.jsonl"
            events = [json.loads(line) for line in audit_file.read_text(encoding="utf-8").splitlines()]
            stage_events = [event for event in events if event["action"] == "fleet_stage"]
            self.assertEqual(
                [event["phase"] for event in stage_events],
                ["plan", "execute", "review", "verify", "verify"],
            )
            self.assertEqual(
                [event["status"] for event in stage_events],
                ["ACTIVE", "ACTIVE", "ACTIVE", "ACTIVE", "DONE"],
            )
            serialized = json.dumps(stage_events)
            for prohibited in (str(worktree), "danger-full-access", "FLOW_FLEET_STAGE", "model", "prompt"):
                self.assertNotIn(prohibited, serialized)

    def test_success_commits_stage_changes_and_marks_done(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository, worktree, environment = self.runner_fixture(root, self.success_sequence())
            baseline = subprocess.run(
                ["git", "-C", str(worktree), "rev-list", "--count", "HEAD"],
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()

            result = self.run_fleet(repository, worktree, environment)

            self.assertEqual(result.returncode, 0, result.stderr)
            final_count = subprocess.run(
                ["git", "-C", str(worktree), "rev-list", "--count", "HEAD"],
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
            self.assertEqual(int(final_count) - int(baseline), 4)
            subjects = subprocess.run(
                ["git", "-C", str(worktree), "log", "-4", "--format=%s"],
                check=True,
                capture_output=True,
                text=True,
            ).stdout.splitlines()
            self.assertEqual(
                subjects,
                [
                    "chore(flow-fleet): demo verify",
                    "chore(flow-fleet): demo review",
                    "chore(flow-fleet): demo execute",
                    "chore(flow-fleet): demo plan",
                ],
            )
            status = self.read_status(worktree)
            self.assertEqual(status["stage"], "verify")
            self.assertEqual(status["status"], "DONE")
            self.assertEqual(status["verdict"], "APPROVED")

    def test_invalid_json_marks_needs_human(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository, worktree, environment = self.runner_fixture(root, ["{broken"])
            baseline = self.commit_count(worktree)

            result = self.run_fleet(repository, worktree, environment)

            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(len(self.argument_calls(root)), 1)
            status = self.read_status(worktree)
            self.assertEqual(status["stage"], "plan")
            self.assertEqual(status["status"], "NEEDS_HUMAN")
            self.assertIn("invalid structured result", status["message"])
            self.assertEqual(self.commit_count(worktree), baseline)

    def test_failed_status_marks_needs_human(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository, worktree, environment = self.runner_fixture(
                root,
                [stage_result("plan", status="FAILED", message="planning cannot continue")],
            )
            baseline = self.commit_count(worktree)

            result = self.run_fleet(repository, worktree, environment)

            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(len(self.argument_calls(root)), 1)
            status = self.read_status(worktree)
            self.assertEqual(status["status"], "NEEDS_HUMAN")
            self.assertEqual(status["message"], "planning cannot continue")
            self.assertEqual(self.commit_count(worktree), baseline)

    def test_three_rejections_stop_after_two_fix_cycles(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sequence = [
                stage_result("plan"),
                stage_result("execute"),
                stage_result("review"),
                stage_result("verify", verdict="REJECTED"),
                stage_result("execute-fix"),
                stage_result("review-fix"),
                stage_result("verify", verdict="REJECTED"),
                stage_result("execute-fix"),
                stage_result("review-fix"),
                stage_result("verify", verdict="REJECTED", message="still rejected"),
            ]
            repository, worktree, environment = self.runner_fixture(root, sequence)

            result = self.run_fleet(repository, worktree, environment)

            self.assertNotEqual(result.returncode, 0)
            calls = self.argument_calls(root)
            self.assertEqual(len(calls), 10)
            for arguments in calls:
                self.assert_structured_dangerous_call(arguments, worktree)
            prompts = [arguments[-1] for arguments in calls]
            self.assertEqual(sum("FLOW_FLEET_STAGE=verify" in prompt for prompt in prompts), 3)
            self.assertEqual(sum("FLOW_FLEET_STAGE=execute-fix" in prompt for prompt in prompts), 2)
            self.assertEqual(sum("FLOW_FLEET_STAGE=review-fix" in prompt for prompt in prompts), 2)
            self.assertEqual(
                [
                    next(
                        stage
                        for stage in (
                            "plan",
                            "execute-fix",
                            "execute",
                            "review-fix",
                            "review",
                            "verify",
                        )
                        if f"FLOW_FLEET_STAGE={stage}" in prompt
                    )
                    for prompt in prompts
                ],
                [
                    "plan",
                    "execute",
                    "review",
                    "verify",
                    "execute-fix",
                    "review-fix",
                    "verify",
                    "execute-fix",
                    "review-fix",
                    "verify",
                ],
            )
            for index in (4, 7):
                self.assertIn("$flow-execute --fix", prompts[index])
                self.assertIn("bounded correction", prompts[index])
            for index in (5, 8):
                self.assertIn("$flow-review", prompts[index])
                self.assertIn("current correction cycle", prompts[index])
            status = self.read_status(worktree)
            self.assertEqual(status["stage"], "verify")
            self.assertEqual(status["status"], "NEEDS_HUMAN")
            self.assertIn("two correction cycles", status["message"])

    def test_missing_expected_plan_artifact_halts_pipeline(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository, worktree, environment = self.runner_fixture(
                root,
                [stage_result("plan")],
                skip_artifact_stage="plan",
            )
            baseline = self.commit_count(worktree)

            result = self.run_fleet(repository, worktree, environment)

            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(len(self.argument_calls(root)), 1)
            status = self.read_status(worktree)
            self.assertEqual(status["stage"], "plan")
            self.assertEqual(status["status"], "NEEDS_HUMAN")
            self.assertIn("missing fresh plan artifact", status["message"])
            self.assertEqual(self.commit_count(worktree), baseline)

    def test_done_and_needs_human_local_states_refuse_real_rerun(self) -> None:
        cases = (
            ("DONE", self.success_sequence()),
            ("NEEDS_HUMAN", ["{broken"]),
        )
        for expected_state, sequence in cases:
            with self.subTest(state=expected_state), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                repository, worktree, environment = self.runner_fixture(root, sequence)

                first = self.run_fleet(repository, worktree, environment)

                if expected_state == "DONE":
                    self.assertEqual(first.returncode, 0, first.stderr)
                else:
                    self.assertNotEqual(first.returncode, 0)
                calls_before = len(self.argument_calls(root))
                commits_before = self.commit_count(worktree)
                self.assertEqual(self.read_status(worktree)["status"], expected_state)

                rerun = self.run_fleet(repository, worktree, environment)

                self.assertNotEqual(rerun.returncode, 0)
                self.assertIn(f"local fleet status {expected_state} is not startable", rerun.stderr)
                self.assertEqual(len(self.argument_calls(root)), calls_before)
                self.assertEqual(self.commit_count(worktree), commits_before)

    def test_running_active_and_malformed_local_states_refuse_start(self) -> None:
        for local_state in ("RUNNING", "ACTIVE", "MALFORMED"):
            with self.subTest(state=local_state), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                repository, worktree, environment = self.runner_fixture(
                    root, self.success_sequence()
                )
                status_file = worktree / ".planning/flow/fleet-status.json"
                if local_state == "MALFORMED":
                    status_file.write_text("{broken\n", encoding="utf-8")
                else:
                    status_file.write_text(
                        json.dumps(
                            {
                                "slug": "demo",
                                "stage": "plan",
                                "status": local_state,
                                "message": "persisted local fixture",
                                "verdict": "NONE",
                                "updated_at": "2026-08-16T00:00:00Z",
                                "correction_cycles": 0,
                            }
                        )
                        + "\n",
                        encoding="utf-8",
                    )
                baseline = self.commit_count(worktree)

                result = self.run_fleet(repository, worktree, environment)

                self.assertNotEqual(result.returncode, 0)
                if local_state == "MALFORMED":
                    self.assertIn("local fleet status is malformed", result.stderr)
                else:
                    self.assertIn(
                        f"local fleet status {local_state} is not startable",
                        result.stderr,
                    )
                self.assertEqual(self.argument_calls(root), [])
                self.assertEqual(self.commit_count(worktree), baseline)

    def test_foreign_lookalike_worktree_is_refused_before_codex(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository, _, environment = self.runner_fixture(root, self.success_sequence())
            foreign = init_repository(root / "foreign")
            foreign_worktree = create_fleet_worktree(
                foreign, "demo", root / "foreign-fleet-demo"
            )

            result = self.run_fleet(repository, foreign_worktree, environment)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("registered fleet member", result.stderr)
            self.assertEqual(self.argument_calls(root), [])

    def test_registered_worktree_uses_its_own_main_root_as_authority(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            invoking_repository, _, environment = self.runner_fixture(
                root, self.success_sequence()
            )
            authoritative_repository = init_repository(root / "authoritative")
            authoritative_worktree = create_fleet_worktree(
                authoritative_repository,
                "demo",
                root / "authoritative-fleet-demo",
            )
            write_registered_fleet_member(
                authoritative_repository,
                "demo",
                authoritative_worktree,
            )

            result = self.run_fleet(
                invoking_repository,
                authoritative_worktree,
                environment,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(len(self.argument_calls(root)), 4)
            self.assertEqual(self.read_status(authoritative_worktree)["status"], "DONE")

    def test_terminal_running_and_invalid_central_states_are_refused(self) -> None:
        for central_status in ("DONE", "NEEDS_HUMAN", "RUNNING", "BROKEN"):
            with self.subTest(status=central_status), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                repository, worktree, environment = self.runner_fixture(
                    root, self.success_sequence()
                )
                write_registered_fleet_member(
                    repository, "demo", worktree, status=central_status
                )

                result = self.run_fleet(repository, worktree, environment)

                self.assertNotEqual(result.returncode, 0)
                self.assertIn("central member status", result.stderr)
                self.assertEqual(self.argument_calls(root), [])

    def test_existing_member_runner_lock_refuses_concurrent_run(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository, worktree, environment = self.runner_fixture(root, self.success_sequence())
            lock = repository / ".planning" / "flow" / "fleet" / ".demo.runner.lock"
            lock.mkdir()

            result = self.run_fleet(repository, worktree, environment)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("already running", result.stderr)
            self.assertEqual(self.argument_calls(root), [])

    def test_second_process_is_refused_while_first_runner_holds_member_lock(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository, worktree, environment = self.runner_fixture(
                root, [stage_result("plan")]
            )
            ready = root / "concurrent-ready"
            release = root / "concurrent-release"
            environment.update(
                {
                    "FLOW_FAKE_BLOCK_CALL": "1",
                    "FLOW_FAKE_BLOCK_READY": str(ready),
                    "FLOW_FAKE_BLOCK_RELEASE": str(release),
                    "LC_ALL": "C",
                }
            )
            first = subprocess.Popen(
                ["/bin/bash", str(RUNNER), "demo", str(worktree)],
                cwd=repository,
                env=environment,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                start_new_session=True,
            )
            try:
                deadline = time.monotonic() + 5
                while not ready.exists() and time.monotonic() < deadline:
                    time.sleep(0.01)
                self.assertTrue(ready.exists(), "first fake Codex call did not block")

                second = self.run_fleet(repository, worktree, environment)

                self.assertNotEqual(second.returncode, 0)
                self.assertIn("already running", second.stderr)
                self.assertEqual(len(self.argument_calls(root)), 1)
            finally:
                if first.poll() is None:
                    os.killpg(first.pid, signal.SIGTERM)
                first.communicate(timeout=5)

    def test_post_codex_branch_switch_is_refused_without_stage_commit(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository, worktree, environment = self.runner_fixture(
                root, [stage_result("plan")]
            )
            environment["FLOW_FAKE_BRANCH_CHANGE_CALL"] = "1"
            baseline = self.commit_count(worktree)

            result = self.run_fleet(repository, worktree, environment)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("fleet worktree changed after Codex", result.stderr)
            self.assertEqual(self.commit_count(worktree), baseline)
            self.assertEqual(self.read_status(worktree)["status"], "NEEDS_HUMAN")

    def test_contract_modification_after_launch_stops_before_dangerous_invocation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository, worktree, environment = self.runner_fixture(
                root, self.success_sequence()
            )
            spec = worktree / ".planning" / "flow" / "phases" / "demo" / "spec.md"
            spec.write_text(spec.read_text(encoding="utf-8") + "\npost-launch change\n", encoding="utf-8")

            result = self.run_fleet(repository, worktree, environment)

            self.assertNotEqual(result.returncode, 0)
            self.assertFalse((root / "codex-counter").exists())
            self.assertFalse((root / "codex-arguments").exists())
            status = self.read_status(worktree)
            self.assertEqual(status["status"], "NEEDS_HUMAN")
            self.assertIn("contract", status["message"])

    def test_each_stage_requires_a_fresh_artifact_even_when_stale_artifacts_exist(self) -> None:
        cases = (
            (
                "execute",
                [stage_result("plan"), stage_result("execute")],
                2,
                ".planning/flow/phases/demo/execution/stale.md",
            ),
            (
                "review",
                [stage_result("plan"), stage_result("execute"), stage_result("review")],
                3,
                ".planning/flow/phases/demo/review/stale.md",
            ),
            (
                "verify",
                [
                    stage_result("plan"),
                    stage_result("execute"),
                    stage_result("review"),
                    stage_result("verify", verdict="APPROVED"),
                ],
                4,
                ".planning/flow/phases/demo/verify/stale.md",
            ),
            (
                "execute-fix",
                [
                    stage_result("plan"),
                    stage_result("execute"),
                    stage_result("review"),
                    stage_result("verify", verdict="REJECTED"),
                    stage_result("execute-fix"),
                ],
                5,
                ".planning/flow/phases/demo/execution/stale-fix.md",
            ),
            (
                "review-fix",
                [
                    stage_result("plan"),
                    stage_result("execute"),
                    stage_result("review"),
                    stage_result("verify", verdict="REJECTED"),
                    stage_result("execute-fix"),
                    stage_result("review-fix"),
                ],
                6,
                ".planning/flow/phases/demo/review/stale-fix.md",
            ),
        )
        for stage, sequence, call_number, stale_path in cases:
            with self.subTest(stage=stage), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                repository, worktree, environment = self.runner_fixture(
                    root, sequence, skip_artifact_calls=str(call_number)
                )
                self.seed_stale_artifact(worktree, stale_path)
                baseline = self.commit_count(worktree)

                result = self.run_fleet(repository, worktree, environment)

                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(len(self.argument_calls(root)), call_number)
                status = self.read_status(worktree)
                self.assertEqual(status["stage"], stage)
                self.assertEqual(status["status"], "NEEDS_HUMAN")
                self.assertIn(f"missing fresh {stage} artifact", status["message"])
                self.assertEqual(
                    self.commit_count(worktree) - baseline,
                    call_number - 1,
                )

    def test_nonzero_codex_exit_marks_needs_human_without_commit(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository, worktree, environment = self.runner_fixture(
                root, [stage_result("plan")]
            )
            environment.update(
                {"FLOW_FAKE_CODEX_EXIT_CALL": "1", "FLOW_FAKE_CODEX_EXIT_CODE": "23"}
            )
            baseline = self.commit_count(worktree)

            result = self.run_fleet(repository, worktree, environment)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Codex exited non-zero for plan: 23", result.stderr)
            self.assertEqual(self.commit_count(worktree), baseline)
            self.assertEqual(self.read_status(worktree)["status"], "NEEDS_HUMAN")

    def test_malformed_structured_results_are_rejected_without_commit(self) -> None:
        cases = (
            ("wrong keys", {**stage_result("plan"), "extra": True}),
            ("wrong stage", stage_result("execute")),
            ("wrong status", stage_result("plan", status="BOGUS")),
            ("wrong verdict", stage_result("plan", verdict="APPROVED")),
            ("empty message", stage_result("plan", message="")),
        )
        for label, malformed in cases:
            with self.subTest(case=label), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                repository, worktree, environment = self.runner_fixture(root, [malformed])
                baseline = self.commit_count(worktree)

                result = self.run_fleet(repository, worktree, environment)

                self.assertNotEqual(result.returncode, 0)
                self.assertIn("invalid structured result for plan", result.stderr)
                self.assertEqual(self.commit_count(worktree), baseline)
                self.assertEqual(self.read_status(worktree)["status"], "NEEDS_HUMAN")

    def test_commit_failure_marks_needs_human_without_failing_stage_commit(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository, worktree, environment = self.runner_fixture(
                root, [stage_result("plan")]
            )
            actual_git = shutil.which("git")
            self.assertIsNotNone(actual_git)
            write_executable(
                root / "bin" / "git",
                'for argument in "$@"; do [ "$argument" = commit ] && exit 41; done\n'
                f'exec "{actual_git}" "$@"',
            )
            baseline = self.commit_count(worktree)

            result = self.run_fleet(repository, worktree, environment)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("failed to commit plan changes", result.stderr)
            self.assertEqual(self.commit_count(worktree), baseline)
            self.assertEqual(self.read_status(worktree)["status"], "NEEDS_HUMAN")

    def test_valid_result_is_atomically_published_from_hidden_temp(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository, worktree, environment = self.runner_fixture(root, self.success_sequence())

            result = self.run_fleet(repository, worktree, environment)

            self.assertEqual(result.returncode, 0, result.stderr)
            calls = self.argument_calls(root)
            for arguments in calls:
                self.assertTrue(Path(arguments[8]).name.startswith("."))
            result_dir = worktree / ".planning" / "flow" / "fleet-results"
            self.assertEqual(len(list(result_dir.glob("[!.]*.json"))), 4)
            self.assertEqual(list(result_dir.glob(".*.json.*")), [])

    def test_term_during_codex_marks_needs_human_and_cleans_owned_state(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository, worktree, environment = self.runner_fixture(
                root, [stage_result("plan")]
            )
            ready = root / "block-ready"
            release = root / "block-release"
            environment.update(
                {
                    "FLOW_FAKE_BLOCK_CALL": "1",
                    "FLOW_FAKE_BLOCK_READY": str(ready),
                    "FLOW_FAKE_BLOCK_RELEASE": str(release),
                    "LC_ALL": "C",
                }
            )
            baseline = self.commit_count(worktree)
            process = subprocess.Popen(
                ["/bin/bash", str(RUNNER), "demo", str(worktree)],
                cwd=repository,
                env=environment,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                start_new_session=True,
            )
            try:
                deadline = time.monotonic() + 5
                while not ready.exists() and time.monotonic() < deadline:
                    time.sleep(0.01)
                self.assertTrue(ready.exists(), "fake Codex did not enter blocking call")
                os.killpg(process.pid, signal.SIGTERM)
                _, stderr = process.communicate(timeout=5)
            finally:
                if process.poll() is None:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.communicate()

            self.assertNotEqual(process.returncode, 0)
            self.assertIn("terminated by TERM", stderr)
            self.assertEqual(self.read_status(worktree)["status"], "NEEDS_HUMAN")
            self.assertFalse(
                (repository / ".planning/flow/fleet/.demo.runner.lock").exists()
            )
            self.assertEqual(
                list((worktree / ".planning/flow/fleet-results").glob(".*.json.*")), []
            )
            self.assertEqual(self.commit_count(worktree), baseline)

    def test_runner_pid_hup_and_term_kill_owned_stubborn_process_group(self) -> None:
        for sent_signal, expected_code, signal_name in (
            (signal.SIGHUP, 129, "HUP"),
            (signal.SIGTERM, 143, "TERM"),
        ):
            with self.subTest(signal=signal_name), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                repository, worktree, environment = self.runner_fixture(
                    root, [stage_result("plan")]
                )
                ready = root / "stubborn-ready"
                descendant_pid_file = root / "stubborn-descendant.pid"
                environment.update(
                    {
                        "FLOW_STUBBORN_READY": str(ready),
                        "FLOW_STUBBORN_DESCENDANT_PID": str(descendant_pid_file),
                    }
                )
                write_executable(
                    root / "bin" / "codex",
                    "/usr/bin/python3 -c 'import os,signal,time,pathlib; "
                    "signal.signal(signal.SIGHUP, signal.SIG_IGN); "
                    "signal.signal(signal.SIGTERM, signal.SIG_IGN); "
                    "pathlib.Path(os.environ[\"FLOW_STUBBORN_DESCENDANT_PID\"]).write_text(str(os.getpid())); "
                    "time.sleep(120)' &\n"
                    "child=$!\n"
                    'printf "ready\\n" > "$FLOW_STUBBORN_READY"\n'
                    "trap '' HUP TERM INT\n"
                    'while kill -0 "$child" 2>/dev/null; do wait "$child" || true; done',
                )
                process = subprocess.Popen(
                    ["/bin/bash", str(RUNNER), "demo", str(worktree)],
                    cwd=repository,
                    env=environment,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    start_new_session=True,
                )
                descendant_pid = 0
                try:
                    deadline = time.monotonic() + 5
                    while (
                        not ready.exists() or not descendant_pid_file.exists()
                    ) and time.monotonic() < deadline:
                        time.sleep(0.01)
                    self.assertTrue(
                        ready.exists() and descendant_pid_file.exists(),
                        "stubborn provider tree did not start",
                    )
                    descendant_pid = int(descendant_pid_file.read_text(encoding="utf-8"))
                    os.kill(process.pid, sent_signal)
                    _, stderr = process.communicate(timeout=7)
                    self.assertEqual(process.returncode, expected_code, stderr)
                    deadline = time.monotonic() + 2
                    while time.monotonic() < deadline:
                        try:
                            os.kill(descendant_pid, 0)
                        except ProcessLookupError:
                            break
                        time.sleep(0.02)
                    else:
                        self.fail("stubborn provider descendant survived runner recovery")
                finally:
                    if process.poll() is None:
                        process.kill()
                        process.communicate()
                    if descendant_pid:
                        try:
                            os.kill(descendant_pid, signal.SIGKILL)
                        except ProcessLookupError:
                            pass

                self.assertEqual(self.read_status(worktree)["status"], "NEEDS_HUMAN")
                self.assertFalse(
                    (repository / ".planning/flow/fleet/.demo.runner.lock").exists()
                )
                self.assertEqual(
                    list((worktree / ".planning/flow/fleet-results").glob(".*.json.*")), []
                )
                self.assertEqual(
                    list((worktree / ".planning/flow/fleet-logs").glob(".*.log.*")), []
                )

    def test_signal_publishes_terminal_state_and_audit_only_after_group_absence(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository, worktree, environment = self.runner_fixture(
                root, [stage_result("plan")]
            )
            config = repository / ".planning" / "flow" / "config.json"
            config.write_text(json.dumps({"audit": True}) + "\n", encoding="utf-8")
            ready = root / "ordered-stubborn-ready"
            descendant_pid_file = root / "ordered-stubborn.pid"
            environment.update(
                {
                    "FLOW_STUBBORN_READY": str(ready),
                    "FLOW_STUBBORN_DESCENDANT_PID": str(descendant_pid_file),
                }
            )
            write_executable(
                root / "bin" / "codex",
                "/usr/bin/python3 -c 'import os,signal,time,pathlib; "
                "signal.signal(signal.SIGHUP, signal.SIG_IGN); "
                "signal.signal(signal.SIGTERM, signal.SIG_IGN); "
                "pathlib.Path(os.environ[\"FLOW_STUBBORN_DESCENDANT_PID\"]).write_text(str(os.getpid())); "
                "time.sleep(120)' &\n"
                "child=$!\n"
                'printf "ready\\n" > "$FLOW_STUBBORN_READY"\n'
                "trap '' HUP TERM INT\n"
                'while kill -0 "$child" 2>/dev/null; do wait "$child" || true; done',
            )
            process = subprocess.Popen(
                ["/bin/bash", str(RUNNER), "demo", str(worktree)],
                cwd=repository,
                env=environment,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                start_new_session=True,
            )
            descendant_pid = 0
            terminal_while_alive = False
            audit_while_alive = False
            unlock_while_alive = False
            try:
                deadline = time.monotonic() + 5
                while (
                    not ready.exists() or not descendant_pid_file.exists()
                ) and time.monotonic() < deadline:
                    time.sleep(0.01)
                self.assertTrue(
                    ready.exists() and descendant_pid_file.exists(),
                    "ordered stubborn provider tree did not start",
                )
                descendant_pid = int(descendant_pid_file.read_text(encoding="utf-8"))
                process.send_signal(signal.SIGTERM)
                audit_file = repository / ".planning" / "flow" / "audit" / "events.jsonl"
                lock = repository / ".planning" / "flow" / "fleet" / ".demo.runner.lock"
                deadline = time.monotonic() + 6
                while time.monotonic() < deadline:
                    try:
                        os.kill(descendant_pid, 0)
                    except ProcessLookupError:
                        break
                    status_file = worktree / ".planning" / "flow" / "fleet-status.json"
                    if status_file.exists():
                        status = json.loads(status_file.read_text(encoding="utf-8"))
                        terminal_while_alive = terminal_while_alive or status.get("status") == "NEEDS_HUMAN"
                    if audit_file.exists():
                        events = [
                            json.loads(line)
                            for line in audit_file.read_text(encoding="utf-8").splitlines()
                            if line
                        ]
                        audit_while_alive = audit_while_alive or any(
                            event.get("action") == "fleet_stage"
                            and event.get("status") == "NEEDS_HUMAN"
                            for event in events
                        )
                    unlock_while_alive = unlock_while_alive or not lock.exists()
                    time.sleep(0.01)
                _, stderr = process.communicate(timeout=5)
            finally:
                if process.poll() is None:
                    process.kill()
                    process.communicate()
                if descendant_pid:
                    try:
                        os.kill(descendant_pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass

            self.assertFalse(terminal_while_alive, "terminal status preceded group absence")
            self.assertFalse(audit_while_alive, "terminal audit preceded group absence")
            self.assertFalse(unlock_while_alive, "runner lock was released while the group lived")
            self.assertEqual(process.returncode, 143, stderr)
            self.assertEqual(self.read_status(worktree)["status"], "NEEDS_HUMAN")
            self.assertFalse(
                (repository / ".planning/flow/fleet/.demo.runner.lock").exists()
            )

    def test_successful_leader_cannot_orphan_group_into_validation_or_commit(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository, worktree, environment = self.runner_fixture(
                root, self.success_sequence()
            )
            orphan_pid_file = root / "successful-leader-orphan.pid"
            orphan_ready = root / "successful-leader-orphan.ready"
            commit_while_alive = root / "commit-while-provider-group-alive"
            environment.update(
                {
                    "FLOW_FAKE_ORPHAN_CALL": "1",
                    "FLOW_FAKE_ORPHAN_PID": str(orphan_pid_file),
                    "FLOW_FAKE_ORPHAN_READY": str(orphan_ready),
                    "FLOW_COMMIT_WHILE_ALIVE": str(commit_while_alive),
                }
            )
            actual_git = shutil.which("git")
            self.assertIsNotNone(actual_git)
            write_executable(
                root / "bin" / "git",
                'for argument in "$@"; do\n'
                '  if [ "$argument" = commit ] && [ -f "$FLOW_FAKE_ORPHAN_PID" ]; then\n'
                '    IFS= read -r orphan_pid < "$FLOW_FAKE_ORPHAN_PID" || true\n'
                '    if kill -0 "$orphan_pid" 2>/dev/null; then : > "$FLOW_COMMIT_WHILE_ALIVE"; fi\n'
                '  fi\n'
                'done\n'
                f'exec "{actual_git}" "$@"',
            )
            baseline = self.commit_count(worktree)
            descendant_pid = 0
            try:
                result = self.run_fleet(repository, worktree, environment)
                self.assertTrue(orphan_ready.is_file(), "fake leader did not leave its descendant")
                descendant_pid = int(orphan_pid_file.read_text(encoding="utf-8"))
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertFalse(
                    commit_while_alive.exists(),
                    "runner entered commit while the owned provider group was alive",
                )
                with self.assertRaises(ProcessLookupError):
                    os.kill(descendant_pid, 0)
                self.assertEqual(self.read_status(worktree)["status"], "DONE")
                self.assertEqual(self.commit_count(worktree), baseline + 4)
                self.assertFalse(
                    (repository / ".planning/flow/fleet/.demo.runner.lock").exists()
                )
            finally:
                if descendant_pid:
                    try:
                        os.kill(descendant_pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass

    def test_unexpected_result_publish_failure_recovers_state_and_lock(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository, worktree, environment = self.runner_fixture(
                root, [stage_result("plan")]
            )
            self.install_mv_failures(root, environment, result_publish_failure=True)
            baseline = self.commit_count(worktree)

            result = self.run_fleet(repository, worktree, environment)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("unexpected runner failure during plan", result.stderr)
            self.assertEqual(self.read_status(worktree)["status"], "NEEDS_HUMAN")
            self.assertFalse(
                (repository / ".planning/flow/fleet/.demo.runner.lock").exists()
            )
            self.assertEqual(self.commit_count(worktree), baseline)

    def test_needs_human_status_rename_failure_is_truthful_and_cleanup_safe(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository, worktree, environment = self.runner_fixture(root, ["{broken"])
            self.install_mv_failures(root, environment, status_fail_at=2)
            baseline = self.commit_count(worktree)

            result = self.run_fleet(repository, worktree, environment)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("failed to publish NEEDS_HUMAN status for plan", result.stderr)
            self.assertEqual(self.read_status(worktree)["status"], "RUNNING")
            self.assertEqual(list((worktree / ".planning/flow").glob(".fleet-status.json.*")), [])
            self.assertFalse(
                (repository / ".planning/flow/fleet/.demo.runner.lock").exists()
            )
            self.assertEqual(self.commit_count(worktree), baseline)

    def test_term_recovery_status_rename_failure_is_truthful_and_cleanup_safe(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository, worktree, environment = self.runner_fixture(
                root, [stage_result("plan")]
            )
            self.install_mv_failures(root, environment, status_fail_at=2)
            ready = root / "status-term-ready"
            release = root / "status-term-release"
            environment.update(
                {
                    "FLOW_FAKE_BLOCK_CALL": "1",
                    "FLOW_FAKE_BLOCK_READY": str(ready),
                    "FLOW_FAKE_BLOCK_RELEASE": str(release),
                    "LC_ALL": "C",
                }
            )
            baseline = self.commit_count(worktree)
            process = subprocess.Popen(
                ["/bin/bash", str(RUNNER), "demo", str(worktree)],
                cwd=repository,
                env=environment,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                start_new_session=True,
            )
            try:
                deadline = time.monotonic() + 5
                while not ready.exists() and time.monotonic() < deadline:
                    time.sleep(0.01)
                self.assertTrue(ready.exists(), "fake Codex did not enter blocking call")
                os.killpg(process.pid, signal.SIGTERM)
                _, stderr = process.communicate(timeout=5)
            finally:
                if process.poll() is None:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.communicate()

            self.assertNotEqual(process.returncode, 0)
            self.assertIn("failed to publish TERM recovery status for plan", stderr)
            self.assertEqual(self.read_status(worktree)["status"], "RUNNING")
            self.assertEqual(list((worktree / ".planning/flow").glob(".fleet-status.json.*")), [])
            self.assertFalse(
                (repository / ".planning/flow/fleet/.demo.runner.lock").exists()
            )
            self.assertEqual(self.commit_count(worktree), baseline)

    def test_err_recovery_status_rename_failure_is_truthful_and_cleanup_safe(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository, worktree, environment = self.runner_fixture(
                root, [stage_result("plan")]
            )
            self.install_mv_failures(
                root,
                environment,
                status_fail_at=2,
                result_publish_failure=True,
            )
            baseline = self.commit_count(worktree)

            result = self.run_fleet(repository, worktree, environment)

            self.assertNotEqual(result.returncode, 0)
            self.assertTrue(
                Path(environment["FLOW_FAKE_RESULT_MV_SENTINEL"]).is_file(),
                "injected result-publication failure was not reached",
            )
            self.assertEqual(len(self.argument_calls(root)), 1)
            self.assertIn("failed to publish ERR recovery status for plan", result.stderr)
            self.assertEqual(self.read_status(worktree)["status"], "RUNNING")
            self.assertEqual(list((worktree / ".planning/flow").glob(".fleet-status.json.*")), [])
            self.assertFalse(
                (repository / ".planning/flow/fleet/.demo.runner.lock").exists()
            )
            self.assertEqual(self.commit_count(worktree), baseline)

    def test_dashboard_once_renders_literal_member_fields(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository = init_repository(root / "repo")
            worktree = create_fleet_worktree(repository, "demo", root / "repo-fleet-demo")
            member = write_registered_fleet_member(repository, "demo", worktree)
            member_payload = json.loads(member.read_text(encoding="utf-8"))
            member_payload.update({"app_port": 3010, "db_port": 5442})
            member.write_text(json.dumps(member_payload) + "\n", encoding="utf-8")
            status_file = worktree / ".planning" / "flow" / "fleet-status.json"
            status_file.parent.mkdir(parents=True, exist_ok=True)
            status_file.write_text(
                json.dumps(
                    {
                        "slug": "demo",
                        "stage": "review",
                        "status": "ACTIVE",
                        "message": "reviewing literal dashboard fixture",
                        "verdict": "NONE",
                        "updated_at": "2026-08-16T12:34:56Z",
                    }
                ),
                encoding="utf-8",
            )
            fake_bin = create_closed_command_path(root, ("jq",))
            environment = {"FLOW_CLEAN_ENV": "1", "PATH": str(fake_bin)}

            result = run_shell(DASHBOARD, repository, "--once", env=environment)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("SLUG", result.stdout)
            self.assertIn("APP:DB", result.stdout)
            for literal in (
                "demo",
                "3010:5442",
                "review",
                "ACTIVE",
                "flow-fleet/demo",
                "2026-08-16T12:34:56Z",
                "reviewing literal dashboard fixture",
            ):
                self.assertIn(literal, result.stdout)

    def test_dashboard_surfaces_malformed_member_and_missing_or_malformed_status(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository = init_repository(root / "repo")
            worktree = create_fleet_worktree(repository, "demo", root / "repo-fleet-demo")
            member = write_registered_fleet_member(repository, "demo", worktree)
            fleet = member.parent
            (fleet / "broken.json").write_text("{broken\n", encoding="utf-8")
            fake_bin = create_closed_command_path(root, ("jq",))
            environment = {"FLOW_CLEAN_ENV": "1", "PATH": str(fake_bin)}

            missing = run_shell(DASHBOARD, repository, "--once", env=environment)

            self.assertEqual(missing.returncode, 0, missing.stderr)
            self.assertIn("broken", missing.stdout)
            self.assertIn("MALFORMED", missing.stdout)
            self.assertIn("UNKNOWN", missing.stdout)
            self.assertIn("status unavailable", missing.stdout)

            status_file = worktree / ".planning/flow/fleet-status.json"
            status_file.parent.mkdir(parents=True, exist_ok=True)
            status_file.write_text('{"stage": 7}\n', encoding="utf-8")
            malformed = run_shell(DASHBOARD, repository, "--once", env=environment)
            self.assertEqual(malformed.returncode, 0, malformed.stderr)
            self.assertIn("malformed status", malformed.stdout)

    def test_dashboard_truncates_message_to_exactly_sixty_characters(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository = init_repository(root / "repo")
            worktree = create_fleet_worktree(repository, "demo", root / "repo-fleet-demo")
            write_registered_fleet_member(repository, "demo", worktree)
            message = "x" * 60 + "Y"
            status_file = worktree / ".planning/flow/fleet-status.json"
            status_file.parent.mkdir(parents=True, exist_ok=True)
            status_file.write_text(
                json.dumps(
                    {
                        "slug": "demo",
                        "stage": "review",
                        "status": "ACTIVE",
                        "message": message,
                        "verdict": "NONE",
                        "updated_at": "2026-08-16T12:34:56Z",
                    }
                ),
                encoding="utf-8",
            )
            fake_bin = create_closed_command_path(root, ("jq",))
            result = run_shell(
                DASHBOARD,
                repository,
                "--once",
                env={"FLOW_CLEAN_ENV": "1", "PATH": str(fake_bin)},
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("x" * 60, result.stdout)
            self.assertNotIn("x" * 60 + "Y", result.stdout)

    def test_dashboard_live_exits_cleanly_on_int_and_term(self) -> None:
        for requested_signal in (signal.SIGINT, signal.SIGTERM):
            with self.subTest(signal=requested_signal), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                repository = init_repository(root / "repo")
                fake_bin = create_closed_command_path(root, ("jq", "sleep"))
                environment = {"PATH": str(fake_bin), "LC_ALL": "C"}
                process = subprocess.Popen(
                    ["/bin/bash", str(DASHBOARD)],
                    cwd=repository,
                    env=environment,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
                time.sleep(0.1)
                process.send_signal(requested_signal)
                _, stderr = process.communicate(timeout=5)
                self.assertEqual(process.returncode, 0, stderr)


if __name__ == "__main__":
    unittest.main()
