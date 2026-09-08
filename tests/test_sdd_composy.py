"""Structural contract tests for the portable sdd-composy plugin."""

import json
import unittest
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "sdd-composy"
CLAUDE_MANIFEST = PLUGIN / ".claude-plugin" / "plugin.json"
CODEX_MANIFEST = PLUGIN / ".codex-plugin" / "plugin.json"
CLAUDE_MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"
CODEX_MARKETPLACE = ROOT / ".agents" / "plugins" / "marketplace.json"
REFERENCES = PLUGIN / "references"
READMES = (PLUGIN / "README.md", PLUGIN / "README.pt-BR.md")
SCHEMAS = PLUGIN / "schemas"


def assert_schema_valid(test, schema, value, root=None, path="$"):
    """Small dependency-free validator for the schema features used by fixtures."""
    root = root or schema
    if "$ref" in schema:
        target = root
        for part in schema["$ref"].removeprefix("#/").split("/"):
            target = target[part]
        return assert_schema_valid(test, target, value, root, path)
    if "const" in schema:
        test.assertEqual(value, schema["const"], path)
    if "enum" in schema:
        test.assertIn(value, schema["enum"], path)
    if "if" in schema:
        try:
            assert_schema_valid(test, schema["if"], value, root, path)
        except AssertionError:
            pass
        else:
            assert_schema_valid(test, schema["then"], value, root, path)
    expected = schema.get("type")
    if expected is None and ("properties" in schema or "required" in schema):
        expected = "object"
    if isinstance(expected, list):
        if value is None and "null" in expected:
            return
        expected = next(item for item in expected if item != "null")
    if expected == "object":
        test.assertIsInstance(value, dict, path)
        for key in schema.get("required", []):
            test.assertIn(key, value, f"{path}.{key}")
        for key, child in schema.get("properties", {}).items():
            if key in value:
                assert_schema_valid(test, child, value[key], root, f"{path}.{key}")
    elif expected == "array":
        test.assertIsInstance(value, list, path)
        test.assertGreaterEqual(len(value), schema.get("minItems", 0), path)
        if schema.get("uniqueItems"):
            test.assertEqual(len(value), len({json.dumps(v, sort_keys=True) for v in value}), path)
        for index, item in enumerate(value):
            assert_schema_valid(test, schema.get("items", {}), item, root, f"{path}[{index}]")
    elif expected == "string":
        test.assertIsInstance(value, str, path)
        test.assertGreaterEqual(len(value), schema.get("minLength", 0), path)
        if "pattern" in schema:
            test.assertRegex(value, schema["pattern"], path)
        if schema.get("format") == "date-time":
            datetime.fromisoformat(value.replace("Z", "+00:00"))
    elif expected == "integer":
        test.assertIsInstance(value, int, path)
        test.assertGreaterEqual(value, schema.get("minimum", value), path)
    elif expected == "boolean":
        test.assertIsInstance(value, bool, path)


class SddComposyManifestTest(unittest.TestCase):
    def test_dual_runtime_manifests_are_discoverable(self) -> None:
        self.assertTrue(CLAUDE_MANIFEST.is_file(), "Claude manifest must exist")
        self.assertTrue(CODEX_MANIFEST.is_file(), "Codex manifest must exist")

        claude = json.loads(CLAUDE_MANIFEST.read_text(encoding="utf-8"))
        codex = json.loads(CODEX_MANIFEST.read_text(encoding="utf-8"))

        self.assertEqual(claude["name"], "sdd-composy")
        self.assertEqual(codex["name"], "sdd-composy")
        self.assertEqual(codex["skills"], "./skills/")
        self.assertEqual(claude["version"].split("+", 1)[0], "0.1.0")
        self.assertEqual(codex["version"].split("+", 1)[0], "0.1.0")
        self.assertEqual(codex["interface"]["displayName"], "SDD Composy")
        for manifest in (claude, codex):
            self.assertNotIn("hooks", manifest)
            self.assertNotIn("mcpServers", manifest)
            self.assertNotIn("apps", manifest)

    def test_claude_marketplace_registers_plugin(self) -> None:
        marketplace = json.loads(CLAUDE_MARKETPLACE.read_text(encoding="utf-8"))
        entries = {entry["name"]: entry for entry in marketplace["plugins"]}
        entry = entries["sdd-composy"]

        self.assertEqual(entry["source"], "./plugins/sdd-composy")
        self.assertEqual(entry["category"], "workflow")
        self.assertTrue(entry["strict"])

    def test_codex_marketplace_registers_plugin(self) -> None:
        marketplace = json.loads(CODEX_MARKETPLACE.read_text(encoding="utf-8"))
        entries = {entry["name"]: entry for entry in marketplace["plugins"]}
        entry = entries["sdd-composy"]

        self.assertEqual(
            entry["source"],
            {"source": "local", "path": "./plugins/sdd-composy"},
        )
        self.assertEqual(entry["policy"]["installation"], "AVAILABLE")
        self.assertEqual(entry["policy"]["authentication"], "ON_INSTALL")
        self.assertEqual(entry["category"], "Developer Tools")


