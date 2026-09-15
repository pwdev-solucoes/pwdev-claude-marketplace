"""Documentation and local catalog contracts for the PWDEV QA plugin."""

import hashlib
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
CLAUDE_EXISTING_DIGESTS = (
    # sdd-composy: description and tags name all four supported runtimes.
    "2652111a1d2cfb45c32f010db347ca084ff3310f62bbebb2dcceac88ee50afc4",
    "4fedf976f5ab35a55d8e61307517e370e1e1396816e50eebf08f73fa4c4a1634",
    "29682dd6eed0918853e4854a0defcc687e2fe36f8f40c5aa55c4370f1e7330ed",
    "c1ef5068d662c6692af9ae4b0935955acc7dad6692990a1fa85c597f6ba935a5",
    "f9d53f05aaf7e7556925200c930fa8c433fe472f93927fc0f77aad643a9c9f9f",
    "39ac01f72c24f15c8df207739ce226c20e1fa3a694a8f934f187ba29f3ebae1a",
    "e8f09de7012e4f104180a44066e67b891b2838710a601f7d543d556cdf617e7f",
    "fcf382868e4706cb53f020566e82cc2b80372a0070e6a3d64b837fee8b722f82",
    "5bf2b3edf26a2bb99e3fb4ea9f7bb027c662e365cc1ede3cefcc8ac49332d4c3",
    "19aa4ed22e18d8dd09d7766a225a0029019687f5346b5b7759302cee9a6b92d7",
    "0c64a804bd8e32b3328148a7a69d39d13e366db397f7619f78f6aec1270ecacb",
    "0c24b7a311e7fcdfe250cfa17ab052f1bf110196ea4eafa3c2d937023a308ed0",
    "0b1343e2d1a0d8358d6475626182bc9caa17f1d885a97b3837b3d955908684b6",
    "679602b6bb871bc6665c81323a5e28b8230825153726996c6ee5d4b7fd6c058b",
    "7ee1b1ae7d4664fa6412c51d79fb1f0438db972c31130ecd1fe275f003b14348",
    "eaf96f952d0cbe005a2502b397b68fbedfd0115efda9aa394baed4bcd51a0ff4",
)
CLAUDE_TOP_LEVEL = {
    "name": "pwdev-claude-marketplace",
    "description": (
        "PWDEV plugins for Claude Code — spec-driven development, feature planning, PRD "
        "creation, UI/UX engineering, copywriting, social media creatives, DevOps, and "
        "terminal status line"
    ),
    "owner": {"name": "Paulo Soares"},
}
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


