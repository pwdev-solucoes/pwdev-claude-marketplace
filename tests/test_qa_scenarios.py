import importlib.util
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
PLUGIN = ROOT / "plugins" / "pwdev-qa"
ACCEPTANCE = PLUGIN / "references" / "acceptance-scenarios.md"
RUNTIME_SMOKE = PLUGIN / "references" / "runtime-smoke.md"

WORKFLOWS = {
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
}
SPECIALISTS = {
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


def backtick_names(text, prefix):
    return {
        name
        for name in re.findall(r"`([^`]+)`", text)
        if name.startswith(prefix)
    }


class TestRootReadmes(unittest.TestCase):
    def test_bilingual_catalogs_add_qa_once_and_group_it_by_goal(self):
        for relative in ("README.md", "README.pt-BR.md"):
            text = (ROOT / relative).read_text(encoding="utf-8")
            link = "[pwdev-qa](./plugins/pwdev-qa/)"
            self.assertEqual(text.count(link), 2, relative)
            self.assertRegex(
                text,
                r"\| (?:Quality assurance|Quality assurance \(QA\)|Garantia de qualidade \(QA\)) "
                r"\| \[pwdev-qa\]\(\./plugins/pwdev-qa/\) \|",
            )
            self.assertIn(
                "| [pwdev-qa](./plugins/pwdev-qa/) | 0.1.0 |", text
            )


class TestAcceptanceScenarios(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = ACCEPTANCE.read_text(encoding="utf-8") if ACCEPTANCE.is_file() else ""

    def test_acceptance_scenario_document_exists(self):
        self.assertTrue(ACCEPTANCE.is_file(), f"missing {ACCEPTANCE}")

    def test_every_workflow_and_specialist_has_complete_scenario_evaluation(self):
        self.assertEqual(backtick_names(self.text, "qa-") & WORKFLOWS, WORKFLOWS)
        self.assertEqual(backtick_names(self.text, "qa-specialist-"), SPECIALISTS)
        for required in (
            "SCN-WORKFLOWS",
            "SCN-SPECIALISTS",
            "positive scenario",
            "failure/limitation scenario",
            "expected",
            "observed",
            "evidence",
            "PASS",
        ):
            self.assertIn(required, self.text)

    def test_missing_tool_scenario_is_explicit_and_never_fabricates_execution(self):
        for required in (
            "SCN-QA-TOOLING-MISSING",
            "qa-tooling",
            "missing",
            "playwright-cli-does-not-exist",
            "command -v playwright-cli-does-not-exist",
            "Playwright Test",
            "not installed",
            "NOT_RUN",
            "BLOCKED",
            "no automatic installation",
        ):
            self.assertIn(required, self.text)

    def test_report_fixture_records_cross_format_acceptance_validation(self):
        for required in (
            "SCN-REPORT-FIXTURE",
            "demo-manifest.json",
            "manifest.json",
            "report.html",
            "report.pdf",
            "BUG-OPEN-UNMAPPED",
            "credential-log.txt",
            "pending-image.png",
            "export_status=complete",
            "verdict=FAIL",
            "pypdf==6.10.0",
            "pdfplumber==0.11.9",
        ):
            self.assertIn(required, self.text)

    @unittest.skipUnless(
        importlib.util.find_spec("reportlab")
        and importlib.util.find_spec("pypdf")
        and importlib.util.find_spec("pdfplumber"),
        "requires the declared Python 3.12 PDF verification environment",
    )
    def test_report_fixture_really_exports_and_validates_html_pdf(self):
        from pypdf import PdfReader
        import pdfplumber

        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "fixture"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(PLUGIN / "scripts" / "qa_demo.py"),
                    "--output-dir",
                    str(output),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=True,
            )
            result = json.loads(completed.stdout)
            package = Path(result["output_dir"])
            public = json.loads((package / "manifest.json").read_text(encoding="utf-8"))
            html = (package / "report.html").read_text(encoding="utf-8")
            pypdf_text = "\n".join(
                page.extract_text() or "" for page in PdfReader(package / "report.pdf").pages
            )
            with pdfplumber.open(package / "report.pdf") as document:
                plumber_text = "\n".join(page.extract_text() or "" for page in document.pages)

            self.assertEqual(result["export_status"], "complete")
            self.assertEqual(result["verdict"], "FAIL")
            self.assertEqual(
                [item["id"] for item in public["verified_evidence"]], ["ev-safe"]
            )
            for value in ("BUG-OPEN-UNMAPPED", "FAIL", "CA-001", "CA-002", "CA-003"):
                self.assertIn(value, html)
                self.assertIn(value, pypdf_text)
                self.assertIn(value, plumber_text)
            for rejected in ("credential-log.txt", "pending-image.png"):
                self.assertNotIn(rejected, json.dumps(public))
                self.assertNotIn(rejected, html)
                self.assertNotIn(rejected, pypdf_text)
                self.assertNotIn(rejected, plumber_text)


class TestRuntimeSmokeLedger(unittest.TestCase):
    def test_real_runtime_results_are_versioned_reproducible_and_honest(self):
        self.assertTrue(RUNTIME_SMOKE.is_file(), f"missing {RUNTIME_SMOKE}")
        text = RUNTIME_SMOKE.read_text(encoding="utf-8") if RUNTIME_SMOKE.is_file() else ""
        for runtime in ("Claude Code", "Codex", "Hermes Agent"):
            self.assertIn(runtime, text)
        for required in (
            "qa-tooling discovery",
            "missing-tool response",
            "fixture report",
            "exact version",
            "command/probe",
            "evidence",
            "limitations",
            "VERIFIED",
            "UNVERIFIED",
            "isolated temporary directory",
            "npx --no-install playwright --version",
            "npx playwright cli",
            "playwright-cli --version",
        ):
            self.assertIn(required, text)
        rows = re.findall(
            r"^\| (Claude Code|Codex|Hermes Agent) \| ([^|]+) \| "
            r"(VERIFIED|UNVERIFIED) \|",
            text,
            flags=re.MULTILINE,
        )
        self.assertEqual(len(rows), 3)
        for _, version, status in rows:
            self.assertNotIn("pending", version.lower())
            if status == "VERIFIED":
                self.assertIn("successful", text)


if __name__ == "__main__":
    unittest.main()
