import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]


def load_module():
    path = ROOT / "scripts" / "sdd_runtime_smoke.py"
    spec = importlib.util.spec_from_file_location("sdd_runtime_smoke_test", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


SMOKE = load_module()


class RuntimeSmokeContractTests(unittest.TestCase):
    def test_runtime_smoke_cli_exists(self):
        self.assertTrue((ROOT / "scripts" / "sdd_runtime_smoke.py").is_file())

    def test_offline_all_never_invokes_a_provider_and_covers_the_matrix(self):
        with tempfile.TemporaryDirectory() as directory:
            def forbidden(*_args, **_kwargs):
                raise AssertionError("offline mode invoked a provider")

            summary = SMOKE.run_acceptance(
                mode="offline", runtime="all", language="both", scenario="all",
                output=Path(directory) / "run", plugin_root=ROOT / "plugins/sdd-composy",
                provider_launcher=forbidden,
            )
        self.assertEqual(summary["verdict"], "PASS")
        self.assertEqual(summary["provider_calls"], {"hermes": 0, "codex": 0, "claude": 0})
        covered = {(row["runtime"], row["language"], row["scenario"]) for row in summary["scenarios"]}
        for runtime in ("hermes", "codex", "claude"):
            for language in ("pt-BR", "en-US"):
                for scenario in ("read-only", "lifecycle", "fleet", "handoff", "evidence", "compose"):
                    self.assertIn((runtime, language, scenario), covered)
        self.assertTrue(all(row["status"] == "PASS" for row in summary["scenarios"]))
        self.assertTrue(all(row["resources"] for row in summary["scenarios"]))
        self.assertTrue(all(row["task_id"] == "TASK-008" for row in summary["scenarios"]))
        self.assertTrue(all(row["duration_seconds"] is not None for row in summary["scenarios"]))
        self.assertTrue(all(row["result_sha256"] for row in summary["scenarios"]))

    def test_budget_is_per_runtime_hard_limit_and_has_no_automatic_retry(self):
        budget = SMOKE.InvocationBudget(2)
        budget.consume("codex")
        budget.consume("codex")
        with self.assertRaisesRegex(SMOKE.SmokeBlocked, "call budget"):
            budget.consume("codex")
        self.assertEqual(budget.counts, {"hermes": 0, "codex": 2, "claude": 0})

    def test_controlled_process_timeout_terminates_child_and_reports_timeout(self):
        with tempfile.TemporaryDirectory() as directory:
            marker = Path(directory) / "child-finished"
            code = (
                "import pathlib,subprocess,sys,time; "
                "subprocess.Popen([sys.executable,'-c',"
                f"\"import time,pathlib;time.sleep(2);pathlib.Path({str(marker)!r}).write_text('bad')\"]); "
                "time.sleep(2)"
            )
            result = SMOKE.run_process([sys.executable, "-c", code], Path(directory), timeout=0.05)
            self.assertEqual(result["status"], "BLOCKED")
            self.assertEqual(result["reason"], "timeout")
            import time
            time.sleep(2.2)
            self.assertFalse(marker.exists())

    def test_fixture_is_exclusive_cleaned_and_copied_plugin_has_no_operational_state(self):
        parent = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: parent.rmdir() if parent.exists() else None)
        with SMOKE.isolated_fixture(ROOT / "plugins/sdd-composy", base_dir=parent) as fixture:
            self.assertEqual(fixture.parent, parent)
            self.assertTrue((fixture / "plugin" / "skills" / "sdd-init" / "SKILL.md").is_file())
            self.assertTrue((fixture / ".git").is_dir())
            self.assertFalse((fixture / "plugin" / ".planning").exists())
            fixture_path = fixture
        self.assertFalse(fixture_path.exists())
        self.assertEqual(list(parent.iterdir()), [])

    def test_fixture_rejects_symlinks_and_excludes_secret_classes(self):
        with tempfile.TemporaryDirectory() as source_dir, tempfile.TemporaryDirectory() as parent_dir:
            source = Path(source_dir)
            (source / "skills").mkdir()
            (source / "skills/public.txt").write_text("ok")
            (source / "private.key").write_text("private")
            (source / "client.pem").write_text("certificate")
            (source / "credentials.json").write_text("credentials")
            (source / ".planning").mkdir()
            (source / ".planning/state.json").write_text("{}")
            (source / "outside-link").symlink_to(Path(parent_dir))
            with self.assertRaisesRegex(SMOKE.SmokeBlocked, "symlink"):
                with SMOKE.isolated_fixture(source, base_dir=Path(parent_dir)):
                    pass
            (source / "outside-link").unlink()
            with SMOKE.isolated_fixture(source, base_dir=Path(parent_dir)) as fixture:
                copied = fixture / "plugin"
                self.assertTrue((copied / "skills/public.txt").is_file())
                self.assertFalse((copied / "private.key").exists())
                self.assertFalse((copied / "client.pem").exists())
                self.assertFalse((copied / "credentials.json").exists())
                self.assertFalse((copied / ".planning").exists())

    def test_sanitizer_redacts_secrets_and_sensitive_absolute_paths(self):
        raw = "token=secret-value Authorization: Bearer abc123 /Users/person/project"
        sanitized = SMOKE.sanitize(raw)
        self.assertNotIn("secret-value", sanitized)
        self.assertNotIn("abc123", sanitized)
        self.assertNotIn("/Users/person", sanitized)
        self.assertIn("[REDACTED]", sanitized)

    def test_fixture_approval_must_be_explicitly_synthetic_and_scoped(self):
        with self.assertRaisesRegex(SMOKE.SmokeBlocked, "invented approval"):
            SMOKE.validate_fixture_approval({"status": "APPROVED"})
        SMOKE.validate_fixture_approval({
            "status": "APPROVED", "synthetic": True, "scope": "task-08-runtime-smoke"
        })

    def test_real_fleet_is_blocked_without_external_acknowledgement(self):
        with tempfile.TemporaryDirectory() as directory:
            called = []
            summary = SMOKE.run_acceptance(
                mode="real", runtime="hermes", language="pt-BR", scenario="fleet",
                output=Path(directory) / "run", plugin_root=ROOT / "plugins/sdd-composy",
                provider_launcher=lambda *args, **kwargs: called.append((args, kwargs)),
                fleet_acknowledged=False,
            )
        self.assertEqual(called, [])
        self.assertEqual(summary["scenarios"][0]["status"], "BLOCKED")
        self.assertIn("acknowledgement", summary["scenarios"][0]["reason"])

    def test_launcher_measurements_are_preserved_in_real_records(self):
        with tempfile.TemporaryDirectory() as directory:
            summary = SMOKE.run_acceptance(
                mode="real", runtime="codex", language="en-US", scenario="read-only",
                output=Path(directory) / "run", plugin_root=ROOT / "plugins/sdd-composy",
                provider_launcher=lambda **_kwargs: {
                    "status": "PASS", "reason": None, "exit_code": 0,
                    "duration_seconds": 1.25, "result_sha256": "a" * 64,
                    "command": ["codex", "exec", "[REDACTED]"],
                    "resources": ["fixture-123"], "version": "test-version",
                    "provider": "fake", "model": None,
                })
        record = summary["scenarios"][0]
        self.assertEqual(record["duration_seconds"], 1.25)
        self.assertEqual(record["result_sha256"], "a" * 64)
        self.assertEqual(record["resources"], ["fixture-123"])
        self.assertEqual(record["version"], "test-version")

    def test_cli_writes_atomic_json_summary_with_null_unavailable_usage(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "offline"
            completed = subprocess.run([
                sys.executable, str(ROOT / "scripts/sdd_runtime_smoke.py"),
                "--mode", "offline", "--runtime", "all", "--language", "both",
                "--scenario", "all", "--output", str(output),
            ], cwd=ROOT, text=True, capture_output=True, check=False)
            self.assertEqual(completed.returncode, 0, completed.stderr)
            summary = json.loads((output / "summary.json").read_text())
            self.assertEqual(summary["verdict"], "PASS")
            self.assertIsNone(summary["usage"])
            self.assertFalse((output / "summary.json.tmp").exists())

    def test_output_and_fingerprint_reject_symlink_leaf_and_ancestors(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            real = root / "real"; real.mkdir()
            alias = root / "alias"; alias.symlink_to(real, target_is_directory=True)
            with self.assertRaisesRegex(SMOKE.SmokeBlocked, "symlink"):
                SMOKE.write_summary(alias / "child", {"verdict": "PASS"})
            source = root / "source"; source.mkdir()
            (source / "target").write_text("secret")
            (source / "linked").symlink_to(source / "target")
            with self.assertRaisesRegex(SMOKE.SmokeBlocked, "symlink"):
                SMOKE.tree_fingerprint(source)

    def test_failed_atomic_replace_preserves_existing_summary(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            target = output / "summary.json"
            target.write_text("original")
            with patch.object(SMOKE.os, "replace", side_effect=OSError("failure")):
                with self.assertRaises(OSError):
                    SMOKE.write_summary(output, {"verdict": "PASS"})
            self.assertEqual(target.read_text(), "original")
            self.assertEqual(list(output.iterdir()), [target])

    def test_real_cli_exposes_provider_entry_point_but_remains_gated(self):
        completed = subprocess.run([
            sys.executable, str(ROOT / "scripts/sdd_runtime_smoke.py"),
            "--mode", "real", "--runtime", "codex", "--language", "pt-BR",
            "--scenario", "fleet", "--provider-entry-point", "production",
            "--output", str(Path(tempfile.gettempdir()) / "sdd-real-gated-test"),
        ], cwd=ROOT, text=True, capture_output=True, check=False)
        self.assertEqual(completed.returncode, 2)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["verdict"], "BLOCKED")


if __name__ == "__main__":
    unittest.main()