def canonical_digest(value):
    serialized = json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def forbidden_documentation_claims(text):
    """Return explicit contradictions to the README safety contract."""
    patterns = {
        "automatic installation": (
            r"\b(?:the\s+)?plugin\s+(?!(?:never|does\s+not|cannot|must\s+not)\b)"
            r"installs?\s+automatically\b",
            r"\b(?:o\s+)?plugin\s+(?!(?:nunca|não)\b)instala\s+automaticamente\b",
        ),
        "verified without real smoke": (
            r"\bruntime\s+(?!(?:cannot|must\s+not|is\s+not|never)\b)"
            r"(?:is\s+)?verified\b[^.\n]{0,80}\bwithout\b[^.\n]{0,40}\b(?:real\s+)?smoke\b",
            r"\bruntime\s+(?!(?:não|nunca)\b)(?:está\s+|é\s+)?verificad[oa]\b"
            r"[^.\n]{0,80}\bsem\b[^.\n]{0,40}\bsmoke\b",
        ),
        "export executes tests or evidence commands": (
            r"\bexport(?:ation)?\s+(?!(?:never|does\s+not|cannot|must\s+not)\b)"
            r"(?:runs?|reruns?|executes?)\b[^.\n]{0,80}\b(?:tests?|commands?)\b",
            r"\b(?:a\s+)?exportação\s+(?!(?:nunca|não)\b)"
            r"(?:roda|executa|reexecuta)\b[^.\n]{0,80}\b(?:testes?|comandos?)\b",
        ),
        "verification dependencies used for runtime export": (
            r"\b(?:pypdf|pdfplumber)\b[^.\n]{0,80}\b(?:are|is)\s+"
            r"(?!not\b)runtime\s+export\s+dependenc(?:y|ies)\b",
            r"\b(?:pypdf|pdfplumber)\b[^.\n]{0,80}(?<!não\s)\bsão\s+"
            r"dependências?\s+de\s+exportação\s+em\s+runtime\b",
            r"\breportlab\b[^.\n]{0,40}\bis\s+(?!not\b)development[- ]only\b",
            r"\breportlab\b[^.\n]{0,40}(?<!não\s)\bé\s+só\s+de\s+desenvolvimento\b",
        ),
        "universal sanitization guarantee": (
            r"\bsanitization\s+(?!(?:does\s+not|cannot|never)\b)guarantees?\b"
            r"[^.\n]{0,80}\buniversal\b",
            r"\b(?:a\s+)?sanitização\s+(?!(?:não|nunca)\b)garante\b"
            r"[^.\n]{0,80}\buniversal\b",
        ),
        "no-install probe downloads or installs": (
            r"\bnpx\s+--no-install\s+playwright\s+--version\s+"
            r"(?!(?:cannot|does\s+not|never)\b)(?:downloads?|installs?)\b",
            r"\bnpx\s+--no-install\s+playwright\s+--version\s+"
            r"(?!(?:não|nunca)\b)(?:baixa|instala)\b",
        ),
    }
    lowered = text.lower()
    return [
        label
        for label, alternatives in patterns.items()
        if any(re.search(pattern, lowered) for pattern in alternatives)
    ]


