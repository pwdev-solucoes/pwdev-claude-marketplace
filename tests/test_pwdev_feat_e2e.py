"""pwdev-feat E2E scenarios: JSON Schema, validation, Playwright export and coverage."""
from __future__ import annotations

import copy
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "pwdev-feat"
SCHEMA = PLUGIN / "schemas" / "e2e-scenario.schema.json"


def load():
    spec = importlib.util.spec_from_file_location("pwdev_feat_e2e", PLUGIN / "scripts" / "e2e_scenarios.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


SCENARIO = {
    "schema_version": 1,
    "id": "E2E-001",
    "title": "Member signs in",
    "feature_slug": "user-login",
    "ac_refs": ["AC-001", "AC-002"],
    "priority": "P1",
    "tags": ["auth"],
    "preconditions": {
        "base_url_env": "APP_BASE_URL",
        "start_path": "/login",
        "users": [{"role": "member", "credentials_env": {"email": "E2E_MEMBER_EMAIL", "password": "E2E_MEMBER_PASSWORD"}}],
        "state": ["a member account exists"],
    },
    "data": {"greeting": "Welcome back"},
    "variants": [
        {"name": "happy_path", "title": "valid credentials", "as_user": "member",
         "steps": [
             {"action": "fill", "target": {"by": "label", "value": "Email"}, "value": "${env:E2E_MEMBER_EMAIL}"},
             {"action": "fill", "target": {"by": "label", "value": "Password"}, "value": "${env:E2E_MEMBER_PASSWORD}"},
             {"action": "click", "target": {"by": "role", "value": "button", "name": "Sign in"}}],
         "assertions": [
             {"expect": "url", "value": "/dashboard"},
             {"expect": "text", "target": {"by": "role", "value": "heading", "name": "Dashboard"}, "value": "${data.greeting}"}]},
        {"name": "validation_error", "title": "empty form",
         "steps": [{"action": "click", "target": {"by": "role", "value": "button", "name": "Sign in"}}],
         "assertions": [{"expect": "visible", "target": {"by": "text", "value": "Email is required", "exact": True}}]},
    ],
    "not_applicable": {"forbidden": "public page", "empty_state": "no list on this screen"},
}
PLAN = """---
type: feat-plan
schema_version: 3
slug: user-login
plan_type: frontend
status: pending
created: 2026-09-27T10:00:00Z
---

## 5. Quality Criteria
| ID | Criterion | Verification |
|----|-----------|--------------|
| AC-001 | signs in | E2E-001 |
| AC-002 | shows greeting | E2E-001 |
| AC-003 | logs the event | UNIT-001 |
"""


class E2EScenariosTest(unittest.TestCase):
    def setUp(self):
        self.mod = load()
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name) / "tests" / "e2e" / "scenarios"
        self.dir.mkdir(parents=True)
        self.plan = Path(self.tmp.name) / "plan.md"
        self.plan.write_text(PLAN, encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, doc: dict, name: str = "E2E-001-member-signs-in.scenario.json") -> Path:
        path = self.dir / name
        path.write_text(json.dumps(doc), encoding="utf-8")
        return path

    def errors(self, doc: dict) -> list[str]:
        self.write(doc)
        return [e for f in self.mod.validate(self.dir, self.plan)["files"] for e in f["errors"]]

    def test_schema_is_draft_2020_12_and_complete(self):
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        for name in ("preconditions", "locator", "step", "assertion", "variant", "user"):
            self.assertIn(name, schema["$defs"])
        try:
            import jsonschema  # type: ignore
        except ImportError:
            return
        jsonschema.Draft202012Validator.check_schema(schema)
        jsonschema.Draft202012Validator(schema).validate(SCENARIO)

    def test_valid_scenario_passes(self):
        self.write(SCENARIO)
        result = self.mod.validate(self.dir, self.plan)
        self.assertTrue(result["ok"], result)

    def test_invalid_scenarios_are_rejected(self):
        cases = {
            "unknown action": lambda d: d["variants"][0]["steps"].append({"action": "teleport"}),
            "missing happy path": lambda d: d["variants"].pop(0),
            "ac not in plan": lambda d: d["ac_refs"].append("AC-999"),
            "literal password": lambda d: d["variants"][0]["steps"][1].update(value="hunter2"),
            "literal token": lambda d: d["data"].update(key="ghp_" + "a" * 30),
            "unknown data ref": lambda d: d["variants"][0]["assertions"][1].update(value="${data.nope}"),
            "fill without value": lambda d: d["variants"][0]["steps"][0].pop("value"),
            "unknown user": lambda d: d["variants"][0].update(as_user="admin"),
            "bad id": lambda d: d.update(id="E2E-1"),
            "extra property": lambda d: d.update(browser="chrome"),
            "slug mismatch": lambda d: d.update(feature_slug="other-feature"),
        }
        for label, mutate in cases.items():
            doc = copy.deepcopy(SCENARIO)
            mutate(doc)
            with self.subTest(label):
                self.assertTrue(self.errors(doc), f"{label} was accepted")

    def test_duplicate_ids_across_files(self):
        self.write(SCENARIO)
        self.write(SCENARIO, "E2E-001-copy.scenario.json")
        result = self.mod.validate(self.dir, None)
        self.assertFalse(result["ok"])
        self.assertTrue(any("duplicate id" in e for f in result["files"] for e in f["errors"]))

    def test_export_is_deterministic_and_well_formed(self):
        self.write(SCENARIO)
        out = Path(self.tmp.name) / "tests" / "e2e" / "generated"
        first = self.mod.export(self.dir, out)
        self.assertTrue(first["ok"], first)
        spec = out / "E2E-001-member-signs-in.spec.ts"
        text = spec.read_text(encoding="utf-8")
        again = self.mod.export(self.dir, out)
        self.assertTrue(again["ok"])
        self.assertEqual(text, spec.read_text(encoding="utf-8"))
        for needle in (
            "GENERATED by pwdev-feat",
            "import { test, expect } from '@playwright/test';",
            "test.use({ baseURL: process.env['APP_BASE_URL'] });",
            "test('happy_path — valid credentials'",
            "test('validation_error — empty form'",
            "{ type: 'AC', description: 'AC-002' }",
            "await page.goto('/login');",
            "await page.getByLabel('Email').fill(env('E2E_MEMBER_EMAIL'));",
            "await page.getByRole('button', { name: 'Sign in' }).click();",
            "await expect(page).toHaveURL(new RegExp(escapeRegExp('/dashboard')));",
            "toContainText(String(data.greeting));",
            "await expect(page.getByText('Email is required', { exact: true })).toBeVisible();",
        ):
            self.assertIn(needle, text)
        self.assertNotIn("hunter2", text)
        node = shutil.which("node")
        if node:
            probe = subprocess.run([node, "--check", str(spec)], capture_output=True, text=True)
            if "Unknown file extension" not in probe.stderr and "ERR_UNKNOWN_FILE_EXTENSION" not in probe.stderr:
                self.assertEqual(probe.returncode, 0, probe.stderr)

    def test_export_refuses_invalid_scenarios(self):
        doc = copy.deepcopy(SCENARIO)
        doc["variants"][0]["steps"][1]["value"] = "hunter2"
        self.write(doc)
        out = Path(self.tmp.name) / "gen"
        result = self.mod.export(self.dir, out)
        self.assertFalse(result["ok"])
        self.assertFalse(out.exists())

    def test_coverage_matrix(self):
        self.write(SCENARIO)
        result = self.mod.coverage(self.plan, self.dir)
        self.assertEqual(result["matrix"], {"AC-001": ["E2E-001"], "AC-002": ["E2E-001"], "AC-003": []})
        self.assertEqual(result["uncovered"], ["AC-003"])


if __name__ == "__main__":
    unittest.main()
