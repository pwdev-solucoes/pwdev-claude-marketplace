"""Behavioral tests for deterministic PWDEV QA verdict consolidation."""

import copy
import importlib.util
import json
import sys
import unittest
from pathlib import Path

from tests.test_qa_contract import load_contract_module, valid_manifest


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "plugins" / "pwdev-qa" / "scripts"
SCRIPT = SCRIPTS / "qa_verdict.py"


def load_verdict_module():
    if not SCRIPT.is_file():
        raise AssertionError("qa_verdict.py is missing")
    spec = importlib.util.spec_from_file_location("qa_verdict", SCRIPT)
    if spec is None or spec.loader is None:
        raise AssertionError("qa_verdict.py cannot be loaded")
    module = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(SCRIPTS))
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path.remove(str(SCRIPTS))
    return module


def inspections(manifest: dict, *blocked_ids: str) -> list:
    blocked = set(blocked_ids)
    records = []
    for item in manifest["evidence"]:
        base = {
            "id": item["id"],
            "target_id": item["target_id"],
            "contract": {
                "path": manifest["contract"]["path"],
                "sha256": manifest["contract"]["sha256"],
            },
        }
        if item["id"] in blocked:
            base.update(
                status="BLOCKED",
                copy_allowed=False,
                diagnostic=f"evidence {item['id']!r}: unavailable",
            )
        else:
            base.update(
                status="VERIFIED",
                copy_allowed=True,
                requires_copy_revalidation=True,
                path=item["path"],
                sha256=item["sha256"],
                media_type=item["media_type"],
                size_bytes=item["size_bytes"],
                diagnostic=None,
            )
        records.append(base)
    return records


def normalized(data: dict) -> dict:
    return load_contract_module().validate_manifest(data)


def add_attempt(data: dict, status: str, *, evidence_ids=None) -> dict:
    previous = data["cases"][-1]
    current = copy.deepcopy(previous)
    current.update(
        id=f"attempt-{previous['attempt'] + 1}",
        status=status,
        attempt=previous["attempt"] + 1,
        supersedes=previous["id"],
    )
    if evidence_ids is not None:
        current["evidence_ids"] = evidence_ids
    data["cases"].append(current)
    return current


