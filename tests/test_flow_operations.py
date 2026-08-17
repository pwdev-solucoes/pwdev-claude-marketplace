import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUDIT_SCRIPT = ROOT / "plugins" / "pwdev-flow" / "scripts" / "flow_audit.py"
MIGRATION_SCRIPT = ROOT / "plugins" / "pwdev-flow" / "scripts" / "migrate_legacy.py"


def run_cli(script: Path, repository: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), "--root", str(repository), *arguments],
        check=False,
        capture_output=True,
        text=True,
    )


class AuditCliTest(unittest.TestCase):
    def create_repository(self, directory: str, *, audit: bool) -> Path:
        repository = Path(directory)
        config = repository / ".planning" / "flow" / "config.json"
        config.parent.mkdir(parents=True)
        config.write_text(json.dumps({"audit": audit}), encoding="utf-8")
        return repository

    def test_record_appends_event_and_summary_reports_literal_counts(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository = self.create_repository(directory, audit=True)
            result = run_cli(
                AUDIT_SCRIPT,
                repository,
                "record",
                "--action",
                "completed",
                "--skill",
                "flow-execute",
                "--phase",
                "EXECUTE",
                "--status",
                "COMPLETE",
                "--target",
                ".planning/flow/phases/demo/execution/01-summary.md",
                "--detail",
                '{"acceptance_criteria": 3}',
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(json.loads(result.stdout)["recorded"])

            summary = run_cli(AUDIT_SCRIPT, repository, "summary")
            self.assertEqual(summary.returncode, 0, summary.stderr)
            self.assertEqual(
                json.loads(summary.stdout),
                {
                    "actions": {"completed": 1},
                    "first_timestamp": json.loads(result.stdout)["event"]["timestamp"],
                    "last_timestamp": json.loads(result.stdout)["event"]["timestamp"],
                    "phases": {"EXECUTE": 1},
                    "skills": {"flow-execute": 1},
                    "total": 1,
                },
            )

    def test_record_accepts_marco_5_actions_and_summary_counts_each_once(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository = self.create_repository(directory, audit=True)
            for action, skill in (
                ("fleet_launched", "flow-fleet"),
                ("fleet_stage", "flow-fleet"),
                ("fleet_teardown", "flow-fleet"),
                ("external_run", "flow-delegate"),
            ):
                result = run_cli(
                    AUDIT_SCRIPT,
                    repository,
                    "record",
                    "--action",
                    action,
                    "--skill",
                    skill,
                )
                self.assertEqual(result.returncode, 0, result.stderr)

            summary = run_cli(AUDIT_SCRIPT, repository, "summary")
            self.assertEqual(summary.returncode, 0, summary.stderr)
            self.assertEqual(
                json.loads(summary.stdout)["actions"],
                {
                    "external_run": 1,
                    "fleet_launched": 1,
                    "fleet_stage": 1,
                    "fleet_teardown": 1,
                },
            )

    def test_record_rejects_model_prompt_variants_and_secret_targets(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository = self.create_repository(directory, audit=True)
            for detail in (
                '{"model": "must-not-be-recorded"}',
                '{"prompt": "must-not-be-recorded"}',
                '{"routing": {"selected_model": "must-not-be-recorded"}}',
                '{"request": {"system_prompt": "must-not-be-recorded"}}',
                '{"model_api_key": "must-not-be-recorded"}',
                '{"prompt_token": "must-not-be-recorded"}',
            ):
                with self.subTest(detail=detail):
                    result = run_cli(
                        AUDIT_SCRIPT,
                        repository,
                        "record",
                        "--action",
                        "completed",
                        "--skill",
                        "flow-execute",
                        "--detail",
                        detail,
                    )
                    self.assertNotEqual(result.returncode, 0)
                    self.assertNotIn("must-not-be-recorded", result.stdout)

            target_result = run_cli(
                AUDIT_SCRIPT,
                repository,
                "record",
                "--action",
                "external_run",
                "--skill",
                "flow-delegate",
                "--target",
                ".env.fleet",
            )
            self.assertNotEqual(target_result.returncode, 0)

            self.assertFalse(
                (repository / ".planning" / "flow" / "audit" / "events.jsonl").exists()
            )

    def test_record_is_noop_when_audit_is_disabled(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository = self.create_repository(directory, audit=False)
            result = run_cli(
                AUDIT_SCRIPT,
                repository,
                "record",
                "--action",
                "started",
                "--skill",
                "flow-design",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(
                json.loads(result.stdout),
                {"reason": "audit_disabled", "recorded": False},
            )
            self.assertFalse(
                (repository / ".planning" / "flow" / "audit" / "events.jsonl").exists()
            )

    def test_record_rejects_secret_detail_without_writing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository = self.create_repository(directory, audit=True)
            result = run_cli(
                AUDIT_SCRIPT,
                repository,
                "record",
                "--action",
                "completed",
                "--skill",
                "flow-execute",
                "--detail",
                '{"access_token": "must-not-be-recorded"}',
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertNotIn("must-not-be-recorded", result.stdout)
            self.assertFalse(
                (repository / ".planning" / "flow" / "audit" / "events.jsonl").exists()
            )

    def test_verify_fails_for_malformed_event_log(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository = self.create_repository(directory, audit=True)
            audit_file = repository / ".planning" / "flow" / "audit" / "events.jsonl"
            audit_file.parent.mkdir(parents=True)
            audit_file.write_text("not-json\n", encoding="utf-8")

            result = run_cli(AUDIT_SCRIPT, repository, "verify")

            self.assertNotEqual(result.returncode, 0)
            payload = json.loads(result.stdout)
            self.assertFalse(payload["valid"])
            self.assertEqual(payload["total"], 0)


class MigrationCliTest(unittest.TestCase):
    def create_legacy_repository(self, directory: str) -> tuple[Path, Path, str]:
        repository = Path(directory)
        source = repository / ".planning" / "config.json"
        source.parent.mkdir(parents=True)
        original = json.dumps(
            {
                "lang": "pt-BR",
                "audit": True,
                "type": "brownfield",
                "framework": "PWDEV-CODE",
                "version": "2.4.0",
                "branch_strategy": "feature-branch",
                "commit_convention": "conventional-commits",
                "model_profile": "performance",
                "external_models": {"reviewer": "provider/model"},
                "api_token": "must-not-be-copied",
            },
            indent=2,
        )
        source.write_text(original, encoding="utf-8")
        return repository, source, original

    def test_plan_reports_safe_mapping_without_writing_target(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository, _, _ = self.create_legacy_repository(directory)
            result = run_cli(MIGRATION_SCRIPT, repository, "plan")

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertFalse(payload["target_exists"])
            self.assertEqual(payload["mapped"]["language"], "pt-BR")
            self.assertEqual(payload["mapped"]["repository_type"], "brownfield")
            self.assertFalse(payload["mapped"]["auto_commit"])
            self.assertNotIn("must-not-be-copied", result.stdout)
            self.assertFalse((repository / ".planning" / "flow" / "config.json").exists())

    def test_apply_creates_flow_config_and_preserves_legacy_source(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository, source, original = self.create_legacy_repository(directory)
            result = run_cli(MIGRATION_SCRIPT, repository, "apply")

            self.assertEqual(result.returncode, 0, result.stderr)
            target = repository / ".planning" / "flow" / "config.json"
            migrated = json.loads(target.read_text(encoding="utf-8"))
            self.assertEqual(source.read_text(encoding="utf-8"), original)
            self.assertEqual(migrated["schema_version"], 1)
            self.assertEqual(migrated["runtime"], "codex")
            self.assertEqual(migrated["legacy"]["branch_strategy"], "feature-branch")
            self.assertNotIn("model_profile", migrated.get("legacy", {}))
            self.assertNotIn("api_token", migrated.get("legacy", {}))
            self.assertEqual(json.loads(result.stdout)["target"], ".planning/flow/config.json")

    def test_migration_records_the_adapter_that_performed_it(self) -> None:
        """A Claude-initiated migration must not stamp the config as codex."""
        for runtime in ("codex", "claude"):
            with self.subTest(runtime=runtime), tempfile.TemporaryDirectory() as directory:
                repository, _, _ = self.create_legacy_repository(directory)

                result = run_cli(MIGRATION_SCRIPT, repository, "--runtime", runtime, "apply")

                self.assertEqual(result.returncode, 0, result.stderr)
                migrated = json.loads(
                    (repository / ".planning" / "flow" / "config.json").read_text(encoding="utf-8")
                )
                self.assertEqual(migrated["runtime"], runtime)

    def test_migration_rejects_an_unknown_runtime(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository, _, _ = self.create_legacy_repository(directory)

            result = run_cli(MIGRATION_SCRIPT, repository, "--runtime", "gemini", "apply")

            self.assertNotEqual(result.returncode, 0)
            self.assertFalse((repository / ".planning" / "flow" / "config.json").exists())

    def test_apply_refuses_to_overwrite_existing_flow_config(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository, _, _ = self.create_legacy_repository(directory)
            target = repository / ".planning" / "flow" / "config.json"
            target.parent.mkdir(parents=True)
            target.write_text('{"existing": true}\n', encoding="utf-8")

            result = run_cli(MIGRATION_SCRIPT, repository, "apply")

            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(target.read_text(encoding="utf-8"), '{"existing": true}\n')


if __name__ == "__main__":
    unittest.main()
