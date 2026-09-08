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


if __name__ == "__main__":
    unittest.main()
