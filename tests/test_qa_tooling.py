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
        r"\| tool \| surface \| platform \| executable \| purpose \| prerequisites \| alternative \| reason \|\n"
        r"\|[- |]+\|\n(?P<rows>(?:\|[^\n]*\|\n)+)",
        text,
    )
    if not match:
        raise AssertionError("catalog has no parseable recommendation rules")
    rules = []
    for line in match.group("rows").splitlines():
        values = [cell.strip() for cell in line.strip("|").split("|")]
        if len(values) != 8:
            raise AssertionError(f"recommendation rule has {len(values)} fields, expected 8")
        rules.append(dict(zip(
            ("tool", "surface", "platform", "executable", "purpose", "prerequisites", "alternative", "reason"),
            values,
        )))
    return rules


def recommend(
    catalog: str,
    *,
    surface: str,
    platform: str,
    executables: dict[str, str],
) -> list[dict[str, str]]:
    output = []
    for rule in parse_rules(catalog):
        if rule["surface"] != surface or rule["platform"] not in ("any", platform):
            continue
        executable = rule["executable"]
        detected = executables.get(executable)
        output.append({
            "tool": rule["tool"],
            "purpose": rule["purpose"],
            "availability": "available" if detected else "missing",
            "evidence": f"command -v {executable} -> {detected or 'not found'}",
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
            executables={"playwright-cli": "/opt/bin/playwright-cli", "npx": "/usr/bin/npx"},
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
            executables={"appium": "/usr/local/bin/appium"},
        )
        self.assertEqual([row["tool"] for row in rows], ["Appium UiAutomator2"])
        self.assertEqual(rows[0]["availability"], "available")
        self.assertIn("Android", rows[0]["prerequisites"])

    def test_missing_cli_is_reported_without_installation_or_fictitious_execution(self) -> None:
        before = set(ROOT.rglob("*"))
        rows = recommend(
            read_required(CATALOG),
            surface="web",
            platform="linux",
            executables={"npx": "/usr/bin/npx"},
        )
        after = set(ROOT.rglob("*"))
        cli = next(row for row in rows if row["tool"] == "playwright-cli")
        self.assertEqual(cli["availability"], "missing")
        self.assertEqual(cli["evidence"], "command -v playwright-cli -> not found")
        self.assertTrue(cli["alternative"])
        self.assertEqual(before, after)

        skill = read_required(SKILL)
        self.assertRegex(skill, r"(?is)never install.*automatically")
        self.assertNotRegex(skill, r"(?m)^\s*(?:npm|npx|pip|brew|apt)\s+install\b")

    def test_current_claims_require_official_source_and_date_or_unverified(self) -> None:
        catalog = read_required(CATALOG)
        claims = re.findall(
            r"(?m)^\| ([^|]+) \| (version|compatibility|cost|license) \| "
            r"(verified|unverified) \| ([^|]+) \| ([^|]+) \|$",
            catalog,
        )
        self.assertTrue(claims)
        for tool, kind, status, source, checked_at in claims:
            with self.subTest(tool=tool.strip(), kind=kind):
                if status == "verified":
                    self.assertRegex(source, r"https://(?:playwright\.dev|github\.com/microsoft|appium\.io)/")
                    self.assertRegex(checked_at, r"^\d{4}-\d{2}-\d{2}\s*$")
                else:
                    self.assertEqual(source.strip(), "unverified")
                    self.assertEqual(checked_at.strip(), "unverified")

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
