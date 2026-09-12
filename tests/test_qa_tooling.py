"""Deterministic behavioural scenarios for the qa-tooling recommendation contract."""

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "plugins" / "pwdev-qa" / "skills" / "qa-tooling" / "SKILL.md"
CATALOG = ROOT / "plugins" / "pwdev-qa" / "references" / "tooling.md"
OUTPUT_FIELDS = (
    "tool",
    "purpose",
    "availability",
    "evidence",
    "prerequisites",
    "alternative",
    "reason",
)


def read_required(path: Path) -> str:
    if not path.is_file():
        raise AssertionError(f"required QA tooling contract is missing: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


def parse_rules(text: str) -> list[dict[str, str]]:
    match = re.search(
        r"(?ms)^## Recommendation rules\n\n"
        r"\| tool \| surface \| platform \| tool probe \| required probes \| purpose \| prerequisites \| alternative \| reason \|\n"
        r"\|[- |]+\|\n(?P<rows>(?:\|[^\n]*\|\n)+)",
        text,
    )
    if not match:
        raise AssertionError("catalog has no parseable recommendation rules")
    rules = []
    for line in match.group("rows").splitlines():
        values = [cell.strip() for cell in line.strip("|").split("|")]
        if len(values) != 9:
            raise AssertionError(f"recommendation rule has {len(values)} fields, expected 9")
        rules.append(dict(zip(
            (
                "tool", "surface", "platform", "tool_probe", "required_probes",
                "purpose", "prerequisites", "alternative", "reason",
            ),
            values,
        )))
    return rules


def recommend(
    catalog: str,
    *,
    surface: str,
    platform: str,
    probes: dict[str, dict[str, str]],
) -> list[dict[str, str]]:
    output = []
    for rule in parse_rules(catalog):
        if rule["surface"] != surface or rule["platform"] not in ("any", platform):
            continue
        required = [name.strip() for name in rule["required_probes"].split(",")]
        observed = {name: probes[name] for name in required if name in probes}
        for name, probe in observed.items():
            if set(probe) != {"state", "result", "evidence"}:
                raise ValueError(f"probe {name} must contain state/result/evidence")
            if probe["state"] not in {"positive", "negative", "not_run"}:
                raise ValueError(f"probe {name} has invalid state")

        tool_probe = probes.get(rule["tool_probe"])
        if tool_probe and tool_probe["state"] == "negative":
            availability = "missing"
        elif all(
            name in probes and probes[name]["state"] == "positive"
            for name in required
        ):
            availability = "available"
        else:
            availability = "unverified"

        evidence = "; ".join(
            probes[name]["evidence"] if name in probes else f"probe {name} -> not provided"
            for name in required
        )
        output.append({
            "tool": rule["tool"],
            "purpose": rule["purpose"],
            "availability": availability,
            "evidence": evidence,
            "prerequisites": rule["prerequisites"],
            "alternative": rule["alternative"],
            "reason": rule["reason"],
        })
    return output


class QaToolingBehaviourTest(unittest.TestCase):
    def test_web_fixture_separates_exploration_from_repeatable_ci_suite(self) -> None:
        rows = recommend(
            read_required(CATALOG),
            surface="web",
            platform="linux",
            probes={
                "playwright-cli": {"state": "positive", "result": "1.2.3", "evidence": "playwright-cli --version -> 1.2.3"},
                "node": {"state": "positive", "result": "20.1", "evidence": "node --version -> 20.1"},
                "browser": {"state": "positive", "result": "chromium", "evidence": "configured browser -> chromium"},
                "playwright-test": {"state": "positive", "result": "1.2.3", "evidence": "npx --no-install playwright --version -> 1.2.3"},
                "browsers": {"state": "positive", "result": "chromium", "evidence": "project browsers -> chromium"},
            },
        )
        by_tool = {row["tool"]: row for row in rows}
        self.assertEqual(set(by_tool), {"playwright-cli", "Playwright Test"})
        self.assertIn("exploratory", by_tool["playwright-cli"]["purpose"].lower())
        self.assertNotIn("repeatable suite", by_tool["playwright-cli"]["purpose"].lower())
        self.assertIn("repeatable suite", by_tool["Playwright Test"]["purpose"].lower())
        self.assertIn("CI", by_tool["Playwright Test"]["purpose"])
        self.assertTrue(all(tuple(row) == OUTPUT_FIELDS for row in rows))

    def test_android_mobile_fixture_returns_only_platform_compatible_option(self) -> None:
        rows = recommend(
            read_required(CATALOG),
            surface="mobile",
            platform="android",
            probes={
                "appium": {"state": "positive", "result": "present", "evidence": "appium --version -> present"},
                "uiautomator2-driver": {"state": "positive", "result": "installed", "evidence": "appium driver list -> uiautomator2 installed"},
                "android-sdk": {"state": "positive", "result": "configured", "evidence": "Android SDK -> configured"},
                "adb": {"state": "positive", "result": "/opt/adb", "evidence": "command -v adb -> /opt/adb"},
                "android-device": {"state": "positive", "result": "emulator-5554", "evidence": "adb devices -> emulator-5554"},
            },
        )
        self.assertEqual([row["tool"] for row in rows], ["Appium UiAutomator2"])
        self.assertEqual(rows[0]["availability"], "available")
        self.assertIn("Android", rows[0]["prerequisites"])

    def test_missing_cli_requires_an_explicit_negative_probe(self) -> None:
        before = set(ROOT.rglob("*"))
        rows = recommend(
            read_required(CATALOG),
            surface="web",
            platform="linux",
            probes={
                "playwright-cli": {
                    "state": "negative",
                    "result": "not found",
                    "evidence": "playwright-cli --version -> command not found",
                },
            },
        )
        after = set(ROOT.rglob("*"))
        cli = next(row for row in rows if row["tool"] == "playwright-cli")
        self.assertEqual(cli["availability"], "missing")
        self.assertIn("playwright-cli --version -> command not found", cli["evidence"])
        self.assertTrue(cli["alternative"])
        self.assertEqual(before, after)

        skill = read_required(SKILL)
        self.assertRegex(skill, r"(?is)never install.*automatically")
        self.assertNotRegex(skill, r"(?m)^\s*(?:npm|npx|pip|brew|apt)\s+install\b")

    def test_absent_probe_is_unverified_and_partial_prerequisites_never_mean_available(self) -> None:
        catalog = read_required(CATALOG)
        web = recommend(catalog, surface="web", platform="linux", probes={})
        cli = next(row for row in web if row["tool"] == "playwright-cli")
        self.assertEqual(cli["availability"], "unverified")
        self.assertIn("probe playwright-cli -> not provided", cli["evidence"])
        self.assertNotIn("command not found", cli["evidence"])

        mobile = recommend(
            catalog,
            surface="mobile",
            platform="android",
            probes={
                "appium": {"state": "positive", "result": "present", "evidence": "appium --version -> present"},
            },
        )
        self.assertEqual(mobile[0]["availability"], "unverified")
        for missing_prerequisite in ("uiautomator2-driver", "android-sdk", "adb", "android-device"):
            self.assertIn(f"probe {missing_prerequisite} -> not provided", mobile[0]["evidence"])

    def test_current_claims_require_official_source_and_date_or_unverified(self) -> None:
        catalog = read_required(CATALOG)
        claims = re.findall(
            r"(?m)^\| ([^|]+) \| (version|compatibility|cost|license) \| "
            r"(verified|unverified) \| ([^|]+) \| ([^|]+) \|$",
            catalog,
        )
        self.assertTrue(claims)
        rules_by_tool = {rule["tool"]: rule for rule in parse_rules(catalog)}
        for tool, kind, status, source, checked_at in claims:
            tool = tool.strip()
            source = source.strip()
            checked_at = checked_at.strip()
            with self.subTest(tool=tool, kind=kind):
                if status == "verified":
                    self.assertRegex(source, r"https://(?:playwright\.dev|github\.com/microsoft|appium\.io)/")
                    self.assertRegex(checked_at, r"^\d{4}-\d{2}-\d{2}$")
                    self.assertIn(source, rules_by_tool[tool]["prerequisites"])
                    self.assertIn(f"checked {checked_at}", rules_by_tool[tool]["prerequisites"])
                else:
                    self.assertEqual(source, "unverified")
                    self.assertEqual(checked_at, "unverified")

        rows = recommend(
            catalog,
            surface="mobile",
            platform="android",
            probes={},
        )
        self.assertEqual(tuple(rows[0]), OUTPUT_FIELDS)
        self.assertIn("https://appium.io/docs/en/latest/intro/drivers/", rows[0]["prerequisites"])
        self.assertIn("checked 2026-09-12", rows[0]["prerequisites"])

    def test_documented_local_playwright_fallback_does_not_install(self) -> None:
        skill = read_required(SKILL)
        self.assertIn("npx --no-install playwright --version", skill)
        self.assertIn("npx playwright cli", skill)
        self.assertNotIn("npx --no-install playwright-cli --version", skill)

    def test_skill_contract_and_catalog_cover_all_qa_surfaces(self) -> None:
        skill = read_required(SKILL)
        self.assertRegex(skill, r"(?s)^---\nname: qa-tooling\ndescription: .+?\n---\n")
        for section in ("Inputs", "Procedure", "Output", "Failure modes", "Safety", "Related skills"):
            self.assertIn(f"## {section}", skill)
        self.assertIn("[Tooling catalog](../../references/tooling.md)", skill)

        catalog = read_required(CATALOG)
        for surface in (
            "Web/UI", "API", "mobile", "data", "accessibility", "performance",
            "security", "automation/CI", "observability", "export",
        ):
            with self.subTest(surface=surface):
                self.assertIn(surface.lower(), catalog.lower())


if __name__ == "__main__":
    unittest.main()
