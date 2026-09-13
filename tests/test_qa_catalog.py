"""Documentation and local catalog contracts for the PWDEV QA plugin."""

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "pwdev-qa"
READMES = (PLUGIN / "README.md", PLUGIN / "README.pt-BR.md")

EXPECTED_SKILLS = {
    "qa",
    "qa-tooling",
    "qa-init",
    "qa-strategy",
    "qa-test",
    "qa-explore",
    "qa-bug",
    "qa-regression",
    "qa-review",
    "qa-release",
    "qa-report",
    "qa-status",
    "qa-specialist-accessibility",
    "qa-specialist-api",
    "qa-specialist-automation",
    "qa-specialist-cicd",
    "qa-specialist-data",
    "qa-specialist-defects",
    "qa-specialist-functional",
    "qa-specialist-metrics",
    "qa-specialist-mobile",
    "qa-specialist-performance",
    "qa-specialist-production",
    "qa-specialist-readiness",
    "qa-specialist-regression",
    "qa-specialist-requirements",
    "qa-specialist-security",
    "qa-specialist-strategy",
    "qa-specialist-web",
}
EXPECTED_COMMANDS = {
    "bug",
    "explore",
    "init",
    "regression",
    "release",
    "report",
    "review",
    "status",
    "strategy",
    "test",
}
CLAUDE_EXISTING_ORDER = (
    "sdd-composy",
    "pwdev-flow",
    "pwdev-power",
    "pwdev-code",
    "pwdev-uiux",
    "pwdev-feat",
    "pwdev-prd",
    "pwdev-statusline",
    "pwdev-copy",
    "pwdev-social-media",
    "pwdev-devops",
    "pwdev-youtrack",
    "pwdev-glpi",
    "pwdev-postgres",
    "pwdev-obsidian",
    "pwdev-brain",
)
CODEX_EXISTING = (
    {
        "name": "sdd-composy",
        "source": {"source": "local", "path": "./plugins/sdd-composy"},
        "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
        "category": "Developer Tools",
    },
    {
        "name": "pwdev-flow",
        "source": {"source": "local", "path": "./plugins/pwdev-flow"},
        "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
        "category": "Developer Tools",
    },
    {
        "name": "pwdev-power",
        "source": {"source": "local", "path": "./plugins/pwdev-power"},
        "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
        "category": "Developer Tools",
    },
)


def load_json(relative_path):
    return json.loads((ROOT / relative_path).read_text(encoding="utf-8"))


