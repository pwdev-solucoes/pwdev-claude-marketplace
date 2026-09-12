"""Behavioural contract tests for the PWDEV QA router and shared references."""

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "pwdev-qa"
SKILL = PLUGIN / "skills" / "qa" / "SKILL.md"
REFERENCES = PLUGIN / "references"


def read_required(path: Path) -> str:
    if not path.is_file():
        raise AssertionError(f"required QA contract is missing: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


class QaCoreContractTest(unittest.TestCase):
    def test_router_selects_by_explicit_intent_then_surface_and_risk(self) -> None:
        text = read_required(SKILL)
        self.assertRegex(text, r"(?is)explicit intent.*surface.*risk")
        for intent, route in {
            "initialize": "qa-init",
            "strategy": "qa-strategy",
            "execute tests": "qa-test",
            "explore": "qa-explore",
            "regression": "qa-regression",
            "bug": "qa-bug",
            "review": "qa-review",
            "release": "qa-release",
            "report": "qa-report",
            "status": "qa-status",
            "tooling": "qa-tooling",
        }.items():
            with self.subTest(intent=intent):
                self.assertRegex(text, rf"(?im)^\| {re.escape(intent)} \| `{route}` \|")
        self.assertIn("not applicable", text.lower())

    def test_router_refuses_a_route_whose_skill_is_not_installed(self) -> None:
        text = read_required(SKILL)
        self.assertIn("skills/<candidate>/SKILL.md", text)
        self.assertRegex(text, r"(?is)regular file.*error")

    def test_review_and_status_are_strictly_read_only(self) -> None:
        workflow = read_required(REFERENCES / "workflow.md")
        for route in ("qa-review", "qa-status"):
            with self.subTest(route=route):
                row = re.search(rf"(?im)^\| `{route}` \|([^\n]+)$", workflow)
                self.assertIsNotNone(row, f"missing workflow row for {route}")
                self.assertIn("read-only", row.group(1).lower())
        self.assertRegex(workflow, r"(?is)read-only.*must not.*(?:execute|mutate|write)")

    def test_missing_or_zero_applicable_criteria_is_blocked(self) -> None:
        workflow = read_required(REFERENCES / "workflow.md")
        self.assertRegex(workflow, r"(?is)(?:missing|absent) criteria.*`BLOCKED`")
        self.assertRegex(workflow, r"(?is)zero applicable criteria.*`BLOCKED`")

    def test_shared_status_and_verdict_contract_is_exact(self) -> None:
        workflow = read_required(REFERENCES / "workflow.md")
        self.assertIn("`PASS`, `FAIL`, `BLOCKED`, `NOT_RUN`, `NOT_APPLICABLE`", workflow)
        self.assertIn("Global verdicts are exactly `PASS`, `FAIL`, or `BLOCKED`", workflow)
        self.assertRegex(workflow, r"(?is)proven.*in-scope.*failure.*`FAIL`")
        self.assertRegex(workflow, r"(?is)`PASS`.*all applicable.*absence of.*current defects")

    def test_privileged_operations_require_explicit_authorization(self) -> None:
        safety = read_required(REFERENCES / "safety.md")
        for operation in ("load", "penetration testing", "production", "external effects"):
            with self.subTest(operation=operation):
                self.assertRegex(safety, rf"(?is){operation}.*explicit authorization")
        self.assertRegex(safety, r"(?is)product corrections.*only.*requested")
        self.assertRegex(safety, r"(?is)report.*must not execute.*evidence commands")

    def test_evidence_contract_is_confined_and_verifiable(self) -> None:
        artifacts = read_required(REFERENCES / "artifacts.md")
        for phrase in (
            "regular local file",
            "repository-relative",
            "symlink",
            "SHA-256",
            "target",
            "contract",
            "sanitization review",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase.lower(), artifacts.lower())

    def test_skill_has_complete_contract_and_all_local_links_resolve(self) -> None:
        text = read_required(SKILL)
        self.assertRegex(text, r"(?s)^---\nname: qa\ndescription: .+?\n---\n")
        for section in ("Inputs", "Procedure", "Output", "Failure modes", "Safety", "Related skills"):
            self.assertIn(f"## {section}", text)

        markdown_files = [SKILL, *(REFERENCES / name for name in ("workflow.md", "safety.md", "artifacts.md"))]
        for source in markdown_files:
            source_text = read_required(source)
            for target in re.findall(r"\[[^\]]+\]\(([^)#]+\.md)\)", source_text):
                with self.subTest(source=source.name, target=target):
                    self.assertTrue((source.parent / target).resolve().is_file())


if __name__ == "__main__":
    unittest.main()
