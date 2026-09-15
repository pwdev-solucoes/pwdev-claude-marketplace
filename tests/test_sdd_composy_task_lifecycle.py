"""Task lifecycle driven only through the documented CLIs, from the packaged template.

Earlier tests injected evidence through the Python API and used fixtures that the
template could not produce, so the documented flow could not get past `qa_required`.
"""

import datetime as dt
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "sdd-composy"
SCRIPTS = PLUGIN / "scripts"
sys.path.insert(0, str(SCRIPTS))
import sdd_execute  # noqa: E402
import sdd_sync  # noqa: E402
import sdd_tasks  # noqa: E402

UTC = dt.timezone.utc


def render_task(task_id="TASK-001", title="Add the export button", dependencies=()):
    text = (PLUGIN / "templates" / "task.md").read_text(encoding="utf-8")
    text = text.replace("id: TASK-001", f"id: {task_id}").replace("# TASK-001", f"# {task_id}")
    text = text.replace("dependencies: []", "dependencies: [" + ", ".join(dependencies) + "]")
    values = {"SLUG": "demo", "ACTOR_ID": "agent:codex", "GENERATED_AT": "2026-09-15T10:00:00Z",
              "TASK_TITLE": title}
    return re.sub(r"\{\{([A-Z_]+)\}\}", lambda m: values[m.group(1)], text)


class TaskCli:
    def __init__(self, test, repo):
        self.test, self.repo = test, repo
        self.state = repo / ".planning/sdd-composy/tasks/demo.json"

    def run(self, *args, ok=True):
        completed = subprocess.run([sys.executable, str(SCRIPTS / "sdd_tasks.py"), *args],
                                   cwd=self.repo, capture_output=True, text=True)
        if ok:
            self.test.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            return json.loads(completed.stdout)
        self.test.assertNotEqual(completed.returncode, 0, completed.stdout)
        return completed

    def task(self, task_id="TASK-001"):
        return next(t for t in json.loads(self.state.read_text())["tasks"] if t["id"] == task_id)


class LifecycleFixture(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name).resolve()
        self.bundle = self.repo / "tasks/prd-demo"
        self.bundle.mkdir(parents=True)
        self.cli = TaskCli(self, self.repo)

    def tearDown(self):
        self.tmp.cleanup()

    def write_task(self, task_id="TASK-001", **kwargs):
        (self.bundle / f"task-{task_id[-3:]}.md").write_text(render_task(task_id, **kwargs), encoding="utf-8")

    def imported(self):
        return self.cli.run("import", str(self.bundle), str(self.cli.state))


class TemplateImportTests(LifecycleFixture):
    def test_task_rendered_from_the_template_imports(self):
        self.write_task(title="Add the export button")
        result = self.imported()
        self.assertEqual(result["tasks"][0]["title"], "Add the export button")
        self.assertEqual(result["tasks"][0]["state"], "pending")


class CliLifecycleTests(LifecycleFixture):
    def advance_to(self, target):
        self.write_task(); self.imported()
        steps = [("transition", "ready"), ("start",), ("evidence", "tests", "passed"),
                 ("transition", "qa_required"), ("evidence", "qa", "passed"),
                 ("transition", "evidence_required"), ("transition", "review_required"),
                 ("evidence", "review", "approved"), ("transition", "verify_required"),
                 ("evidence", "verify", "approved"), ("evidence", "trace", "consistent"),
                 ("transition", "complete")]
        for step in steps:
            if step[0] == "transition":
                self.cli.run("transition", str(self.cli.state), "TASK-001", step[1])
            elif step[0] == "start":
                self.cli.run("start", str(self.cli.state), "TASK-001")
            else:
                self.cli.run("evidence", str(self.cli.state), "TASK-001", step[1], "--status", step[2])
            if self.cli.task()["state"] == target:
                return

    def test_documented_cli_reaches_complete(self):
        self.advance_to("verify_required")
        self.cli.run("evidence", str(self.cli.state), "TASK-001", "verify", "--status", "approved")
        self.cli.run("evidence", str(self.cli.state), "TASK-001", "trace", "--status", "consistent")
        report = self.cli.run("verify", str(self.cli.state))
        self.assertTrue(report["completion_permitted"])
        self.cli.run("transition", str(self.cli.state), "TASK-001", "complete")
        self.assertEqual(self.cli.task()["state"], "complete")

    def test_evidence_records_reference_and_rejects_unknown_kind_or_status(self):
        self.advance_to("running")
        self.cli.run("evidence", str(self.cli.state), "TASK-001", "tests", "--status", "passed",
                     "--ref", "tasks/prd-demo/evidences/unit.txt")
        record = self.cli.task()["evidence"]["tests"]
        self.assertEqual(record["ref"], "tasks/prd-demo/evidences/unit.txt")
        self.assertTrue(record["timestamp"].endswith("Z"))
        self.cli.run("evidence", str(self.cli.state), "TASK-001", "vibes", "--status", "passed", ok=False)
        self.cli.run("evidence", str(self.cli.state), "TASK-001", "tests", "--status", "great", ok=False)
        self.cli.run("evidence", str(self.cli.state), "TASK-001", "tests", "--status", "passed",
                     "--ref", "../outside.txt", ok=False)

    def test_documented_rejections_and_blocks_are_legal_with_a_reason(self):
        for source, target in (("qa_required", "rejected"), ("evidence_required", "rejected"),
                               ("ready", "blocked"), ("ready", "rejected")):
            with self.subTest(source=source, target=target):
                self.tearDown(); self.setUp()
                self.advance_to(source)
                self.assertEqual(self.cli.task()["state"], source)
                self.cli.run("transition", str(self.cli.state), "TASK-001", target, ok=False)
                self.cli.run("transition", str(self.cli.state), "TASK-001", target, "--reason", "QA found a blocker")
                self.assertEqual(self.cli.task()["state"], target)

    def test_skip_through_cli_requires_reason_and_authority(self):
        self.advance_to("ready")
        self.cli.run("transition", str(self.cli.state), "TASK-001", "skipped", "--reason", "obsolete", ok=False)
        self.cli.run("transition", str(self.cli.state), "TASK-001", "skipped", "--reason", "obsolete",
                     "--authority", "human:product-owner")
        self.assertEqual(self.cli.task()["skip_authority"], "human:product-owner")


