import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "pwdev-flow"
MANIFEST = PLUGIN / ".codex-plugin" / "plugin.json"
MARKETPLACE = ROOT / ".agents" / "plugins" / "marketplace.json"
SKILLS = (
    "flow-init",
    "flow-quick",
    "flow-discover",
    "flow-design",
    "flow-plan",
    "flow-execute",
    "flow-review",
    "flow-verify",
    "flow-product",
    "flow-memory",
    "flow-simplify",
    "flow-health",
    "flow-maintenance",
    "flow-audit",
    "flow-compat",
    "flow-fleet",
    "flow-delegate",
)
REFERENCES = (
    "workflow.md",
    "artifacts.md",
    "collaboration.md",
    "safety.md",
    "discovery.md",
    "specification.md",
    "planning.md",
    "execution.md",
    "product.md",
    "memory.md",
    "health.md",
    "maintenance.md",
    "audit.md",
    "migration.md",
    "fleet.md",
    "delegation.md",
)
SCRIPTS = (
    "flow_audit.py",
    "migrate_legacy.py",
    "run-agent.sh",
    "fleet-up.sh",
    "fleet-run.sh",
    "fleet-dashboard.sh",
    "fleet-teardown.sh",
)
TEMPLATES = (
    "docker-compose.flow-fleet.yml",
    "fleet-env.example",
    "fleet-result.schema.json",
)
FORBIDDEN_RUNTIME_TERMS = (
    "${CLAUDE_PLUGIN_ROOT}",
    "subagent_type",
    "Task tool",
    "model: opus",
    "model: sonnet",
    "model: haiku",
)


def read_frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n", text, flags=re.DOTALL)
    if not match:
        raise AssertionError(f"missing YAML frontmatter: {path}")

    metadata: dict[str, str] = {}
    for line in match.group(1).splitlines():
        key, separator, value = line.partition(":")
        if not separator:
            raise AssertionError(f"invalid frontmatter line in {path}: {line}")
        metadata[key.strip()] = value.strip().strip('"')
    return metadata


