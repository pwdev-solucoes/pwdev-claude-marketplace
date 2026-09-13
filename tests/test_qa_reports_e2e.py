"""End-to-end parity tests for reproducible PWDEV QA report fixtures."""

from __future__ import annotations

import html
import importlib.util
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

import pdfplumber
from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "pwdev-qa"
SCRIPTS = PLUGIN / "scripts"
DEMO_SCRIPT = SCRIPTS / "qa_demo.py"
DEV_REQUIREMENTS = PLUGIN / "requirements-dev.txt"
SECRET_VALUE = "qa-secret-value-123456789"


def load_demo():
    if not DEMO_SCRIPT.is_file():
        raise AssertionError("qa_demo.py is missing")
    spec = importlib.util.spec_from_file_location("qa_demo_e2e", DEMO_SCRIPT)
    if spec is None or spec.loader is None:
        raise AssertionError("qa_demo.py cannot be loaded")
    module = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(SCRIPTS))
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path.remove(str(SCRIPTS))
    return module


def extracted_pdf(path: Path) -> tuple[str, str]:
    reader_text = "\n".join(page.extract_text() or "" for page in PdfReader(path).pages)
    with pdfplumber.open(path) as document:
        plumber_text = "\n".join(page.extract_text() or "" for page in document.pages)
    return reader_text, plumber_text


class QaReportsE2ETest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.destination = Path(self.temporary.name) / "demo"

    def test_demo_generates_independently_verified_html_pdf_and_public_model(self) -> None:
        result = load_demo().create_demo(self.destination)

        self.assertEqual(result["export_status"], "complete")
        self.assertEqual(result["verdict"], "FAIL")
        output = Path(result["output_dir"])
        source = json.loads((self.destination / "demo-manifest.json").read_text("utf-8"))
        public = json.loads((output / "manifest.json").read_text("utf-8"))
        html_report = (output / "report.html").read_text("utf-8")
        pypdf_text, plumber_text = extracted_pdf(output / "report.pdf")

        self.assertEqual(len(source["criteria"]), 100)
        self.assertTrue(all(len(item["text"]) == 2000 for item in source["criteria"]))
        self.assertEqual(public["verdict"], "FAIL")
        self.assertEqual(public["criteria"], source["criteria"])
        self.assertEqual(public["cases"], source["cases"])
        self.assertEqual(public["defects"], source["defects"])
        self.assertEqual(
            [item["id"] for item in public["verified_evidence"]], ["ev-safe"]
        )

        rendered_texts = (pypdf_text, plumber_text)
        for criterion, criterion_result in zip(
            source["criteria"], public["criterion_results"]
        ):
            self.assertIn(html.escape(criterion["text"], quote=True), html_report)
            complete_tokens = re.findall(r"c\d{3}w\d{4}á", criterion["text"])
            for rendered in rendered_texts:
                self.assertEqual(
                    re.findall(rf"c{criterion['id'][-3:]}w\d{{4}}á", rendered),
                    complete_tokens,
                )
                for value in (
                    criterion["id"],
                    criterion["assessment"]["expected"],
                    criterion["assessment"]["observed"],
                    criterion_result["result"],
                ):
                    self.assertIn(value, rendered)

        for case in source["cases"]:
            for value in (
                case["id"],
                case["case_id"],
                case["expected"],
                case["observed"],
                case["status"],
            ):
                self.assertIn(html.escape(value, quote=True), html_report)
                for rendered in rendered_texts:
                    self.assertIn(value, rendered)
        self.assertGreaterEqual(html_report.count("ev-safe"), len(source["cases"]) + 2)
        for rendered in rendered_texts:
            self.assertGreaterEqual(rendered.count("ev-safe"), len(source["cases"]) + 2)

        defect = source["defects"][0]
        for value in (defect["id"], defect["summary"], "ev-safe", "FAIL"):
            self.assertIn(html.escape(value, quote=True), html_report)
            for rendered in rendered_texts:
                self.assertIn(value, rendered)

        package_files = [path for path in output.rglob("*") if path.is_file()]
        self.assertEqual(
            sorted(path.relative_to(output).as_posix() for path in package_files),
            sorted(
                [
                    public["verified_evidence"][0]["path"],
                    "manifest.json",
                    "report.html",
                    "report.pdf",
                ]
            ),
        )
        self.assertNotIn(SECRET_VALUE, html_report)
        self.assertNotIn(SECRET_VALUE, pypdf_text)
        self.assertNotIn(SECRET_VALUE, plumber_text)
        self.assertNotIn("ev-secret", json.dumps(public, ensure_ascii=False))
        self.assertNotIn("ev-pending-image", json.dumps(public["verified_evidence"]))
        self.assertEqual(sum(len(page.images) for page in PdfReader(output / "report.pdf").pages), 0)
        self.assertTrue(any("credential-like data" in item for item in result["diagnostics"]))
        self.assertTrue(any("sanitization review is pending" in item for item in result["diagnostics"]))

    def test_demo_requires_a_new_explicit_output_directory(self) -> None:
        self.destination.mkdir()
        marker = self.destination / "keep.txt"
        marker.write_text("preserve", encoding="utf-8")

        with self.assertRaises(FileExistsError):
            load_demo().create_demo(self.destination)

        self.assertEqual(marker.read_text("utf-8"), "preserve")
        self.assertEqual(list(self.destination.iterdir()), [marker])

    def test_development_pdf_verification_dependencies_are_exactly_pinned(self) -> None:
        self.assertEqual(
            DEV_REQUIREMENTS.read_text("utf-8").splitlines(),
            ["pypdf==6.10.0", "pdfplumber==0.11.9"],
        )


if __name__ == "__main__":
    unittest.main()