class FreshnessTests(unittest.TestCase):
    def data(self):
        base = {"dependencies": [], "acceptance_criteria": ["CA-001"], "verification_commands": ["true"],
                "allowed_paths": ["src"], "evidence_required": False}
        return {"schema_version": "1", "prd_slug": "demo", "updated_at": "2026-01-01T00:00:00Z", "tasks": [
            {**base, "id": "TASK-001", "title": "one", "state": "ready"},
            {**base, "id": "TASK-002", "title": "two", "state": "ready"}]}

    def test_another_task_changing_does_not_stale_this_task_evidence(self):
        data = self.data()
        sdd_tasks.transition(data, "TASK-001", "running", now=dt.datetime(2026, 1, 2, 9, tzinfo=UTC))
        sdd_tasks.record_evidence(data, "TASK-001", "tests", "passed", now=dt.datetime(2026, 1, 2, 10, tzinfo=UTC))
        sdd_tasks.transition(data, "TASK-002", "running", now=dt.datetime(2026, 1, 2, 11, tzinfo=UTC))
        sdd_tasks.transition(data, "TASK-001", "qa_required", now=dt.datetime(2026, 1, 2, 12, tzinfo=UTC))
        sdd_tasks.transition(data, "TASK-001", "evidence_required", now=dt.datetime(2026, 1, 2, 12, tzinfo=UTC))
        self.assertEqual(data["tasks"][0]["state"], "evidence_required")

    def test_evidence_from_a_previous_attempt_is_stale_for_verify_and_complete_alike(self):
        data = self.data()
        task = data["tasks"][0]
        sdd_tasks.transition(data, "TASK-001", "running", now=dt.datetime(2026, 1, 2, 9, tzinfo=UTC))
        for kind, status in (("tests", "passed"), ("qa", "passed"), ("review", "approved"),
                             ("verify", "approved"), ("trace", "consistent")):
            sdd_tasks.record_evidence(data, "TASK-001", kind, status, now=dt.datetime(2026, 1, 2, 10, tzinfo=UTC))
        # Rejected and restarted: the first attempt's evidence no longer counts.
        task["state"] = "verify_required"
        sdd_tasks.transition(data, "TASK-001", "rejected", reason="verification failed",
                             now=dt.datetime(2026, 1, 3, tzinfo=UTC))
        sdd_tasks.transition(data, "TASK-001", "ready", now=dt.datetime(2026, 1, 3, 1, tzinfo=UTC))
        sdd_tasks.transition(data, "TASK-001", "running", now=dt.datetime(2026, 1, 3, 2, tzinfo=UTC))
        task["state"] = "verify_required"
        report = sdd_tasks.verify(data, now=dt.datetime(2026, 1, 3, 3, tzinfo=UTC))
        self.assertFalse(report["completion_permitted"])
        with self.assertRaisesRegex(sdd_tasks.TaskError, "stale"):
            sdd_tasks.transition(data, "TASK-001", "complete", now=dt.datetime(2026, 1, 3, 3, tzinfo=UTC))

    def test_import_keeps_recorded_evidence_valid(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp).resolve(); bundle = repo / "tasks/prd-demo"; bundle.mkdir(parents=True)
            (bundle / "task-001.md").write_text(render_task(), encoding="utf-8")
            state = repo / ".planning/sdd-composy/tasks/demo.json"
            sdd_tasks.import_tasks(bundle, state, now=dt.datetime(2026, 1, 1, tzinfo=UTC))
            data = sdd_tasks.load(state)
            sdd_tasks.transition(data, "TASK-001", "ready", now=dt.datetime(2026, 1, 2, 8, tzinfo=UTC))
            sdd_tasks.transition(data, "TASK-001", "running", now=dt.datetime(2026, 1, 2, 9, tzinfo=UTC))
            sdd_tasks.record_evidence(data, "TASK-001", "tests", "passed", now=dt.datetime(2026, 1, 2, 10, tzinfo=UTC))
            sdd_tasks._atomic_write(state, data)
            sdd_tasks.import_tasks(bundle, state, now=dt.datetime(2026, 1, 5, tzinfo=UTC))
            data = sdd_tasks.load(state)
            sdd_tasks.transition(data, "TASK-001", "qa_required", now=dt.datetime(2026, 1, 5, 1, tzinfo=UTC))
            sdd_tasks.transition(data, "TASK-001", "evidence_required", now=dt.datetime(2026, 1, 5, 1, tzinfo=UTC))