class SddComposySharedContractTest(unittest.TestCase):
    def reference(self, name: str) -> str:
        path = REFERENCES / f"{name}.md"
        self.assertTrue(path.is_file(), f"shared reference must exist: {path}")
        return path.read_text(encoding="utf-8")

    def test_workflow_defines_canonical_lifecycle_and_gates(self) -> None:
        workflow = self.reference("workflow")
        for phase in (
            "INIT", "MAP", "PRD", "STORIES", "TECHSPEC", "TASKS",
            "EXECUTE", "QA", "EVIDENCE", "REVIEW", "VERIFY", "COMPLETE",
        ):
            self.assertIn(phase, workflow)
        self.assertIn("NOT_APPLICABLE", workflow)
        self.assertIn("explicit human approval", workflow)
        self.assertIn("fresh", workflow)
        self.assertIn("QUICK", workflow)
        self.assertIn("5 implementation files", workflow)

    def test_artifacts_separate_human_and_operational_roots(self) -> None:
        artifacts = self.reference("artifacts")
        self.assertIn("tasks/prd-<slug>/", artifacts)
        self.assertIn(".planning/sdd-composy/", artifacts)
        self.assertIn("OKF v0.2", artifacts)
        self.assertIn("type", artifacts)
        self.assertIn("unknown", artifacts.lower())
        self.assertIn("events.jsonl", artifacts)
        self.assertIn("trace.json", artifacts)
        self.assertIn("never edited directly", artifacts.lower())

    def test_states_define_guarded_task_transitions(self) -> None:
        states = self.reference("states")
        for state in (
            "pending", "ready", "running", "qa_required", "evidence_required",
            "review_required", "verify_required", "complete", "blocked",
            "rejected", "skipped",
        ):
            self.assertIn(state, states)
        self.assertIn("rejected -> ready", states)
        self.assertIn("dependencies", states)
        self.assertIn("explicit justification", states)
        self.assertIn("fresh test evidence", states)

    def test_safety_prohibits_secrets_and_unsafe_automation(self) -> None:
        safety = self.reference("safety")
        for prohibited in (
            ".env", "credentials", "tokens", "private keys", "certificates",
            "fleet environment files",
        ):
            self.assertIn(prohibited, safety)
        self.assertIn("Never merge fleet branches automatically", safety)
        self.assertIn("Never infer human approval", safety)
        self.assertIn("Preserve unknown JSON fields", safety)
        self.assertIn("same-directory temporary files", safety)
        self.assertIn("atomically replace", safety)


class SddComposyRuntimeContractTest(unittest.TestCase):
    def test_runtime_contract_defines_shared_core_discovery(self) -> None:
        runtime = (REFERENCES / "runtime.md").read_text(encoding="utf-8")
        for shared_root in ("skills/", "references/", "scripts/", "templates/", "schemas/"):
            self.assertIn(shared_root, runtime)
        self.assertIn(".claude-plugin/plugin.json", runtime)
        self.assertIn(".codex-plugin/plugin.json", runtime)
        self.assertIn('"skills": "./skills/"', runtime)
        self.assertIn("commands/<name>.md", runtime)
        self.assertIn("thin adapter", runtime.lower())
        self.assertIn("must not duplicate", runtime.lower())
        self.assertIn("must not depend", runtime.lower())
        self.assertIn("pwdev-flow", runtime)
        self.assertIn("pwdev-feat", runtime)

    def test_bilingual_readmes_describe_the_same_portable_contract(self) -> None:
        for path in READMES:
            text = path.read_text(encoding="utf-8")
            self.assertIn("Claude Code", text)
            self.assertIn("Codex", text)
            self.assertIn("tasks/prd-<slug>/", text)
            self.assertIn(".planning/sdd-composy/", text)
            self.assertIn("OKF v0.2", text)
            self.assertIn("$sdd-composy-<name>", text)
            self.assertIn("/sdd-composy:<name>", text)
            self.assertIn("references/runtime.md", text)