class PwdevFlowContractTest(unittest.TestCase):
    def test_manifest_declares_native_codex_plugin(self) -> None:
        self.assertTrue(MANIFEST.is_file(), "Codex manifest must exist")
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

        self.assertEqual(manifest["name"], "pwdev-flow")
        self.assertEqual(manifest["skills"], "./skills/")
        self.assertRegex(
            manifest["version"],
            r"^0\.5\.0(?:\+codex\.\d{14})?$",
        )
        self.assertEqual(manifest["interface"]["displayName"], "PWDEV Flow")
        self.assertNotIn("hooks", manifest)
        self.assertNotIn("mcpServers", manifest)
        self.assertNotIn("apps", manifest)

    def test_all_workflow_skills_are_valid_and_have_ui_metadata(self) -> None:
        for skill_name in SKILLS:
            with self.subTest(skill=skill_name):
                skill_root = PLUGIN / "skills" / skill_name
                skill_file = skill_root / "SKILL.md"
                metadata_file = skill_root / "agents" / "openai.yaml"
                self.assertTrue(skill_file.is_file())
                self.assertTrue(metadata_file.is_file())

                metadata = read_frontmatter(skill_file)
                self.assertEqual(metadata["name"], skill_name)
                self.assertEqual(set(metadata), {"name", "description"})
                self.assertGreater(len(metadata["description"]), 40)

    def test_runtime_neutral_references_exist(self) -> None:
        for reference in REFERENCES:
            with self.subTest(reference=reference):
                path = PLUGIN / "references" / reference
                self.assertTrue(path.is_file())
                self.assertGreater(len(path.read_text(encoding="utf-8")), 100)

    def test_operational_scripts_are_packaged(self) -> None:
        for script_name in SCRIPTS:
            with self.subTest(script=script_name):
                script = PLUGIN / "scripts" / script_name
                self.assertTrue(script.is_file())
                self.assertGreater(len(script.read_text(encoding="utf-8")), 200)

    def test_fleet_templates_are_packaged(self) -> None:
        for template_name in TEMPLATES:
            with self.subTest(template=template_name):
                path = PLUGIN / "templates" / template_name
                self.assertTrue(path.is_file())
                self.assertGreater(len(path.read_text(encoding="utf-8")), 40)

    def test_full_lifecycle_contract_is_explicit(self) -> None:
        workflow = (PLUGIN / "references" / "workflow.md").read_text(encoding="utf-8")
        specification = (PLUGIN / "references" / "specification.md").read_text(
            encoding="utf-8"
        )
        execution = (PLUGIN / "references" / "execution.md").read_text(encoding="utf-8")

        self.assertIn("DISCOVER → DESIGN → PLAN → EXECUTE → REVIEW → VERIFY", workflow)
        self.assertIn("maximum of two correction cycles", execution)
        for section in (
            "Persona and stack context",
            "Objective",
            "Inputs and business rules",
            "Output format and file boundaries",
            "Quality criteria",
            "Stop conditions",
            "Prohibitions",
            "Definition of done",
        ):
            with self.subTest(section=section):
                self.assertIn(section, specification)

    def test_product_memory_and_simplification_contracts_are_explicit(self) -> None:
        product = (PLUGIN / "references" / "product.md").read_text(encoding="utf-8")
        memory = (PLUGIN / "references" / "memory.md").read_text(encoding="utf-8")
        simplify = (PLUGIN / "skills" / "flow-simplify" / "SKILL.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("Phase → Epic → Feature → Task", product)
        for memory_type in ("decision", "lesson", "convention"):
            with self.subTest(memory_type=memory_type):
                self.assertIn(f"`{memory_type}`", memory)
        self.assertIn("MODE: ANALYZE", simplify)
        self.assertIn("MODE: APPLY", simplify)
        self.assertIn("explicit approval", simplify)

    def test_execution_defaults_are_safe_and_runtime_neutral(self) -> None:
        execution_skill = (PLUGIN / "skills" / "flow-execute" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        collaboration = (PLUGIN / "references" / "collaboration.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("Execute inline by default", execution_skill)
        self.assertIn("Do not commit", execution_skill)
        self.assertIn("user explicitly requests", collaboration)

    def test_markdown_links_resolve_inside_plugin(self) -> None:
        markdown_files = list(PLUGIN.rglob("*.md")) if PLUGIN.exists() else []
        self.assertTrue(markdown_files, "plugin must contain Markdown files")

        broken: list[str] = []
        for markdown_file in markdown_files:
            text = markdown_file.read_text(encoding="utf-8")
            for target in re.findall(r"\[[^\]]+\]\(([^)]+\.md)\)", text):
                resolved = (markdown_file.parent / target).resolve()
                if not resolved.is_file():
                    broken.append(f"{markdown_file.relative_to(ROOT)} -> {target}")
        self.assertEqual(broken, [], "broken Markdown links found")

    def test_claude_runtime_dependencies_are_absent(self) -> None:
        files = list(PLUGIN.rglob("*.md")) + list(PLUGIN.rglob("*.json"))
        self.assertTrue(files, "plugin files must exist")
        violations: list[str] = []
        for path in files:
            text = path.read_text(encoding="utf-8")
            for term in FORBIDDEN_RUNTIME_TERMS:
                if term in text:
                    violations.append(f"{path.relative_to(ROOT)}: {term}")
        self.assertEqual(violations, [])

    def test_repository_marketplace_registers_plugin(self) -> None:
        self.assertTrue(MARKETPLACE.is_file(), "Codex marketplace must exist")
        marketplace = json.loads(MARKETPLACE.read_text(encoding="utf-8"))
        entries = {entry["name"]: entry for entry in marketplace["plugins"]}
        entry = entries["pwdev-flow"]

        self.assertEqual(entry["source"], {"source": "local", "path": "./plugins/pwdev-flow"})
        self.assertEqual(entry["policy"]["installation"], "AVAILABLE")
        self.assertEqual(entry["policy"]["authentication"], "ON_INSTALL")
        self.assertEqual(entry["category"], "Developer Tools")


if __name__ == "__main__":
    unittest.main()
