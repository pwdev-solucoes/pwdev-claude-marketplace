import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from typing import Optional

from tests.flow_m5_fixtures import init_repository, run_shell, write_executable


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "plugins" / "pwdev-flow" / "scripts" / "run-agent.sh"


def configure_external_model(
    repository: Path,
    agent: str,
    *,
    model: str = "fixture/model",
    timeout_s: int = 30,
    extra_args: Optional[list[str]] = None,
) -> None:
    config = repository / ".planning" / "flow" / "config.json"
    config.parent.mkdir(parents=True, exist_ok=True)
    config.write_text(
        json.dumps(
            {
                "external_models": {
                    agent: {
                        "model": model,
                        "timeout_s": timeout_s,
                        "extra_args": [] if extra_args is None else extra_args,
                    }
                }
            }
        ),
        encoding="utf-8",
    )


class DelegationContractTest(unittest.TestCase):
    def fake_environment(self, fake_bin: Path, argument_log: Path) -> dict[str, str]:
        return {
            "PATH": f"{fake_bin}:{os.environ['PATH']}",
            "FLOW_FAKE_ARGS": str(argument_log),
        }

    def preview_and_run(
        self,
        repository: Path,
        fake_bin: Path,
        argument_log: Path,
        agent: str,
        mode: str,
        task: str,
    ) -> tuple[subprocess.CompletedProcess[str], subprocess.CompletedProcess[str]]:
        environment = self.fake_environment(fake_bin, argument_log)
        preview = run_shell(
            RUNNER,
            repository,
            "--preview",
            agent,
            mode,
            task,
            env=environment,
        )
        self.assertEqual(preview.returncode, 0, preview.stderr)
        token_lines = [
            line.removeprefix("confirmation token: ")
            for line in preview.stdout.splitlines()
            if line.startswith("confirmation token: ")
        ]
        self.assertEqual(len(token_lines), 1, preview.stdout)
        environment["FLOW_DELEGATION_CONFIRM_TOKEN"] = token_lines[0]
        result = run_shell(RUNNER, repository, agent, mode, task, env=environment)
        return preview, result

    def test_unknown_provider_is_rejected_before_execution(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository = init_repository(root / "repo")
            fake_bin = root / "bin"
            fake_bin.mkdir()
            argument_log = root / "arguments.txt"
            write_executable(fake_bin / "other", 'printf "%s\\n" "$@" > "$FLOW_FAKE_ARGS"')

            result = run_shell(
                RUNNER,
                repository,
                "other",
                "write",
                "task",
                env=self.fake_environment(fake_bin, argument_log),
            )

            self.assertEqual(result.returncode, 2)
            self.assertFalse(argument_log.exists())

    def test_codex_write_vector_never_contains_fleet_dangerous_flag(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository = init_repository(root / "repo")
            configure_external_model(repository, "codex")
            fake_bin = root / "bin"
            fake_bin.mkdir()
            argument_log = root / "arguments.txt"
            write_executable(
                fake_bin / "codex",
                'printf "%s\\n" "$@" > "$FLOW_FAKE_ARGS"\nprintf "delegated-result\\n"',
            )

            _, result = self.preview_and_run(
                repository, fake_bin, argument_log, "codex", "write", "implement fixture"
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            arguments = argument_log.read_text(encoding="utf-8").splitlines()
            self.assertEqual(arguments[0], "exec")
            self.assertNotIn("--dangerously-bypass-approvals-and-sandbox", arguments)
            output_files = list((repository / ".planning" / "flow" / "delegation").glob("*.md"))
            self.assertEqual(len(output_files), 1)
            self.assertIn("MANDATORY RULES", output_files[0].read_text(encoding="utf-8"))

    def test_codex_rejects_configured_dangerous_bypass_before_execution(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository = init_repository(root / "repo")
            configure_external_model(
                repository,
                "codex",
                extra_args=["--dangerously-bypass-approvals-and-sandbox"],
            )
            fake_bin = root / "bin"
            fake_bin.mkdir()
            argument_log = root / "arguments.txt"
            write_executable(fake_bin / "codex", 'printf "%s\\n" "$@" > "$FLOW_FAKE_ARGS"')

            result = run_shell(
                RUNNER,
                repository,
                "codex",
                "write",
                "implement fixture",
                env=self.fake_environment(fake_bin, argument_log),
            )

            self.assertEqual(result.returncode, 2)
            self.assertFalse(argument_log.exists())

    def test_codex_rejects_every_safety_root_config_and_prompt_override(self) -> None:
        unsafe_vectors = (
            ["--sandbox", "danger-full-access"],
            ["--sandbox=danger-full-access"],
            ["-s=danger-full-access"],
            ["-s", "danger-full-access"],
            ["-c", "approval_policy=never"],
            ["-c=approval_policy=never"],
            ["--config", "approval_policy=never"],
            ["--config=approval_policy=never"],
            ["--add-dir", "/tmp/outside"],
            ["--add-dir=/tmp/outside"],
            ["--dangerously-bypass-hook-trust"],
            ["--full-auto"],
            ["--cd", "/tmp/outside"],
            ["-C=/tmp/outside"],
            ["--output-last-message", "/tmp/outside"],
            ["--output-schema=/tmp/outside"],
            ["--json"],
        )
        for extra_args in unsafe_vectors:
            with self.subTest(extra_args=extra_args), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                repository = init_repository(root / "repo")
                configure_external_model(repository, "codex", extra_args=list(extra_args))
                fake_bin = root / "bin"
                fake_bin.mkdir()
                argument_log = root / "arguments.txt"
                write_executable(fake_bin / "codex", 'printf "%s\\n" "$@" > "$FLOW_FAKE_ARGS"')

                result = run_shell(
                    RUNNER,
                    repository,
                    "codex",
                    "write",
                    "implement fixture",
                    env=self.fake_environment(fake_bin, argument_log),
                )

                self.assertEqual(result.returncode, 2, (extra_args, result.stdout, result.stderr))
                self.assertFalse(argument_log.exists())

    def test_codex_preview_binds_confirmation_to_exact_expanded_argv(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository = init_repository(root / "repo")
            configure_external_model(repository, "codex", model="fixture safe model")
            fake_bin = root / "bin"
            fake_bin.mkdir()
            argument_log = root / "arguments.txt"
            write_executable(
                fake_bin / "codex",
                'printf "%s\\n" "$@" > "$FLOW_FAKE_ARGS"\nprintf "delegated-result\\n"',
            )

            preview, result = self.preview_and_run(
                repository,
                fake_bin,
                argument_log,
                "codex",
                "write",
                "implement exact fixture",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("provider argv: codex exec --ephemeral --cd ", preview.stdout)
            self.assertIn("--model fixture\\ safe\\ model", preview.stdout)
            arguments = argument_log.read_text(encoding="utf-8").splitlines()
            self.assertEqual(
                arguments[:6],
                ["exec", "--ephemeral", "--cd", str(repository.resolve()), "--model", "fixture safe model"],
            )

            changed = json.loads(
                (repository / ".planning" / "flow" / "config.json").read_text(encoding="utf-8")
            )
            changed["external_models"]["codex"]["model"] = "changed-after-confirmation"
            (repository / ".planning" / "flow" / "config.json").write_text(
                json.dumps(changed), encoding="utf-8"
            )
            old_token = next(
                line.removeprefix("confirmation token: ")
                for line in preview.stdout.splitlines()
                if line.startswith("confirmation token: ")
            )
            stale_environment = self.fake_environment(fake_bin, root / "stale-arguments.txt")
            stale_environment["FLOW_DELEGATION_CONFIRM_TOKEN"] = old_token
            stale = run_shell(
                RUNNER,
                repository,
                "codex",
                "write",
                "implement exact fixture",
                env=stale_environment,
            )
            self.assertEqual(stale.returncode, 5)
            self.assertFalse((root / "stale-arguments.txt").exists())

    def test_kiro_trusts_all_tools_only_in_write_mode(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository = init_repository(root / "repo")
            configure_external_model(repository, "kiro")
            fake_bin = root / "bin"
            fake_bin.mkdir()
            write_executable(
                fake_bin / "kiro-cli",
                'printf "%s\\n" "$@" > "$FLOW_FAKE_ARGS"\nprintf "delegated-result\\n"',
            )

            write_log = root / "write-arguments.txt"
            _, write_result = self.preview_and_run(
                repository, fake_bin, write_log, "kiro", "write", "implement fixture"
            )
            self.assertEqual(write_result.returncode, 0, write_result.stderr)
            write_arguments = write_log.read_text(encoding="utf-8").splitlines()

            read_log = root / "read-arguments.txt"
            _, read_result = self.preview_and_run(
                repository, fake_bin, read_log, "kiro", "read", "inspect fixture"
            )
            self.assertEqual(read_result.returncode, 0, read_result.stderr)
            read_arguments = read_log.read_text(encoding="utf-8").splitlines()

            self.assertIn("--trust-all-tools", write_arguments)
            self.assertNotIn("--trust-all-tools", read_arguments)

    def test_kiro_read_rejects_configured_trust_all_tools_before_execution(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository = init_repository(root / "repo")
            configure_external_model(repository, "kiro", extra_args=["--trust-all-tools"])
            fake_bin = root / "bin"
            fake_bin.mkdir()
            argument_log = root / "arguments.txt"
            write_executable(fake_bin / "kiro-cli", 'printf "%s\\n" "$@" > "$FLOW_FAKE_ARGS"')

            result = run_shell(
                RUNNER,
                repository,
                "kiro",
                "read",
                "inspect fixture",
                env=self.fake_environment(fake_bin, argument_log),
            )

            self.assertEqual(result.returncode, 2)
            self.assertFalse(argument_log.exists())

    def test_read_mode_detects_a_real_worktree_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository = init_repository(root / "repo")
            configure_external_model(repository, "gemini")
            fake_bin = root / "bin"
            fake_bin.mkdir()
            write_executable(fake_bin / "gemini", 'printf "changed" >> README.md')

            _, result = self.preview_and_run(
                repository,
                fake_bin,
                root / "arguments.txt",
                "gemini",
                "read",
                "inspect fixture",
            )

            self.assertEqual(result.returncode, 3)
            self.assertEqual((repository / "README.md").read_text(encoding="utf-8"), "# Fixture\nchanged")

    def test_read_status_is_checked_before_best_effort_audit_writes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository = init_repository(root / "repo")
            configure_external_model(repository, "gemini")
            config = repository / ".planning" / "flow" / "config.json"
            payload = json.loads(config.read_text(encoding="utf-8"))
            payload["audit"] = True
            config.write_text(json.dumps(payload), encoding="utf-8")
            subprocess.run(["git", "add", ".planning/flow/config.json"], cwd=repository, check=True)
            subprocess.run(["git", "commit", "-qm", "track flow configuration"], cwd=repository, check=True)
            fake_bin = root / "bin"
            fake_bin.mkdir()
            write_executable(fake_bin / "gemini", 'printf "clean provider output\\n"')
            write_executable(
                fake_bin / "python3",
                'mkdir -p .planning/flow/audit\nprintf "audit event\\n" > .planning/flow/audit/events.jsonl',
            )

            _, result = self.preview_and_run(
                repository,
                fake_bin,
                root / "arguments.txt",
                "gemini",
                "read",
                "inspect fixture",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((repository / ".planning" / "flow" / "audit" / "events.jsonl").is_file())

    def test_audit_failure_warns_without_changing_provider_result(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository = init_repository(root / "repo")
            configure_external_model(repository, "opencode")
            config = repository / ".planning" / "flow" / "config.json"
            payload = json.loads(config.read_text(encoding="utf-8"))
            payload["audit"] = True
            config.write_text(json.dumps(payload), encoding="utf-8")
            fake_bin = root / "bin"
            fake_bin.mkdir()
            write_executable(
                fake_bin / "opencode",
                'printf "provider-result-preserved\\n"\nexit 17',
            )
            write_executable(fake_bin / "python3", "exit 23")

            _, result = self.preview_and_run(
                repository,
                fake_bin,
                root / "arguments.txt",
                "opencode",
                "write",
                "sensitive delegated task",
            )

            self.assertEqual(result.returncode, 17)
            self.assertIn("provider-result-preserved", result.stdout)
            self.assertIn("warning: external_run audit record failed", result.stderr)
            for prohibited in (
                "sensitive delegated task",
                "fixture/model",
                "provider-result-preserved",
                str(repository),
            ):
                self.assertNotIn(prohibited, result.stderr)

    def test_existing_write_lock_refuses_second_writer(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository = init_repository(root / "repo")
            configure_external_model(repository, "codex")
            lock = repository / ".planning" / "flow" / "delegation" / ".lock"
            lock.parent.mkdir(parents=True)
            lock.write_text("occupied\n", encoding="utf-8")
            fake_bin = root / "bin"
            fake_bin.mkdir()
            argument_log = root / "arguments.txt"
            write_executable(fake_bin / "codex", 'printf "%s\\n" "$@" > "$FLOW_FAKE_ARGS"')

            _, result = self.preview_and_run(
                repository, fake_bin, argument_log, "codex", "write", "implement fixture"
            )

            self.assertEqual(result.returncode, 4)
            self.assertFalse(argument_log.exists())

    def test_missing_binary_returns_127(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository = init_repository(root / "repo")
            configure_external_model(repository, "opencode")
            fake_bin = root / "bin"
            fake_bin.mkdir()
            utility_bin = root / "utilities"
            utility_bin.mkdir()
            for utility in ("git", "jq"):
                executable = shutil.which(utility)
                self.assertIsNotNone(executable, f"{utility} is required for this contract test")
                write_executable(utility_bin / utility, f'exec "{executable}" "$@"')

            self.assertTrue(
                RUNNER.is_file(),
                "run-agent.sh must exist before this test can prove an absent provider returns 127",
            )
            result = run_shell(
                RUNNER,
                repository,
                "opencode",
                "write",
                "implement fixture",
                env={"PATH": f"{fake_bin}:{utility_bin}:/usr/bin:/bin"},
            )

            self.assertEqual(result.returncode, 127)

    def test_timeout_exit_is_preserved(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository = init_repository(root / "repo")
            configure_external_model(repository, "opencode")
            fake_bin = root / "bin"
            fake_bin.mkdir()
            argument_log = root / "arguments.txt"
            write_executable(fake_bin / "opencode", 'printf "%s\\n" "$@" > "$FLOW_FAKE_ARGS"')
            write_executable(fake_bin / "timeout", "exit 124")

            _, result = self.preview_and_run(
                repository, fake_bin, argument_log, "opencode", "write", "implement fixture"
            )

            self.assertEqual(result.returncode, 124)

    def test_output_is_copied_under_flow_delegation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository = init_repository(root / "repo")
            configure_external_model(repository, "gemini")
            fake_bin = root / "bin"
            fake_bin.mkdir()
            write_executable(fake_bin / "gemini", 'printf "delegated-result\\n"')

            _, result = self.preview_and_run(
                repository,
                fake_bin,
                root / "arguments.txt",
                "gemini",
                "write",
                "implement fixture",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            output_files = list((repository / ".planning" / "flow" / "delegation").glob("*.md"))
            self.assertEqual(len(output_files), 1)
            self.assertIn("delegated-result", output_files[0].read_text(encoding="utf-8"))

    def test_json_array_extra_args_are_passed_as_distinct_arguments(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository = init_repository(root / "repo")
            configure_external_model(
                repository,
                "opencode",
                extra_args=["--model", "vendor/model;touch-not-run"],
            )
            fake_bin = root / "bin"
            fake_bin.mkdir()
            argument_log = root / "arguments.txt"
            write_executable(
                fake_bin / "opencode",
                'printf "%s\\n" "$@" > "$FLOW_FAKE_ARGS"\nprintf "delegated-result\\n"',
            )

            _, result = self.preview_and_run(
                repository, fake_bin, argument_log, "opencode", "write", "implement fixture"
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            arguments = argument_log.read_text(encoding="utf-8").splitlines()
            self.assertIn("--model", arguments)
            self.assertIn("vendor/model;touch-not-run", arguments)
            self.assertFalse((repository / "touch-not-run").exists())

    def test_symlinked_delegation_parent_is_rejected_without_external_write_or_provider(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository = init_repository(root / "repo")
            configure_external_model(repository, "codex")
            outside = root / "outside"
            outside.mkdir()
            sentinel = outside / "sentinel.txt"
            sentinel.write_bytes(b"outside-bytes\n")
            (repository / ".planning" / "flow" / "delegation").symlink_to(
                outside, target_is_directory=True
            )
            fake_bin = root / "bin"
            fake_bin.mkdir()
            argument_log = root / "arguments.txt"
            write_executable(fake_bin / "codex", 'printf "%s\\n" "$@" > "$FLOW_FAKE_ARGS"')

            _, result = self.preview_and_run(
                repository, fake_bin, argument_log, "codex", "write", "implement fixture"
            )

            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertEqual(sentinel.read_bytes(), b"outside-bytes\n")
            self.assertEqual(sorted(path.name for path in outside.iterdir()), ["sentinel.txt"])
            self.assertFalse(argument_log.exists())


if __name__ == "__main__":
    unittest.main()
