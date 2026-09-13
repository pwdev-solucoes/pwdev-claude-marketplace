"""Behavioural contract tests for the PWDEV QA workflows."""

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


def exact_output_labels(output_section: str) -> list[str]:
    match = re.search(r"```text\n(?P<record>.*?)\n```", output_section, re.DOTALL)
    if match is None:
        raise AssertionError("Output section must contain one exact text record")
    return re.findall(r"(?m)^([A-Z][A-Z_]*): ", match.group("record"))


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

    def test_explicit_objective_and_authorization_are_preserved_end_to_end(self) -> None:
        for name in ("qa-init", "qa-strategy"):
            with self.subTest(name=name):
                text = read_required(SKILLS / name / "SKILL.md")
                inputs, procedure, output = re.split(
                    r"(?m)^## (?:Inputs|Procedure|Output)\n", text
                )[1:4]
                self.assertRegex(inputs, r"(?is)explicit.*(?:objective|intent)")
                self.assertRegex(inputs, r"(?is)(?:explicit )?authorization")
                self.assertRegex(
                    procedure,
                    r"(?is)preserve.*(?:objective|intent).*authorization",
                )
                self.assertRegex(output, r"(?m)^OBJECTIVE: <preserved explicit .+>$")
                self.assertRegex(output, r"(?m)^AUTHORIZATION: <preserved .+>$")

    def test_shared_workflow_bodies_have_no_claude_only_dependencies(self) -> None:
        forbidden = ("CLAUDE.md", "AGENTS.md", "${CLAUDE_PLUGIN_ROOT}", "$ARGUMENTS")
        for name in ("qa-init", "qa-strategy"):
            with self.subTest(name=name):
                text = read_required(SKILLS / name / "SKILL.md")
                for token in forbidden:
                    self.assertNotIn(token, text)

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

    def test_test_and_explore_have_the_complete_portable_contract(self) -> None:
        for name in ("qa-test", "qa-explore"):
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
                for token in (
                    "CLAUDE.md",
                    "AGENTS.md",
                    "${CLAUDE_PLUGIN_ROOT}",
                    "$ARGUMENTS",
                ):
                    self.assertNotIn(token, text)

    def test_test_materializes_traceable_execution_and_verdict(self) -> None:
        text = read_required(SKILLS / "qa-test" / "SKILL.md")
        inputs, procedure, output = re.split(
            r"(?m)^## (?:Inputs|Procedure|Output)\n", text
        )[1:4]
        self.assertRegex(inputs, r"(?is)explicit.*(?:objective|intent)")
        self.assertRegex(inputs, r"(?is)explicit.*authorization")
        self.assertRegex(
            procedure,
            r"(?is)preserve.*(?:objective|intent).*authorization",
        )
        for phrase in (
            "criterion IDs",
            "case IDs",
            "expected",
            "observed",
            "evidence",
            "PASS",
            "FAIL",
            "BLOCKED",
            "NOT_RUN",
            "NOT_APPLICABLE",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)
        expected_labels = [
            "TARGET",
            "OBJECTIVE",
            "CONTRACT",
            "CRITERIA",
            "OPERATION",
            "AUTHORIZATION",
            "CASES",
            "RESULTS",
            "LIMITATIONS",
            "EVIDENCE_REFERENCES",
            "CURRENT_DEFECTS",
            "VERDICT",
            "NEXT",
        ]
        self.assertEqual(exact_output_labels(output), expected_labels)
        self.assertRegex(text, r"(?is)load.*penetration.*production.*external effects.*explicit")
        self.assertRegex(text, r"(?is)product (?:code|corrections?).*only.*requested")
        self.assertRegex(text, r"(?is)report.*does not (?:run|execute|re-run).*tests")

    def test_explore_keeps_charter_notes_findings_and_follow_up_without_false_pass(self) -> None:
        text = read_required(SKILLS / "qa-explore" / "SKILL.md")
        inputs, procedure, output = re.split(
            r"(?m)^## (?:Inputs|Procedure|Output)\n", text
        )[1:4]
        self.assertRegex(inputs, r"(?is)explicit.*(?:objective|intent)")
        self.assertRegex(inputs, r"(?is)explicit.*authorization")
        self.assertRegex(
            procedure,
            r"(?is)preserve.*(?:objective|intent).*authorization",
        )
        for phrase in ("charter", "notes", "findings", "follow-up"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text.lower())
        expected_labels = [
            "TARGET",
            "OBJECTIVE",
            "CONTRACT",
            "CRITERIA",
            "OPERATION",
            "AUTHORIZATION",
            "CHARTER",
            "NOTES",
            "FINDINGS",
            "FOLLOW_UP",
            "RESULTS",
            "LIMITATIONS",
            "EVIDENCE_REFERENCES",
            "CURRENT_DEFECTS",
            "VERDICT",
            "NEXT",
        ]
        self.assertEqual(exact_output_labels(output), expected_labels)
        self.assertRegex(
            procedure,
            r"(?is)(?:exploration|this workflow).*never (?:establishes|declares) `PASS`",
        )
        self.assertNotRegex(
            procedure,
            r"(?is)(?:exploration|this workflow)\s+(?:does establish|declares) `PASS`",
        )
        self.assertRegex(text, r"(?is)findings?.*(?:expected|oracle).*observed.*evidence")
        self.assertRegex(text, r"(?is)load.*penetration.*production.*external effects.*explicit")

    def test_test_and_explore_consult_only_applicable_installed_specialists(self) -> None:
        for name in ("qa-test", "qa-explore"):
            with self.subTest(name=name):
                text = read_required(SKILLS / name / "SKILL.md")
                procedure = re.split(r"(?m)^## Procedure\n", text, maxsplit=1)[1].split(
                    "\n## Output\n", 1
                )[0]
                self.assertRegex(
                    procedure,
                    r"(?is)identify.*surfaces.*consult.*installed.*applicable.*`qa-specialist-",
                )
                self.assertRegex(
                    procedure,
                    r"(?is)(?:unavailable|absent|missing).*specialist.*limitation",
                )
                self.assertRegex(
                    procedure,
                    r"(?is)specialist.*(?:does not|cannot|never).*expand.*authorization",
                )

    def test_test_and_explore_claude_commands_are_thin_adapters(self) -> None:
        for command_name, skill_name in (("test", "qa-test"), ("explore", "qa-explore")):
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
                self.assertIn("current repository context", text)
                self.assertIn("return the shared skill's result unchanged", text)
                self.assertNotIn("qa_report.py", text)
                self.assertLessEqual(len(text.splitlines()), 12)

    def test_regression_and_bug_have_the_complete_portable_contract(self) -> None:
        for name in ("qa-regression", "qa-bug"):
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
                for token in (
                    "CLAUDE.md",
                    "AGENTS.md",
                    "${CLAUDE_PLUGIN_ROOT}",
                    "$ARGUMENTS",
                ):
                    self.assertNotIn(token, text)

    def test_regression_selects_by_impact_with_materialized_traceability(self) -> None:
        text = read_required(SKILLS / "qa-regression" / "SKILL.md")
        inputs, procedure, output = re.split(
            r"(?m)^## (?:Inputs|Procedure|Output)\n", text
        )[1:4]
        self.assertRegex(inputs, r"(?is)explicit.*(?:objective|intent)")
        self.assertRegex(inputs, r"(?is)(?:explicit )?authorization")
        self.assertRegex(
            procedure,
            r"(?is)preserve.*(?:objective|intent).*authorization",
        )
        self.assertRegex(procedure, r"(?is)select.*impact.*(?:rationale|justification)")
        self.assertRegex(
            procedure,
            r"(?is)change ID,\s+impact ID,\s+risk ID,\s+criterion ID,\s+prior defect ID.*stable case ID;\s+use an\s+explicit `none`.*no defect or criterion",
        )
        self.assertRegex(procedure, r"(?is)selected.*excluded.*(?:rationale|reason)")
        for token in (
            "CHG-AUTH-017",
            "IMP-SESSION-01",
            "RISK-AUTH-04",
            "AC-LOGIN-01",
            "DEF-SESSION-09",
            "TC-LOGIN",
            "TC-PROFILE",
        ):
            self.assertIn(token, text)
        expected_labels = [
            "TARGET",
            "OBJECTIVE",
            "CONTRACT",
            "CRITERIA",
            "OPERATION",
            "AUTHORIZATION",
            "CHANGE_IMPACT",
            "SELECTED_CASES",
            "EXCLUDED_CASES",
            "RESULTS",
            "LIMITATIONS",
            "EVIDENCE_REFERENCES",
            "CURRENT_DEFECTS",
            "VERDICT",
            "NEXT",
        ]
        self.assertEqual(exact_output_labels(output), expected_labels)
        self.assertRegex(text, r"(?is)convenience.*(?:never|not).*impact")

    def test_bug_records_reproduction_triage_scope_evidence_and_terminal_retest(self) -> None:
        text = read_required(SKILLS / "qa-bug" / "SKILL.md")
        inputs, procedure, output = re.split(
            r"(?m)^## (?:Inputs|Procedure|Output)\n", text
        )[1:4]
        self.assertRegex(inputs, r"(?is)explicit.*(?:objective|intent)")
        self.assertRegex(inputs, r"(?is)(?:explicit )?authorization")
        self.assertRegex(
            procedure,
            r"(?is)preserve.*(?:objective|intent).*authorization",
        )
        for phrase in (
            "reproduction",
            "environment",
            "expected",
            "observed",
            "evidence",
            "severity",
            "scope",
            "retest",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text.lower())
        self.assertRegex(
            procedure,
            r"(?is)`PASS`.*terminal.*retest.*valid.*evidence.*all applicable criteria.*`PASS`.*no (?:other )?current\s+in-scope defects",
        )
        self.assertRegex(
            procedure,
            r"(?is)all applicable criteria.*`PASS`.*no pending.*no other current\s+in-scope defects",
        )
        self.assertRegex(
            procedure,
            r"(?is)severity from product/user impact.*priority independently from\s+delivery order.*neither value rewrites the other",
        )
        self.assertRegex(
            procedure,
            r"(?is)one stable logical\s+case ID, unique attempt IDs, strictly increasing attempt numbers, the same target, and a\s+linear `supersedes` chain.*never delete.*branch/cycle",
        )
        for token in (
            "ATT-LOGIN-01",
            "ATT-LOGIN-02",
            "CASE-LOGIN-LOCK",
            "DEF-LOGIN-01",
            "AC-LOGIN-01",
        ):
            self.assertIn(token, text)
        expected_labels = [
            "TARGET",
            "OBJECTIVE",
            "CONTRACT",
            "CRITERIA",
            "OPERATION",
            "AUTHORIZATION",
            "DEFECT",
            "REPRODUCTION",
            "TRIAGE",
            "ATTEMPT_HISTORY",
            "RETEST",
            "RESULTS",
            "LIMITATIONS",
            "EVIDENCE_REFERENCES",
            "CURRENT_DEFECTS",
            "VERDICT",
            "NEXT",
        ]
        self.assertEqual(exact_output_labels(output), expected_labels)

    def test_regression_and_bug_consult_applicable_installed_specialists(self) -> None:
        expected = {
            "qa-regression": "qa-specialist-regression",
            "qa-bug": "qa-specialist-defects",
        }
        for name, primary_specialist in expected.items():
            with self.subTest(name=name):
                text = read_required(SKILLS / name / "SKILL.md")
                procedure = re.split(r"(?m)^## Procedure\n", text, maxsplit=1)[1].split(
                    "\n## Output\n", 1
                )[0]
                self.assertIn(f"`{primary_specialist}`", procedure)
                self.assertRegex(
                    procedure,
                    r"(?is)identify.*surfaces.*consult.*installed.*applicable.*`qa-specialist-",
                )
                self.assertRegex(
                    procedure,
                    r"(?is)(?:unavailable|absent|missing).*specialist.*limitation",
                )
                self.assertRegex(
                    procedure,
                    r"(?is)specialist.*(?:does not|cannot|never).*expand.*authorization",
                )

    def test_regression_and_bug_keep_safety_and_report_commands_inert(self) -> None:
        command = "qa_report.py report --manifest PATH --project-root PATH"
        for name in ("qa-regression", "qa-bug"):
            with self.subTest(name=name):
                text = read_required(SKILLS / name / "SKILL.md")
                self.assertRegex(
                    text,
                    r"(?is)load.*penetration.*production.*external effects.*explicit",
                )
                self.assertRegex(
                    text,
                    r"(?is)product (?:code|corrections?).*only.*requested",
                )
                self.assertIn(command, text)
                self.assertRegex(
                    text,
                    r"(?is)report.*does not (?:run|execute|re-run).*tests",
                )

    def test_regression_and_bug_claude_commands_are_thin_adapters(self) -> None:
        for command_name, skill_name in (
            ("regression", "qa-regression"),
            ("bug", "qa-bug"),
        ):
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
                self.assertIn("current repository context", text)
                self.assertIn("return the shared skill's result unchanged", text)
                self.assertNotIn("qa_report.py", text)
                self.assertLessEqual(len(text.splitlines()), 12)

    def test_review_and_release_have_the_complete_portable_contract(self) -> None:
        for name in ("qa-review", "qa-release"):
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
                for token in (
                    "CLAUDE.md",
                    "AGENTS.md",
                    "${CLAUDE_PLUGIN_ROOT}",
                    "$ARGUMENTS",
                ):
                    self.assertNotIn(token, text)

    def test_review_is_read_only_and_reports_requirements_coverage_and_findings(self) -> None:
        text = read_required(SKILLS / "qa-review" / "SKILL.md")
        inputs, procedure, output = re.split(
            r"(?m)^## (?:Inputs|Procedure|Output)\n", text
        )[1:4]
        self.assertRegex(inputs, r"(?is)explicit.*(?:objective|intent)")
        self.assertRegex(inputs, r"(?is)(?:explicit )?authorization")
        self.assertRegex(
            procedure,
            r"(?is)preserve.*(?:objective|intent).*limitations.*authorization",
        )
        self.assertRegex(
            procedure,
            r"(?is)read.only.*(?:never|does not).*(?:correct|modify|mutate).*product",
        )
        self.assertRegex(
            procedure,
            r"(?is)requirements.*coverage.*findings",
        )
        expected_labels = [
            "TARGET",
            "OBJECTIVE",
            "CONTRACT",
            "CRITERIA",
            "OPERATION",
            "AUTHORIZATION",
            "REQUIREMENTS_REVIEW",
            "COVERAGE_REVIEW",
            "FINDINGS",
            "RESULTS",
            "LIMITATIONS",
            "EVIDENCE_REFERENCES",
            "CURRENT_DEFECTS",
            "VERDICT",
            "NEXT",
        ]
        self.assertEqual(exact_output_labels(output), expected_labels)

    def test_release_keeps_qa_verdict_and_human_decision_separate(self) -> None:
        text = read_required(SKILLS / "qa-release" / "SKILL.md")
        inputs, procedure, output = re.split(
            r"(?m)^## (?:Inputs|Procedure|Output)\n", text
        )[1:4]
        self.assertRegex(inputs, r"(?is)explicit.*(?:objective|intent)")
        self.assertRegex(inputs, r"(?is)(?:explicit )?authorization")
        self.assertRegex(
            procedure,
            r"(?is)preserve.*(?:objective|intent).*limitations.*authorization",
        )
        self.assertRegex(
            procedure,
            r"(?is)human.*decision.*separate.*(?:QA|verdict)",
        )
        self.assertRegex(
            procedure,
            r"(?is)`PASS` requires all applicable criteria `PASS`.*no current in-scope defects.*no (?:failure|pending work|pending item|pending risk|pending limitation|pending evidence|pending decision)",
        )
        self.assertRegex(
            procedure,
            r"(?is)zero applicable criteria.*`BLOCKED`",
        )
        expected_labels = [
            "TARGET",
            "OBJECTIVE",
            "CONTRACT",
            "CRITERIA",
            "OPERATION",
            "AUTHORIZATION",
            "FAILURES",
            "PENDING",
            "RISKS",
            "HUMAN_DECISION",
            "RESULTS",
            "LIMITATIONS",
            "EVIDENCE_REFERENCES",
            "CURRENT_DEFECTS",
            "VERDICT",
            "RECOMMENDATION",
            "NEXT",
        ]
        self.assertEqual(exact_output_labels(output), expected_labels)

    def test_review_and_release_consult_applicable_installed_specialists(self) -> None:
        expected = {
            "qa-review": "qa-specialist-requirements",
            "qa-release": "qa-specialist-readiness",
        }
        for name, primary_specialist in expected.items():
            with self.subTest(name=name):
                text = read_required(SKILLS / name / "SKILL.md")
                procedure = re.split(r"(?m)^## Procedure\n", text, maxsplit=1)[1].split(
                    "\n## Output\n", 1
                )[0]
                self.assertIn(f"`{primary_specialist}`", procedure)
                self.assertRegex(
                    procedure,
                    r"(?is)identify.*surfaces.*consult.*installed.*applicable.*`qa-specialist-",
                )
                self.assertRegex(
                    procedure,
                    r"(?is)(?:unavailable|absent|missing).*specialist.*limitation",
                )
                self.assertRegex(
                    procedure,
                    r"(?is)specialist.*(?:does not|cannot|never).*expand.*authorization",
                )

    def test_review_and_release_enforce_safety_and_inert_reporting(self) -> None:
        command = "qa_report.py report --manifest PATH --project-root PATH"
        for name in ("qa-review", "qa-release"):
            with self.subTest(name=name):
                text = read_required(SKILLS / name / "SKILL.md")
                self.assertRegex(
                    text,
                    r"(?is)load.*penetration.*production.*external effects.*explicit",
                )
                self.assertRegex(
                    text,
                    r"(?is)product (?:code|corrections?).*only.*requested",
                )
                self.assertRegex(text, r"(?is)never.*publish.*push.*merge")
                self.assertIn(command, text)
                self.assertRegex(
                    text,
                    r"(?is)report.*does not (?:run|execute|re-run).*tests",
                )

    def test_review_and_release_claude_commands_are_thin_adapters(self) -> None:
        for command_name, skill_name in (
            ("review", "qa-review"),
            ("release", "qa-release"),
        ):
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
                self.assertIn("current repository context", text)
                self.assertIn("return the shared skill's result unchanged", text)
                self.assertNotIn("qa_report.py", text)
                self.assertLessEqual(len(text.splitlines()), 12)


if __name__ == "__main__":
    unittest.main()
