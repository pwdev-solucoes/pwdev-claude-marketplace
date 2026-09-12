"""Deterministic behavioural scenarios for the first PWDEV QA specialists."""

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
            ("scenario", "platform", "tool", "sdk", "driver", "device", "outcome"),
        )
        ready = [row for row in rows if row["scenario"] == "platform-ready"]
        self.assertEqual(
            ready,
            [
                {
                    "scenario": "platform-ready",
                    "platform": "Android",
                    "tool": "Appium UiAutomator2",
                    "sdk": "available",
                    "driver": "available",
                    "device": "available emulator",
                    "outcome": "READY",
                },
                {
                    "scenario": "platform-ready",
                    "platform": "iOS",
                    "tool": "Appium XCUITest",
                    "sdk": "available",
                    "driver": "available",
                    "device": "available simulator",
                    "outcome": "READY",
                },
            ],
        )
        self.assertRegex(text, r"(?is)Android.*SDK.*driver.*device")
        self.assertRegex(text, r"(?is)iOS.*Xcode.*driver.*device")

    def test_mobile_missing_device_is_blocked_and_never_fabricated(self) -> None:
        rows = parse_scenarios(
            read_required(SPECIALISTS["qa-specialist-mobile"]),
            ("scenario", "platform", "tool", "sdk", "driver", "device", "outcome"),
        )
        limited = next(row for row in rows if row["scenario"] == "missing-device")
        self.assertEqual(limited["platform"], "Android")
        self.assertEqual(limited["device"], "missing")
        self.assertEqual(limited["outcome"], "BLOCKED")


if __name__ == "__main__":
    unittest.main()
