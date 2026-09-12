"""Behavioral tests for the paginated PWDEV QA PDF renderer."""

import builtins
import copy
import importlib.util
import re
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import pdfplumber
from pypdf import PdfReader

from tests.test_qa_contract import load_contract_module, valid_manifest
from tests.test_qa_verdict import inspections


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "plugins" / "pwdev-qa" / "scripts"
PDF_SCRIPT = SCRIPTS / "qa_pdf.py"
VERDICT_SCRIPT = SCRIPTS / "qa_verdict.py"
REQUIREMENTS = ROOT / "plugins" / "pwdev-qa" / "requirements.txt"


def load_module(name: str, path: Path):
    if not path.is_file():
        raise AssertionError(f"{path.name} is missing")
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"{path.name} cannot be loaded")
    module = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(SCRIPTS))
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path.remove(str(SCRIPTS))
    return module


def build(data: dict) -> dict:
    manifest = load_contract_module().validate_manifest(data)
    verdict = load_module("qa_verdict_for_pdf", VERDICT_SCRIPT)
    return verdict.build_report(manifest, inspections(manifest))


def long_criterion(index: int):
    tokens = []
    word = 0
    while len(" ".join(tokens)) < 2000:
        tokens.append(f"c{index:03d}w{word:04d}á")
        word += 1
    return " ".join(tokens)[:2000], tokens[:-1]


class QaPdfTest(unittest.TestCase):
    def setUp(self) -> None:
        self.renderer = load_module("qa_pdf", PDF_SCRIPT)
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.destination = Path(self.temporary.name) / "report.pdf"

    def test_renders_a4_paginated_complete_public_report_with_textual_statuses(self) -> None:
        report = build(valid_manifest())
        report["project"] = "Qualidade — ação <b>não é markup</b>"
        self.renderer.render_pdf(report, self.destination)

        reader = PdfReader(self.destination)
        self.assertGreaterEqual(len(reader.pages), 2)
        self.assertAlmostEqual(float(reader.pages[0].mediabox.width), 595.2756, places=2)
        self.assertAlmostEqual(float(reader.pages[0].mediabox.height), 841.8898, places=2)
        extracted = "\n".join(page.extract_text() or "" for page in reader.pages)
        for label in (
            "PWDEV QA report",
            "Contents",
            "Status legend",
            "Summary",
            "Acceptance criteria",
            "Cases and attempts",
            "Defects",
            "Approved evidence",
            "Diagnostics",
            "Verdict",
            "PASS",
            "BLOCKED",
            "NOT_RUN",
            "NOT_APPLICABLE",
            "Page 1 of",
            "Qualidade — ação <b>não é markup</b>",
            "O relatório é exportado.",
            "Dois formatos",
            "python3 -m unittest tests.test_qa_contract",
            "Defeito corrigido",
            "artifacts/qa-output.txt",
        ):
            self.assertIn(label, extracted)

    def test_preserves_all_tokens_in_one_hundred_2000_character_criteria(self) -> None:
        data = valid_manifest()
        base_criterion = data["criteria"][0]
        base_case = data["cases"][0]
        data["criteria"] = []
        data["cases"] = []
        expected_tokens = []
        for index in range(100):
            text, tokens = long_criterion(index)
            expected_tokens.extend(tokens)
            criterion = copy.deepcopy(base_criterion)
            criterion.update(id=f"CA-{index:03d}", text=text, case_ids=[f"case-{index:03d}"])
            case = copy.deepcopy(base_case)
            case.update(
                id=f"attempt-{index:03d}",
                case_id=f"case-{index:03d}",
                criterion_ids=[f"CA-{index:03d}"],
            )
            data["criteria"].append(criterion)
            data["cases"].append(case)
        data["defects"] = []
        report = build(data)

        self.renderer.render_pdf(report, self.destination)

        reader = PdfReader(self.destination)
        self.assertGreater(len(reader.pages), 20)
        pypdf_text = "\n".join(page.extract_text() or "" for page in reader.pages)
        with pdfplumber.open(self.destination) as document:
            plumber_text = "\n".join(page.extract_text() or "" for page in document.pages)
        token_pattern = re.compile(r"c\d{3}w\d{4}á")
        self.assertCountEqual(token_pattern.findall(pypdf_text), expected_tokens)
        self.assertCountEqual(token_pattern.findall(plumber_text), expected_tokens)

    def test_fails_explicitly_when_reportlab_is_unavailable(self) -> None:
        report = build(valid_manifest())
        real_import = builtins.__import__

        def unavailable(name, *args, **kwargs):
            if name == "reportlab" or name.startswith("reportlab."):
                raise ModuleNotFoundError("No module named 'reportlab'", name="reportlab")
            return real_import(name, *args, **kwargs)

        with mock.patch("builtins.__import__", side_effect=unavailable):
            with self.assertRaisesRegex(RuntimeError, "reportlab==4.4.9 is required"):
                self.renderer.render_pdf(report, self.destination)
        self.assertFalse(self.destination.exists())

    def test_lists_only_verified_evidence_as_approved_references(self) -> None:
        data = valid_manifest()
        pending = copy.deepcopy(data["evidence"][0])
        pending.update(
            id="ev-pending",
            path="artifacts/SECRET-unreviewed.png",
            media_type="image/png",
        )
        pending["sanitization"]["status"] = "pending"
        data["evidence"].append(pending)
        data["cases"][0]["evidence_ids"].append("ev-pending")
        data["defects"][0]["evidence_ids"].append("ev-pending")
        manifest = load_contract_module().validate_manifest(data)
        verdict = load_module("qa_verdict_filtered_pdf", VERDICT_SCRIPT)
        report = verdict.build_report(manifest, inspections(manifest, "ev-pending"))

        self.renderer.render_pdf(report, self.destination)

        extracted = "\n".join(
            page.extract_text() or "" for page in PdfReader(self.destination).pages
        )
        self.assertNotIn("ev-1, ev-pending", extracted)
        self.assertNotIn("SECRET-unreviewed.png", extracted)
        self.assertIn("Approved evidence IDs\nev-1", extracted)
        self.assertIn("evidence 'ev-pending': unavailable", extracted)

    def test_declares_exact_runtime_and_verification_dependencies(self) -> None:
        lines = [
            line.strip()
            for line in REQUIREMENTS.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        ]
        self.assertEqual(
            lines,
            ["reportlab==4.4.9", "pypdf==6.10.0", "pdfplumber==0.11.9"],
        )


if __name__ == "__main__":
    unittest.main()
