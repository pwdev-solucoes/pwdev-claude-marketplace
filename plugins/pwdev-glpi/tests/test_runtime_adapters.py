import json
import re
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
        tools = re.findall(r"^\| `([a-z_]+)` \|", reference.split("## Prompts MCP", 1)[0], re.MULTILINE)
        self.assertEqual(len(tools), 20)
        self.assertEqual(len(set(tools)), 20)
        self.assertEqual(
            set(tools),
            {
                "search_tickets", "get_ticket", "create_ticket", "update_ticket",
                "add_ticket_followup", "close_ticket", "request_ticket_validation",
                "answer_ticket_validation", "upload_document", "link_document",
                "search_users", "get_user", "search_groups", "get_group",
                "search_assets", "get_asset", "search_projects", "get_project",
                "search_kb", "get_kb_article",
            },
        )

    def test_mcp_server_contract_is_pinned_and_keeps_runtime_env(self):
        config = json.loads((PLUGIN / ".mcp.json").read_text())
        server = config["glpi"]
        self.assertEqual(server["command"], "npx")
        self.assertEqual(server["args"], ["-y", "@soarescbm/mcp-glpi@0.4.0"])
        self.assertEqual(
            set(server["env"]),
            {"GLPI_BASE_URL", "GLPI_PAT", "GLPI_APP_TOKEN", "GLPI_USE_SESSION", "GLPI_TIMEOUT_MS"},
        )

    def test_mcp_prompt_and_resource_sections_have_exact_entries(self):
        reference = (PLUGIN / "references" / "mcp-tools.md").read_text()
        prompts = re.findall(r"^\| `([a-z_]+)` \|.*\|", reference.split("## Prompts MCP", 1)[1].split("## Resources MCP", 1)[0], re.MULTILINE)
        self.assertEqual(prompts, ["triage_ticket", "summarize_tickets"])
        resources = re.findall(r"`(glpi://[^`]+)`", reference.split("## Resources MCP", 1)[1].split("## O que", 1)[0])
        self.assertEqual(resources, ["glpi://ticket/{id}", "glpi://asset/{itemtype}/{id}", "glpi://kb/{id}"])


if __name__ == "__main__":
    unittest.main()
