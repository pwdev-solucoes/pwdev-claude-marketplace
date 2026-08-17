import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "pwdev-flow"
CLAUDE_MANIFEST = PLUGIN / ".claude-plugin" / "plugin.json"
CLAUDE_MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"

CLAUDE_COMMANDS = {
    "audit", "compat", "delegate", "design", "discover", "execute",
    "fleet", "health", "init", "maintenance", "memory", "plan",
    "product", "quick", "review", "simplify", "verify",
}

COMMAND_TO_SKILL = {name: f"flow-{name}" for name in CLAUDE_COMMANDS}

EXPECTED_SCRIPTS = {
    "claude-fleet-run.sh",
    "claude-fleet-up.sh",
    "fleet-common.sh",
    "fleet-dashboard.sh",
    "fleet-engine-claude.sh",
    "fleet-engine-codex.sh",
    "fleet-launch-core.sh",
    "fleet-run-core.sh",
    "fleet-run.sh",
    "fleet-teardown.sh",
    "fleet-up.sh",
    "flow_audit.py",
    "migrate_legacy.py",
    "run-agent.sh",
}


class ClaudeCompatibilityTests(unittest.TestCase):
    def test_claude_manifest_is_native_and_hook_free(self):
        manifest = json.loads(CLAUDE_MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual(manifest["name"], "pwdev-flow")
        self.assertEqual(manifest["version"], "0.6.0")
        self.assertFalse({"hooks", "mcpServers", "apps"} & manifest.keys())

    def test_every_claude_command_maps_to_one_portable_skill(self):
        command_files = {p.stem: p for p in (PLUGIN / "commands").glob("*.md")}
        self.assertEqual(set(command_files), CLAUDE_COMMANDS)
        for name, path in command_files.items():
            text = path.read_text(encoding="utf-8")
            self.assertIn("$ARGUMENTS", text)
            self.assertEqual(text.count("$ARGUMENTS"), 1)
            self.assertIn(
                f"${{CLAUDE_PLUGIN_ROOT}}/skills/{COMMAND_TO_SKILL[name]}/SKILL.md",
                text,
            )
            self.assertNotIn("--dangerously-bypass-approvals-and-sandbox", text)

    def test_command_adapters_have_frontmatter_and_safe_resource_paths(self):
        for path in (PLUGIN / "commands").glob("*.md"):
            with self.subTest(command=path.name):
                text = path.read_text(encoding="utf-8")
                self.assertRegex(text, r"^---\ndescription: .+\n(?:argument-hint: .+\n)?---\n")
                for target in re.findall(r"\$\{CLAUDE_PLUGIN_ROOT\}([^\s)`]+)", text):
                    self.assertFalse(".." in Path(target).parts)
                    self.assertTrue((PLUGIN / target.lstrip("/")).is_file())

    def test_claude_marketplace_registers_strict_local_plugin(self):
        marketplace = json.loads(CLAUDE_MARKETPLACE.read_text(encoding="utf-8"))
        entries = {entry["name"]: entry for entry in marketplace["plugins"]}
        entry = entries["pwdev-flow"]
        self.assertEqual(entry["source"], "./plugins/pwdev-flow")
        self.assertEqual(entry["category"], "workflow")
        self.assertTrue(entry["strict"])

    def test_public_docs_describe_dual_runtime_commands(self):
        for readme in (ROOT / "README.md", ROOT / "README.pt-BR.md"):
            text = readme.read_text(encoding="utf-8")
            with self.subTest(readme=readme.name):
                self.assertIn("pwdev-flow", text)
                self.assertIn("claude -p", text)
                self.assertIn("codex exec", text)
                for command in CLAUDE_COMMANDS:
                    self.assertIn(f"/pwdev-flow:{command}", text)

    def test_codex_version_is_new_compatible_base(self):
        manifest = json.loads(
            (PLUGIN / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
        )
        self.assertRegex(manifest["version"], r"^0\.6\.0(?:\+codex\.\d{14})?$")

    def test_dual_runtime_script_inventory_is_exact(self):
        actual = {p.name for p in (PLUGIN / "scripts").iterdir() if p.is_file()}
        self.assertEqual(actual, EXPECTED_SCRIPTS)

    def test_no_claude_hooks_agents_mcp_or_apps_are_packaged(self):
        manifest = json.loads(CLAUDE_MANIFEST.read_text(encoding="utf-8"))
        self.assertFalse({"hooks", "agents", "mcpServers", "apps"} & manifest.keys())
        self.assertFalse((PLUGIN / "hooks").exists())
        self.assertFalse((PLUGIN / "agents").exists())

    def test_native_engines_keep_privileged_vectors_separate(self):
        codex = (PLUGIN / "scripts/fleet-engine-codex.sh").read_text(encoding="utf-8")
        claude = (PLUGIN / "scripts/fleet-engine-claude.sh").read_text(encoding="utf-8")
        self.assertIn("codex exec", codex)
        self.assertIn("--sandbox danger-full-access", codex)
        self.assertIn("claude -p", claude)
        self.assertNotIn("codex exec", claude)
        self.assertNotIn("--sandbox", claude)

    def test_claude_launcher_selects_claude_runner(self):
        launcher = (PLUGIN / "scripts/claude-fleet-up.sh").read_text(encoding="utf-8")
        runner = (PLUGIN / "scripts/claude-fleet-run.sh").read_text(encoding="utf-8")
        self.assertIn('fleet-launch-core.sh" claude', launcher)
        self.assertIn('fleet-run-core.sh" claude', runner)

    def test_claude_runner_exports_runtime_identity(self):
        runner = (PLUGIN / "scripts/claude-fleet-run.sh").read_text(encoding="utf-8")
        self.assertRegex(runner, r"FLOW_FLEET_RUNTIME=claude")


if __name__ == "__main__":
    unittest.main()
