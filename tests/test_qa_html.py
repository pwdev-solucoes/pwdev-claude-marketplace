"""Behavioral tests for the static offline PWDEV QA HTML renderer."""

import importlib.util
import re
import sys
import unittest
from pathlib import Path

from tests.test_qa_contract import load_contract_module, valid_manifest
from tests.test_qa_verdict import inspections


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "plugins" / "pwdev-qa" / "scripts"
HTML_SCRIPT = SCRIPTS / "qa_html.py"
VERDICT_SCRIPT = SCRIPTS / "qa_verdict.py"


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
    verdict = load_module("qa_verdict_for_html", VERDICT_SCRIPT)
    return verdict.build_report(manifest, inspections(manifest))


class QaHtmlTest(unittest.TestCase):
    def setUp(self) -> None:
        self.renderer = load_module("qa_html", HTML_SCRIPT)

    def test_renders_complete_allowlisted_report_with_internal_dom_ids(self) -> None:
        report = build(valid_manifest())
        report["x-private"] = "MUST-NOT-BE-RENDERED"
        report["criteria"][0]["x-private"] = "CRITERION-PRIVATE"

        html = self.renderer.render_html(report)

        self.assertTrue(html.startswith("<!doctype html>"))
        self.assertIn('<meta charset="utf-8">', html)
        for section in (
            "summary",
            "criteria",
            "cases",
            "defects",
            "evidence",
            "diagnostics",
            "verdict",
        ):
            self.assertIn(f'id="section-{section}"', html)
        for value in (
            "release-2026-09-12",
            "PWDEV QA",
            "web-app",
            "web",
            "tasks/prd-pwdev-qa/prd.md",
            "qa-reviewer",
            "CA-001",
            "O relatório é exportado.",
            "Escopo da entrega",
            "export-report",
            "attempt-1",
            "Dois formatos",
            "python3 -m unittest tests.test_qa_contract",
            "BUG-1",
            "Defeito corrigido",
            "ev-1",
            "artifacts/qa-output.txt",
            "text/plain",
            "PASS",
        ):
            self.assertIn(value, html)
        self.assertIn('id="criterion-1"', html)
        self.assertIn('id="case-1"', html)
        self.assertIn('id="defect-1"', html)
        self.assertIn('id="evidence-1"', html)
        self.assertNotIn('id="CA-001"', html)
        self.assertNotIn('id="attempt-1"', html)
        self.assertNotIn('id="ev-1"', html)
        self.assertNotIn("MUST-NOT-BE-RENDERED", html)
        self.assertNotIn("CRITERION-PRIVATE", html)

    def test_escapes_malicious_content_in_every_allowed_string_field(self) -> None:
        report = build(valid_manifest())
        payload = '<img src=x onerror="alert(1)">&\'PAYLOAD'

        def poison(value):
            if isinstance(value, dict):
                return {key: poison(item) for key, item in value.items()}
            if isinstance(value, list):
                return [poison(item) for item in value]
            if isinstance(value, str):
                return payload
            return value

        html = self.renderer.render_html(poison(report))

        self.assertNotIn("<img", html.lower())
        self.assertNotIn("<script", html.lower())
        self.assertNotIn("onerror=\"alert(1)\"", html)
        self.assertIn("&lt;img src=x onerror=&quot;alert(1)&quot;&gt;&amp;&#x27;PAYLOAD", html)
        input_derived_ids = re.findall(r'\bid="([^"]*PAYLOAD[^"]*)"', html)
        self.assertEqual(input_derived_ids, [])

    def test_is_self_contained_offline_without_javascript_or_remote_resources(self) -> None:
        html = self.renderer.render_html(build(valid_manifest()))
        lowered = html.lower()

        self.assertNotIn("<script", lowered)
        self.assertNotIn("javascript:", lowered)
        self.assertNotRegex(lowered, r'\b(?:src|href)\s*=\s*["\'](?:https?:)?//')
        self.assertNotRegex(lowered, r'@import\s+url')
        self.assertNotIn("<link", lowered)

    def test_renders_unicode_and_only_approved_evidence_references(self) -> None:
        data = valid_manifest()
        data["project"] = "Qualidade — ação, 中文, 🚀"
        data["criteria"][0]["assessment"]["observed"] = "Saída íntegra: café ☕"
        data["evidence"].append(
            {
                "id": "ev-pending",
                "path": "artifacts/pending.txt",
                "sha256": "c" * 64,
                "media_type": "text/plain",
                "size_bytes": 7,
                "target_id": "web-app",
                "sanitization": {
                    "status": "pending",
                    "actor": "qa-reviewer",
                    "at": "2026-09-12T19:02:00Z",
                },
            }
        )
        manifest = load_contract_module().validate_manifest(data)
        evidence = inspections(manifest, "ev-pending")
        report = load_module("qa_verdict_unicode", VERDICT_SCRIPT).build_report(
            manifest, evidence
        )

        html = self.renderer.render_html(report)

        self.assertIn("Qualidade — ação, 中文, 🚀", html)
        self.assertIn("Saída íntegra: café ☕", html)
        self.assertIn("ev-1", html)
        self.assertIn("artifacts/qa-output.txt", html)
        self.assertNotIn('id="ev-pending"', html)
        self.assertNotIn('href="#ev-pending"', html)
        self.assertNotIn("artifacts/pending.txt", html)
        self.assertIn("evidence &#x27;ev-pending&#x27;: unavailable", html)

    def test_renders_explicit_empty_states_for_zero_items(self) -> None:
        data = valid_manifest()
        data["criteria"] = []
        data["cases"] = []
        data["evidence"] = []
        data["defects"] = []
        report = build(data)

        html = self.renderer.render_html(report)

        self.assertIn("BLOCKED", html)
        self.assertIn("No criteria.", html)
        self.assertIn("No cases or attempts.", html)
        self.assertIn("No defects.", html)
        self.assertIn("No approved evidence.", html)
        self.assertIn("no criteria", html)
        self.assertIn("no applicable criteria", html)
        self.assertIn("no required cases", html)


if __name__ == "__main__":
    unittest.main()
