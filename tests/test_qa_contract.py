"""Behavioral tests for the PWDEV QA report manifest contract."""

import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "plugins" / "pwdev-qa" / "scripts" / "qa_contract.py"
SCHEMA = ROOT / "plugins" / "pwdev-qa" / "schemas" / "report.schema.json"
MIB = 1024 * 1024


def load_contract_module():
    if not SCRIPT.is_file():
        raise AssertionError("qa_contract.py is missing")
    spec = importlib.util.spec_from_file_location("qa_contract", SCRIPT)
    if spec is None or spec.loader is None:
        raise AssertionError("qa_contract.py cannot be loaded")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def valid_manifest() -> dict:
    return {
        "schema_version": 1,
        "run_id": "release-2026-09-12",
        "project": "PWDEV QA",
        "target": {"id": "web-app", "kind": "web", "x-target": "kept"},
        "executed_at": "2026-09-12T19:00:00Z",
        "contract": {
            "path": "tasks/prd-pwdev-qa/prd.md",
            "sha256": "a" * 64,
            "criteria_review": {
                "actor": "qa-reviewer",
                "at": "2026-09-12T18:00:00+00:00",
                "complete": True,
            },
        },
        "criteria": [
            {
                "id": "CA-001",
                "text": "O relatório é exportado.",
                "applicable": True,
                "applicability_reason": "Escopo da entrega",
                "assessment": {
                    "actor": "qa-reviewer",
                    "at": "2026-09-12T19:00:00-03:00",
                    "expected": "Dois formatos",
                    "observed": "Dois formatos",
                },
                "case_ids": ["export-report"],
            }
        ],
        "cases": [
            {
                "id": "attempt-1",
                "case_id": "export-report",
                "criterion_ids": ["CA-001"],
                "status": "PASS",
                "required": True,
                "expected": "Dois formatos",
                "observed": "Dois formatos",
                "command": "python3 -m unittest tests.test_qa_contract",
                "exit_code": 0,
                "evidence_ids": ["ev-1"],
                "attempt": 1,
                "supersedes": None,
            }
        ],
        "evidence": [
            {
                "id": "ev-1",
                "path": "artifacts/qa-output.txt",
                "sha256": "b" * 64,
                "media_type": "text/plain",
                "size_bytes": 42,
                "target_id": "web-app",
                "sanitization": {
                    "status": "reviewed",
                    "actor": "qa-reviewer",
                    "at": "2026-09-12T19:01:00Z",
                },
            }
        ],
        "defects": [
            {
                "id": "BUG-1",
                "summary": "Defeito corrigido",
                "in_scope": True,
                "status": "resolved",
                "severity": "high",
                "criterion_ids": ["CA-001"],
                "evidence_ids": ["ev-1"],
                "supersedes": None,
                "retest_attempt_id": "attempt-1",
            }
        ],
        "x-private": {"owner": "internal", "publish": False},
    }


