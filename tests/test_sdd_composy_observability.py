import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "plugins" / "sdd-composy" / "scripts"))
import sdd_trace
import sdd_status
import subprocess


class TraceContractTest(unittest.TestCase):
    def event(self):
        return {"actor_id": "agent:test", "type": "task.started", "stage": "EXECUTE", "task_id": "TASK-001", "data": {"from": "ready"}}

    def test_disabled_is_noop(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self.assertIsNone(sdd_trace.record(root, self.event(), enabled=False))
            self.assertFalse((root / ".planning" / "sdd-composy" / "trace" / "events.jsonl").exists())

    def test_safe_append_and_preserve_existing_lines(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); path = root / ".planning" / "sdd-composy" / "trace" / "events.jsonl"
            first = sdd_trace.record(root, self.event(), now="2026-01-01T00:00:00Z")
            second = sdd_trace.record(root, self.event(), now="2026-01-01T00:00:01Z")
            self.assertEqual([first["sequence"], second["sequence"]], [1, 2])
            self.assertEqual(len(path.read_text().splitlines()), 2)
            self.assertEqual(sdd_trace.events(root)["source_event_count"], 2)

    def test_invalid_jsonl_and_prohibited_keys_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); path = root / ".planning" / "sdd-composy" / "trace" / "events.jsonl"; path.parent.mkdir(parents=True)
            path.write_text("not-json\n")
            with self.assertRaises(ValueError): sdd_trace.record(root, self.event())
            path.unlink()
            for key in ("prompt", "output", "environment", "secret", "model", "private_path"):
                with self.assertRaises(ValueError): sdd_trace.record(root, {**self.event(), "data": {key: "x"}})

    def test_unsafe_target_and_queries(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); outside = root.parent / (root.name + "-outside"); outside.mkdir()
            link = root / ".planning" / "sdd-composy" / "trace"; link.parent.mkdir(parents=True); link.symlink_to(outside, target_is_directory=True)
            with self.assertRaises(ValueError): sdd_trace.record(root, self.event())

    def test_summary_verify_are_read_only_and_deterministic(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); sdd_trace.record(root, self.event(), now="2026-01-01T00:00:00Z")
            before = (root / ".planning" / "sdd-composy" / "trace" / "events.jsonl").read_bytes()
            self.assertTrue(sdd_trace.verify(root)["ok"])
            self.assertEqual(sdd_trace.summary(root)["source_event_count"], 1)
            self.assertEqual(before, (root / ".planning" / "sdd-composy" / "trace" / "events.jsonl").read_bytes())

    def test_existing_trace_directory_is_restricted_before_append(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); trace = root / ".planning" / "sdd-composy" / "trace"; trace.mkdir(mode=0o755, parents=True)
            trace.chmod(0o755)
            sdd_trace.record(root, self.event(), now="2026-01-01T00:00:00Z")
            self.assertEqual(trace.stat().st_mode & 0o777, 0o700)

    def test_projection_links_and_rebuild_are_deterministic(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); sdd_trace.record(root, self.event(), now="2026-01-01T00:00:00Z")
            graph = {"nodes": [{"id": x, "kind": x.split("-")[0]} for x in
                ("RF-001", "US-001", "SC-001", "CA-001", "TASK-001", "TEST-001", "EVIDENCE-001", "MANIFEST-001", "ARTIFACT-001", "HASH-001", "VERDICT-001")],
                "links": [{"from": a, "to": b} for a, b in (("RF-001","US-001"),("US-001","SC-001"),("SC-001","CA-001"),("CA-001","TASK-001"),("TASK-001","TEST-001"),("TEST-001","EVIDENCE-001"),("EVIDENCE-001","MANIFEST-001"),("MANIFEST-001","ARTIFACT-001"),("ARTIFACT-001","HASH-001"),("HASH-001","VERDICT-001"))]}
            first = sdd_trace.build(root, graph); raw = (root / ".planning" / "sdd-composy" / "trace" / "trace.json").read_bytes()
            second = sdd_trace.build(root, graph)
            self.assertEqual(first, second); self.assertEqual(raw, (root / ".planning" / "sdd-composy" / "trace" / "trace.json").read_bytes())
            self.assertEqual(sdd_trace.query(root, "TASK-001")["node"]["id"], "TASK-001")
            self.assertTrue(sdd_trace.verify_projection(root)["ok"])

    def test_projection_rejects_dangling_and_duplicate_ids(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); sdd_trace.record(root, self.event(), now="2026-01-01T00:00:00Z")
            with self.assertRaises(ValueError): sdd_trace.build(root, {"nodes": [{"id": "RF-001"}], "links": [{"from": "RF-001", "to": "US-999"}]})
            with self.assertRaises(ValueError): sdd_trace.build(root, {"nodes": [{"id": "RF-001"}, {"id": "RF-001"}]})

    def test_projection_verification_detects_tamper_and_is_read_only(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); sdd_trace.record(root, self.event(), now="2026-01-01T00:00:00Z")
            graph = {"nodes": [{"id": "RF-001"}], "links": []}; sdd_trace.build(root, graph)
            path = root / ".planning" / "sdd-composy" / "trace" / "trace.json"; before = path.read_bytes()
            data = json.loads(path.read_text()); data["nodes"].append({"id": "RF-001"}); path.write_text(json.dumps(data))
            result = sdd_trace.verify_projection(root)
            self.assertFalse(result["ok"]); self.assertIn("duplicate graph id", result["errors"][0])
            path.write_bytes(before); data = json.loads(path.read_text()); data["projection_hash"] = "tampered"; path.write_text(json.dumps(data))
            tampered = path.read_bytes(); self.assertFalse(sdd_trace.verify_projection(root)["ok"])
            self.assertEqual(tampered, path.read_bytes())

    def test_projection_target_symlink_rejected_for_all_operations(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); sdd_trace.record(root, self.event(), now="2026-01-01T00:00:00Z")
            target = root.parent / (root.name + "-outside.json"); target.write_text("{}")
            path = root / ".planning" / "sdd-composy" / "trace" / "trace.json"; path.symlink_to(target)
            with self.assertRaises(ValueError): sdd_trace.build(root, {"nodes": [], "links": []})
            with self.assertRaises(ValueError): sdd_trace.query(root)
            self.assertFalse(sdd_trace.verify_projection(root)["ok"])

    def test_projection_publish_does_not_follow_predictable_temp_symlink(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); sdd_trace.record(root, self.event(), now="2026-01-01T00:00:00Z")
            trace = root / ".planning" / "sdd-composy" / "trace"
            outside = root / "outside"; outside.write_text("sentinel", encoding="utf-8")
            (trace / "trace.json.tmp").symlink_to(outside)
            sdd_trace.build(root, {"nodes": [], "links": []})
            self.assertEqual(outside.read_text(encoding="utf-8"), "sentinel")


