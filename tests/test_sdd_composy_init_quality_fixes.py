"""Init on existing repositories, OKF approval linting, QA applicability, and evidence export.

Each case reproduces a documented flow that the helpers refused or corrupted.
"""

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "sdd-composy"
SCRIPTS = PLUGIN / "scripts"
sys.path.insert(0, str(SCRIPTS))
import sdd_evidence  # noqa: E402
import sdd_okf  # noqa: E402
import sdd_qa  # noqa: E402


def init(root, command, *extra):
    options = list(extra)
    if command in {"plan", "apply"}:
        options += ["--lang", "en-US"]
    result = subprocess.run([sys.executable, str(SCRIPTS / "sdd_init.py"), command, str(root), "--actor", "agent:codex", *options],
                            capture_output=True, text=True)
    return result, json.loads(result.stdout)


class BrownfieldInitTests(unittest.TestCase):
    def test_repository_with_its_own_agents_md_initializes_and_verifies(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "AGENTS.md").write_text("# Team rules\n", encoding="utf-8")
            _, plan = init(root, "plan")
            self.assertEqual([c["path"] for c in plan["conflicts"]], ["AGENTS.md"])
            result, applied = init(root, "apply", "--plan-token", plan["plan_token"])
            self.assertEqual(result.returncode, 0, applied)
            self.assertTrue(applied["ok"])
            self.assertEqual(applied["preserved"], ["AGENTS.md"])
            self.assertEqual((root / "AGENTS.md").read_text(), "# Team rules\n")
            self.assertTrue((root / ".planning/sdd-composy/state.json").is_file())
            verified_result, verified = init(root, "verify")
            self.assertTrue(verified["state_ok"], verified)

    def test_unsafe_conflicts_still_block_the_init_state(self):
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as outside:
            root = Path(tmp)
            (root / ".agents").symlink_to(outside, target_is_directory=True)
            _, plan = init(root, "plan")
            result, applied = init(root, "apply", "--plan-token", plan["plan_token"])
            self.assertFalse(applied["ok"])
            self.assertFalse((root / ".planning/sdd-composy/state.json").exists())
            self.assertEqual(list(Path(outside).iterdir()), [], "init must not create rules through a symlinked .agents")

    def test_rerun_after_a_new_commit_does_not_conflict_with_its_own_agents_md(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            git = lambda *args: subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True)
            git("init", "-q"); git("config", "user.email", "t@example.invalid"); git("config", "user.name", "T")
            (root / "README").write_text("x\n"); git("add", "."); git("commit", "-qm", "first")
            init(root, "apply")
            (root / "README").write_text("y\n"); git("add", "."); git("commit", "-qm", "second")
            _, plan = init(root, "plan")
            self.assertEqual(plan["conflicts"], [])


class OkfApprovalLintTests(unittest.TestCase):
    META = {"type": "PRD", "generated": {"by": "agent:codex", "at": "2026-09-15T10:00:00Z"},
            "verified": [{"by": "human:paulo", "at": "2026-09-15T11:00:00Z"}]}

    def test_human_approval_by_someone_else_is_valid(self):
        self.assertEqual(sdd_okf.validate_frontmatter(self.META, actor="agent:codex"), [])

    def test_generating_actor_cannot_approve_its_own_document(self):
        meta = {**self.META, "verified": [{"by": "agent:codex", "at": "2026-09-15T11:00:00Z"}]}
        self.assertTrue(any("approve" in error for error in sdd_okf.validate_frontmatter(meta, actor="agent:codex")))

    def test_generated_actor_must_match(self):
        meta = {**self.META, "generated": {"by": "agent:other", "at": "2026-09-15T10:00:00Z"}}
        self.assertTrue(any("generated actor mismatch" in error for error in sdd_okf.validate_frontmatter(meta, actor="agent:codex")))