class TestQaCatalog(unittest.TestCase):
    def test_catalogs_append_qa_without_reordering_or_changing_marketplace_identity(self):
        # pwdev-qa was appended after the sixteen existing entries without reordering or changing any
        # of them. Later plugins may be appended after it; the entries up to and including pwdev-qa
        # stay pinned by position and content, so a reorder or an edit still fails here.
        claude = load_json(".claude-plugin/marketplace.json")
        self.assertEqual(
            {key: value for key, value in claude.items() if key != "plugins"},
            CLAUDE_TOP_LEVEL,
        )
        names = tuple(plugin["name"] for plugin in claude["plugins"])
        qa_index = len(CLAUDE_EXISTING_ORDER)
        self.assertEqual(names[: qa_index + 1], CLAUDE_EXISTING_ORDER + ("pwdev-qa",))
        self.assertEqual(len(set(names)), len(names), "a plugin is listed twice")
        self.assertEqual(
            tuple(canonical_digest(plugin) for plugin in claude["plugins"][:qa_index]),
            CLAUDE_EXISTING_DIGESTS,
        )
        qa_claude = claude["plugins"][qa_index]
        self.assertEqual(qa_claude["source"], "./plugins/pwdev-qa")
        self.assertTrue(qa_claude["strict"])

        codex = load_json(".agents/plugins/marketplace.json")
        # One marketplace identity for both runtimes: the repository name.
        self.assertEqual(codex["name"], claude["name"])
        self.assertEqual(codex["interface"], {"displayName": "PWDEV Marketplace"})
        codex_qa_index = len(CODEX_EXISTING)
        self.assertEqual(tuple(codex["plugins"][:codex_qa_index]), CODEX_EXISTING)
        self.assertEqual(
            codex["plugins"][codex_qa_index],
            {
                "name": "pwdev-qa",
                "source": {"source": "local", "path": "./plugins/pwdev-qa"},
                "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
                "category": "Developer Tools",
            },
        )
        codex_names = tuple(plugin["name"] for plugin in codex["plugins"])
        self.assertEqual(len(set(codex_names)), len(codex_names), "a plugin is listed twice")

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
                self.assertEqual(forbidden_documentation_claims(text), [])

    def assert_bilingual_mutation_is_rejected(self, english, portuguese):
        for readme, mutation in zip(READMES, (english, portuguese)):
            with self.subTest(readme=readme.name):
                mutated = readme.read_text(encoding="utf-8") + "\n\n" + mutation + "\n"
                self.assertTrue(
                    forbidden_documentation_claims(mutated),
                    f"contradictory claim survived in {readme.name}: {mutation}",
                )

    def assert_bilingual_control_is_accepted(self, english, portuguese):
        for readme, control in zip(READMES, (english, portuguese)):
            with self.subTest(readme=readme.name):
                controlled = readme.read_text(encoding="utf-8") + "\n\n" + control + "\n"
                self.assertEqual(
                    forbidden_documentation_claims(controlled),
                    [],
                    f"valid prohibition was rejected in {readme.name}: {control}",
                )

    def test_rejects_automatic_installation_claims_in_both_languages(self):
        self.assert_bilingual_mutation_is_rejected(
            "The plugin installs automatically and changes personal configuration.",
            "O plugin instala automaticamente e altera configuração pessoal.",
        )
        self.assert_bilingual_control_is_accepted(
            "The plugin never installs automatically or changes personal configuration.",
            "O plugin nunca instala automaticamente nem altera configuração pessoal.",
        )

    def test_rejects_verified_runtime_without_real_smoke_in_both_languages(self):
        self.assert_bilingual_mutation_is_rejected(
            "The runtime is verified without a real smoke.",
            "O runtime está verificado sem smoke real.",
        )
        self.assert_bilingual_control_is_accepted(
            "The runtime cannot be verified without a real smoke.",
            "O runtime não pode ser verificado sem smoke real.",
        )

    def test_rejects_export_that_reruns_tests_in_both_languages(self):
        self.assert_bilingual_mutation_is_rejected(
            "Export reruns the stored tests and evidence commands.",
            "A exportação reexecuta os testes e comandos de evidência armazenados.",
        )
        self.assert_bilingual_control_is_accepted(
            "Export never runs tests or stored evidence commands.",
            "A exportação nunca executa testes nem comandos de evidência armazenados.",
        )

    def test_rejects_inverted_runtime_and_development_dependencies(self):
        self.assert_bilingual_mutation_is_rejected(
            "pypdf and pdfplumber are runtime export dependencies; "
            "ReportLab is development-only.",
            "pypdf e pdfplumber são dependências de exportação em runtime; "
            "ReportLab é só de desenvolvimento.",
        )
        self.assert_bilingual_control_is_accepted(
            "pypdf and pdfplumber are not runtime export dependencies; "
            "ReportLab is not development-only.",
            "pypdf e pdfplumber não são dependências de exportação em runtime; "
            "ReportLab não é só de desenvolvimento.",
        )

    def test_rejects_universal_sanitization_claims_in_both_languages(self):
        self.assert_bilingual_mutation_is_rejected(
            "Sanitization guarantees universal detection of every secret and personal datum.",
            "A sanitização garante detecção universal de todo segredo e dado pessoal.",
        )
        self.assert_bilingual_control_is_accepted(
            "Sanitization does not guarantee universal detection of secrets or personal data.",
            "A sanitização não garante detecção universal de segredos ou dados pessoais.",
        )

    def test_rejects_no_install_probe_that_downloads_playwright(self):
        self.assert_bilingual_mutation_is_rejected(
            "npx --no-install playwright --version downloads and installs Playwright "
            "when missing.",
            "npx --no-install playwright --version baixa e instala Playwright quando "
            "ausente.",
        )
        self.assert_bilingual_control_is_accepted(
            "npx --no-install playwright --version cannot download or install Playwright.",
            "npx --no-install playwright --version não baixa nem instala Playwright.",
        )


if __name__ == "__main__":
    unittest.main()
