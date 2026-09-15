"""LOOP, trace, and global state driven through their CLIs, checked against the schemas.

The LOOP had no CLI path to publish a stage, the trace CLI could not record, schemas lagged
behind the records the code writes, and state.json was never updated after INIT.
"""

import datetime as dt
import hashlib
import json
import multiprocessing
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "sdd-composy"
SCRIPTS = PLUGIN / "scripts"
SCHEMAS = PLUGIN / "schemas"
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(ROOT / "tests"))
import sdd_init  # noqa: E402
import sdd_language  # noqa: E402
import sdd_loop  # noqa: E402
import sdd_tasks  # noqa: E402
import sdd_trace  # noqa: E402
from test_sdd_composy import assert_schema_valid  # noqa: E402

UTC = dt.timezone.utc


def schema(name):
    return json.loads((SCHEMAS / f"{name}.schema.json").read_text(encoding="utf-8"))


def cli(script, *args, cwd=None):
    return subprocess.run([sys.executable, str(SCRIPTS / script), *args], cwd=cwd, capture_output=True, text=True)


def result(stage, **extra):
    value = {"stage": stage, "status": "completed", "message": "ok", "verdict": "passed",
             "evidence": {"status": "passed"}}
    value.update(extra)
    return value


def _record_worker(root, index):
    sdd_trace.record(root, {"actor_id": "agent:codex", "type": "task.recorded", "stage": "EXECUTE",
                            "data": {"n": index}})


class Workspace(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name).resolve()
        self.tasks = self.root / ".planning/sdd-composy/tasks/demo.json"

    def tearDown(self):
        self.tmp.cleanup()

    def task_state(self, state="ready"):
        data = {"schema_version": "1", "prd_slug": "demo", "updated_at": "2026-01-01T00:00:00Z", "tasks": [{
            "id": "TASK-001", "title": "one", "state": state, "dependencies": [],
            "acceptance_criteria": ["CA-001"], "verification_commands": ["true"],
            "allowed_paths": ["src"], "evidence_required": True}]}
        self.tasks.parent.mkdir(parents=True, exist_ok=True)
        sdd_tasks._atomic_write(self.tasks, data)
        return data

    def initialize_state(self):
        path = self.root / ".planning/sdd-composy/state.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(sdd_init._state("2026-01-01T00:00:00Z")), encoding="utf-8")
        return path


class LoopCliPublishTests(Workspace):
    def loop(self, *args):
        return cli("sdd_loop.py", "--root", str(self.root), *args)

    def write(self, name, value):
        path = self.root / name
        path.write_text(json.dumps(value), encoding="utf-8")
        return path

    def test_cli_publishes_every_stage_and_completes_with_real_verification(self):
        self.task_state("ready")
        started = self.loop("start", "TASK-001", "--task-state", str(self.tasks), "--human-approved")
        self.assertEqual(started.returncode, 0, started.stdout + started.stderr)
        loop_id = json.loads(started.stdout)["id"]
        for stage in ("EXECUTE", "QA", "EVIDENCE", "REVIEW"):
            published = self.loop("publish", loop_id, stage, "--result", str(self.write(f"{stage}.json", result(stage))),
                                  "--task-state", str(self.tasks), "--human-approved")
            self.assertEqual(published.returncode, 0, published.stdout + published.stderr)
        records = self.root / "evidence"; records.mkdir()
        now = time.time() + 1
        command = {"task_id": "TASK-001", "loop_id": loop_id, "status": "passed", "exit_code": 0,
                   "command": ["true"], "stdout": "", "stderr": "", "started_at": now, "ended_at": now}
        command["sha256"] = hashlib.sha256(b"\n").hexdigest()
        raw = json.dumps(command).encode(); (records / "verify.json").write_bytes(raw)
        verify = result("VERIFY", evidence={"status": "passed", "command_record": {
            "path": "evidence/verify.json", "sha256": hashlib.sha256(raw).hexdigest()}})
        published = self.loop("publish", loop_id, "VERIFY", "--result", str(self.write("VERIFY.json", verify)),
                               "--task-state", str(self.tasks), "--human-approved")
        self.assertEqual(published.returncode, 0, published.stdout + published.stderr)
        self.assertEqual(sdd_loop.resume(self.root, loop_id)["next_stage"], None)

    def test_cli_refuses_unsuccessful_results_and_missing_approval(self):
        self.task_state("ready")
        loop_id = json.loads(self.loop("start", "TASK-001", "--task-state", str(self.tasks), "--human-approved").stdout)["id"]
        failed = self.write("failed.json", result("EXECUTE", status="failed", verdict="rejected"))
        refused = self.loop("publish", loop_id, "EXECUTE", "--result", str(failed), "--task-state", str(self.tasks), "--human-approved")
        self.assertNotEqual(refused.returncode, 0)
        good = self.write("good.json", result("EXECUTE"))
        unapproved = self.loop("publish", loop_id, "EXECUTE", "--result", str(good), "--task-state", str(self.tasks))
        self.assertNotEqual(unapproved.returncode, 0)
        wrong_stage = self.loop("publish", loop_id, "QA", "--result", str(good), "--task-state", str(self.tasks), "--human-approved")
        self.assertNotEqual(wrong_stage.returncode, 0)