class TestQaCatalog(unittest.TestCase):
    def test_catalogs_append_qa_without_reordering_or_changing_marketplace_identity(self):
        claude = load_json(".claude-plugin/marketplace.json")
        self.assertEqual(claude["name"], "pwdev-claude-marketplace")
        self.assertEqual(
            tuple(plugin["name"] for plugin in claude["plugins"]),
            CLAUDE_EXISTING_ORDER + ("pwdev-qa",),
        )
        qa_claude = claude["plugins"][-1]
        self.assertEqual(qa_claude["source"], "./plugins/pwdev-qa")
        self.assertTrue(qa_claude["strict"])

        codex = load_json(".agents/plugins/marketplace.json")
        self.assertEqual(codex["name"], "pwdev-flow")
        self.assertEqual(codex["interface"], {"displayName": "Pwdev Flow"})
        self.assertEqual(tuple(codex["plugins"][:-1]), CODEX_EXISTING)
        self.assertEqual(
            codex["plugins"][-1],
            {
                "name": "pwdev-qa",
                "source": {"source": "local", "path": "./plugins/pwdev-qa"},
                "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
                "category": "Developer Tools",
            },
        )

    def test_bilingual_readmes_publish_the_exact_inventory(self):
        actual_skills = {path.parent.name for path in (PLUGIN / "skills").glob("*/SKILL.md")}
        actual_commands = {path.stem for path in (PLUGIN / "commands").glob("*.md")}
        self.assertEqual(actual_skills, EXPECTED_SKILLS)
        self.assertEqual(actual_commands, EXPECTED_COMMANDS)

        for readme in READMES:
            with self.subTest(readme=readme.name):
                self.assertTrue(readme.is_file(), f"missing documentation: {readme}")
                text = readme.read_text(encoding="utf-8")
                self.assertRegex(text, r"\b29 skills\b")
                self.assertRegex(text, r"\b10 (?:commands|comandos)\b")
                for name in EXPECTED_SKILLS:
                    self.assertRegex(text, rf"(?<![a-z0-9-]){re.escape(name)}(?![a-z0-9-])")
                for name in EXPECTED_COMMANDS:
                    self.assertIn(f"pwdev-qa:{name}", text)
                inventory = re.search(
                    r"## (?:Exact inventory|Inventário exato)\n(?P<body>.*?)(?=\n## )",
                    text,
                    re.S,
                )
                self.assertIsNotNone(inventory)
                documented_skills = set(
                    re.findall(r"`(qa(?:-[a-z]+)*)`", inventory.group("body"))
                )
                documented_commands = set(re.findall(r"/pwdev-qa:([a-z]+)", text))
                self.assertEqual(documented_skills, EXPECTED_SKILLS)
                self.assertEqual(documented_commands, EXPECTED_COMMANDS)

    def test_readmes_document_portable_manual_setup_and_runtime_verification_boundary(self):
        required = (
            "Claude Code",
            "Codex",
            "Hermes",
            "claude --plugin-dir ./plugins/pwdev-qa",
            '"skills": "./skills/"',
            "hermes plugins doctor plugins/pwdev-qa",
            "0 mandatory MCP servers",
            "smoke",
            "unverified",
        )
        for readme in READMES:
            with self.subTest(readme=readme.name):
                self.assertTrue(readme.is_file(), f"missing documentation: {readme}")
                text = readme.read_text(encoding="utf-8")
                for value in required:
                    self.assertIn(value, text)
                self.assertRegex(text.lower(), r"(?:does not install|não instala) automatically|não instala\s+automaticamente")

    def test_readmes_separate_execution_from_export_and_state_report_contract(self):
        required = (
            "reportlab==4.4.9",
            "pypdf==6.10.0",
            "pdfplumber==0.11.9",
            "Python >=3.9",
            "HTML",
            "PDF",
            "A4",
            "18 mm",
            "PASS",
            "FAIL",
            "BLOCKED",
            "NOT_RUN",
            "NOT_APPLICABLE",
            ".planning/pwdev-qa/reports/<run-id>/",
        )
        for readme in READMES:
            with self.subTest(readme=readme.name):
                self.assertTrue(readme.is_file(), f"missing documentation: {readme}")
                text = readme.read_text(encoding="utf-8")
                for value in required:
                    self.assertIn(value, text)
                self.assertRegex(text.lower(), r"reporting (?:does not execute|não executa)")
                self.assertRegex(text.lower(), r"(?s)execution.{0,160}export")

    def test_readmes_explain_tool_recommendations_playwright_and_safety_limits(self):
        required = (
            "qa-tooling",
            "available",
            "missing",
            "unverified",
            "evidence",
            "alternative",
            "npx --no-install playwright --version",
            "npx playwright cli",
            "playwright-cli",
            "regular local files",
            "SHA-256",
            "symlinks",
            "5 MiB",
            "1000 criteria",
            "1000 evidence",
            "10 MiB",
            "100 MiB",
            "20 megapixels",
            "authorization",
            "load",
            "pentest",
            "production",
        )
        for readme in READMES:
            with self.subTest(readme=readme.name):
                self.assertTrue(readme.is_file(), f"missing documentation: {readme}")
                text = readme.read_text(encoding="utf-8")
                for value in required:
                    self.assertIn(value.lower(), text.lower())
                self.assertRegex(
                    text.lower(),
                    r"(?s)sanitization.{0,180}(?:cannot guarantee|não pode garantir)",
                )


if __name__ == "__main__":
    unittest.main()
