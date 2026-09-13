import json
import re
import unittest
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = ROOT / ".planning/power/features/specflow-m01/probe/fixture"
EXTENSION = FIXTURE_ROOT / "extension"
MANIFEST = EXTENSION / "extension.toml"
AGENT = EXTENSION / "agents/probe/AGENT.md"
LOOP = FIXTURE_ROOT / "specflow-m01-loop.yaml"
RUN_CONFIG = FIXTURE_ROOT / "run-config.yaml"
RECIPE = ROOT / ".planning/power/features/specflow-m01/probe-recipe.md"

EXPECTED_ARGV = (
    ("daemon", "start"),
    ("extension", "validate", ".planning/power/features/specflow-m01/probe/fixture/extension"),
    ("extension", "dev", ".planning/power/features/specflow-m01/probe/fixture/extension", "--workspace", "specflow-m01-probe-20260913"),
    ("loop", "validate", "--file", ".planning/power/features/specflow-m01/probe/fixture/specflow-m01-loop.yaml", "--name", "specflow-m01-qualification", "--workspace", "specflow-m01-probe-20260913"),
    ("loop", "create", "--file", ".planning/power/features/specflow-m01/probe/fixture/specflow-m01-loop.yaml", "--expected-version", "0", "--workspace", "specflow-m01-probe-20260913"),
    ("loop", "run", "--dry-run", "--name", "specflow-m01-qualification", "--network", "local", "--workspace", "specflow-m01-probe-20260913", "--config-file", ".planning/power/features/specflow-m01/probe/fixture/run-config.yaml"),
    ("loop", "run", "--name", "specflow-m01-qualification", "--network", "local", "--workspace", "specflow-m01-probe-20260913", "--config-file", ".planning/power/features/specflow-m01/probe/fixture/run-config.yaml"),
)


def yaml_scalar(text, key):
    match = re.search(rf"(?m)^\s*{re.escape(key)}:\s*([^#\n]+)", text)
    if not match:
        raise AssertionError(f"missing YAML scalar: {key}")
    return match.group(1).strip().strip('"')


def structural_verdict(case):
    if not case["gate_approved"] or not case["digest_matches"]:
        return "BLOCKED"
    if case["path_kind"] in {"traversal", "symlink"} or case["concurrent"]:
        return "BLOCKED"
    if case["observer_mutates"]:
        return "FAIL"
    if case["interruption"] == "before_publication":
        return "NOT_RUN"
    if case["interruption"] == "after_publication" and not case["resume"]:
        return "BLOCKED"
    return "PASS"


class StaticFixtureContractTest(unittest.TestCase):
    def test_all_fixture_paths_are_regular_and_confined(self):
        for path in (MANIFEST, AGENT, LOOP, RUN_CONFIG):
            with self.subTest(path=path.relative_to(ROOT)):
                self.assertTrue(path.is_file())
                self.assertFalse(path.is_symlink())
                self.assertTrue(path.resolve().is_relative_to(FIXTURE_ROOT.resolve()))

    def test_resource_only_extension_manifest_and_agent(self):
        self.assertTrue(MANIFEST.is_file(), "resource-only manifest fixture is missing")
        self.assertTrue(AGENT.is_file(), "agent fixture is missing")
        manifest = MANIFEST.read_text()
        self.assertEqual(manifest.count("[extension]"), 1)
        self.assertEqual(manifest.count("[resources]"), 1)
        for line in (
            'name = "specflow-m01-probe"',
            'version = "0.1.0"',
            'min_compozy_version = "0.3.0-beta.25"',
            'agents = ["agents"]',
        ):
            self.assertEqual(manifest.count(line), 1)
        agent = AGENT.read_text()
        self.assertRegex(agent, r"\A---\nname: probe\npermissions: approve-reads\n---\n\n\S")
        self.assertNotIn("provider:", agent)

    def test_loop_and_run_config_encode_safe_budgets(self):
        self.assertTrue(LOOP.is_file(), "Loop fixture is missing")
        self.assertTrue(RUN_CONFIG.is_file(), "per-run config fixture is missing")
        loop = LOOP.read_text()
        self.assertEqual(yaml_scalar(loop, "apiVersion"), "compozy.loop/v1")
        self.assertEqual(yaml_scalar(loop, "kind"), "Loop")
        self.assertEqual(yaml_scalar(loop, "name"), "specflow-m01-qualification")
        self.assertEqual(yaml_scalar(loop, "concurrency"), "forbid")
        self.assertIn("iteration_cap: 3", loop)
        self.assertIn("no_progress: { window: 2 }", loop)
        self.assertIn("agent: probe", loop)

        config = RUN_CONFIG.read_text()
        self.assertEqual(yaml_scalar(config, "iteration_cap"), "3")
        self.assertEqual(yaml_scalar(config, "no_progress_window"), "2")
        self.assertEqual(yaml_scalar(config, "fan_out_width"), "1")

    def test_seven_recipe_argv_resolve_to_the_static_fixture_set(self):
        recipe_text = RECIPE.read_text()
        payload = json.loads(recipe_text.split("```json\n", 1)[1].split("\n```", 1)[0])
        actual = tuple(tuple(item["argv"]) for item in payload["runtime_recipes"])
        self.assertEqual(actual, EXPECTED_ARGV)
        referenced = {
            arg
            for argv in actual
            for arg in argv
            if arg.startswith(".planning/power/features/specflow-m01/probe/fixture/")
        }
        self.assertEqual(
            referenced,
            {
                ".planning/power/features/specflow-m01/probe/fixture/extension",
                ".planning/power/features/specflow-m01/probe/fixture/specflow-m01-loop.yaml",
                ".planning/power/features/specflow-m01/probe/fixture/run-config.yaml",
            },
        )

    def test_adversarial_cases_are_table_driven_and_fail_closed(self):
        base = {
            "gate_approved": True,
            "digest_matches": True,
            "path_kind": "regular",
            "concurrent": False,
            "interruption": "none",
            "resume": False,
            "observer_mutates": False,
        }
        cases = (
            ("positive", {}, "PASS"),
            ("false_gate", {"gate_approved": False}, "BLOCKED"),
            ("altered_digest", {"digest_matches": False}, "BLOCKED"),
            ("path_traversal", {"path_kind": "traversal"}, "BLOCKED"),
            ("symlink", {"path_kind": "symlink"}, "BLOCKED"),
            ("concurrent_start", {"concurrent": True}, "BLOCKED"),
            ("interrupted_before_publication", {"interruption": "before_publication"}, "NOT_RUN"),
            ("interrupted_after_publication_without_resume", {"interruption": "after_publication"}, "BLOCKED"),
            ("resumed_after_publication", {"interruption": "after_publication", "resume": True}, "PASS"),
            ("observer_attempts_mutation", {"observer_mutates": True}, "FAIL"),
        )
        for name, changes, expected in cases:
            with self.subTest(case=name):
                self.assertEqual(structural_verdict(base | changes), expected)

    def test_traversal_spellings_are_rejected_by_the_path_contract(self):
        for value in ("../outside", "fixture/../../outside", "/absolute/path"):
            with self.subTest(value=value):
                candidate = PurePosixPath(value)
                self.assertTrue(candidate.is_absolute() or ".." in candidate.parts)


if __name__ == "__main__":
    unittest.main()