class SddComposyCoreSchemaTest(unittest.TestCase):
    def schema(self, name: str) -> dict:
        path = SCHEMAS / f"{name}.schema.json"
        self.assertTrue(path.is_file(), f"core schema must exist: {path}")
        return json.loads(path.read_text(encoding="utf-8"))

    def test_schema_shape_is_versioned_strict_and_extension_safe(self) -> None:
        for name in ("config", "state", "tasks", "trace"):
            schema = self.schema(name)
            self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
            self.assertEqual(schema["type"], "object")
            self.assertIn("schema_version", schema["required"])
            self.assertEqual(schema["properties"]["schema_version"]["const"], "1")
            self.assertTrue(schema["additionalProperties"])
            self.assertIn("definitions", schema)

    def test_valid_core_documents_include_portable_extensions(self) -> None:
        fixtures = {
            "config": {"schema_version": "1", "actor_id": "agent:codex-1", "human_root": "tasks", "operational_root": ".planning/sdd-composy", "x-team": {"mode": "safe"}},
            "state": {"schema_version": "1", "revision": 3, "stage": "EXECUTE", "active_prd": "billing-api", "active_task": "TASK-004", "last_gate": {"name": "TASKS", "status": "approved", "at": "2026-09-08T12:00:00+00:00", "actor_id": "human:paulo"}, "blockers": [], "loops": [], "fleet": [], "trace": {"healthy": True, "source_event_count": 8}, "updated_at": "2026-09-08T12:01:00Z", "next_action": "Run focused tests", "x-runtime": "codex"},
            "tasks": {"schema_version": "1", "prd_slug": "billing-api", "updated_at": "2026-09-08T12:01:00Z", "tasks": [{"id": "TASK-004", "title": "Add schemas", "state": "ready", "dependencies": ["TASK-003"], "acceptance_criteria": ["CA-001"], "verification_commands": ["python3 -m unittest"], "allowed_paths": ["plugins/sdd-composy/schemas/"], "evidence_required": False, "x-owner": "platform"}]},
            "trace": {"schema_version": "1", "source_event_count": 1, "generated_at": "2026-09-08T12:02:00Z", "events": [{"sequence": 1, "id": "EVT-000001", "at": "2026-09-08T12:01:00Z", "actor_id": "agent:codex-1", "type": "task.transitioned", "stage": "EXECUTE", "task_id": "TASK-004", "data": {"from": "ready", "to": "running"}, "x-host": "codex"}]},
        }
        for name, fixture in fixtures.items():
            assert_schema_valid(self, self.schema(name), fixture)

    def test_invalid_identifiers_states_and_roots_are_rejected(self) -> None:
        invalid = {
            "config": {"schema_version": "1", "actor_id": "bad id", "human_root": ".planning", "operational_root": "tasks"},
            "state": {"schema_version": "1", "revision": 0, "stage": "DONE", "active_prd": None, "active_task": None, "last_gate": None, "blockers": [], "loops": [], "fleet": [], "trace": {"healthy": True, "source_event_count": 0}, "updated_at": "2026-09-08T12:01:00Z", "next_action": "none"},
            "tasks": {"schema_version": "1", "prd_slug": "Bad Slug", "updated_at": "2026-09-08T12:01:00Z", "tasks": [{"id": "4", "title": "Bad", "state": "done", "dependencies": [], "acceptance_criteria": [], "verification_commands": [], "allowed_paths": [], "evidence_required": False}]},
            "trace": {"schema_version": "1", "source_event_count": 1, "generated_at": "2026-09-08T12:02:00Z", "events": [{"sequence": 0, "id": "event 1", "at": "2026-09-08T12:01:00Z", "actor_id": "bad id", "type": "bad type!", "stage": "DONE", "task_id": "4", "data": {}}]},
        }
        for name, fixture in invalid.items():
            with self.assertRaises(AssertionError, msg=name):
                assert_schema_valid(self, self.schema(name), fixture)

    def test_skipped_task_requires_explicit_non_empty_justification(self) -> None:
        schema = self.schema("tasks")
        task_schema = schema["definitions"]["task"]
        skipped = {
            "id": "TASK-004",
            "title": "Superseded task",
            "state": "skipped",
            "dependencies": [],
            "acceptance_criteria": ["CA-001"],
            "verification_commands": ["python3 -m unittest"],
            "allowed_paths": ["plugins/sdd-composy/schemas/"],
            "evidence_required": False,
            "justification": "Superseded by the approved TASK-005 contract",
            "x-authority": "human:paulo",
        }

        assert_schema_valid(self, task_schema, skipped, schema)
        for invalid_justification in (None, ""):
            invalid = dict(skipped)
            if invalid_justification is None:
                invalid.pop("justification")
            else:
                invalid["justification"] = invalid_justification
            with self.subTest(justification=invalid_justification):
                with self.assertRaises(AssertionError):
                    assert_schema_valid(self, task_schema, invalid, schema)


if __name__ == "__main__":
    unittest.main()
