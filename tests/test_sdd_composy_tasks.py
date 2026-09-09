import unittest
from pathlib import Path
import json, tempfile, sys, datetime as dt, subprocess
from unittest import mock


ROOT = Path(__file__).parents[1]
PLUGIN = ROOT / "plugins" / "sdd-composy"
sys.path.insert(0, str(PLUGIN / "scripts"))
import sdd_tasks
import sdd_sync
import sdd_quick


class QuickBehaviorIntegrationTest(unittest.TestCase):
    """Exercise the documented quick boundary through the public task API."""

    def _task(self, state="pending"):
        return {"id": "TASK-001", "title": "Bounded change", "state": state,
                "dependencies": [], "acceptance_criteria": ["CA-001"],
                "verification_commands": ["python3 -m unittest"],
                "allowed_paths": ["src/app.py"], "evidence_required": True}

    def test_valid_quick_request_registers_normal_task_and_stays_bounded(self):
        self.assertEqual(sdd_quick.evaluate({"quick": {"allowed_files": ["src/app.py"], "verification_commands": ["true"]}})["decision"], "QUICK")
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td); source = repo / "tasks" / "prd-demo"; source.mkdir(parents=True)
            source.joinpath("task-001.md").write_text(
                "---\ntype: TASK\ntask:\n  id: TASK-001\n  title: Bounded change\n  state: pending\n  dependencies: []\n  acceptance_criteria:\n    - 'CA-001'\n  verification_commands:\n    - 'python3 -m unittest'\n  allowed_paths:\n    - 'src/app.py'\n  evidence_required: true\n---\n", encoding="utf-8")
            output = repo / ".planning" / "tasks.json"; output.parent.mkdir()
            result = sdd_tasks.import_tasks(source, output, root=repo, now=dt.datetime(2026, 1, 1, tzinfo=dt.timezone.utc))
            self.assertEqual(result["tasks"][0]["id"], "TASK-001")
            self.assertEqual(sdd_tasks.transition(result, "TASK-001", "ready")["tasks"][0]["state"], "ready")

    def test_over_boundary_or_unknown_verification_escalates_before_edit(self):
        self.assertEqual(sdd_quick.evaluate({"quick": {"allowed_files": [f"src/{i}.py" for i in range(6)], "verification_commands": ["true"]}})["decision"], "ESCALATE")
        self.assertEqual(sdd_quick.evaluate({"quick": {"allowed_files": ["src/app.py"], "verification_commands": []}})["decision"], "ESCALATE")
        self.assertEqual(sdd_quick.evaluate({"quick": {"allowed_files": ["src/app.py"], "verification_commands": ["true"], "architecture": True}})["decision"], "ESCALATE")

    def test_quick_cannot_complete_without_task_evidence_trace_and_verification_guards(self):
        data = {"schema_version": "1", "prd_slug": "demo", "updated_at": "2026-01-01T00:00:00Z", "tasks": [self._task("verify_required")]}
        report = sdd_tasks.verify(data, now=dt.datetime(2026, 1, 1, tzinfo=dt.timezone.utc))
        self.assertFalse(report["ok"])
        with self.assertRaises(sdd_tasks.TaskError):
            sdd_tasks.transition(data, "TASK-001", "complete", now=dt.datetime(2026, 1, 1, tzinfo=dt.timezone.utc))


class SynchronizationInspectionTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.repo = Path(self.tmp.name)
        self.src = self.repo / "tasks" / "prd-demo"; self.src.mkdir(parents=True)
        self.state = self.repo / ".planning" / "tasks.json"; self.state.parent.mkdir()
    def tearDown(self): self.tmp.cleanup()
    def md(self, title="First", state="pending"):
        (self.src / "task-001.md").write_text(f"---\ntype: TASK\ntask:\n  id: TASK-001\n  title: {title}\n  state: {state}\n---\n", encoding="utf-8")
    def js(self, task=None):
        self.state.write_text(json.dumps({"tasks": task or [{"id":"TASK-001","title":"First","state":"pending"}], "unknown":"keep"}), encoding="utf-8")
    def test_matrix_and_determinism(self):
        self.md(); self.js(); a=sdd_sync.inspect(self.src,self.state,root=self.repo); self.assertEqual(a["items"][0]["classification"],"no_change")
        self.js([{"id":"TASK-999","title":"Other","state":"pending"}]); b=sdd_sync.inspect(self.src,self.state,root=self.repo); self.assertEqual({x["classification"] for x in b["items"]},{"markdown_only","json_only"})
        self.js(); (self.src / "task-001.md").unlink(); self.assertEqual(sdd_sync.inspect(self.src,self.state,root=self.repo)["items"][0]["classification"],"json_only")
        self.md("Changed"); self.assertEqual(sdd_sync.inspect(self.src,self.state,root=self.repo)["items"][0]["classification"],"identity_changed")
        self.md(state="running"); self.assertEqual(sdd_sync.inspect(self.src,self.state,root=self.repo)["items"][0]["classification"],"status_divergence")
        self.md(state="pending"); self.js([{"id":"TASK-001","title":"First"}]); self.assertEqual(sdd_sync.inspect(self.src,self.state,root=self.repo)["items"][0]["classification"],"status_divergence")
        self.assertEqual(sdd_sync.inspect(self.src,self.state,root=self.repo), sdd_sync.inspect(self.src,self.state,root=self.repo))
        self.assertEqual(sdd_sync.plan(sdd_sync.inspect(self.src,self.state,root=self.repo)), sdd_sync.plan(sdd_sync.inspect(self.src,self.state,root=self.repo)))
        self.assertEqual(sdd_sync.CONFIRMATION_TOKEN, "CONFIRM-SDD-SYNC")
    def test_malformed_and_read_only_and_symlink_safety(self):
        self.md(); self.js(); before=(self.src / "task-001.md").read_bytes(), self.state.read_bytes()
        (self.src / "task-001.md").write_text("bad", encoding="utf-8"); self.assertEqual(sdd_sync.inspect(self.src,self.state,root=self.repo)["items"][0]["classification"],"malformed_markdown")
        (self.src / "task-001.md").write_text("---\ntask:\n  id: TASK-001\n---\n", encoding="utf-8"); self.state.write_text("{bad",encoding="utf-8"); self.assertEqual(sdd_sync.inspect(self.src,self.state,root=self.repo)["items"][0]["classification"],"malformed_json")
        snap = ((self.src / "task-001.md").read_bytes(), self.state.read_bytes()); sdd_sync.inspect(self.src,self.state,root=self.repo); self.assertEqual(snap, ((self.src / "task-001.md").read_bytes(), self.state.read_bytes()))
        link=self.repo / "link.json"; link.symlink_to(self.state); self.assertRaises(ValueError, sdd_sync.inspect, self.src, link, root=self.repo)
        external=self.repo.parent / ("external-tasks-" + self.repo.name); external.mkdir(); self.assertRaises(ValueError, sdd_sync.inspect, external, self.state, root=self.repo)
        root_link=self.repo.parent / ("repo-link-" + self.repo.name); root_link.symlink_to(self.repo, target_is_directory=True); self.assertRaises(ValueError, sdd_sync.inspect, root_link / "tasks" / "prd-demo", self.state, root=root_link)
        self.js(); self.assertEqual(sdd_sync._json(self.state)["TASK-001"]["id"], "TASK-001"); self.assertIn("unknown", json.loads(self.state.read_text()))

    def test_apply_requires_exact_token_and_rejects_stale_inputs(self):
        self.md(state="running"); self.js(); plan = sdd_sync.plan(sdd_sync.inspect(self.src, self.state, root=self.repo))
        with self.assertRaises(ValueError): sdd_sync.apply(self.src, self.state, plan, authority="markdown", confirmation_token="wrong", root=self.repo)
        self.state.write_text(self.state.read_text() + "\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "stale"): sdd_sync.apply(self.src, self.state, plan, authority="markdown", confirmation_token=sdd_sync.CONFIRMATION_TOKEN, root=self.repo)

    def test_apply_explicit_authority_and_post_apply_verification(self):
        self.md(state="running"); self.js(); plan = sdd_sync.plan(sdd_sync.inspect(self.src, self.state, root=self.repo))
        result = sdd_sync.apply(self.src, self.state, plan, authority="markdown", confirmation_token=sdd_sync.CONFIRMATION_TOKEN, root=self.repo)
        self.assertTrue(result["verified"]); self.assertEqual(sdd_sync._json(self.state)["TASK-001"]["state"], "running")
        self.md(state="complete"); self.js(); plan = sdd_sync.plan(sdd_sync.inspect(self.src, self.state, root=self.repo))
        result = sdd_sync.apply(self.src, self.state, plan, authority="json", confirmation_token=sdd_sync.CONFIRMATION_TOKEN, root=self.repo)
        self.assertTrue(result["verified"]); self.assertIn('state: "pending"', (self.src / "task-001.md").read_text())

    def test_apply_rejects_symlink_destination(self):
        self.md(state="running"); self.js(); plan = sdd_sync.plan(sdd_sync.inspect(self.src, self.state, root=self.repo))
        real = self.repo / "real.json"; real.write_bytes(self.state.read_bytes()); self.state.unlink(); self.state.symlink_to(real)
        with self.assertRaises(ValueError): sdd_sync.apply(self.src, self.state, plan, authority="markdown", confirmation_token=sdd_sync.CONFIRMATION_TOKEN, root=self.repo)

    def test_apply_authority_resolves_identity_conflicts(self):
        self.md(title="From Markdown"); self.js([{"id":"TASK-001","title":"From JSON","state":"pending"}])
        plan = sdd_sync.plan(sdd_sync.inspect(self.src, self.state, root=self.repo))
        sdd_sync.apply(self.src, self.state, plan, authority="markdown", confirmation_token=sdd_sync.CONFIRMATION_TOKEN, root=self.repo)
        self.assertEqual(sdd_sync._json(self.state)["TASK-001"]["title"], "From Markdown")
        self.md(title="From Markdown"); self.js([{"id":"TASK-001","title":"From JSON","state":"pending"}])
        plan = sdd_sync.plan(sdd_sync.inspect(self.src, self.state, root=self.repo))
        sdd_sync.apply(self.src, self.state, plan, authority="json", confirmation_token=sdd_sync.CONFIRMATION_TOKEN, root=self.repo)
        self.assertIn('title: "From JSON"', (self.src / "task-001.md").read_text())

    def test_json_authority_materializes_json_only_task(self):
        self.md()
        self.src.joinpath("task-001.md").unlink(); self.js([{"id":"TASK-002","title":"Second","state":"pending"}])
        plan = sdd_sync.plan(sdd_sync.inspect(self.src, self.state, root=self.repo))
        result = sdd_sync.apply(self.src, self.state, plan, authority="json", confirmation_token=sdd_sync.CONFIRMATION_TOKEN, root=self.repo)
        self.assertTrue(result["verified"]); self.assertTrue((self.src / "task-002.md").exists())

    def test_public_cli_apply_loads_plan_and_requires_exact_approval(self):
        self.md(state="running"); self.js()
        script = PLUGIN / "scripts" / "sdd_sync.py"
        planned = subprocess.run(
            [sys.executable, str(script), "plan", str(self.src), str(self.state), "--root", str(self.repo)],
            capture_output=True, text=True, check=True,
        )
        plan_path = self.repo / "plan.json"; plan_path.write_text(planned.stdout, encoding="utf-8")
        applied = subprocess.run(
            [sys.executable, str(script), "apply", str(self.src), str(self.state), str(plan_path),
             "--root", str(self.repo), "--authority", "markdown",
             "--confirmation-token", sdd_sync.CONFIRMATION_TOKEN],
            capture_output=True, text=True, check=True,
        )
        self.assertTrue(json.loads(applied.stdout)["verified"])
        self.assertEqual(sdd_sync._json(self.state)["TASK-001"]["state"], "running")

    def test_public_cli_apply_rejects_wrong_token_and_authority(self):
        self.md(); self.js(); script = PLUGIN / "scripts" / "sdd_sync.py"
        planned = subprocess.run(
            [sys.executable, str(script), "plan", str(self.src), str(self.state), "--root", str(self.repo)],
            capture_output=True, text=True, check=True,
        )
        plan_path = self.repo / "plan.json"; plan_path.write_text(planned.stdout, encoding="utf-8")
        for option, value in (("--confirmation-token", "wrong"), ("--authority", "neither")):
            args = [sys.executable, str(script), "apply", str(self.src), str(self.state), str(plan_path),
                    "--root", str(self.repo), "--authority", "markdown",
                    "--confirmation-token", sdd_sync.CONFIRMATION_TOKEN]
            index = args.index(option) if option in args else -1
            if index >= 0: args[index + 1] = value
            else: args[-1] = value
            rejected = subprocess.run(args, capture_output=True, text=True)
            self.assertNotEqual(rejected.returncode, 0)
            self.assertIn("invalid", rejected.stderr.lower())


class TaskContractTemplatesTest(unittest.TestCase):
    def read(self, name):
        return (PLUGIN / name).read_text(encoding="utf-8")

    def test_index_is_okf_traceable_and_dependency_explicit(self):
        text = self.read("templates/tasks.md")
        for value in ('type: TASKS', 'okf_version: "0.2"', 'tasks/prd-{{SLUG}}/prd.md',
                      'tasks/prd-{{SLUG}}/stories.md', 'tasks/prd-{{SLUG}}/techspec.md',
                      'TASK-001', 'Dependencies', 'ready', 'human_approval: PENDING'):
            self.assertIn(value, text)

    def test_task_contract_covers_trace_paths_subtasks_and_commands(self):
        text = self.read("templates/task.md")
        for value in ('type: TASK', 'TASK-001', 'RF-001', 'US-001', 'SC-001', 'CA-001',
                      'allowed_paths', 'Allowed files', 'Subtasks', 'verification_commands',
                      'evidence_required: true', 'TEST-001',
                      '[tests/test_sdd_composy_tasks.py::TaskContractTemplatesTest::test_task_contract_covers_trace_paths_subtasks_and_commands](../../tests/test_sdd_composy_tasks.py#test_task_contract_covers_trace_paths_subtasks_and_commands)',
                      'python3 -m unittest', 'human_approval: PENDING',
                      'lifecycle.status: APPROVED'):
            self.assertIn(value, text)
        self.assertRegex(text, r'\[tests/test_[^\]]+\.py(?:::|#)[^\]]*\]\([^\s)]+\.py#')

    def test_reference_defines_stable_ids_gate_and_exact_ownership(self):
        text = self.read("references/tasks.md")
        for value in ('TASK-NNN', 'stable', 'ready', 'complete', 'RF-*', 'US-*', 'SC-*',
                      'CA-*', 'OKF v0.2', 'human approval', 'tasks/prd-<slug>/',
                      '.planning/sdd-composy/', 'atomic replacement'):
            self.assertIn(value, text)

class TaskRuntimeTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.repo = Path(self.tmp.name)
        self.src = self.repo / "tasks" / "prd-demo"; self.src.mkdir(parents=True)
        (self.src / "task-001.md").write_text('''---\ntype: TASK\ntask:\n  id: TASK-001\n  title: First\n  state: pending\n  dependencies: []\n  acceptance_criteria: [CA-001]\n  verification_commands: ["true"]\n  allowed_paths: ["src/app.py"]\n  evidence_required: true\n---\n''', encoding='utf-8')
        self.out = self.repo / ".planning" / "tasks.json"
    def tearDown(self): self.tmp.cleanup()
    def test_import_list_show_merge_and_deterministic(self):
        self.out.parent.mkdir(); self.out.write_text(json.dumps({"schema_version":"1","prd_slug":"demo","updated_at":"2026-01-01T00:00:00Z","custom":"keep","tasks":[{"id":"TASK-001","old":"keep"}]}), encoding='utf-8')
        fixed = dt.datetime(2026, 1, 2, tzinfo=dt.timezone.utc)
        first = sdd_tasks.import_tasks(self.src, self.out, root=self.repo, now=fixed)
        self.assertEqual(first["tasks"][0]["old"], "keep"); self.assertEqual(first["custom"], "keep")
        self.assertEqual(sdd_tasks.load(self.out)["tasks"][0]["id"], "TASK-001")
        before = self.out.read_text(); sdd_tasks.import_tasks(self.src, self.out, root=self.repo, now=fixed); self.assertEqual(before, self.out.read_text())

    def test_import_preserves_live_json_state_and_reports_markdown_divergence(self):
        self.out.parent.mkdir(); self.out.write_text(json.dumps({"schema_version":"1","prd_slug":"demo",
            "updated_at":"2026-01-01T00:00:00Z","custom":"keep","tasks":[{
            "id":"TASK-001","title":"First","state":"running","dependencies":[],
            "acceptance_criteria":["CA-001"],"verification_commands":["true"],
            "allowed_paths":["src/app.py"],"evidence_required":True,"runtime_note":"keep"}]}))
        result = sdd_tasks.import_tasks(self.src, self.out, root=self.repo,
            now=dt.datetime(2026, 1, 2, tzinfo=dt.timezone.utc))
        self.assertEqual(result["tasks"][0]["state"], "running")
        self.assertEqual(result["tasks"][0]["runtime_note"], "keep")
        self.assertEqual(result["divergences"][0]["field"], "state")

    def test_import_rejects_new_task_prepromoted_by_markdown(self):
        text = (self.src / "task-001.md").read_text(encoding="utf-8").replace("state: pending", "state: ready")
        (self.src / "task-001.md").write_text(text, encoding="utf-8")
        with self.assertRaises(sdd_tasks.TaskError):
            sdd_tasks.import_tasks(self.src, self.out, root=self.repo)

    def test_import_preserves_json_only_tasks(self):
        self.out.parent.mkdir(); existing = self._graph()
        self.out.write_text(json.dumps(existing), encoding="utf-8")
        result = sdd_tasks.import_tasks(self.src, self.out, root=self.repo,
            now=dt.datetime(2026, 1, 2, tzinfo=dt.timezone.utc))
        self.assertEqual([task["id"] for task in result["tasks"]], ["TASK-001", "TASK-002"])

    def test_validate_rejects_wrong_json_types_and_symlink_ancestors(self):
        data = self._graph(); data["tasks"][0]["state"] = 1
        with self.assertRaises(sdd_tasks.TaskError): sdd_tasks.validate(data)
        outside = self.repo.parent / (self.repo.name + "-outside"); outside.mkdir()
        linked = self.repo / "linked"; linked.symlink_to(outside, target_is_directory=True)
        with self.assertRaises(sdd_tasks.TaskError):
            sdd_tasks.import_tasks(self.src, linked / "tasks.json", root=self.repo)
    def test_invalid_timestamp_and_unsafe_outputs(self):
        for stamp in ("not-a-date", "2026-01-01", "2026-01-01T00:00:00"):
            data={"schema_version":"1","prd_slug":"demo","updated_at":stamp,"tasks":[]}
            with self.assertRaises(sdd_tasks.TaskError): sdd_tasks.validate(data)
        for target in (Path("/tmp/out.json"), self.repo / ".." / "escape.json"):
            with self.assertRaises(sdd_tasks.TaskError): sdd_tasks.import_tasks(self.src, target, root=self.repo)
        link=self.repo / "link.json"; link.symlink_to(self.repo / "elsewhere.json")
        with self.assertRaises(sdd_tasks.TaskError): sdd_tasks.import_tasks(self.src, link, root=self.repo)
    def test_atomic_failure_cleans_temporary_file(self):
        with mock.patch("sdd_tasks.os.replace", side_effect=OSError("boom")):
            with self.assertRaises(OSError): sdd_tasks.import_tasks(self.src, self.out, root=self.repo)
        self.assertFalse(list(self.out.parent.glob(f".{self.out.name}.*.tmp")))
    def test_public_cli_list_show_and_unknown(self):
        sdd_tasks.import_tasks(self.src, self.out, root=self.repo, now=dt.datetime(2026, 1, 2, tzinfo=dt.timezone.utc))
        script = PLUGIN / "scripts" / "sdd_tasks.py"
        listed = subprocess.run([sys.executable, str(script), "list", str(self.out)], capture_output=True, text=True, check=True)
        self.assertEqual(json.loads(listed.stdout)[0]["id"], "TASK-001")
        shown = subprocess.run([sys.executable, str(script), "show", str(self.out), "TASK-001"], capture_output=True, text=True, check=True)
        self.assertEqual(json.loads(shown.stdout)["title"], "First")
        missing = subprocess.run([sys.executable, str(script), "show", str(self.out), "TASK-999"], capture_output=True, text=True)
        self.assertNotEqual(missing.returncode, 0); self.assertIn("ok", json.loads(missing.stdout))

    def test_verify_is_read_only_and_reports_completion_gate(self):
        data = self._evidence_task()
        data["tasks"][0]["state"] = "verify_required"
        before = json.dumps(data, sort_keys=True)
        report = sdd_tasks.verify(data, now=dt.datetime(2026, 1, 2, tzinfo=dt.timezone.utc))
        self.assertTrue(report["ok"])
        self.assertTrue(report["completion_permitted"])
        self.assertEqual(before, json.dumps(data, sort_keys=True))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "state.json"; path.write_text(json.dumps(data), encoding="utf-8")
            script = PLUGIN / "scripts" / "sdd_tasks.py"
            result = subprocess.run([sys.executable, str(script), "verify", str(path)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0)
            self.assertTrue(json.loads(result.stdout)["completion_permitted"])
            self.assertEqual(json.loads(path.read_text(encoding="utf-8")), data)

    def test_verify_has_nonzero_failure_for_invalid_evidence(self):
        data = self._evidence_task(); data["tasks"][0]["state"] = "verify_required"
        data["tasks"][0]["evidence"]["trace"]["status"] = "inconsistent"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "state.json"; path.write_text(json.dumps(data), encoding="utf-8")
            script = PLUGIN / "scripts" / "sdd_tasks.py"
            result = subprocess.run([sys.executable, str(script), "verify", str(path)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            report = json.loads(result.stdout)
            self.assertFalse(report["ok"])
            self.assertEqual(report["checks"][0]["status"], "blocked")

    def _graph(self, states=("complete", "pending"), deps=([], ["TASK-001"])):
        base = {"schema_version":"1", "prd_slug":"demo", "updated_at":"2026-01-01T00:00:00Z", "tasks":[]}
        for i, state in enumerate(states):
            base["tasks"].append({"id":f"TASK-{i+1:03}", "title":str(i), "state":state,
                "dependencies":deps[i], "acceptance_criteria":[f"CA-{i+1:03}"],
                "verification_commands":["true"], "allowed_paths":["src/a"], "evidence_required":True})
        return base

    def test_graph_rejects_missing_dependencies_and_cycles(self):
        missing = self._graph(); missing["tasks"][1]["dependencies"] = ["TASK-999"]
        with self.assertRaises(sdd_tasks.TaskError): sdd_tasks.validate(missing)
        cycle = self._graph(); cycle["tasks"][0]["dependencies"] = ["TASK-002"]
        with self.assertRaises(sdd_tasks.TaskError): sdd_tasks.validate(cycle)

    def test_next_is_deterministic_and_transitions_guarded(self):
        data = self._graph(); self.assertEqual([t["id"] for t in sdd_tasks.ready_tasks(data)], ["TASK-002"])
        with self.assertRaises(sdd_tasks.TaskError): sdd_tasks.transition(data, "TASK-002", "running")
        sdd_tasks.transition(data, "TASK-002", "ready")
        # A published ready task must not bypass a dependency mutation.
        data["tasks"][0]["state"] = "running"
        with self.assertRaises(sdd_tasks.TaskError): sdd_tasks.transition(data, "TASK-002", "running")
        data["tasks"][0]["state"] = "complete"
        sdd_tasks.transition(data, "TASK-002", "running")
        with self.assertRaises(sdd_tasks.TaskError): sdd_tasks.transition(data, "TASK-002", "pending")

    def test_block_reason_and_rejected_blocked_recovery(self):
        data = self._graph(states=("complete", "running"));
        with self.assertRaises(sdd_tasks.TaskError): sdd_tasks.transition(data, "TASK-002", "blocked")
        sdd_tasks.transition(data, "TASK-002", "blocked", reason="waiting")
        sdd_tasks.transition(data, "TASK-002", "ready")
        self.assertNotIn("blocked_reason", data["tasks"][1])
        data["tasks"][1]["state"] = "rejected"; data["tasks"][1]["rejection_reason"] = "review"
        sdd_tasks.transition(data, "TASK-002", "ready")
        self.assertNotIn("rejection_reason", data["tasks"][1])

    def _evidence_task(self, required=True):
        stamp = "2026-01-02T00:00:00Z"
        record = lambda status: {"status": status, "timestamp": stamp}
        return {"schema_version":"1", "prd_slug":"demo", "updated_at":"2026-01-01T00:00:00Z", "tasks":[{
            "id":"TASK-001", "title":"evidence", "state":"running", "dependencies":[],
            "acceptance_criteria":["CA-001"], "verification_commands":["true"], "allowed_paths":["src/a"],
            "evidence_required":required, "evidence":{"tests":record("passed"), "qa":record("passed"),
            "review":record("approved"), "verify":record("approved"), "trace":record("consistent")}}]}

    def test_completion_evidence_guards_and_fresh_boundary(self):
        data = self._evidence_task(); sdd_tasks.transition(data, "TASK-001", "qa_required", now=dt.datetime(2026,1,2,tzinfo=dt.timezone.utc))
        sdd_tasks.transition(data, "TASK-001", "evidence_required", now=dt.datetime(2026,1,2,tzinfo=dt.timezone.utc))
        sdd_tasks.transition(data, "TASK-001", "review_required", now=dt.datetime(2026,1,2,tzinfo=dt.timezone.utc))
        sdd_tasks.transition(data, "TASK-001", "verify_required", now=dt.datetime(2026,1,2,tzinfo=dt.timezone.utc))
        sdd_tasks.transition(data, "TASK-001", "complete", now=dt.datetime(2026,1,2,tzinfo=dt.timezone.utc))
        self.assertEqual(data["tasks"][0]["state"], "complete")

    def test_stale_missing_blocking_and_rejected_guards(self):
        data = self._evidence_task(); data["tasks"][0]["evidence"]["tests"].pop("status")
        with self.assertRaises(sdd_tasks.TaskError): sdd_tasks.transition(data, "TASK-001", "complete", now=dt.datetime(2026,1,2,tzinfo=dt.timezone.utc))
        data = self._evidence_task(); data["tasks"][0]["evidence"]["qa"]["status"] = "blocked"
        with self.assertRaises(sdd_tasks.TaskError): sdd_tasks.transition(data, "TASK-001", "review_required", now=dt.datetime(2026,1,2,tzinfo=dt.timezone.utc))
        data = self._evidence_task(); data["tasks"][0]["evidence"]["verify"]["timestamp"] = "2025-12-01T00:00:00Z"
        with self.assertRaises(sdd_tasks.TaskError): sdd_tasks.transition(data, "TASK-001", "complete", now=dt.datetime(2026,1,2,tzinfo=dt.timezone.utc))
        with self.assertRaises(sdd_tasks.TaskError): sdd_tasks.transition(self._evidence_task(), "TASK-001", "rejected")

    def test_skip_requires_human_authority_and_optional_dossier_bypass(self):
        with self.assertRaises(sdd_tasks.TaskError): sdd_tasks.transition(self._evidence_task(), "TASK-001", "skipped", reason="obsolete")
        data = self._evidence_task(False); sdd_tasks.transition(data, "TASK-001", "qa_required", now=dt.datetime(2026,1,2,tzinfo=dt.timezone.utc))
        sdd_tasks.transition(data, "TASK-001", "review_required", now=dt.datetime(2026,1,2,tzinfo=dt.timezone.utc))
        self.assertEqual(data["tasks"][0]["state"], "review_required")

    def test_review_trace_verify_and_future_predicates(self):
        for field, status in (("review", "rejected"), ("trace", "inconsistent"), ("verify", "rejected")):
            data = self._evidence_task(); data["tasks"][0]["evidence"][field]["status"] = status
            with self.assertRaises(sdd_tasks.TaskError):
                sdd_tasks.transition(data, "TASK-001", "complete", now=dt.datetime(2026,1,2,tzinfo=dt.timezone.utc))
        data = self._evidence_task(); data["tasks"][0]["evidence"]["tests"]["timestamp"] = "2026-01-03T00:00:00Z"
        with self.assertRaises(sdd_tasks.TaskError):
            sdd_tasks.transition(data, "TASK-001", "complete", now=dt.datetime(2026,1,2,tzinfo=dt.timezone.utc))

    def test_valid_rejection_and_skip_metadata(self):
        data = self._evidence_task(); data["tasks"][0]["state"] = "verify_required"
        sdd_tasks.transition(data, "TASK-001", "rejected", reason="verification failed", now=dt.datetime(2026,1,2,tzinfo=dt.timezone.utc))
        task = data["tasks"][0]
        self.assertEqual(task["rejection_reason"], "verification failed")
        self.assertEqual(task["rejection_stage"], "verify_required")
        self.assertEqual(task["evidence_invalidated_at"], "2026-01-02T00:00:00Z")
        data = self._evidence_task(); sdd_tasks.transition(data, "TASK-001", "skipped", reason="out of scope", authority="product-owner")
        self.assertEqual(data["tasks"][0]["skip_authority"], "product-owner")

    def test_quality_artifacts_advance_running_task_to_complete(self):
        data = self._evidence_task(); data["tasks"][0]["state"] = "running"
        now = dt.datetime(2026, 1, 2, tzinfo=dt.timezone.utc)
        artifact = lambda status, **extra: {"lifecycle": {"status": status, "human_approval": "APPROVED"}, "verified": [{"by": "reviewer"}], **extra}
        artifact_types = {"qa": "QA_REPORT", "review": "CODE_REVIEW", "verdict": "VERIFICATION_VERDICT"}
        artifacts = {name: artifact("APPROVED", type=kind) for name, kind in artifact_types.items()}
        artifacts["verdict"]["verdict"] = "COMPLETE"
        result = sdd_tasks.integrate_quality_artifacts(data, "TASK-001", artifacts, now=now)
        self.assertEqual(result["tasks"][0]["state"], "complete")

    def test_quality_artifacts_reject_blockers_and_missing_approval(self):
        data = self._evidence_task(); data["tasks"][0]["state"] = "running"
        now = dt.datetime(2026, 1, 2, tzinfo=dt.timezone.utc)
        with self.assertRaises(sdd_tasks.TaskError):
            sdd_tasks.integrate_quality_artifacts(data, "TASK-001", {
                "qa": {"lifecycle": {"status": "REJECTED", "human_approval": "PENDING"}}}, now=now)
        data = self._evidence_task(); data["tasks"][0]["state"] = "running"
        with self.assertRaises(sdd_tasks.TaskError):
            sdd_tasks.integrate_quality_artifacts(data, "TASK-001", {
                "qa": {"lifecycle": {"status": "APPROVED", "human_approval": "PENDING"}}}, now=now)

    def test_quality_artifact_rejections_are_atomic_across_each_gate(self):
        now = dt.datetime(2026, 1, 2, tzinfo=dt.timezone.utc)
        kinds = {"qa": "QA_REPORT", "review": "CODE_REVIEW", "verdict": "VERIFICATION_VERDICT"}
        def valid():
            return {name: {"type": kind, "lifecycle": {"status": "APPROVED", "human_approval": "APPROVED"},
                           "verified": [{"by": "reviewer"}], "verdict": "COMPLETE"}
                    for name, kind in kinds.items()}
        for name, change in (("qa", {"lifecycle": {"status": "REJECTED", "human_approval": "PENDING"}}),
                             ("review", {"lifecycle": {"status": "REJECTED", "human_approval": "PENDING"}}),
                             ("verdict", {"verdict": "REJECTED"}),
                             ("verdict", {"verdict": None}),
                             ("review", {"lifecycle": {"status": "APPROVED", "human_approval": "PENDING"}}),
                             ("verdict", {"verified": []}), ("qa", {"type": "WRONG"})):
            data = self._evidence_task(); data["tasks"][0]["state"] = "running"
            before = json.dumps(data, sort_keys=True)
            candidate = valid(); candidate[name].update(change)
            with self.assertRaises(sdd_tasks.TaskError):
                sdd_tasks.integrate_quality_artifacts(data, "TASK-001", candidate, now=now)
            self.assertEqual(before, json.dumps(data, sort_keys=True), name)
        data = self._evidence_task(); data["tasks"][0]["state"] = "running"
        candidate = valid(); del candidate["verdict"]["verdict"]
        before = json.dumps(data, sort_keys=True)
        with self.assertRaises(sdd_tasks.TaskError):
            sdd_tasks.integrate_quality_artifacts(data, "TASK-001", candidate, now=now)
        self.assertEqual(before, json.dumps(data, sort_keys=True))


if __name__ == "__main__":
    unittest.main()