class OrchestratorStopTests(Workspace):
    def test_needs_human_and_blocked_results_stop_without_spending_iterations(self):
        for status in ("needs_human", "blocked"):
            with self.subTest(status=status):
                calls = []
                def engine(contract):
                    calls.append(contract)
                    return result(contract["stage"], status=status, verdict=status, message="need a decision")
                record = sdd_loop.orchestrate(self.root, "TASK-001", engine, human_approved=True,
                                              loop_id=f"stop-{status.replace('_', '-')}")
                self.assertEqual(record["status"], status)
                self.assertEqual(len(calls), 1)
                self.assertEqual(record["iteration"], 0)
                assert_schema_valid(self, schema("loop"), record)

    def test_resume_honours_the_recorded_iteration_cap(self):
        sdd_loop.start(self.root, "TASK-001", max_iterations=1, loop_id="capped")
        calls = []
        def engine(contract):
            calls.append(contract)
            return result(contract["stage"], status="failed", verdict="rejected", message="red")
        record = sdd_loop.orchestrate(self.root, "TASK-001", engine, human_approved=True, loop_id="capped")
        self.assertEqual(record["status"], "iteration_cap")
        self.assertEqual(len(calls), 1)

    def test_correction_contract_carries_the_previous_failure(self):
        calls = []
        def engine(contract):
            calls.append(contract)
            return result(contract["stage"], status="failed", verdict="rejected", message=f"red {len(calls)}",
                          failure=f"failure {len(calls)}")
        sdd_loop.orchestrate(self.root, "TASK-001", engine, human_approved=True, max_iterations=2)
        self.assertEqual(len(calls), 2)
        self.assertNotIn("previous_failure", calls[0])
        self.assertEqual(calls[1]["previous_failure"], "red 1")


class TraceCliTests(Workspace):
    def event_file(self, **overrides):
        event = {"actor_id": "agent:codex", "type": "task.transitioned", "stage": "EXECUTE", "task_id": "TASK-001",
                 "data": {"to": "running"}}
        event.update(overrides)
        path = self.root / "event.json"; path.write_text(json.dumps(event), encoding="utf-8")
        return path

    def test_cli_records_and_verify_exit_codes_follow_the_result(self):
        recorded = cli("sdd_trace.py", "record", str(self.root), "--event", str(self.event_file()))
        self.assertEqual(recorded.returncode, 0, recorded.stdout + recorded.stderr)
        self.assertEqual(json.loads(recorded.stdout)["sequence"], 1)
        self.assertEqual(cli("sdd_trace.py", "verify", str(self.root)).returncode, 0)
        events = self.root / ".planning/sdd-composy/trace/events.jsonl"
        events.write_text(events.read_text() + '{"sequence": 7}\n', encoding="utf-8")
        self.assertNotEqual(cli("sdd_trace.py", "verify", str(self.root)).returncode, 0)
        self.assertNotEqual(cli("sdd_trace.py", "verify-projection", str(self.root)).returncode, 0)

    def test_cli_rejects_forbidden_event_content(self):
        refused = cli("sdd_trace.py", "record", str(self.root), "--event", str(self.event_file(data={"prompt": "x"})))
        self.assertNotEqual(refused.returncode, 0)
        self.assertIn("prohibited", refused.stdout)

    def test_concurrent_records_keep_a_contiguous_sequence(self):
        with multiprocessing.get_context("spawn").Pool(6) as pool:
            pool.starmap(_record_worker, [(str(self.root), index) for index in range(24)])
        report = sdd_trace.verify(self.root)
        self.assertTrue(report["ok"], report)
        self.assertEqual(report["source_event_count"], 24)