class StatusContractTest(unittest.TestCase):
    def event(self):
        return {"actor_id": "agent:test", "type": "task.started", "stage": "EXECUTE", "task_id": "TASK-001", "data": {"from": "ready"}}
    def write_state(self, root, **values):
        op = root / ".planning" / "sdd-composy"; op.mkdir(parents=True, exist_ok=True)
        base = {"schema_version": "1", "stage": "EXECUTE", "next_action": "inspect the active stage"}
        base.update(values); (op / "state.json").write_text(json.dumps(base, sort_keys=True))

    def write_tasks(self, root, slug="demo", states=("pending",)):
        op = root / ".planning" / "sdd-composy" / "tasks"; op.mkdir(parents=True, exist_ok=True)
        tasks = [{"id": f"TASK-{n:03d}", "title": f"Task {n}", "state": state,
                  "dependencies": [], "acceptance_criteria": [f"CA-{n:03d}"],
                  "verification_commands": ["true"], "allowed_paths": ["src/app.py"],
                  "evidence_required": True} for n, state in enumerate(states, 1)]
        (op / f"{slug}.json").write_text(json.dumps({"schema_version": "1", "prd_slug": slug,
            "updated_at": "2026-01-01T00:00:00Z", "tasks": tasks}), encoding="utf-8")

    def test_uninitialized_and_active(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); result = sdd_status.status(root)
            self.assertEqual(result["status"], "uninitialized")
            self.assertEqual(result["next_action"], "run sdd-init")
            self.write_state(root, active_task="TASK-001")
            result = sdd_status.status(root)
            self.assertEqual(result["status"], "active")
            self.assertEqual(result["next_action"], "inspect the active stage")

    def test_blocked_divergent_looping_and_fleet(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); self.write_state(root, blockers=[{"id":"B-1","reason":"review"}])
            result = sdd_status.status(root)
            self.assertEqual(result["status"], "blocked")
            self.assertEqual(result["next_action"], "resolve the recorded blocker before continuing")
            self.write_state(root, trace={"healthy": False})
            result = sdd_status.status(root)
            self.assertEqual(result["status"], "divergent")
            self.assertEqual(result["next_action"], "verify trace integrity and resolve the reported divergence")
            self.write_state(root, trace={"healthy": True})
            op = root / ".planning" / "sdd-composy"; (op / "loops").mkdir(); (op / "loops" / "L.json").write_text(json.dumps({"status":"running"}))
            result = sdd_status.status(root)
            self.assertEqual(result["status"], "looping")
            self.assertEqual(result["next_action"], "continue the loop or stop it at its configured guard")
            (op / "fleet").mkdir(); (op / "fleet" / "F.json").write_text(json.dumps({"status":"running"}))
            result = sdd_status.status(root)
            self.assertEqual(result["status"], "fleet")
            self.assertEqual(result["next_action"], "inspect fleet members and collect their results")

    def test_malformed_json_and_next_action_contract(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); op = root / ".planning" / "sdd-composy"; op.mkdir(parents=True)
            (op / "state.json").write_text("{broken", encoding="utf-8")
            result = sdd_status.status(root)
            self.assertEqual(result["status"], "malformed")
            self.assertEqual(result["next_action"], "repair the malformed source manually, then rerun sdd-status")
            (op / "state.json").unlink(); (op / "state.json").symlink_to(op / "missing-state.json")
            result = sdd_status.status(root)
            self.assertEqual(result["status"], "malformed")
            self.assertEqual(result["next_action"], "repair the malformed source manually, then rerun sdd-status")

    def test_malformed_markdown_and_symlink_are_fail_closed(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); task = root / "tasks"; task.mkdir(); (task / "task-001.md").write_text("not frontmatter")
            result = sdd_status.status(root); self.assertEqual(result["status"], "malformed"); self.assertEqual(result["sources"]["tasks"]["state"], "malformed")
            (task / "task-001.md").unlink(); outside = root.parent / (root.name + "-outside.md"); outside.write_text("x"); (task / "task-001.md").symlink_to(outside)
            result = sdd_status.status(root); self.assertEqual(result["status"], "malformed"); self.assertEqual(result["sources"]["tasks"]["state"], "unsafe_symlink")

    def test_cli_json_text_deterministic_and_read_only(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); before = {p: p.read_bytes() for p in root.rglob("*") if p.is_file()}
            script = ROOT / "plugins" / "sdd-composy" / "scripts" / "sdd_status.py"
            a = subprocess.run([sys.executable, str(script), str(root), "--json"], capture_output=True, text=True, check=True)
            b = subprocess.run([sys.executable, str(script), str(root)], capture_output=True, text=True, check=True)
            self.assertEqual(json.loads(a.stdout)["status"], "uninitialized")
            self.assertIn("uninitialized", b.stdout); self.assertEqual(a.stdout, subprocess.run([sys.executable, str(script), str(root), "--json"], capture_output=True, text=True, check=True).stdout)
            self.assertEqual(before, {p: p.read_bytes() for p in root.rglob("*") if p.is_file()})

    def test_broken_projection_symlink_fails_closed_and_is_unchanged(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); (root / ".planning" / "sdd-composy" / "trace").mkdir(parents=True); path = root / ".planning" / "sdd-composy" / "trace" / "trace.json"
            path.symlink_to(root / "missing-trace.json")
            before = path.read_bytes() if path.exists() else os.readlink(path).encode()
            with self.assertRaises(ValueError): sdd_trace.build(root, {"nodes": [], "links": []})
            with self.assertRaises(ValueError): sdd_trace.query(root)
            result = sdd_trace.verify_projection(root); self.assertFalse(result["ok"])
            self.assertEqual(before, os.readlink(path).encode())

    def test_broken_status_inputs_are_unsafe_not_missing(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); op = root / ".planning" / "sdd-composy"; op.mkdir(parents=True)
            for name in ("state.json", "loops", "fleet"):
                (op / name).symlink_to(op / ("missing-" + name))
            (root / "tasks").symlink_to(root / "missing-tasks", target_is_directory=True)
            (root / ".planning" / "sdd-composy" / "trace").mkdir(); (root / ".planning" / "sdd-composy" / "trace" / "events.jsonl").symlink_to(root / "missing-events.jsonl")
            result = sdd_status.status(root)
            self.assertEqual(result["status"], "malformed")
            for source in ("global", "loops", "fleet", "tasks", "trace"):
                self.assertEqual(result["sources"][source]["state"], "unsafe_symlink")
            self.assertNotEqual(result["sources"]["trace"]["state"], "missing")

    def test_status_rejects_each_controlled_symlink_ancestor(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); outside = root.parent / (root.name + "-outside"); (outside / "sdd-composy").mkdir(parents=True)
            (outside / "sdd-composy" / "config.json").write_text(json.dumps({"schema_version": "1"}))
            (root / ".planning").symlink_to(outside, target_is_directory=True)
            result = sdd_status.status(root)
            self.assertEqual(result["status"], "malformed")
            for source in ("config", "global", "tasks", "trace", "loops", "fleet"):
                self.assertEqual(result["sources"][source]["state"], "unsafe_symlink", source)
                self.assertEqual(result["sources"][source]["confidence"], "low", source)
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); planning = root / ".planning"; planning.mkdir()
            outside = root.parent / (root.name + "-operational"); outside.mkdir()
            (planning / "sdd-composy").symlink_to(outside, target_is_directory=True)
            result = sdd_status.status(root)
            self.assertEqual(result["status"], "malformed")
            self.assertTrue(all(source["state"] == "unsafe_symlink" for source in result["sources"].values()))

    def test_trace_directory_symlink_is_unsafe_not_divergent(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); op = root / ".planning" / "sdd-composy"; op.mkdir(parents=True)
            outside = root.parent / (root.name + "-trace"); outside.mkdir()
            (op / "trace").symlink_to(outside, target_is_directory=True)
            result = sdd_status.status(root)
            self.assertEqual(result["status"], "malformed")
            self.assertEqual(result["sources"]["trace"]["state"], "unsafe_symlink")

    def test_loop_and_fleet_non_object_json_fail_closed(self):
        for source in ("loops", "fleet"):
            with self.subTest(source=source), tempfile.TemporaryDirectory() as d:
                root = Path(d); directory = root / ".planning" / "sdd-composy" / source; directory.mkdir(parents=True)
                (directory / "bad.json").write_text("[]", encoding="utf-8")
                result = sdd_status.status(root)
                self.assertEqual(result["status"], "malformed")
                self.assertEqual(result["sources"][source]["state"], "malformed")
                self.assertEqual(result["sources"][source]["confidence"], "low")

    def test_projection_verification_detects_source_event_divergence(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); sdd_trace.record(root, self.event(), now="2026-01-01T00:00:00Z")
            sdd_trace.build(root, {"nodes": [], "links": []})
            path = root / ".planning" / "sdd-composy" / "trace" / "trace.json"; data = json.loads(path.read_text()); data["source_event_count"] = 0
            path.write_text(json.dumps(data))
            self.assertFalse(sdd_trace.verify_projection(root)["ok"])

    def test_malformed_status_has_priority_over_running_tasks_loop_and_fleet(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); op = root / ".planning" / "sdd-composy"; op.mkdir(parents=True)
            (op / "config.json").write_text("{broken", encoding="utf-8")
            self.write_tasks(root, states=("running",))
            (op / "loops").mkdir(); (op / "loops" / "L.json").write_text(json.dumps({"status": "running"}))
            (op / "fleet").mkdir(); (op / "fleet" / "F.json").write_text(json.dumps({"status": "running"}))
            result = sdd_status.status(root)
            self.assertEqual(result["status"], "malformed")
            self.assertEqual(result["sources"]["config"]["state"], "malformed")

    def test_empty_or_missing_task_frontmatter_is_malformed_and_low_confidence(self):
        for body in ("---\ntype: TASK\n---\n", "---\ntype: TASK\ntask: {}\n---\n"):
            with self.subTest(body=body), tempfile.TemporaryDirectory() as d:
                root = Path(d); task = root / "tasks" / "prd-demo"; task.mkdir(parents=True)
                (task / "task-001.md").write_text(body, encoding="utf-8")
                result = sdd_status.status(root)
                self.assertEqual(result["status"], "malformed")
                self.assertEqual(result["sources"]["tasks"]["confidence"], "low")

    def test_canonical_task_queue_filters_feature_and_complete_is_not_active(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); self.write_tasks(root, "alpha", ("complete",)); self.write_tasks(root, "beta", ("ready",))
            alpha = sdd_status.status(root, feature="alpha", include_tasks=True)
            beta = sdd_status.status(root, feature="beta", include_tasks=True)
            self.assertEqual(alpha["status"], "active")
            self.assertEqual(alpha["task_summary"][0]["prd_slug"], "alpha")
            self.assertFalse(alpha["task_summary"][0]["has_ready_task"])
            self.assertTrue(beta["task_summary"][0]["has_ready_task"])
            self.assertEqual({x["prd_slug"] for x in sdd_status.status(root, include_tasks=True)["task_summary"]}, {"alpha", "beta"})

    def test_status_reads_operational_trace_and_does_not_mutate_sources(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); op = root / ".planning" / "sdd-composy"; op.mkdir(parents=True)
            (op / "config.json").write_text(json.dumps({"schema_version": "1", "language": "en-US"}))
            self.write_tasks(root)
            sdd_trace.record(root, self.event(), now="2026-01-01T00:00:00Z")
            sentinel = root / "sentinel"; sentinel.write_text("keep")
            before = {p: p.read_bytes() for p in root.rglob("*") if p.is_file()}
            result = sdd_status.status(root)
            after = {p: p.read_bytes() for p in root.rglob("*") if p.is_file()}
            self.assertEqual(result["sources"]["trace"]["value"]["source_event_count"], 1)
            self.assertEqual(before, after)


