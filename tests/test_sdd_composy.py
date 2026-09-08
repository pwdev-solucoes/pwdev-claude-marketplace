"""Structural contract tests for the portable sdd-composy plugin."""

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "sdd-composy"
CLAUDE_MANIFEST = PLUGIN / ".claude-plugin" / "plugin.json"
CODEX_MANIFEST = PLUGIN / ".codex-plugin" / "plugin.json"
CLAUDE_MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"
CODEX_MARKETPLACE = ROOT / ".agents" / "plugins" / "marketplace.json"
REFERENCES = PLUGIN / "references"
READMES = (PLUGIN / "README.md", PLUGIN / "README.pt-BR.md")


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


if __name__ == "__main__":
    unittest.main()
