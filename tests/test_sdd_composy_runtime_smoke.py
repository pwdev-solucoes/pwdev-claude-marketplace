import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest


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


if __name__ == "__main__":
    unittest.main()