class FleetInteractiveDashboardTest(unittest.TestCase):
    DASHBOARD = ROOT / "plugins" / "sdd-composy" / "scripts" / "fleet" / "dashboard.sh"

    def invoke(self, root, *extra):
        return subprocess.run(
            [str(self.DASHBOARD), "--root", str(root), "--fleet-id", "demo", "--json", *extra],
            capture_output=True, text=True)

    def test_projects_authoritative_interaction_and_bound_loop(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); members = root / ".planning/sdd-composy/fleet/demo/members"
            members.mkdir(parents=True)
            record = {
                "id": "MEMBER-01", "task_id": "TASK-006", "runtime": "codex", "ui": "tmux",
                "status": "pending", "started_at": "top-level-is-not-authoritative",
                "interaction": {
                    "state": "awaiting_human", "started_at": "2026-09-12T00:00:00Z",
                    "updated_at": "2026-09-12T00:05:00Z", "next_action": "Approve LOOP evidence",
                    "loop": {"id": "loop-demo-task-006", "task_id": "TASK-006"},
                    "handle": {"driver": "tmux", "session_name": "fleet-demo", "pane_id": "%6"},
                },
            }
            (members / "MEMBER-01.json").write_text(json.dumps(record), encoding="utf-8")
            result = self.invoke(root)
            self.assertEqual(result.returncode, 0, result.stderr)
            member = json.loads(result.stdout)["members"][0]
            self.assertEqual(member, {
                "runtime": "codex", "ui": "tmux", "member": "MEMBER-01", "task": "TASK-006",
                "loop": "loop-demo-task-006", "state": "awaiting_human",
                "handle": {"driver": "tmux", "session_name": "fleet-demo", "pane_id": "%6"},
                "timestamps": {"started_at": "2026-09-12T00:00:00Z", "updated_at": "2026-09-12T00:05:00Z"},
                "next_action": "Approve LOOP evidence",
            })

    def test_missing_optional_fields_remain_absent_and_values_are_sanitized(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); members = root / ".planning/sdd-composy/fleet/demo/members"
            members.mkdir(parents=True)
            record = {
                "id": "MEMBER\n01", "task_id": "TASK\t006", "runtime": "co\u001bdex", "ui": "cmux\r",
                "interaction": {"state": "running\nforged", "started_at": "2026-09-12T00:00:00Z\nBAD"},
            }
            (members / "member.json").write_text(json.dumps(record), encoding="utf-8")
            before = (members / "member.json").read_bytes()
            result = self.invoke(root)
            self.assertEqual(result.returncode, 0, result.stderr)
            member = json.loads(result.stdout)["members"][0]
            self.assertEqual(member["member"], "MEMBER 01")
            self.assertEqual(member["task"], "TASK 006")
            self.assertEqual(member["runtime"], "co dex")
            self.assertEqual(member["ui"], "cmux")
            self.assertEqual(member["state"], "running forged")
            self.assertEqual(member["timestamps"], {"started_at": "2026-09-12T00:00:00Z BAD"})
            self.assertNotIn("loop", member)
            self.assertNotIn("handle", member)
            self.assertNotIn("next_action", member)
            self.assertEqual(before, (members / "member.json").read_bytes())