class ExecutePreflightTests(unittest.TestCase):
    def test_preflight_resolves_dependency_ids_from_the_projection(self):
        tasks = [{"id": "TASK-001", "state": "complete"}, {"id": "TASK-002", "state": "running"}]
        task = {"id": "TASK-003", "state": "ready", "dependencies": ["TASK-001"], "allowed_paths": ["src"]}
        result = sdd_execute.preflight(task, tasks=tasks, red_evidence=True, human_approved=True)
        self.assertEqual(result["transition"], "running")
        blocked = sdd_execute.preflight({**task, "dependencies": ["TASK-002"]}, tasks=tasks,
                                        red_evidence=True, human_approved=True)
        self.assertEqual(blocked["reason"], "dependency_missing")
        unknown = sdd_execute.preflight({**task, "dependencies": ["TASK-009"]}, tasks=tasks,
                                        red_evidence=True, human_approved=True)
        self.assertEqual(unknown["reason"], "dependency_missing")

    def test_path_prefix_is_normalized(self):
        task = {"id": "TASK-003", "state": "ready", "dependencies": [], "allowed_paths": ["src"]}
        result = sdd_execute.preflight(task, tasks=[], red_evidence=True, human_approved=True,
                                       changed_paths=["src/../etc/passwd"])
        self.assertEqual(result["reason"], "path_violation")


class SyncTests(LifecycleFixture):
    def state_file(self, **task_overrides):
        self.write_task()
        data = self.imported()
        data["tasks"][0].update(task_overrides)
        self.cli.state.write_text(json.dumps(data), encoding="utf-8")
        return data

    def test_default_root_is_the_repository_not_its_parent(self):
        self.state_file()
        outside = self.repo.parent / f"outside-{self.repo.name}.json"
        outside.write_text(json.dumps({"tasks": []}), encoding="utf-8")
        try:
            with self.assertRaisesRegex(ValueError, "inside repository root"):
                sdd_sync.inspect(self.bundle, outside)
            report = sdd_sync.inspect(self.bundle, self.cli.state)
            self.assertEqual([item["classification"] for item in report["items"]], ["no_change"])
        finally:
            outside.unlink()

    def test_token_is_bound_to_the_plan(self):
        self.state_file()
        plan = sdd_sync.plan(sdd_sync.inspect(self.bundle, self.cli.state))
        self.assertTrue(plan["confirmation_token"].startswith("CONFIRM-SDD-SYNC-"))
        with self.assertRaisesRegex(ValueError, "confirmation token"):
            sdd_sync.apply(self.bundle, self.cli.state, plan, authority="json", confirmation_token="CONFIRM-SDD-SYNC")

    def test_markdown_authority_never_moves_lifecycle_state(self):
        self.state_file()
        md = self.bundle / "task-001.md"
        md.write_text(md.read_text().replace("state: pending", "state: complete"), encoding="utf-8")
        plan = sdd_sync.plan(sdd_sync.inspect(self.bundle, self.cli.state))
        before = self.cli.state.read_bytes()
        with self.assertRaisesRegex(ValueError, "sdd_tasks"):
            sdd_sync.apply(self.bundle, self.cli.state, plan, authority="markdown",
                           confirmation_token=plan["confirmation_token"])
        self.assertEqual(before, self.cli.state.read_bytes())

    def test_markdown_authority_output_is_validated(self):
        self.state_file()
        md = self.bundle / "task-001.md"
        md.write_text(md.read_text().replace("acceptance_criteria: [CA-001]", "acceptance_criteria: [BAD]"),
                      encoding="utf-8")
        plan = sdd_sync.plan(sdd_sync.inspect(self.bundle, self.cli.state))
        before = self.cli.state.read_bytes()
        with self.assertRaises(ValueError):
            sdd_sync.apply(self.bundle, self.cli.state, plan, authority="markdown",
                           confirmation_token=plan["confirmation_token"])
        self.assertEqual(before, self.cli.state.read_bytes())


if __name__ == "__main__":
    unittest.main()