class QaContractTest(unittest.TestCase):
    def setUp(self) -> None:
        self.contract = load_contract_module()

    def assert_invalid(self, data: dict, pattern: str) -> None:
        with self.assertRaisesRegex(self.contract.ValidationError, pattern):
            self.contract.validate_manifest(data)

    def test_valid_manifest_is_copied_and_preserves_unknown_fields(self) -> None:
        source = valid_manifest()
        normalized = self.contract.validate_manifest(source)
        self.assertEqual(normalized, source)
        self.assertIsNot(normalized, source)
        self.assertIsNot(normalized["x-private"], source["x-private"])
        self.assertEqual(normalized["x-private"], {"owner": "internal", "publish": False})
        self.assertNotIn("x-private", normalized.get("public", {}))

    def test_schema_documents_v1_limits_and_preserves_extensions(self) -> None:
        self.assertTrue(SCHEMA.is_file(), "report.schema.json is missing")
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        self.assertEqual(schema["properties"]["schema_version"]["const"], 1)
        self.assertEqual(schema["properties"]["criteria"]["maxItems"], 1000)
        self.assertEqual(schema["properties"]["evidence"]["maxItems"], 1000)
        self.assertTrue(schema["additionalProperties"])

    def test_bool_is_never_accepted_as_an_integer(self) -> None:
        locations = (
            ("schema_version", lambda data: data.__setitem__("schema_version", True)),
            ("exit_code", lambda data: data["cases"][0].__setitem__("exit_code", False)),
            ("attempt", lambda data: data["cases"][0].__setitem__("attempt", True)),
            ("size_bytes", lambda data: data["evidence"][0].__setitem__("size_bytes", True)),
        )
        for label, mutate in locations:
            with self.subTest(label=label):
                data = valid_manifest()
                mutate(data)
                self.assert_invalid(data, label)

    def test_rejects_unknown_enums_and_wrong_scalar_types(self) -> None:
        mutations = (
            ("status", lambda d: d["cases"][0].__setitem__("status", "SKIPPED")),
            ("media_type", lambda d: d["evidence"][0].__setitem__("media_type", "text/html")),
            ("sanitization", lambda d: d["evidence"][0]["sanitization"].__setitem__("status", "approved")),
            ("defect status", lambda d: d["defects"][0].__setitem__("status", "closed")),
            ("required", lambda d: d["cases"][0].__setitem__("required", 1)),
            ("applicable", lambda d: d["criteria"][0].__setitem__("applicable", "yes")),
        )
        for label, mutate in mutations:
            with self.subTest(label=label):
                data = valid_manifest()
                mutate(data)
                self.assert_invalid(data, label.split()[0])

    def test_rejects_duplicate_ids_and_case_attempts(self) -> None:
        for collection in ("criteria", "cases", "evidence", "defects"):
            with self.subTest(collection=collection):
                data = valid_manifest()
                data[collection].append(copy.deepcopy(data[collection][0]))
                self.assert_invalid(data, "duplicate")

        data = valid_manifest()
        second = copy.deepcopy(data["cases"][0])
        second.update(id="attempt-other", attempt=1, supersedes="attempt-1")
        data["cases"].append(second)
        self.assert_invalid(data, "attempt")

    def test_rejects_unresolved_references_and_invalid_retest_links(self) -> None:
        mutations = (
            ("logical case", lambda d: d["criteria"][0].__setitem__("case_ids", ["missing"])),
            ("criterion", lambda d: d["cases"][0].__setitem__("criterion_ids", ["missing"])),
            ("evidence", lambda d: d["cases"][0].__setitem__("evidence_ids", ["missing"])),
            ("target", lambda d: d["evidence"][0].__setitem__("target_id", "other")),
            ("retest", lambda d: d["defects"][0].__setitem__("retest_attempt_id", "missing")),
        )
        for label, mutate in mutations:
            with self.subTest(label=label):
                data = valid_manifest()
                mutate(data)
                self.assert_invalid(data, label)

        data = valid_manifest()
        data["defects"][0].update(status="resolved", retest_attempt_id=None)
        self.assert_invalid(data, "retest_attempt_id")

    def test_retest_chain_requires_prior_same_case_without_branching(self) -> None:
        data = valid_manifest()
        attempt_2 = copy.deepcopy(data["cases"][0])
        attempt_2.update(id="attempt-2", attempt=2, supersedes="attempt-1")
        data["cases"].append(attempt_2)
        self.contract.validate_manifest(data)

        wrong_case = copy.deepcopy(data)
        wrong_case["cases"][1]["case_id"] = "other-case"
        self.assert_invalid(wrong_case, "same case_id")

        future = copy.deepcopy(data)
        future["cases"][0]["supersedes"] = "attempt-2"
        self.assert_invalid(future, "prior")

        branch = copy.deepcopy(data)
        attempt_3 = copy.deepcopy(branch["cases"][1])
        attempt_3.update(id="attempt-3", attempt=3, supersedes="attempt-1")
        branch["cases"].append(attempt_3)
        self.assert_invalid(branch, "branch")

        disconnected = copy.deepcopy(data)
        disconnected["cases"][1]["supersedes"] = None
        self.assert_invalid(disconnected, "chain")

    def test_non_applicable_criterion_requires_a_reason(self) -> None:
        data = valid_manifest()
        data["criteria"][0].update(applicable=False, applicability_reason="")
        self.assert_invalid(data, "applicability_reason")

    def test_rejects_declared_evidence_size_limits(self) -> None:
        data = valid_manifest()
        data["evidence"][0]["size_bytes"] = 10 * MIB + 1
        self.assert_invalid(data, "10 MiB")

        data = valid_manifest()
        data["evidence"] = []
        for number in range(11):
            item = copy.deepcopy(valid_manifest()["evidence"][0])
            item.update(
                id=f"ev-{number}",
                path=f"artifacts/{number}.txt",
                size_bytes=10 * MIB,
            )
            data["evidence"].append(item)
        data["cases"][0]["evidence_ids"] = []
        data["defects"][0]["evidence_ids"] = []
        self.assert_invalid(data, "100 MiB")

    def test_rejects_invalid_or_timezone_free_timestamps(self) -> None:
        locations = (
            lambda d: d.__setitem__("executed_at", "2026-09-12T19:00:00"),
            lambda d: d["contract"]["criteria_review"].__setitem__("at", "2026-02-30T00:00:00Z"),
            lambda d: d["criteria"][0]["assessment"].__setitem__("at", "not-a-date"),
            lambda d: d["evidence"][0]["sanitization"].__setitem__("at", 123),
        )
        for mutate in locations:
            data = valid_manifest()
            mutate(data)
            self.assert_invalid(data, "timestamp")

    def test_rejects_collection_limits(self) -> None:
        data = valid_manifest()
        data["criteria"] = []
        for number in range(1001):
            item = copy.deepcopy(valid_manifest()["criteria"][0])
            item.update(id=f"CA-{number}", case_ids=[])
            data["criteria"].append(item)
        data["cases"][0]["criterion_ids"] = []
        data["defects"][0]["criterion_ids"] = []
        self.assert_invalid(data, "1000")

        data = valid_manifest()
        data["evidence"] = []
        for number in range(1001):
            item = copy.deepcopy(valid_manifest()["evidence"][0])
            item.update(id=f"ev-{number}", path=f"artifacts/{number}.txt")
            data["evidence"].append(item)
        data["cases"][0]["evidence_ids"] = []
        data["defects"][0]["evidence_ids"] = []
        self.assert_invalid(data, "1000")

    def test_rejects_absolute_traversing_or_non_normalized_paths(self) -> None:
        invalid_paths = (
            "/tmp/evidence.txt",
            "../evidence.txt",
            "artifacts/../evidence.txt",
            "artifacts//evidence.txt",
            "C:\\temp\\evidence.txt",
        )
        for value in invalid_paths:
            for owner in ("contract", "evidence"):
                with self.subTest(value=value, owner=owner):
                    data = valid_manifest()
                    if owner == "contract":
                        data["contract"]["path"] = value
                    else:
                        data["evidence"][0]["path"] = value
                    self.assert_invalid(data, "path")

    def test_load_manifest_enforces_five_mib_before_json_parsing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            valid_path = root / "valid.json"
            valid_path.write_text(json.dumps(valid_manifest()), encoding="utf-8")
            self.assertEqual(self.contract.load_manifest(valid_path), valid_manifest())

            exact_path = root / "exact.json"
            payload = json.dumps(valid_manifest()).encode("utf-8")
            exact_path.write_bytes(payload + b" " * (5 * MIB - len(payload)))
            self.assertEqual(self.contract.load_manifest(exact_path), valid_manifest())

            oversized_path = root / "oversized.json"
            oversized_path.write_bytes(b"{" + b" " * (5 * MIB))
            self.assertGreater(oversized_path.stat().st_size, 5 * MIB)
            with self.assertRaisesRegex(self.contract.ValidationError, "5 MiB"):
                self.contract.load_manifest(oversized_path)

            malformed = root / "malformed.json"
            malformed.write_text('{"schema_version": 1', encoding="utf-8")
            with self.assertRaisesRegex(self.contract.ValidationError, "JSON"):
                self.contract.load_manifest(malformed)

            duplicate = root / "duplicate.json"
            duplicate.write_text('{"schema_version": 1, "schema_version": 1}', encoding="utf-8")
            with self.assertRaisesRegex(self.contract.ValidationError, "duplicate field"):
                self.contract.load_manifest(duplicate)


if __name__ == "__main__":
    unittest.main()
