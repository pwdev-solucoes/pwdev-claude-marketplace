"""Behavioural contract tests for the PWDEV QA router and shared references."""

import re
import stat
import tempfile
import unittest
from pathlib import Path
from typing import Optional


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "pwdev-qa"
SKILL = PLUGIN / "skills" / "qa" / "SKILL.md"
REFERENCES = PLUGIN / "references"


def read_required(path: Path) -> str:
    if not path.is_file():
        raise AssertionError(f"required QA contract is missing: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


def parse_routes(text: str) -> dict[str, str]:
    rows = re.findall(r"(?m)^\| ([a-z ]+) \| `(qa-[a-z-]+)` \|$", text)
    if not rows:
        raise AssertionError("router table has no parseable routes")
    return dict(rows)


def resolve_route(
    text: str,
    plugin_root: Path,
    explicit_intent: Optional[str] = None,
    surface_intent: Optional[str] = None,
    risk_intent: Optional[str] = None,
) -> str:
    intent = explicit_intent or surface_intent or risk_intent
    if intent is None:
        raise ValueError("routing intent is missing")
    try:
        candidate = parse_routes(text)[intent]
    except KeyError as error:
        raise ValueError(f"unsupported intent: {intent}") from error

    skill_file = plugin_root / "skills" / candidate / "SKILL.md"
    try:
        mode = skill_file.lstat().st_mode
    except FileNotFoundError as error:
        raise ValueError(f"route is unavailable: {candidate}") from error
    if skill_file.is_symlink() or not stat.S_ISREG(mode):
        raise ValueError(f"route is not a regular installed skill: {candidate}")
    return candidate


def parse_workflow_modes(text: str) -> dict[str, str]:
    rows = re.findall(
        r"(?m)^\| `(qa-[a-z-]+)` \| `(read-only|observe|write|execute|export)` \| [^\n]+\|$",
        text,
    )
    if not rows:
        raise AssertionError("workflow table has no parseable operation modes")
    return dict(rows)


def snapshot_tree(root: Path) -> tuple[tuple[str, bytes], ...]:
    return tuple(
        (str(path.relative_to(root)), path.read_bytes())
        for path in sorted(root.rglob("*"))
        if path.is_file() and not path.is_symlink()
    )


def inspect_read_only(text: str, route: str, state_root: Path) -> tuple[tuple[str, bytes], ...]:
    if parse_workflow_modes(text).get(route) != "read-only":
        raise ValueError(f"workflow is not read-only: {route}")
    return snapshot_tree(state_root)


def evaluate_empty_criteria(
    text: str, criteria: Optional[list[dict[str, bool]]]
) -> str:
    if criteria is None:
        match = re.search(r"Missing criteria are `([A-Z_]+)`", text)
    elif not any(criterion["applicable"] for criterion in criteria):
        match = re.search(r"Zero applicable criteria are `([A-Z_]+)`", text)
    else:
        raise ValueError("fixture only evaluates missing or zero-applicable criteria")
    if not match:
        raise AssertionError("criteria fallback is not machine-readable")
    return match.group(1)


class QaCoreContractTest(unittest.TestCase):
    def test_router_selects_by_explicit_intent_then_surface_and_risk(self) -> None:
        text = read_required(SKILL)
        with tempfile.TemporaryDirectory() as directory:
            plugin_root = Path(directory)
            skill_file = plugin_root / "skills" / "qa-review" / "SKILL.md"
            skill_file.parent.mkdir(parents=True)
            skill_file.write_text("---\nname: qa-review\n---\n", encoding="utf-8")

            # Explicit review wins even when hypothetical surface/risk hints could suggest report.
            self.assertEqual(
                resolve_route(
                    text,
                    plugin_root,
                    explicit_intent="review",
                    surface_intent="report",
                    risk_intent="release",
                ),
                "qa-review",
            )

    def test_router_refuses_a_route_whose_skill_is_not_installed(self) -> None:
        text = read_required(SKILL)
        with tempfile.TemporaryDirectory() as directory:
            plugin_root = Path(directory)
            skill_file = plugin_root / "skills" / "qa-review" / "SKILL.md"

            with self.subTest(kind="missing"):
                with self.assertRaisesRegex(ValueError, "unavailable"):
                    resolve_route(text, plugin_root, explicit_intent="review")

            with self.subTest(kind="directory"):
                skill_file.mkdir(parents=True)
                with self.assertRaisesRegex(ValueError, "not a regular"):
                    resolve_route(text, plugin_root, explicit_intent="review")
                skill_file.rmdir()

            with self.subTest(kind="symlink"):
                target = plugin_root / "real-skill.md"
                target.write_text("skill", encoding="utf-8")
                skill_file.parent.mkdir(parents=True, exist_ok=True)
                skill_file.symlink_to(target)
                with self.assertRaisesRegex(ValueError, "not a regular"):
                    resolve_route(text, plugin_root, explicit_intent="review")

    def test_review_and_status_are_strictly_read_only(self) -> None:
        workflow = read_required(REFERENCES / "workflow.md")
        with tempfile.TemporaryDirectory() as directory:
            state_root = Path(directory)
            (state_root / "nested").mkdir()
            (state_root / "state.json").write_bytes(b'{"status":"BLOCKED"}\n')
            (state_root / "nested" / "evidence.txt").write_bytes(b"observed\x00bytes\n")
            before = snapshot_tree(state_root)

            for route in ("qa-review", "qa-status"):
                with self.subTest(route=route):
                    observed = inspect_read_only(workflow, route, state_root)
                    self.assertEqual(observed, before)
                    self.assertEqual(snapshot_tree(state_root), before)

    def test_missing_or_zero_applicable_criteria_is_blocked(self) -> None:
        workflow = read_required(REFERENCES / "workflow.md")
        self.assertEqual(evaluate_empty_criteria(workflow, None), "BLOCKED")
        self.assertEqual(evaluate_empty_criteria(workflow, []), "BLOCKED")
        self.assertEqual(
            evaluate_empty_criteria(workflow, [{"applicable": False}, {"applicable": False}]),
            "BLOCKED",
        )

    def test_shared_status_and_verdict_contract_is_exact(self) -> None:
        workflow = read_required(REFERENCES / "workflow.md")
        self.assertIn("`PASS`, `FAIL`, `BLOCKED`, `NOT_RUN`, `NOT_APPLICABLE`", workflow)
        self.assertIn("Global verdicts are exactly `PASS`, `FAIL`, or `BLOCKED`", workflow)
        self.assertRegex(workflow, r"(?is)proven.*in-scope.*failure.*`FAIL`")
        self.assertRegex(workflow, r"(?is)`PASS`.*all applicable.*absence of.*current defects")

    def test_privileged_operations_require_explicit_authorization(self) -> None:
        safety = read_required(REFERENCES / "safety.md")
        for operation in ("load", "penetration testing", "production", "external effects"):
            with self.subTest(operation=operation):
                self.assertRegex(safety, rf"(?is){operation}.*explicit authorization")
        self.assertRegex(safety, r"(?is)product corrections.*only.*requested")
        self.assertRegex(safety, r"(?is)report.*must not execute.*evidence commands")

    def test_evidence_contract_is_confined_and_verifiable(self) -> None:
        artifacts = read_required(REFERENCES / "artifacts.md")
        for phrase in (
            "regular local file",
            "repository-relative",
            "symlink",
            "SHA-256",
            "target",
            "contract",
            "sanitization review",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase.lower(), artifacts.lower())

    def test_pending_sanitization_requires_an_explicit_diagnostic(self) -> None:
        artifacts = read_required(REFERENCES / "artifacts.md")
        self.assertRegex(
            artifacts,
            r"(?is)pending sanitization review[^.]*(?:produce|record|emit)[^.]*diagnostic",
        )

    def test_skill_has_complete_contract_and_all_local_links_resolve(self) -> None:
        text = read_required(SKILL)
        self.assertRegex(text, r"(?s)^---\nname: qa\ndescription: .+?\n---\n")
        for section in ("Inputs", "Procedure", "Output", "Failure modes", "Safety", "Related skills"):
            self.assertIn(f"## {section}", text)

        markdown_files = [SKILL, *(REFERENCES / name for name in ("workflow.md", "safety.md", "artifacts.md"))]
        for source in markdown_files:
            source_text = read_required(source)
            for target in re.findall(r"\[[^\]]+\]\(([^)#]+\.md)\)", source_text):
                with self.subTest(source=source.name, target=target):
                    self.assertTrue((source.parent / target).resolve().is_file())


if __name__ == "__main__":
    unittest.main()