class QaApplicabilityTests(unittest.TestCase):
    def payload(self):
        not_applicable = lambda why: {"status": "NOT_APPLICABLE", "justification": why}
        return {
            "state": "qa_required", "human_approved": True, "task_id": "TASK-001",
            "acceptance": [{"id": "CA-001", "story": "SC-001", "tests": ["TU-001"]}],
            "results": {"unit": {"status": "passed", "command": "python3 -m unittest", "environment": "local",
                                 "exit_code": 0, "evidence": "evidence/unit.log"},
                        "integration": not_applicable("no external boundary"),
                        "e2e": not_applicable("command-line tool without a user interface")},
            "browser": {"available": False},
            "accessibility": not_applicable("no user interface"),
            "responsiveness": not_applicable("no user interface"),
            "environment": {"ready": True, "runtime": "python3", "versions": {"app": "1"}, "cleanup": "cleaned"},
            "regression": {"status": "passed", "evidence": "evidence/unit.log"},
            "evidence": [{"path": "evidence/unit.log", "type": "log", "result": "passed", "summary": "unit run", "source": "unit"}],
        }

    def root(self, tmp):
        root = Path(tmp); (root / "evidence").mkdir(); (root / "evidence/unit.log").write_text("ok\n")
        return root

    def test_backend_task_with_justified_not_applicable_levels_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = sdd_qa.assess(self.payload(), evidence_root=self.root(tmp))
            self.assertEqual((report["status"], report["transition"]), ("APPROVED", "evidence_required"), report)

    def test_not_applicable_without_justification_is_rejected(self):
        for field in ("integration", "e2e"):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as tmp:
                payload = self.payload(); payload["results"][field] = {"status": "NOT_APPLICABLE"}
                self.assertEqual(sdd_qa.assess(payload, evidence_root=self.root(tmp))["reason"], f"{field}_failed")
        with tempfile.TemporaryDirectory() as tmp:
            payload = self.payload(); payload["accessibility"] = {"status": "NOT_APPLICABLE", "justification": ""}
            self.assertEqual(sdd_qa.assess(payload, evidence_root=self.root(tmp))["reason"], "accessibility_failed")

    def test_executed_e2e_still_requires_a_browser(self):
        with tempfile.TemporaryDirectory() as tmp:
            payload = self.payload()
            payload["results"]["e2e"] = {"status": "passed", "command": "npx playwright test", "environment": "local",
                                         "exit_code": 0, "evidence": "evidence/unit.log"}
            self.assertEqual(sdd_qa.assess(payload, evidence_root=self.root(tmp))["reason"], "browser_unavailable")

    def test_persisted_report_has_iso_timestamps_and_valid_okf_frontmatter(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.root(tmp)
            import sdd_language
            sdd_language.persist_language(root, "en-US")
            sdd_qa.assess(self.payload(), evidence_root=root, report_path="qa/qa-TASK-001.md", allowed_root=root,
                          generated_by="agent:codex", verified_by="human:paulo")
            meta, _ = sdd_okf.parse_frontmatter((root / "qa/qa-TASK-001.md").read_text(encoding="utf-8"))
            self.assertEqual(sdd_okf.validate_frontmatter(meta, actor="agent:codex"), [])


class EvidenceExportTests(unittest.TestCase):
    ENTRY = {"requirement_id": "RF-001", "story_id": "US-001", "scenario_id": "SC-001", "criterion_id": "CA-001",
             "test_id": "TEST-001", "result": "passed", "evidence_type": "log", "path": "unit.log"}

    def test_export_writes_the_report_into_the_prd_bundle_and_finds_the_workspace(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            import sdd_language
            sdd_language.persist_language(workspace, "en-US")
            bundle = workspace / "tasks/prd-demo"; evidences = bundle / "evidences"; evidences.mkdir(parents=True)
            (evidences / "unit.log").write_text("ok\n")
            manifest = evidences / "manifest.json"
            sdd_evidence.build({"prd_slug": "demo", "task_id": "TASK-001", "entries": [self.ENTRY]}, evidences, manifest,
                               generated_at="2026-09-15T10:00:00-03:00")
            output = bundle / "evidence-report.html"
            result = subprocess.run([sys.executable, str(SCRIPTS / "sdd_evidence.py"), "export", str(manifest),
                                     str(evidences), str(output)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue(output.is_file())
            outside = workspace / "report.html"
            refused = subprocess.run([sys.executable, str(SCRIPTS / "sdd_evidence.py"), "export", str(manifest),
                                      str(evidences), str(outside)], capture_output=True, text=True)
            self.assertNotEqual(refused.returncode, 0)

    def test_verify_requires_hashes_and_schema_version(self):
        with tempfile.TemporaryDirectory() as tmp:
            evidences = Path(tmp); (evidences / "unit.log").write_text("ok\n")
            built = sdd_evidence.build({"prd_slug": "demo", "task_id": "TASK-001", "entries": [self.ENTRY]}, evidences)
            self.assertTrue(sdd_evidence.verify(built, evidences)["ok"])
            unhashed = json.loads(json.dumps(built)); del unhashed["entries"][0]["sha256"]
            self.assertFalse(sdd_evidence.verify(unhashed, evidences)["ok"])
            self.assertFalse(sdd_evidence.verify({**built, "schema_version": "9"}, evidences)["ok"])


class StatusFleetActivityTests(unittest.TestCase):
    def test_a_fleet_whose_members_all_completed_is_not_current_activity(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); members = root / ".planning/sdd-composy/fleet/demo/members"; members.mkdir(parents=True)
            (members / "TASK-001.json").write_text(json.dumps({"id": "TASK-001", "status": "completed"}))
            status = subprocess.run([sys.executable, str(SCRIPTS / "sdd_status.py"), str(root), "--json"], capture_output=True, text=True)
            self.assertNotEqual(json.loads(status.stdout)["status"], "fleet")


if __name__ == "__main__":
    unittest.main()
