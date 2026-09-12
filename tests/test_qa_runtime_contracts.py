"""Behavioural contract tests for PWDEV QA runtime capability mappings."""

import re
import unittest
from pathlib import Path
from typing import Dict, List


ROOT = Path(__file__).resolve().parents[1]
REFERENCES = ROOT / "plugins" / "pwdev-qa" / "references"
RUNTIMES = ("claude", "codex", "hermes")
CAPABILITIES = ("read", "write", "execute", "load_skill")


def read_mapping(runtime: str) -> str:
    path = REFERENCES / f"{runtime}-tools.md"
    if not path.is_file():
        raise AssertionError(f"required runtime mapping is missing: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


def parse_capabilities(text: str) -> Dict[str, Dict[str, str]]:
    match = re.search(
        r"(?ms)^## Capability mapping\n\n"
        r"\| capability \| candidate mechanisms \| fallback \| limitation \|\n"
        r"\|[- |]+\|\n(?P<rows>(?:\|[^\n]*\|\n)+)",
        text,
    )
    if not match:
        raise AssertionError("runtime contract has no parseable capability mapping")
    rows = {}
    for line in match.group("rows").splitlines():
        values = [cell.strip() for cell in line.strip("|").split("|")]
        if len(values) != 4:
            raise AssertionError(f"capability row has {len(values)} fields, expected 4")
        rows[values[0].strip("`")] = dict(
            zip(("mechanisms", "fallback", "limitation"), values[1:])
        )
    return rows


def observe_capability(
    runtime: str,
    capability: str,
    probe: Dict[str, str] = None,
) -> Dict[str, str]:
    mapping = parse_capabilities(read_mapping(runtime))[capability]
    if probe is None or probe["state"] == "not_run":
        status = "unverified"
        evidence = "probe not run"
    elif probe["state"] == "negative":
        status = "missing"
        evidence = probe["evidence"]
    elif probe["state"] == "positive" and probe.get("result") == "success":
        status = "available"
        evidence = probe["evidence"]
    else:
        status = "unverified"
        evidence = probe.get("evidence", "probe did not prove success")
    diagnostic = (
        f"runtime={runtime} capability={capability} status={status} evidence={evidence}; "
        f"limitation={mapping['limitation']}; fallback={mapping['fallback']}"
    )
    return {"status": status, "diagnostic": diagnostic}


def verify_runtime(runtime: str, probes: Dict[str, Dict[str, str]]) -> str:
    results = [
        observe_capability(runtime, capability, probes.get(capability))
        for capability in CAPABILITIES
    ]
    return "verified" if all(result["status"] == "available" for result in results) else "limited"


class QaRuntimeContractsTest(unittest.TestCase):
    def test_each_runtime_maps_all_required_capabilities_as_candidates(self) -> None:
        for runtime in RUNTIMES:
            with self.subTest(runtime=runtime):
                text = read_mapping(runtime)
                rows = parse_capabilities(text)
                self.assertEqual(tuple(rows), CAPABILITIES)
                self.assertRegex(text, r"(?is)candidate.*must be observed")
                self.assertRegex(text, r"(?is)names?.*not.*guarantee")
                for capability, row in rows.items():
                    with self.subTest(runtime=runtime, capability=capability):
                        self.assertTrue(row["mechanisms"])
                        self.assertTrue(row["fallback"])
                        self.assertTrue(row["limitation"])

    def test_missing_and_unverified_are_diagnostics_not_fictitious_execution(self) -> None:
        for runtime in RUNTIMES:
            with self.subTest(runtime=runtime, state="missing"):
                missing = observe_capability(
                    runtime,
                    "execute",
                    {"state": "negative", "result": "not found", "evidence": "negative probe"},
                )
                self.assertEqual(missing["status"], "missing")
                self.assertIn("status=missing", missing["diagnostic"])
                self.assertIn("negative probe", missing["diagnostic"])

            with self.subTest(runtime=runtime, state="unverified"):
                unverified = observe_capability(runtime, "execute")
                self.assertEqual(unverified["status"], "unverified")
                self.assertIn("status=unverified", unverified["diagnostic"])
                self.assertIn("probe not run", unverified["diagnostic"])

    def test_runtime_is_verified_only_after_real_success_for_every_capability(self) -> None:
        successful = {
            capability: {
                "state": "positive",
                "result": "success",
                "evidence": f"real smoke {capability} succeeded",
            }
            for capability in CAPABILITIES
        }
        for runtime in RUNTIMES:
            with self.subTest(runtime=runtime, result="verified"):
                self.assertEqual(verify_runtime(runtime, successful), "verified")
            with self.subTest(runtime=runtime, result="limited"):
                incomplete = dict(successful)
                incomplete.pop("load_skill")
                self.assertEqual(verify_runtime(runtime, incomplete), "limited")
                text = read_mapping(runtime)
                self.assertRegex(text, r"(?is)real smoke.*all four.*verified")

    def test_contracts_do_not_install_bypass_or_change_personal_configuration(self) -> None:
        texts: List[str] = [read_mapping(runtime) for runtime in RUNTIMES]
        combined = "\n".join(texts)
        self.assertRegex(combined, r"(?is)must not change personal configuration")
        self.assertRegex(combined, r"(?is)must not install")
        for forbidden in (
            "dangerously-bypass",
            "--yolo",
            "--ignore-rules",
            "--safe-mode",
            "claude --",
            "codex --",
            "hermes --",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, combined.lower())

    def test_hermes_registration_is_distinct_from_on_demand_loading(self) -> None:
        text = read_mapping("hermes")
        self.assertRegex(text, r"(?is)adapter.*`register_skill`.*`pathlib\.Path`")
        self.assertRegex(text, r"(?is)`register_skill`.*does not load")
        self.assertRegex(text, r"(?is)on-demand loading.*`skill_view`")
        self.assertEqual(parse_capabilities(text)["load_skill"]["mechanisms"], "`skill_view`")


if __name__ == "__main__":
    unittest.main()
