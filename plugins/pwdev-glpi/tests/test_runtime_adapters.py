import json
import importlib.util
import re
import shutil
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[3]
PLUGIN = ROOT / "plugins" / "pwdev-glpi"
HERMES_INIT = PLUGIN / ".hermes-plugin" / "__init__.py"


def load(path, name="glpi_hermes_test"):
    spec = importlib.util.spec_from_file_location(name, str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class HermesContext:
    def __init__(self):
        self.skills = {}
        self.hooks = {}

    def register_skill(self, name, path):
        self.skills[name] = path

    def register_hook(self, event, handler):
        self.hooks[event] = handler


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

    def test_hermes_manifest_and_bootstrap_register_glpi(self):
        manifest = (PLUGIN / ".hermes-plugin" / "plugin.yaml").read_text()
        self.assertIn("name: pwdev-glpi", manifest)
        self.assertIn("version: 1.2.0", manifest)
        self.assertIn("- pre_llm_call", manifest)
        ctx = HermesContext()
        load(HERMES_INIT).register(ctx)
        self.assertIn("glpi", ctx.skills)
        self.assertIn("pre_llm_call", ctx.hooks)

    def test_hermes_bootstrap_works_in_clone_and_flattened_layouts(self):
        with tempfile.TemporaryDirectory() as temp:
            for layout in ("clone", "flat"):
                root = Path(temp) / layout / "pwdev-glpi"
                plugin_dir = root / ".hermes-plugin" if layout == "clone" else root
                (root / "skills" / "glpi").mkdir(parents=True)
                shutil.copy(PLUGIN / "skills/glpi/SKILL.md", root / "skills/glpi/SKILL.md")
                plugin_dir.mkdir(exist_ok=True)
                shutil.copy(HERMES_INIT, plugin_dir / "__init__.py")
                ctx = HermesContext()
                load(plugin_dir / "__init__.py", "hermes_" + layout).register(ctx)
                self.assertEqual(list(ctx.skills), ["glpi"])

    def test_hermes_hook_injects_only_on_first_turn_without_mutating_config(self):
        module = load(HERMES_INIT, "hermes_hook")
        ctx = HermesContext()
        module.register(ctx)
        config = {"user": {"theme": "dark"}}
        before = json.dumps(config, sort_keys=True)
        first = ctx.hooks["pre_llm_call"](is_first_turn=True, config=config)
        self.assertIsInstance(first, dict)
        self.assertIn("glpi", first["context"].lower())
        self.assertEqual(json.dumps(config, sort_keys=True), before)
        self.assertIsNone(ctx.hooks["pre_llm_call"](is_first_turn=False, config=config))


if __name__ == "__main__":
    unittest.main()
