import json
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[3]
PLUGIN = ROOT / "plugins" / "pwdev-glpi"


class RuntimeAdapterContractTests(unittest.TestCase):
    def test_codex_manifest_declares_glpi_skill_and_mcp_config(self):
        manifest_path = PLUGIN / ".codex-plugin" / "plugin.json"
        self.assertTrue(manifest_path.is_file())
        manifest = json.loads(manifest_path.read_text())
        self.assertEqual(manifest["name"], "pwdev-glpi")
        self.assertEqual(manifest["version"], "1.2.0")
        self.assertEqual(manifest["skills"], "./skills/")
        self.assertEqual(manifest["mcpServers"], "./.mcp.json")

    def test_openai_skill_adapter_is_named_glpi(self):
        adapter = (PLUGIN / "skills" / "glpi" / "agents" / "openai.yaml").read_text()
        self.assertIn("display_name:", adapter)
        self.assertIn("$glpi", adapter)

    def test_mcp_contract_preserves_twenty_tools_two_prompts_three_resources(self):
        reference = (PLUGIN / "references" / "mcp-tools.md").read_text()
        self.assertIn("20 tools + 2 prompts + 3 resources", reference)


if __name__ == "__main__":
    unittest.main()
