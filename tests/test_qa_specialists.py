"""Deterministic behavioural scenarios for the PWDEV QA specialists."""

import re
import unittest
from pathlib import Path
from typing import Dict, List


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "plugins" / "pwdev-qa" / "skills"
SPECIALISTS = {
    name: SKILLS / name / "SKILL.md"
    for name in (
        "qa-specialist-strategy",
        "qa-specialist-requirements",
        "qa-specialist-functional",
        "qa-specialist-web",
        "qa-specialist-api",
        "qa-specialist-mobile",
        "qa-specialist-data",
        "qa-specialist-accessibility",
        "qa-specialist-performance",
        "qa-specialist-security",
        "qa-specialist-automation",
        "qa-specialist-cicd",
    )
}
COMMON_SECTIONS = (
    "Inputs",
    "Procedure",
    "Output",
    "Failure modes",
    "Safety",
    "Related skills",
)


def read_required(path: Path) -> str:
    if not path.is_file():
        raise AssertionError(f"required QA specialist is missing: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


def parse_scenarios(text: str, columns: tuple[str, ...]) -> List[Dict[str, str]]:
    heading = " | ".join(columns)
    match = re.search(
        rf"(?ms)^## Reference scenarios\n\n\| {re.escape(heading)} \|\n"
        rf"\|[- |]+\|\n(?P<rows>(?:\|[^\n]*\|\n)+)",
        text,
    )
    if not match:
        raise AssertionError("specialist has no parseable reference scenario table")
    rows = []
    for line in match.group("rows").splitlines():
        values = [cell.strip() for cell in line.strip("|").split("|")]
        if len(values) != len(columns):
            raise AssertionError(
                f"scenario row has {len(values)} fields, expected {len(columns)}"
            )
        rows.append(dict(zip(columns, values)))
    return rows


class QaSpecialistContractTest(unittest.TestCase):
    def test_all_specialists_have_the_common_contract_and_remain_advisory(self) -> None:
        for name, path in SPECIALISTS.items():
            with self.subTest(specialist=name):
                text = read_required(path)
                self.assertRegex(
                    text,
                    rf"(?s)^---\nname: {re.escape(name)}\ndescription: .+?\n---\n",
                )
                for section in COMMON_SECTIONS:
                    self.assertIn(f"## {section}", text)
                self.assertRegex(text, r"(?is)does not execute (?:a )?workflow")
                self.assertRegex(text, r"(?is)(?:cannot|does not) grant authorization")
                self.assertIn("[workflow](../../references/workflow.md)", text)
                self.assertIn("[safety](../../references/safety.md)", text)

    def test_strategy_success_prioritizes_risk_and_produces_coverage(self) -> None:
        text = read_required(SPECIALISTS["qa-specialist-strategy"])
        rows = parse_scenarios(
            text,
            (
                "scenario",
                "risk",
                "likelihood",
                "impact",
                "oracle",
                "coverage",
                "outcome",
            ),
        )
        success = [row for row in rows if row["scenario"] == "complete-risk"]
        self.assertEqual(len(success), 2)
        self.assertEqual(
            [(row["risk"], row["likelihood"], row["impact"]) for row in success],
            [
                ("unauthorized access", "high", "high"),
                ("export format drift", "medium", "high"),
            ],
        )
        for row in success:
            self.assertEqual(row["oracle"], "observable")
            self.assertTrue(set(row["coverage"].split(",")) >= {"positive", "negative", "boundary"})
            self.assertEqual(row["outcome"], "READY")

        self.assertRegex(text, r"(?is)risk.*likelihood.*impact.*priority")
        self.assertRegex(text, r"(?is)coverage gap.*residual risk")

    def test_strategy_missing_oracle_is_a_blocking_coverage_gap(self) -> None:
        rows = parse_scenarios(
            read_required(SPECIALISTS["qa-specialist-strategy"]),
            (
                "scenario",
                "risk",
                "likelihood",
                "impact",
                "oracle",
                "coverage",
                "outcome",
            ),
        )
        limited = [row for row in rows if row["scenario"] == "missing-oracle"]
        self.assertEqual(len(limited), 1)
        self.assertEqual(limited[0]["oracle"], "missing")
        self.assertEqual(limited[0]["coverage"], "none")
        self.assertEqual(limited[0]["outcome"], "BLOCKED")

    def test_requirements_accepts_observable_criteria_and_preserves_traceability(self) -> None:
        text = read_required(SPECIALISTS["qa-specialist-requirements"])
        rows = parse_scenarios(
            text,
            (
                "scenario",
                "criterion_id",
                "criterion_text",
                "oracle",
                "traceability",
                "outcome",
            ),
        )
        clear = next(row for row in rows if row["scenario"] == "clear-criterion")
        self.assertEqual(clear["criterion_id"], "AC-LOGIN-01")
        self.assertIn("three failed attempts", clear["criterion_text"])
        self.assertEqual(clear["oracle"], "observable")
        self.assertEqual(clear["traceability"], "preserved")
        self.assertEqual(clear["outcome"], "READY")
        self.assertRegex(text, r"(?is)preserve.*criterion ID.*text")

    def test_requirements_blocks_ambiguity_without_inventing_a_threshold(self) -> None:
        text = read_required(SPECIALISTS["qa-specialist-requirements"])
        rows = parse_scenarios(
            text,
            (
                "scenario",
                "criterion_id",
                "criterion_text",
                "oracle",
                "traceability",
                "outcome",
            ),
        )
        ambiguous = next(row for row in rows if row["scenario"] == "ambiguous-criterion")
        self.assertEqual(ambiguous["criterion_text"], "The response should be fast")
        self.assertEqual(ambiguous["oracle"], "missing threshold and environment")
        self.assertEqual(ambiguous["traceability"], "preserved")
        self.assertEqual(ambiguous["outcome"], "BLOCKED")
        self.assertNotRegex(ambiguous["criterion_text"], r"\d+\s*(?:ms|seconds?)")
        self.assertRegex(text, r"(?is)do not invent.*threshold")

    def test_functional_success_covers_positive_negative_and_boundary_observably(self) -> None:
        text = read_required(SPECIALISTS["qa-specialist-functional"])
        rows = parse_scenarios(
            text,
            (
                "scenario",
                "partition",
                "input",
                "expected",
                "observable",
                "outcome",
            ),
        )
        triplet = [row for row in rows if row["scenario"] == "complete-triplet"]
        self.assertEqual(
            [row["partition"] for row in triplet],
            ["positive", "negative", "boundary"],
        )
        self.assertTrue(all(row["expected"] for row in triplet))
        self.assertTrue(all(row["observable"] == "yes" for row in triplet))
        self.assertTrue(all(row["outcome"] == "READY" for row in triplet))
        self.assertRegex(text, r"(?is)expected.*observable")

    def test_functional_missing_expected_observation_is_blocked(self) -> None:
        rows = parse_scenarios(
            read_required(SPECIALISTS["qa-specialist-functional"]),
            (
                "scenario",
                "partition",
                "input",
                "expected",
                "observable",
                "outcome",
            ),
        )
        limited = [row for row in rows if row["scenario"] == "missing-observation"]
        self.assertEqual(len(limited), 1)
        self.assertEqual(limited[0]["partition"], "error")
        self.assertEqual(limited[0]["expected"], "unspecified")
        self.assertEqual(limited[0]["observable"], "no")
        self.assertEqual(limited[0]["outcome"], "BLOCKED")

    def test_web_available_cli_uses_isolated_observed_interaction(self) -> None:
        text = read_required(SPECIALISTS["qa-specialist-web"])
        rows = parse_scenarios(
            text,
            (
                "scenario",
                "availability",
                "browser",
                "session",
                "snapshot",
                "action",
                "capture",
                "suite",
                "outcome",
            ),
        )
        success = next(row for row in rows if row["scenario"] == "available-cli")
        self.assertEqual(success["availability"], "available")
        self.assertEqual(success["browser"], "chromium")
        self.assertEqual(success["session"], "qa-report")
        self.assertEqual(success["snapshot"], "fresh")
        self.assertEqual(success["action"], "observed refs")
        self.assertEqual(success["capture"], "reviewed")
        self.assertEqual(success["suite"], "Playwright Test")
        self.assertEqual(success["outcome"], "READY")
        self.assertIn("playwright-cli --version", text)
        self.assertIn("npx --no-install playwright --version", text)
        self.assertIn("npx playwright cli", text)
        self.assertRegex(text, r"playwright-cli -s=qa-report (?:open|snapshot)")
        self.assertRegex(text, r"(?is)screenshot.*review.*before.*attach")
        self.assertRegex(text, r"(?is)does not replace.*(?:repeatable|deterministic).*suite")

    def test_web_missing_cli_records_limitation_without_execution(self) -> None:
        rows = parse_scenarios(
            read_required(SPECIALISTS["qa-specialist-web"]),
            (
                "scenario",
                "availability",
                "browser",
                "session",
                "snapshot",
                "action",
                "capture",
                "suite",
                "outcome",
            ),
        )
        limited = next(row for row in rows if row["scenario"] == "missing-cli")
        self.assertEqual(limited["availability"], "missing")
        self.assertEqual(limited["session"], "none")
        self.assertEqual(limited["snapshot"], "not run")
        self.assertEqual(limited["action"], "not run")
        self.assertEqual(limited["outcome"], "BLOCKED")

    def test_api_success_covers_contract_access_errors_and_idempotency(self) -> None:
        text = read_required(SPECIALISTS["qa-specialist-api"])
        rows = parse_scenarios(
            text,
            (
                "scenario",
                "contract",
                "authentication",
                "authorization",
                "errors",
                "idempotency",
                "outcome",
            ),
        )
        success = next(row for row in rows if row["scenario"] == "complete-api")
        self.assertEqual(
            success,
            {
                "scenario": "complete-api",
                "contract": "schema and status verified",
                "authentication": "valid and invalid credentials",
                "authorization": "allowed and denied roles",
                "errors": "mapped responses verified",
                "idempotency": "same key no duplicate effect",
                "outcome": "READY",
            },
        )
        self.assertRegex(text, r"(?is)expected.*observed")
        self.assertRegex(text, r"(?is)side effect.*idempot")

    def test_api_missing_authorization_oracle_is_blocked(self) -> None:
        rows = parse_scenarios(
            read_required(SPECIALISTS["qa-specialist-api"]),
            (
                "scenario",
                "contract",
                "authentication",
                "authorization",
                "errors",
                "idempotency",
                "outcome",
            ),
        )
        limited = next(row for row in rows if row["scenario"] == "missing-authz-oracle")
        self.assertEqual(limited["authorization"], "missing role policy")
        self.assertEqual(limited["outcome"], "BLOCKED")

    def test_mobile_ready_scenarios_distinguish_android_and_ios_prerequisites(self) -> None:
        text = read_required(SPECIALISTS["qa-specialist-mobile"])
        rows = parse_scenarios(
            text,
            (
                "scenario",
                "platform",
                "tool_probe",
                "host_probe",
                "sdk_probe",
                "adb_probe",
                "driver_probe",
                "build_probe",
                "signing_probe",
                "device_probe",
                "service_probe",
                "outcome",
            ),
        )
        ready = [row for row in rows if row["scenario"] == "platform-ready"]
        self.assertEqual(
            ready,
            [
                {
                    "scenario": "platform-ready",
                    "platform": "Android",
                    "tool_probe": "positive: Appium",
                    "host_probe": "positive: compatible host",
                    "sdk_probe": "positive: Android SDK",
                    "adb_probe": "positive: connected",
                    "driver_probe": "positive: UiAutomator2",
                    "build_probe": "positive: test build",
                    "signing_probe": "positive: installable",
                    "device_probe": "positive: emulator",
                    "service_probe": "positive: test backend",
                    "outcome": "READY",
                },
                {
                    "scenario": "platform-ready",
                    "platform": "iOS",
                    "tool_probe": "positive: Appium",
                    "host_probe": "positive: macOS",
                    "sdk_probe": "positive: Xcode iOS SDK",
                    "adb_probe": "not applicable: iOS",
                    "driver_probe": "positive: XCUITest",
                    "build_probe": "positive: test build",
                    "signing_probe": "positive: simulator-valid",
                    "device_probe": "positive: simulator",
                    "service_probe": "positive: test backend",
                    "outcome": "READY",
                },
            ],
        )
        self.assertRegex(text, r"(?is)Android.*SDK.*driver.*device")
        self.assertRegex(text, r"(?is)iOS.*Xcode.*driver.*device")

    def test_mobile_missing_device_is_blocked_and_never_fabricated(self) -> None:
        rows = parse_scenarios(
            read_required(SPECIALISTS["qa-specialist-mobile"]),
            (
                "scenario",
                "platform",
                "tool_probe",
                "host_probe",
                "sdk_probe",
                "adb_probe",
                "driver_probe",
                "build_probe",
                "signing_probe",
                "device_probe",
                "service_probe",
                "outcome",
            ),
        )
        limited = next(row for row in rows if row["scenario"] == "missing-device")
        self.assertEqual(limited["platform"], "Android")
        self.assertEqual(limited["device_probe"], "negative: missing")
        self.assertEqual(limited["outcome"], "BLOCKED")

    def test_mobile_omitted_host_build_signing_or_adb_never_becomes_ready(self) -> None:
        rows = parse_scenarios(
            read_required(SPECIALISTS["qa-specialist-mobile"]),
            (
                "scenario",
                "platform",
                "tool_probe",
                "host_probe",
                "sdk_probe",
                "adb_probe",
                "driver_probe",
                "build_probe",
                "signing_probe",
                "device_probe",
                "service_probe",
                "outcome",
            ),
        )
        expected = {
            "missing-host": ("host_probe", "not_run: host", "unverified"),
            "missing-build": ("build_probe", "negative: missing", "BLOCKED"),
            "missing-signing": ("signing_probe", "not_run: signing", "unverified"),
            "missing-adb": ("adb_probe", "not_run: ADB", "unverified"),
        }
        for scenario, (field, value, outcome) in expected.items():
            with self.subTest(scenario=scenario):
                row = next(item for item in rows if item["scenario"] == scenario)
                self.assertEqual(row[field], value)
                self.assertEqual(row["outcome"], outcome)
                self.assertNotEqual(row["outcome"], "READY")

    def test_data_ready_scenario_separates_reconciliation_integrity_and_transactions(self) -> None:
        text = read_required(SPECIALISTS["qa-specialist-data"])
        rows = parse_scenarios(
            text,
            (
                "scenario",
                "authorization",
                "target",
                "dataset",
                "write_limit",
                "evidence",
                "reconciliation",
                "integrity",
                "transaction",
                "atomicity",
                "outcome",
            ),
        )
        ready = next(row for row in rows if row["scenario"] == "complete-data-check")
        self.assertEqual(
            ready,
            {
                "scenario": "complete-data-check",
                "authorization": "explicit mutation grant",
                "target": "qa-db.orders",
                "dataset": "synthetic orders v1",
                "write_limit": "20 rows in one transaction",
                "evidence": "EV-DATA-001",
                "reconciliation": "source and target totals match",
                "integrity": "constraints and relationships verified",
                "transaction": "commit and rollback observed",
                "atomicity": "failure leaves no partial write",
                "outcome": "READY",
            },
        )
        self.assertRegex(text, r"(?is)reconciliation.*does not prove.*atomicity")
        self.assertRegex(text, r"(?is)integrity.*does not prove.*transaction")

    def test_data_missing_authorization_scope_or_evidence_never_runs_transaction(self) -> None:
        rows = parse_scenarios(
            read_required(SPECIALISTS["qa-specialist-data"]),
            (
                "scenario",
                "authorization",
                "target",
                "dataset",
                "write_limit",
                "evidence",
                "reconciliation",
                "integrity",
                "transaction",
                "atomicity",
                "outcome",
            ),
        )
        expected = {
            "missing-data-authorization": ("authorization", "missing"),
            "missing-data-target": ("target", "missing"),
            "missing-data-dataset": ("dataset", "missing"),
            "missing-write-limit": ("write_limit", "missing"),
            "missing-data-evidence": ("evidence", "missing"),
        }
        for scenario, (field, value) in expected.items():
            with self.subTest(scenario=scenario):
                limited = next(row for row in rows if row["scenario"] == scenario)
                self.assertEqual(limited[field], value)
                self.assertEqual(limited["transaction"], "NOT_RUN")
                self.assertEqual(limited["atomicity"], "unverified")
                self.assertEqual(limited["outcome"], "BLOCKED")
                self.assertNotEqual(limited["outcome"], "READY")

    def test_accessibility_ready_requires_observed_keyboard_and_focus_beyond_scanner(self) -> None:
        text = read_required(SPECIALISTS["qa-specialist-accessibility"])
        rows = parse_scenarios(
            text,
            ("scenario", "scanner", "keyboard", "focus", "semantics", "outcome"),
        )
        ready = next(row for row in rows if row["scenario"] == "complete-accessibility-check")
        self.assertEqual(
            ready,
            {
                "scenario": "complete-accessibility-check",
                "scanner": "no reported violations",
                "keyboard": "journey observed without pointer",
                "focus": "order and visible indicator observed",
                "semantics": "name role and state observed",
                "outcome": "READY",
            },
        )
        self.assertRegex(text, r"(?is)scanner.*does not prove.*accessib")
        self.assertRegex(text, r"(?is)keyboard.*focus.*observ")

    def test_accessibility_scanner_only_is_blocked(self) -> None:
        rows = parse_scenarios(
            read_required(SPECIALISTS["qa-specialist-accessibility"]),
            ("scenario", "scanner", "keyboard", "focus", "semantics", "outcome"),
        )
        limited = next(row for row in rows if row["scenario"] == "scanner-only")
        self.assertEqual(limited["scanner"], "no reported violations")
        self.assertEqual(limited["keyboard"], "not run")
        self.assertEqual(limited["focus"], "not observed")
        self.assertEqual(limited["outcome"], "BLOCKED")

    def test_performance_ready_has_authorized_profile_sample_context_and_percentiles(self) -> None:
        text = read_required(SPECIALISTS["qa-specialist-performance"])
        rows = parse_scenarios(
            text,
            (
                "scenario",
                "authorization",
                "target",
                "limits",
                "environment",
                "window",
                "workload",
                "sample",
                "context",
                "percentiles",
                "threshold",
                "outcome",
            ),
        )
        ready = next(row for row in rows if row["scenario"] == "authorized-profile")
        self.assertEqual(ready["authorization"], "explicit load grant")
        self.assertEqual(ready["target"], "https://staging.example.test/search")
        self.assertEqual(ready["limits"], "50 VUs and 500 requests/s maximum")
        self.assertEqual(ready["environment"], "staging")
        self.assertEqual(ready["window"], "2026-09-12T14:00Z to 2026-09-12T14:10Z")
        self.assertEqual(ready["workload"], "50 VUs for 10 minutes")
        self.assertEqual(ready["sample"], "12000 requests")
        self.assertEqual(ready["context"], "staging build abc123 warm cache")
        self.assertEqual(ready["percentiles"], "p50 80 ms, p95 210 ms, p99 290 ms")
        self.assertEqual(ready["threshold"], "p95 at most 250 ms")
        self.assertEqual(ready["outcome"], "READY")
        self.assertRegex(text, r"(?is)explicit authorization.*target.*limits.*environment.*time window")

    def test_performance_missing_authorization_component_never_runs_load(self) -> None:
        text = read_required(SPECIALISTS["qa-specialist-performance"])
        rows = parse_scenarios(
            text,
            (
                "scenario",
                "authorization",
                "target",
                "limits",
                "environment",
                "window",
                "workload",
                "sample",
                "context",
                "percentiles",
                "threshold",
                "outcome",
            ),
        )
        expected = {
            "missing-load-authorization": ("authorization", "missing"),
            "missing-load-target": ("target", "missing"),
            "missing-load-limits": ("limits", "missing"),
            "missing-load-environment": ("environment", "missing"),
            "missing-load-window": ("window", "missing"),
        }
        for scenario, (field, value) in expected.items():
            with self.subTest(scenario=scenario):
                limited = next(row for row in rows if row["scenario"] == scenario)
                self.assertEqual(limited[field], value)
                self.assertEqual(limited["workload"], "NOT_RUN")
                self.assertEqual(limited["outcome"], "BLOCKED")
                self.assertNotEqual(limited["outcome"], "READY")
        self.assertRegex(text, r"(?is)average.*(?:alone|isolated).*does not.*(?:PASS|READY|approval)")

    def test_security_authorized_pentest_stays_inside_the_bounded_scope(self) -> None:
        text = read_required(SPECIALISTS["qa-specialist-security"])
        rows = parse_scenarios(
            text,
            (
                "scenario",
                "scanner",
                "pentest_authorization",
                "target",
                "methods",
                "environment",
                "window",
                "owner",
                "rate_limit",
                "stop_conditions",
                "cleanup",
                "execution",
                "outcome",
            ),
        )
        ready = next(row for row in rows if row["scenario"] == "bounded-pentest")
        self.assertEqual(
            ready,
            {
                "scenario": "bounded-pentest",
                "scanner": "reviewed findings",
                "pentest_authorization": "explicit bounded grant",
                "target": "staging.example.test/api",
                "methods": "OWASP API checks excluding denial of service",
                "environment": "staging",
                "window": "2026-09-12T15:00Z to 2026-09-12T16:00Z",
                "owner": "qa-security-owner",
                "rate_limit": "20 requests/s maximum",
                "stop_conditions": "service degradation or unexpected data access",
                "cleanup": "revoke test tokens and remove synthetic data",
                "execution": "authorized reproducible checks",
                "outcome": "READY",
            },
        )
        self.assertRegex(
            text,
            r"(?is)explicit authorization.*target.*methods.*environment.*time window",
        )

    def test_security_missing_operational_boundary_never_runs_or_becomes_ready(self) -> None:
        rows = parse_scenarios(
            read_required(SPECIALISTS["qa-specialist-security"]),
            (
                "scenario",
                "scanner",
                "pentest_authorization",
                "target",
                "methods",
                "environment",
                "window",
                "owner",
                "rate_limit",
                "stop_conditions",
                "cleanup",
                "execution",
                "outcome",
            ),
        )
        expected = {
            "missing-owner": ("owner", "missing"),
            "missing-rate-limit": ("rate_limit", "missing"),
            "missing-stop-conditions": ("stop_conditions", "missing"),
            "missing-cleanup": ("cleanup", "missing"),
        }
        for scenario, (field, value) in expected.items():
            with self.subTest(scenario=scenario):
                limited = next(row for row in rows if row["scenario"] == scenario)
                self.assertEqual(limited[field], value)
                self.assertEqual(limited["target"], "staging.example.test/api")
                self.assertEqual(
                    limited["methods"],
                    "OWASP API checks excluding denial of service",
                )
                self.assertEqual(limited["environment"], "staging")
                self.assertEqual(
                    limited["window"],
                    "2026-09-12T15:00Z to 2026-09-12T16:00Z",
                )
                self.assertEqual(limited["execution"], "NOT_RUN")
                self.assertEqual(limited["outcome"], "BLOCKED")
                self.assertNotEqual(limited["outcome"], "READY")

    def test_security_scanner_never_becomes_pentest_authorization(self) -> None:
        text = read_required(SPECIALISTS["qa-specialist-security"])
        rows = parse_scenarios(
            text,
            (
                "scenario",
                "scanner",
                "pentest_authorization",
                "target",
                "methods",
                "environment",
                "window",
                "owner",
                "rate_limit",
                "stop_conditions",
                "cleanup",
                "execution",
                "outcome",
            ),
        )
        limited = next(row for row in rows if row["scenario"] == "scanner-only")
        self.assertEqual(limited["scanner"], "available with findings")
        self.assertEqual(limited["pentest_authorization"], "missing")
        self.assertEqual(limited["execution"], "NOT_RUN")
        self.assertEqual(limited["outcome"], "BLOCKED")
        self.assertRegex(text, r"(?is)scanner.*does not.*(?:grant|become).*pentest")
        self.assertRegex(text, r"(?is)(?:never|do not).*expand.*scope")

    def test_automation_separates_interactive_cli_from_repeatable_suite(self) -> None:
        text = read_required(SPECIALISTS["qa-specialist-automation"])
        rows = parse_scenarios(
            text,
            (
                "scenario",
                "cli_availability",
                "session",
                "snapshot",
                "interaction",
                "capture",
                "repeatable_suite",
                "outcome",
            ),
        )
        ready = next(row for row in rows if row["scenario"] == "interactive-exploration")
        self.assertEqual(
            ready,
            {
                "scenario": "interactive-exploration",
                "cli_availability": "available",
                "session": "qa-report",
                "snapshot": "fresh",
                "interaction": "observed refs",
                "capture": "reviewed screenshot",
                "repeatable_suite": "Playwright Test",
                "outcome": "READY",
            },
        )
        self.assertRegex(text, r"(?is)playwright-cli.*interactive.*explor")
        self.assertRegex(text, r"(?is)Playwright Test.*repeatable.*CI")

    def test_automation_missing_cli_uses_probe_based_alternative(self) -> None:
        rows = parse_scenarios(
            read_required(SPECIALISTS["qa-specialist-automation"]),
            (
                "scenario",
                "cli_availability",
                "session",
                "snapshot",
                "interaction",
                "capture",
                "repeatable_suite",
                "outcome",
            ),
        )
        missing = next(row for row in rows if row["scenario"] == "missing-cli")
        self.assertEqual(missing["cli_availability"], "missing")
        self.assertEqual(missing["session"], "none")
        self.assertEqual(missing["snapshot"], "not run")
        self.assertEqual(missing["interaction"], "not run")
        self.assertEqual(missing["repeatable_suite"], "existing Web/UI test runner")
        self.assertEqual(missing["outcome"], "BLOCKED")

    def test_automation_flaky_result_requires_reproduction_not_rerun_until_pass(self) -> None:
        text = read_required(SPECIALISTS["qa-specialist-automation"])
        rows = parse_scenarios(
            text,
            (
                "scenario",
                "attempts",
                "evidence",
                "reproduction",
                "classification",
                "action",
                "outcome",
            ),
        )
        flaky = next(row for row in rows if row["scenario"] == "reproduced-flaky")
        self.assertEqual(
            flaky,
            {
                "scenario": "reproduced-flaky",
                "attempts": "three recorded under same conditions",
                "evidence": "failure and pass artifacts retained",
                "reproduction": "intermittent failure reproduced",
                "classification": "flaky",
                "action": "quarantine with owner and root-cause investigation",
                "outcome": "BLOCKED",
            },
        )
        self.assertRegex(text, r"(?is)do not.*rerun.*until.*pass")
        self.assertRegex(text, r"(?is)flaky.*evidence.*reproduc")

    def test_cicd_gate_uses_manifest_verdict_not_export_exit_code(self) -> None:
        text = read_required(SPECIALISTS["qa-specialist-cicd"])
        rows = parse_scenarios(
            text,
            (
                "scenario",
                "manifest_verdict",
                "export_exit_code",
                "export_status",
                "qa_gate",
                "pipeline_action",
            ),
        )
        self.assertEqual(
            rows,
            [
                {
                    "scenario": "qa-fail-exported",
                    "manifest_verdict": "FAIL",
                    "export_exit_code": "0",
                    "export_status": "complete",
                    "qa_gate": "FAIL",
                    "pipeline_action": "stop for QA failure",
                },
                {
                    "scenario": "qa-pass-export-failed",
                    "manifest_verdict": "PASS",
                    "export_exit_code": "3",
                    "export_status": "incomplete",
                    "qa_gate": "PASS",
                    "pipeline_action": "report export failure separately",
                },
            ],
        )
        self.assertRegex(text, r"(?is)manifest.*verdict.*(?:source|authoritative)")
        self.assertRegex(text, r"(?is)exit code.*does not.*QA.*verdict")


if __name__ == "__main__":
    unittest.main()
