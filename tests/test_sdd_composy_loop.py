import json, tempfile, unittest, sys
import importlib.util
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1] / "plugins/sdd-composy/scripts"))
import sdd_loop

def _adapter(name):
    path = Path(__file__).parents[1] / "plugins/sdd-composy/scripts" / name
    spec = importlib.util.spec_from_file_location(name.replace("-", "_"), path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module); return module

class LoopTests(unittest.TestCase):
    def setUp(self): self.tmp=tempfile.TemporaryDirectory(); self.root=Path(self.tmp.name)
    def tearDown(self): self.tmp.cleanup()

    def test_progress_fingerprint_is_stable_and_ignores_metadata(self):
        a = {"diff": {"files": ["a.py"]}, "failure": {"test": "x"}, "at": "one"}
        b = {"diff": {"files": ["a.py"]}, "failure": {"test": "x"}, "at": "two"}
        self.assertEqual(sdd_loop.progress_fingerprint(a), sdd_loop.progress_fingerprint(b))

    def test_correction_stops_on_all_non_progress_guards(self):
        cases = [
            ("identical_diff", {"diff": "same"}, {"diff": "same"}),
            ("identical_failure", {"failure": "red"}, {"failure": "red"}),
            ("scope_drift", {"scope": ["approved"], "scope_changed": True}, {}),
            ("new_architecture", {"architecture_changed": True}, {}),
            ("destructive_request", {"destructive": True}, {}),
            ("repeated_environment_failure", {"environment": "offline", "environment_failure": True}, {}),
        ]
        for reason, current, previous in cases:
            with self.subTest(reason=reason):
                if reason == "repeated_environment_failure":
                    previous = {"environment": "offline", "environment_failure": True}
                result = sdd_loop.correction_decision(previous, current)
                self.assertEqual(result, {"status": "needs_human", "reason": reason})
        self.assertEqual(sdd_loop.correction_decision({}, {"verdict": "rejected"}, rejection_count=2),
                         {"status": "needs_human", "reason": "third_rejection"})

    def test_progress_allows_bounded_correction_when_changed(self):
        result = sdd_loop.correction_decision({"diff": "old", "failure": "old"},
                                               {"diff": "new", "failure": "new"})
        self.assertEqual(result["status"], "correction")
        self.assertEqual(result["reason"], "progress")
    def test_start_defaults_and_atomic_record(self):
        x=sdd_loop.start(self.root,"TASK-001",now="2026-01-01T00:00:00Z"); self.assertEqual(x["status"],"running"); self.assertEqual(x["max_iterations"],3)
        self.assertEqual(sdd_loop.status(self.root,x["id"]),x)
    def test_caps_and_transitions(self):
        x=sdd_loop.start(self.root,"TASK-001",max_iterations=2,now="2026-01-01T00:00:00Z"); x=sdd_loop.continue_loop(self.root,x["id"],now="2026-01-01T00:01:00Z"); self.assertEqual(x["iteration"],1); x=sdd_loop.continue_loop(self.root,x["id"],now="2026-01-01T00:02:00Z"); self.assertEqual(x["status"],"iteration_cap")
        with self.assertRaises(sdd_loop.LoopError): sdd_loop.continue_loop(self.root,x["id"])
    def test_terminal_reasons_cancel_and_invalid_cap(self):
        with self.assertRaises(sdd_loop.LoopError): sdd_loop.start(self.root,"TASK-001",max_iterations=4)
        x=sdd_loop.start(self.root,"TASK-002"); x=sdd_loop.cancel(self.root,x["id"],reason="human stop"); self.assertEqual(x["status"],"cancelled"); self.assertEqual(x["stop_reason"],"human stop")
    def test_outcomes(self):
        x=sdd_loop.start(self.root,"TASK-003"); x=sdd_loop.continue_loop(self.root,x["id"],outcome="scope_expansion"); self.assertEqual(x["status"],"scope_expansion"); self.assertIn("finished_at",x)
    def test_all_terminal_reasons_and_immutability(self):
        reasons=["missing_progress","scope_expansion","architectural_ambiguity","destructive_action","external_authorization","environment_failure"]
        for index, reason in enumerate(reasons, 10):
            x=sdd_loop.start(self.root, f"TASK-{index:03d}", loop_id=f"loop-{index}")
            before=(self.root/".planning/sdd-composy/loops"/f"loop-{index}.json").read_bytes()
            y=sdd_loop.continue_loop(self.root,x["id"],outcome=reason)
            self.assertEqual(y["status"],reason); self.assertNotEqual(before,(self.root/".planning/sdd-composy/loops"/f"loop-{index}.json").read_bytes())
            after=(self.root/".planning/sdd-composy/loops"/f"loop-{index}.json").read_bytes()
            with self.assertRaises(sdd_loop.LoopError): sdd_loop.continue_loop(self.root,x["id"])
            self.assertEqual(after,(self.root/".planning/sdd-composy/loops"/f"loop-{index}.json").read_bytes())
    def test_directory_symlink_is_rejected(self):
        (self.root/".planning").mkdir(); target=self.root/"outside"; target.mkdir()
        (self.root/".planning/sdd-composy").symlink_to(target, target_is_directory=True)
        with self.assertRaises(sdd_loop.LoopError): sdd_loop.start(self.root,"TASK-099")
    def test_invalid_task_and_caps(self):
        for cap in (0,4,-1):
            with self.assertRaises(sdd_loop.LoopError): sdd_loop.start(self.root,"TASK-001",max_iterations=cap)
        with self.assertRaises(sdd_loop.LoopError): sdd_loop.start(self.root,"bad")

    def test_resume_returns_first_unpublished_stage_without_replaying(self):
        x=sdd_loop.start(self.root,"TASK-100",now="2026-01-01T00:00:00Z")
        sdd_loop.publish_stage(self.root,x["id"],"EXECUTE",artifact={"id":"a"},evidence={"status":"passed"},now="2026-01-01T00:01:00Z")
        resumed=sdd_loop.resume(self.root,x["id"])
        self.assertEqual(resumed["next_stage"],"QA")
        self.assertEqual(resumed["completed_stages"],["EXECUTE"])

    def test_resume_rejects_stale_or_unbound_stage_evidence(self):
        x=sdd_loop.start(self.root,"TASK-101")
        with self.assertRaises(sdd_loop.LoopError):
            sdd_loop.publish_stage(self.root,x["id"],"EXECUTE",artifact={"id":"wrong"},evidence={},now="2026-01-01T00:00:00Z")
        sdd_loop.publish_stage(self.root,x["id"],"EXECUTE",artifact={"id":"a"},evidence={"status":"passed"},now="2026-01-01T00:00:00Z")
        path=self.root/".planning/sdd-composy/loops"/f"{x['id']}.json"
        data=json.loads(path.read_text()); data["stages"][0]["artifact"]["id"]="changed"; path.write_text(json.dumps(data))
        with self.assertRaises(sdd_loop.LoopError): sdd_loop.resume(self.root,x["id"])

    def test_resume_interruption_before_publication_does_not_mark_stage(self):
        x=sdd_loop.start(self.root,"TASK-102")
        resumed=sdd_loop.resume(self.root,x["id"])
        self.assertEqual(resumed["next_stage"],"EXECUTE")
        self.assertEqual(resumed["completed_stages"],[])

    def test_stage_order_requires_evidence_and_artifact(self):
        x=sdd_loop.start(self.root,"TASK-103")
        with self.assertRaises(sdd_loop.LoopError):
            sdd_loop.publish_stage(self.root,x["id"],"QA",artifact={"id":"q"},evidence={"status":"passed"})

    def test_publish_rejects_backfill_when_later_stage_is_durable(self):
        x=sdd_loop.start(self.root,"TASK-104")
        path=self.root/".planning/sdd-composy/loops"/f"{x['id']}.json"
        data=json.loads(path.read_text()); data["stages"][2].update(status="complete",artifact={"id":"e"},evidence={"status":"passed"},artifact_digest=sdd_loop._digest({"id":"e"}),evidence_digest=sdd_loop._digest({"status":"passed"}))
        path.write_text(json.dumps(data, sort_keys=True))
        before=path.read_bytes()
        with self.assertRaises(sdd_loop.LoopError): sdd_loop.publish_stage(self.root,x["id"],"EXECUTE",artifact={"id":"a"},evidence={"status":"passed"})
        self.assertEqual(before,path.read_bytes())

    def test_resume_matrix_after_each_publication_boundary(self):
        x=sdd_loop.start(self.root,"TASK-105")
        for index, stage in enumerate(sdd_loop.LOOP_STAGES):
            sdd_loop.publish_stage(self.root,x["id"],stage,artifact={"stage":stage},evidence={"status":"passed"},now=f"2026-01-01T00:0{index}:00Z")
            resumed=sdd_loop.resume(self.root,x["id"])
            expected=sdd_loop.LOOP_STAGES[index+1] if index+1 < len(sdd_loop.LOOP_STAGES) else None
            self.assertEqual(resumed["next_stage"],expected)
            self.assertEqual(resumed["completed_stages"],list(sdd_loop.LOOP_STAGES[:index+1]))

    def test_failed_atomic_publication_preserves_prior_bytes(self):
        x=sdd_loop.start(self.root,"TASK-106")
        path=self.root/".planning/sdd-composy/loops"/f"{x['id']}.json"; before=path.read_bytes()
        original=sdd_loop.os.replace
        try:
            sdd_loop.os.replace=lambda *_args: (_ for _ in ()).throw(OSError("injected publish failure"))
            with self.assertRaises(OSError): sdd_loop.publish_stage(self.root,x["id"],"EXECUTE",artifact={"id":"a"},evidence={"status":"passed"})
        finally: sdd_loop.os.replace=original
        self.assertEqual(before,path.read_bytes())

    def test_publish_rejects_failed_prior_evidence_without_mutation(self):
        x=sdd_loop.start(self.root,"TASK-107")
        sdd_loop.publish_stage(self.root,x["id"],"EXECUTE",artifact={"id":"a"},evidence={"status":"passed"})
        path=self.root/".planning/sdd-composy/loops"/f"{x['id']}.json"
        data=json.loads(path.read_text()); data["stages"][0]["evidence"]={"status":"failed"}; data["stages"][0]["evidence_digest"]=sdd_loop._digest({"status":"failed"}); path.write_text(json.dumps(data, sort_keys=True)); before=path.read_bytes()
        with self.assertRaises(sdd_loop.LoopError): sdd_loop.publish_stage(self.root,x["id"],"QA",artifact={"id":"q"},evidence={"status":"passed"})
        self.assertEqual(before,path.read_bytes())

    def test_orchestrator_requires_approval_and_runs_canonical_lifecycle(self):
        with self.assertRaises(sdd_loop.LoopError): sdd_loop.orchestrate(self.root, "TASK-200", lambda _: {}, human_approved=False)
        seen, published = [], []
        def engine(contract):
            seen.append(contract["stage"])
            return {"stage": contract["stage"], "status":"completed", "message":"ok", "verdict":"passed", "evidence":{"status":"passed"}}
        result = sdd_loop.orchestrate(self.root, "TASK-200", engine, human_approved=True,
                                      task_publish=published.append, trace_publish=published.append)
        self.assertEqual(result["status"], "completed")
        self.assertEqual(seen, list(sdd_loop.LOOP_STAGES)); self.assertEqual(len(published), 10)

    def test_orchestrator_failure_has_no_publication_and_cap(self):
        published=[]
        def engine(contract):
            return {"stage":contract["stage"],"status":"failed","message":"red","verdict":"rejected","evidence":{"status":"failed"}}
        result=sdd_loop.orchestrate(self.root,"TASK-201",engine,max_iterations=1,human_approved=True,task_publish=published.append,trace_publish=published.append)
        self.assertEqual(result["status"],"iteration_cap"); self.assertEqual(published,[])

    def test_orchestrator_cancel_and_resume_existing_loop(self):
        loop=sdd_loop.start(self.root,"TASK-202",loop_id="resume-me")
        sdd_loop.publish_stage(self.root,loop["id"],"EXECUTE",artifact={"x":1},evidence={"status":"passed"})
        seen=[]
        def engine(contract):
            seen.append(contract["stage"])
            return {"stage":contract["stage"],"status":"completed","message":"ok","verdict":"passed","evidence":{"status":"passed"}}
        result=sdd_loop.orchestrate(self.root,"TASK-202",engine,loop_id="resume-me",human_approved=True)
        self.assertEqual(result["status"],"completed"); self.assertEqual(seen,list(sdd_loop.LOOP_STAGES[1:]))
        cancelled=sdd_loop.start(self.root,"TASK-203",loop_id="cancel-me")
        self.assertEqual(sdd_loop.orchestrate(self.root,"TASK-203",engine,loop_id=cancelled["id"],human_approved=True,cancel_check=lambda: True)["status"],"cancelled")

    def test_autonomous_loop_requires_explicit_approval_and_safe_stops(self):
        with self.assertRaisesRegex(sdd_loop.LoopError, "human approval"):
            sdd_loop.orchestrate(self.root, "TASK-204", lambda _: {}, human_approved=False)
        loop = sdd_loop.start(self.root, "TASK-205")
        stopped = sdd_loop.continue_loop(self.root, loop["id"], outcome="scope_expansion")
        self.assertEqual(stopped["status"], "scope_expansion")
        with self.assertRaises(sdd_loop.LoopError):
            sdd_loop.continue_loop(self.root, loop["id"], outcome="progress")

    def test_cancellation_is_durable_and_idempotent_failure_is_safe(self):
        loop = sdd_loop.start(self.root, "TASK-206")
        cancelled = sdd_loop.cancel(self.root, loop["id"], reason="operator cancellation")
        self.assertEqual(sdd_loop.status(self.root, loop["id"])["stop_reason"], "operator cancellation")
        before = (self.root / ".planning/sdd-composy/loops" / f"{loop['id']}.json").read_bytes()
        with self.assertRaises(sdd_loop.LoopError):
            sdd_loop.cancel(self.root, loop["id"])
        self.assertEqual(before, (self.root / ".planning/sdd-composy/loops" / f"{loop['id']}.json").read_bytes())

    def test_orchestrator_preserves_exact_safe_stop_reason(self):
        cases = [
            ("destructive_request", {"destructive_request": True}),
            ("scope_drift", {"scope_drift": True}),
            ("new_architecture", {"new_architecture": True}),
        ]
        for reason, flags in cases:
            with self.subTest(reason=reason):
                def engine(contract, flags=flags):
                    return {"stage": contract["stage"], "status": "failed", "message": "blocked", "verdict": "rejected", "evidence": {"status": "failed"}, **flags}
                result = sdd_loop.orchestrate(self.root, "TASK-207", engine, loop_id="loop-" + reason,
                                              max_iterations=3, human_approved=True)
                self.assertEqual(result["status"], reason)
                self.assertEqual(result["stop_reason"], reason)
                self.assertEqual(sdd_loop.status(self.root, result["id"])["stop_reason"], reason)
        calls = []
        def repeated_engine(contract):
            calls.append(contract)
            return {"stage": contract["stage"], "status": "failed", "message": "offline", "verdict": "rejected", "evidence": {"status": "failed"}, "environment_failure": True, "environment": "offline"}
        result = sdd_loop.orchestrate(self.root, "TASK-207", repeated_engine, loop_id="loop-repeated-environment-failure",
                                      max_iterations=3, human_approved=True)
        self.assertEqual(result["status"], "repeated_environment_failure")
        self.assertEqual(result["stop_reason"], "repeated_environment_failure")

    def test_orchestrator_classifies_runtime_exception_as_environment_failure_without_mutation(self):
        events = []
        def engine(_):
            raise TimeoutError("runtime timeout")
        result = sdd_loop.orchestrate(self.root, "TASK-208", engine, loop_id="loop-runtime-failure",
                                      max_iterations=3, human_approved=True,
                                      task_publish=events.append, trace_publish=events.append)
        self.assertEqual(result["status"], "environment_failure")
        self.assertEqual(result["stop_reason"], "environment_failure")
        self.assertEqual(result["next_action"], "inspect runtime environment and retry")
        self.assertEqual(events, [])
        state = sdd_loop.status(self.root, result["id"])
        self.assertTrue(all(stage["status"] == "pending" for stage in state["stages"]))

    def test_orchestrator_second_rejection_continues_correction(self):
        calls = []

        def engine(contract):
            calls.append(contract["iteration"])
            return {"stage": contract["stage"], "status": "failed", "message": "needs correction",
                    "verdict": "rejected", "evidence": {"status": "failed"},
                    "diff": f"iteration-{contract['iteration']}"}

        result = sdd_loop.orchestrate(self.root, "TASK-209", engine, max_iterations=2,
                                      human_approved=True)
        self.assertEqual(result["status"], "iteration_cap")
        self.assertEqual(calls, [1, 2])

    def test_orchestrator_third_rejection_stops_with_third_rejection(self):
        calls = []

        def engine(contract):
            calls.append(contract["iteration"])
            return {"stage": contract["stage"], "status": "failed", "message": "still rejected",
                    "verdict": "rejected", "evidence": {"status": "failed"},
                    "diff": f"iteration-{contract['iteration']}"}

        result = sdd_loop.orchestrate(self.root, "TASK-210", engine, max_iterations=3,
                                      human_approved=True)
        self.assertEqual(result["status"], "third_rejection")
        self.assertEqual(result["stop_reason"], "third_rejection")
        self.assertEqual(calls, [1, 2, 3])