class QuickContractTest(unittest.TestCase):
    BASE = ROOT / "plugins" / "sdd-composy"

    def test_quick_contract_and_report_are_okf_and_linked(self):
        for name, kind in (("quick-contract.md", "QUICK_CONTRACT"), ("quick-report.md", "QUICK_REPORT")):
            text = (self.BASE / "templates" / name).read_text()
            self.assertIn("okf_version: \"0.2\"", text)
            self.assertIn(f"type: {kind}", text)
            self.assertIn("verified:", text)
            self.assertIn("sdd-composy", text)

    def test_quick_reference_enforces_scope_tdd_forbidden_and_escalation(self):
        text = (self.BASE / "references" / "quick.md").read_text().lower()
        for phrase in ("five", "architecture", "migration", "destructive", "unknown verification",
                       "failing test", "tdd", "escalat", "normal task", "evidence", "trace"):
            self.assertIn(phrase, text)

    def test_quick_skill_is_portable_and_integrates_normal_task_trace_and_verdict(self):
        skill = (self.BASE / "skills" / "sdd-quick" / "SKILL.md").read_text()
        for phrase in ("$sdd-quick", "sdd_tasks.py", "sdd_trace.py", "Q-ID", "five",
                       "CONFIRM-SDD-SYNC", "failing test", "ESCALATE", "verified verdict"):
            self.assertIn(phrase, skill)
        self.assertTrue((self.BASE / "skills" / "sdd-quick" / "agents" / "openai.yaml").exists())