class SchemaMatchesProducedRecordsTests(Workspace):
    def test_every_terminal_loop_record_matches_the_loop_schema(self):
        for index, outcome in enumerate(sorted(sdd_loop.TERMINAL - {"completed", "cancelled", "iteration_cap"})):
            loop_id = f"loop-{index}"
            sdd_loop.start(self.root, "TASK-001", loop_id=loop_id)
            record = sdd_loop.continue_loop(self.root, loop_id, outcome=outcome)
            with self.subTest(outcome=outcome):
                assert_schema_valid(self, schema("loop"), record)
        loop_schema = schema("loop")
        self.assertEqual(set(loop_schema["definitions"]["loop_status"]["enum"]), sdd_loop.STAGES)
        self.assertEqual(loop_schema["properties"]["max_iterations"].get("maximum"), 3)

    def test_persisted_language_config_matches_the_config_schema(self):
        sdd_language.persist_language(self.root, "pt-BR")
        config = json.loads((self.root / ".planning/sdd-composy/config.json").read_text())
        assert_schema_valid(self, schema("config"), config)


class GlobalStateTests(Workspace):
    def state(self):
        value = json.loads((self.root / ".planning/sdd-composy/state.json").read_text())
        self.assertTrue(sdd_init._valid_state(value))
        assert_schema_valid(self, schema("state"), value)
        return value

    def test_task_transitions_update_stage_active_task_blockers_and_revision(self):
        self.initialize_state(); self.task_state("ready")
        self.assertEqual(cli("sdd_tasks.py", "start", str(self.tasks), "TASK-001", cwd=self.root).returncode, 0)
        state = self.state()
        self.assertEqual((state["stage"], state["active_prd"], state["active_task"]), ("EXECUTE", "demo", "TASK-001"))
        self.assertEqual(state["revision"], 1)
        blocked = cli("sdd_tasks.py", "block", str(self.tasks), "TASK-001", "waiting on credentials", cwd=self.root)
        self.assertEqual(blocked.returncode, 0, blocked.stdout)
        state = self.state()
        self.assertEqual(state["blockers"], [{"id": "TASK-001", "status": "blocked", "reason": "waiting on credentials"}])
        self.assertEqual(cli("sdd_tasks.py", "transition", str(self.tasks), "TASK-001", "ready", cwd=self.root).returncode, 0)
        self.assertEqual(self.state()["blockers"], [])

    def test_loop_and_trace_cli_update_their_summaries(self):
        self.initialize_state(); self.task_state("ready")
        started = cli("sdd_loop.py", "--root", str(self.root), "start", "TASK-001", "--task-state", str(self.tasks),
                      "--human-approved")
        self.assertEqual(started.returncode, 0, started.stdout)
        self.assertEqual(self.state()["loops"], [{"id": "loop-task-001", "status": "running", "task_id": "TASK-001"}])
        cli("sdd_loop.py", "--root", str(self.root), "cancel", "loop-task-001")
        self.assertEqual(self.state()["loops"][0]["status"], "cancelled")
        event = self.root / "event.json"
        event.write_text(json.dumps({"actor_id": "agent:codex", "type": "loop.cancelled", "stage": "EXECUTE"}))
        self.assertEqual(cli("sdd_trace.py", "record", str(self.root), "--event", str(event)).returncode, 0)
        self.assertEqual(self.state()["trace"], {"healthy": True, "source_event_count": 1})

    def test_uninitialized_repository_is_left_without_state(self):
        self.task_state("ready")
        self.assertEqual(cli("sdd_tasks.py", "start", str(self.tasks), "TASK-001", cwd=self.root).returncode, 0)
        self.assertFalse((self.root / ".planning/sdd-composy/state.json").exists())


class StatusExitCodeTests(Workspace):
    def test_malformed_sources_exit_non_zero(self):
        self.assertEqual(cli("sdd_status.py", str(self.root)).returncode, 0)
        state = self.initialize_state()
        state.write_text("{broken", encoding="utf-8")
        self.assertNotEqual(cli("sdd_status.py", str(self.root)).returncode, 0)


if __name__ == "__main__":
    unittest.main()