class RuntimeEngineTests(unittest.TestCase):
    def setUp(self): self.tmp=tempfile.TemporaryDirectory(); self.root=Path(self.tmp.name)
    def tearDown(self): self.tmp.cleanup()
    def test_provider_vectors_are_fixed_and_isolated(self):
        codex, claude = _adapter("loop-engine-codex.py"), _adapter("loop-engine-claude.py")
        contract={"stage":"EXECUTE","task":"TASK-001"}
        self.assertEqual(codex.build_command(contract,self.root)[:3],["codex","exec","--json"])
        self.assertEqual(claude.build_command(contract,self.root)[:2],["claude","-p"])
        self.assertEqual(codex.build_command(contract,self.root)[-3],"--cd")
        self.assertEqual(claude.build_command(contract,self.root)[-2],"--add-dir")
        self.assertEqual(codex.build_command(contract,self.root)[-1],json.dumps(contract,sort_keys=True,separators=(",",":")))
    def test_strict_result_validation(self):
        mod=_adapter("loop-engine-codex.py")
        good={"stage":"QA","status":"completed","message":"ok","verdict":"passed","evidence":{}}
        self.assertEqual(mod.validate_result(good),good)
        for bad in ({**good,"extra":1},{**good,"status":"wat"},{**good,"evidence":[]},{**good,"message":""}):
            with self.assertRaises(mod.RuntimeError_): mod.validate_result(bad)
    def test_nonzero_malformed_and_timeout_are_rejected(self):
        mod=_adapter("loop-engine-codex.py"); contract={"stage":"EXECUTE"}
        scripts={"bad": "import sys; sys.exit(4)", "json": "print('no-json')", "slow": "import time; time.sleep(2)"}
        for key, body in scripts.items():
            exe=self.root/key; exe.write_text("#!/usr/bin/env python3\n"+body+"\n"); exe.chmod(0o755)
            expected="runtime exited" if key=="bad" else "malformed" if key=="json" else "timeout"
            with self.subTest(key=key), self.assertRaisesRegex(mod.RuntimeError_, expected): mod.run(contract,self.root,timeout=.05 if key=="slow" else 1,executable=str(exe))

if __name__ == "__main__": unittest.main()