class QaVerdictTest(unittest.TestCase):
    def setUp(self) -> None:
        self.verdict = load_verdict_module()

    def build(self, data: dict, *blocked_ids: str) -> dict:
        manifest = normalized(data)
        return self.verdict.build_report(manifest, inspections(manifest, *blocked_ids))

    def test_pass_projects_only_the_public_contract_and_exact_counts(self) -> None:
        data = valid_manifest()
        data["defects"] = []
        data["target"]["x-target"] = "PRIVATE-TARGET-EXTENSION"
        data["criteria"][0]["x-criterion"] = "PRIVATE-CRITERION-EXTENSION"
        report = self.build(data)

        self.assertEqual(report["verdict"], "PASS")
        self.assertEqual(report["criterion_results"], [{"id": "CA-001", "result": "PASS"}])
        self.assertEqual(
            report["counts"],
            {
                "criteria_total": 1,
                "criteria_applicable": 1,
                "criteria_pass": 1,
                "criteria_fail": 0,
                "criteria_blocked": 0,
                "criteria_not_run": 0,
                "criteria_not_applicable": 0,
                "cases_total": 1,
                "cases_terminal": 1,
                "defects_total": 0,
                "defects_current_in_scope": 0,
                "defects_out_of_scope": 0,
                "evidence_verified": 1,
                "evidence_blocked": 0,
            },
        )
        self.assertEqual(report["diagnostics"], [])
        self.assertEqual(report["verified_evidence"], inspections(normalized(data)))
        encoded = json.dumps(report)
        self.assertNotIn("PRIVATE-", encoded)
        self.assertNotIn("x-private", report)
        self.assertNotIn("evidence", report)
        self.assertEqual(report["target"], {"id": "web-app", "kind": "web"})

    def test_failure_precedes_every_blocker_and_unlinked_defect_is_counted(self) -> None:
        data = valid_manifest()
        data["contract"]["criteria_review"]["complete"] = False
        data["cases"][0]["status"] = "NOT_RUN"
        data["defects"] = [
            {
                "id": "BUG-open",
                "summary": "Falha vigente sem critério",
                "in_scope": True,
                "status": "open",
                "severity": "high",
                "criterion_ids": [],
                "evidence_ids": ["ev-1"],
                "supersedes": None,
                "retest_attempt_id": None,
            }
        ]
        report = self.build(data)

        self.assertEqual(report["verdict"], "FAIL")
        self.assertEqual(report["criterion_results"][0]["result"], "NOT_RUN")
        self.assertEqual(report["counts"]["defects_current_in_scope"], 1)
        self.assertTrue(any("criteria transcription" in item for item in report["diagnostics"]))
        self.assertTrue(any("BUG-open" in item for item in report["diagnostics"]))

    def test_zero_criteria_zero_applicable_or_zero_required_cases_are_blocked(self) -> None:
        empty = valid_manifest()
        empty.update(criteria=[], cases=[], evidence=[], defects=[])
        no_applicable = valid_manifest()
        no_applicable["criteria"][0].update(applicable=False, applicability_reason="Fora do escopo")
        no_applicable["cases"][0]["required"] = False
        no_required = valid_manifest()
        no_required["cases"][0]["required"] = False
        no_required["defects"] = []

        for label, data in (
            ("no criteria", empty),
            ("no applicable criteria", no_applicable),
            ("no required cases", no_required),
        ):
            with self.subTest(label=label):
                report = self.build(data)
                self.assertEqual(report["verdict"], "BLOCKED")
                self.assertTrue(any(label in item for item in report["diagnostics"]))

    def test_applicable_criterion_requires_substantive_assessment_without_equality(self) -> None:
        for field, value in (("expected", "  \n"), ("observed", "")):
            with self.subTest(field=field):
                data = valid_manifest()
                data["defects"] = []
                data["criteria"][0]["assessment"][field] = value
                report = self.build(data)
                self.assertEqual(report["verdict"], "BLOCKED")
                self.assertEqual(report["criterion_results"][0]["result"], "BLOCKED")
                self.assertTrue(any("substantive assessment" in d for d in report["diagnostics"]))

        unequal = valid_manifest()
        unequal["defects"] = []
        unequal["criteria"][0]["assessment"].update(
            expected="A pagina responde",
            observed="A pagina respondeu em 120 ms",
        )
        self.assertEqual(self.build(unequal)["verdict"], "PASS")

    def test_executed_required_case_requires_expected_and_observed_but_not_run_may_omit(self) -> None:
        for field, value in (("expected", ""), ("observed", " \t")):
            with self.subTest(field=field):
                data = valid_manifest()
                data["defects"] = []
                data["cases"][0][field] = value
                report = self.build(data)
                self.assertEqual(report["verdict"], "BLOCKED")
                self.assertTrue(any("executed required case" in d for d in report["diagnostics"]))

        not_run = valid_manifest()
        not_run["defects"] = []
        not_run["cases"][0].update(status="NOT_RUN", expected="", observed="")
        report = self.build(not_run)
        self.assertEqual(report["verdict"], "BLOCKED")
        self.assertFalse(any("executed required case" in d for d in report["diagnostics"]))

    def test_pending_states_invalid_waiver_and_blocked_evidence_never_pass(self) -> None:
        for status, expected_result, diagnostic in (
            ("BLOCKED", "BLOCKED", "terminal status BLOCKED"),
            ("NOT_RUN", "NOT_RUN", "terminal status NOT_RUN"),
            ("NOT_APPLICABLE", "BLOCKED", "invalid NOT_APPLICABLE"),
        ):
            with self.subTest(status=status):
                data = valid_manifest()
                data["defects"] = []
                data["cases"][0]["status"] = status
                report = self.build(data)
                self.assertEqual(report["verdict"], "BLOCKED")
                self.assertEqual(report["criterion_results"][0]["result"], expected_result)
                self.assertTrue(any(diagnostic in item for item in report["diagnostics"]))

        data = valid_manifest()
        data["defects"] = []
        report = self.build(data, "ev-1")
        self.assertEqual(report["verdict"], "BLOCKED")
        self.assertEqual(report["criterion_results"][0]["result"], "BLOCKED")
        self.assertEqual(report["verified_evidence"], [])
        self.assertTrue(any("unavailable" in item for item in report["diagnostics"]))

    def test_valid_not_applicable_case_does_not_block_other_applicable_criteria(self) -> None:
        data = valid_manifest()
        data["defects"] = []
        data["criteria"][0].update(
            applicable=False,
            applicability_reason="Fora do escopo contratado",
        )
        data["cases"][0].update(status="NOT_APPLICABLE", required=False)
        applicable = copy.deepcopy(data["criteria"][0])
        applicable.update(
            id="CA-002",
            applicable=True,
            applicability_reason="Escopo da entrega",
            case_ids=["required-pass"],
        )
        passing_case = copy.deepcopy(data["cases"][0])
        passing_case.update(
            id="attempt-pass",
            case_id="required-pass",
            criterion_ids=["CA-002"],
            status="PASS",
            required=True,
            attempt=1,
            supersedes=None,
        )
        data["criteria"].append(applicable)
        data["cases"].append(passing_case)

        report = self.build(data)

        self.assertEqual(report["verdict"], "PASS")
        self.assertEqual(
            report["criterion_results"],
            [
                {"id": "CA-001", "result": "NOT_APPLICABLE"},
                {"id": "CA-002", "result": "PASS"},
            ],
        )
        self.assertEqual(report["diagnostics"], [])

    def test_non_reciprocal_criterion_case_links_are_incomplete_coverage(self) -> None:
        data = valid_manifest()
        data["defects"] = []
        data["criteria"].append(copy.deepcopy(data["criteria"][0]))
        data["criteria"][1].update(id="CA-002", case_ids=[])
        data["cases"][0]["criterion_ids"] = ["CA-002"]
        report = self.build(data)

        self.assertEqual(report["verdict"], "BLOCKED")
        self.assertEqual(report["criterion_results"][0]["result"], "BLOCKED")
        self.assertTrue(any("non-reciprocal" in item for item in report["diagnostics"]))

    def test_current_proven_case_failure_fails_but_unproved_failure_blocks(self) -> None:
        data = valid_manifest()
        data["defects"] = []
        data["cases"][0]["status"] = "FAIL"
        proved = self.build(data)
        unproved = self.build(data, "ev-1")

        self.assertEqual(proved["verdict"], "FAIL")
        self.assertEqual(proved["criterion_results"][0]["result"], "FAIL")
        self.assertEqual(unproved["verdict"], "BLOCKED")
        self.assertEqual(unproved["criterion_results"][0]["result"], "BLOCKED")

    def test_terminal_retest_controls_result_without_erasing_history(self) -> None:
        data = valid_manifest()
        data["defects"] = []
        data["cases"][0]["status"] = "FAIL"
        add_attempt(data, "PASS")
        passed = self.build(data)
        self.assertEqual(passed["verdict"], "PASS")
        self.assertEqual([case["status"] for case in passed["cases"]], ["FAIL", "PASS"])
        self.assertEqual(passed["counts"]["cases_terminal"], 1)

        data["cases"][-1]["status"] = "BLOCKED"
        blocked = self.build(data)
        self.assertEqual(blocked["verdict"], "BLOCKED")
        self.assertEqual([case["status"] for case in blocked["cases"]], ["FAIL", "BLOCKED"])

    def test_resolved_defect_requires_a_passing_retest_with_valid_evidence(self) -> None:
        closed = self.build(valid_manifest())
        self.assertEqual(closed["verdict"], "PASS")
        self.assertEqual(closed["counts"]["defects_current_in_scope"], 0)

        failed_retest = valid_manifest()
        failed_retest["cases"][0]["status"] = "FAIL"
        report = self.build(failed_retest)
        self.assertEqual(report["verdict"], "FAIL")
        self.assertEqual(report["counts"]["defects_current_in_scope"], 1)

        unproved_resolution = self.build(valid_manifest(), "ev-1")
        self.assertEqual(unproved_resolution["verdict"], "BLOCKED")
        self.assertEqual(unproved_resolution["counts"]["defects_current_in_scope"], 1)

    def test_superseded_passing_retest_does_not_resolve_a_defect(self) -> None:
        for terminal_status in ("FAIL", "BLOCKED", "NOT_RUN"):
            with self.subTest(terminal_status=terminal_status):
                data = valid_manifest()
                terminal = add_attempt(data, terminal_status, evidence_ids=[])
                self.assertEqual(data["defects"][0]["retest_attempt_id"], "attempt-1")
                self.assertEqual(terminal["supersedes"], "attempt-1")

                report = self.build(data)

                self.assertEqual(report["verdict"], "FAIL")
                self.assertEqual(report["counts"]["defects_current_in_scope"], 1)
                self.assertTrue(
                    any(
                        "BUG-1" in item and "proven current" in item
                        for item in report["diagnostics"]
                    )
                )

    def test_out_of_scope_defect_is_visible_without_forcing_failure(self) -> None:
        data = valid_manifest()
        data["defects"][0].update(
            id="BUG-external",
            summary="Defeito fora do escopo",
            in_scope=False,
            status="out_of_scope",
            retest_attempt_id=None,
        )
        report = self.build(data)
        self.assertEqual(report["verdict"], "PASS")
        self.assertEqual(report["counts"]["defects_out_of_scope"], 1)
        self.assertEqual(report["defects"][0]["id"], "BUG-external")

    def test_contradictory_defect_scope_markers_are_blocked(self) -> None:
        for in_scope, status in (
            (True, "out_of_scope"),
            (False, "open"),
            (False, "resolved"),
        ):
            with self.subTest(in_scope=in_scope, status=status):
                data = valid_manifest()
                data["defects"][0].update(in_scope=in_scope, status=status)
                if status != "resolved":
                    data["defects"][0]["retest_attempt_id"] = None

                report = self.build(data)

                self.assertEqual(report["verdict"], "BLOCKED")
                self.assertEqual(report["counts"]["defects_current_in_scope"], 0)
                self.assertEqual(report["counts"]["defects_out_of_scope"], 0)
                self.assertTrue(
                    any("contradictory scope" in item for item in report["diagnostics"])
                )

    def test_coherent_proven_in_scope_defect_keeps_fail_precedence(self) -> None:
        data = valid_manifest()
        data["contract"]["criteria_review"]["complete"] = False
        data["defects"][0].update(status="open", retest_attempt_id=None)

        report = self.build(data)

        self.assertEqual(report["verdict"], "FAIL")
        self.assertEqual(report["counts"]["defects_current_in_scope"], 1)

    def test_cyclic_attempt_input_is_diagnosed_without_hanging_or_discarding_history(self) -> None:
        data = normalized(valid_manifest())
        data["defects"] = []
        data["cases"][0]["supersedes"] = data["cases"][0]["id"]
        report = self.verdict.build_report(data, inspections(data))
        self.assertEqual(report["verdict"], "BLOCKED")
        self.assertEqual(len(report["cases"]), 1)
        self.assertTrue(any("cycle" in item for item in report["diagnostics"]))

    def test_unreferenced_or_duplicate_inspections_block_and_never_leak(self) -> None:
        data = normalized(valid_manifest())
        data["defects"] = []
        records = inspections(data)
        records.append({"id": "extra", "status": "VERIFIED", "path": "PRIVATE-PATH"})
        report = self.verdict.build_report(data, records)
        self.assertEqual(report["verdict"], "BLOCKED")
        self.assertNotIn("PRIVATE-PATH", json.dumps(report))
        self.assertTrue(any("unexpected inspection" in item for item in report["diagnostics"]))

    def test_known_credential_in_public_diagnostic_is_neutrally_refused(self) -> None:
        data = normalized(valid_manifest())
        data["defects"] = []
        records = inspections(data)
        records[0].update(
            status="BLOCKED",
            copy_allowed=False,
            diagnostic="Authorization: Bearer SYNTHETIC_DIAGNOSTIC_TOKEN_123456",
        )
        private_before = copy.deepcopy(data)

        with self.assertRaisesRegex(self.verdict.EvidenceError, "public report") as raised:
            self.verdict.build_report(data, records)

        self.assertNotIn("SYNTHETIC_DIAGNOSTIC_TOKEN", str(raised.exception))
        self.assertEqual(data, private_before)


if __name__ == "__main__":
    unittest.main()
