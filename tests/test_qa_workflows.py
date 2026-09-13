"""Behavioural contract tests for the PWDEV QA init and strategy workflows."""

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "pwdev-qa"
SKILLS = PLUGIN / "skills"
COMMANDS = PLUGIN / "commands"


def read_required(path: Path) -> str:
    if not path.is_file():
        raise AssertionError(f"required workflow file is missing: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


class QaWorkflowContractTest(unittest.TestCase):
    def test_workflows_have_the_complete_portable_contract(self) -> None:
        for name in ("qa-init", "qa-strategy"):
            with self.subTest(name=name):
                text = read_required(SKILLS / name / "SKILL.md")
                self.assertRegex(
                    text,
                    rf"(?s)^---\nname: {re.escape(name)}\ndescription: .+?\n---\n",
                )
                for section in (
                    "Inputs",
                    "Procedure",
                    "Output",
                    "Failure modes",
                    "Safety",
                    "Related skills",
                ):
                    self.assertIn(f"## {section}", text)

    def test_init_is_project_confined_non_destructive_and_probe_driven(self) -> None:
        text = read_required(SKILLS / "qa-init" / "SKILL.md")
        self.assertIn(".planning/pwdev-qa/context.md", text)
        self.assertRegex(text, r"(?is)project root.*(?:within|beneath|inside)")
        self.assertRegex(text, r"(?is)(?:preserve|never overwrite).*existing")
        self.assertRegex(text, r"(?is)symlink.*refus")
        self.assertIn("`qa-tooling`", text)
        self.assertRegex(text, r"(?is)probe.*positive.*negative.*not_run")
        self.assertRegex(text, r"(?is)available.*missing.*unverified")
        self.assertNotRegex(text, r"(?im)^\s*(?:pip|npm|npx|brew|apt)\s+install\b")

    def test_init_output_is_exact_and_exposes_limitations(self) -> None:
        text = read_required(SKILLS / "qa-init" / "SKILL.md")
        for field in (
            "TARGET",
            "CONTRACT",
            "CRITERIA",
            "OPERATION",
            "CONTEXT",
            "TOOLS_AVAILABLE",
            "TOOLS_MISSING",
            "TOOLS_UNVERIFIED",
            "RESULTS",
            "LIMITATIONS",
            "EVIDENCE_REFERENCES",
            "CURRENT_DEFECTS",
            "VERDICT",
            "NEXT",
        ):
            self.assertRegex(text, rf"(?m)^{field}: ")
        self.assertRegex(text, r"(?is)missing criteria.*`BLOCKED`")

    def test_strategy_preserves_contract_and_plans_risk_coverage_without_execution(self) -> None:
        text = read_required(SKILLS / "qa-strategy" / "SKILL.md")
        self.assertRegex(text, r"(?is)preserve.*criterion IDs.*text")
        for phrase in (
            "risk register",
            "coverage matrix",
            "environments",
            "test data",
            "entry criteria",
            "exit criteria",
            "authorization",
            "limitations",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text.lower())
        self.assertIn("`qa-tooling`", text)
        self.assertRegex(text, r"(?is)probe.*available.*missing.*unverified")
        self.assertRegex(text, r"(?is)does not execute.*tests")
        self.assertRegex(text, r"(?is)stored commands.*inert")

    def test_strategy_output_is_exact_and_blocks_missing_or_unverified_inputs(self) -> None:
        text = read_required(SKILLS / "qa-strategy" / "SKILL.md")
        for field in (
            "TARGET",
            "CONTRACT",
            "CRITERIA",
            "OPERATION",
            "AUTHORIZATION",
            "RISK_REGISTER",
            "COVERAGE_MATRIX",
            "ENVIRONMENTS",
            "TEST_DATA",
            "ENTRY_CRITERIA",
            "EXIT_CRITERIA",
            "TOOLING",
            "RESULTS",
            "LIMITATIONS",
            "EVIDENCE_REFERENCES",
            "CURRENT_DEFECTS",
            "VERDICT",
            "NEXT",
        ):
            self.assertRegex(text, rf"(?m)^{field}: ")
        self.assertRegex(text, r"(?is)(?:missing|unverified).*`BLOCKED`")
        self.assertRegex(text, r"(?is)load.*penetration.*production.*external effects.*explicit")

    def test_report_cli_is_documented_as_a_later_inert_export(self) -> None:
        command = "qa_report.py report --manifest PATH --project-root PATH"
        for name in ("qa-init", "qa-strategy"):
            with self.subTest(name=name):
                text = read_required(SKILLS / name / "SKILL.md")
                self.assertIn(command, text)
                self.assertRegex(text, r"(?is)report.*does not (?:run|execute|re-run).*tests")

    def test_claude_commands_are_thin_argument_forwarding_adapters(self) -> None:
        for command_name, skill_name in (("init", "qa-init"), ("strategy", "qa-strategy")):
            with self.subTest(command=command_name):
                text = read_required(COMMANDS / f"{command_name}.md")
                self.assertRegex(
                    text,
                    r"(?s)^---\ndescription: .+\nargument-hint: .+\n---\n",
                )
                self.assertIn(
                    f"${{CLAUDE_PLUGIN_ROOT}}/skills/{skill_name}/SKILL.md", text
                )
                self.assertIn("$ARGUMENTS", text)
                self.assertIn("return the shared skill's result unchanged", text)
                self.assertNotIn("qa_report.py", text)
                self.assertLessEqual(len(text.splitlines()), 12)


if __name__ == "__main__":
    unittest.main()
