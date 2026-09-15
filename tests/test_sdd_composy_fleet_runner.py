import importlib.util, json, os, subprocess, tempfile, unittest
from pathlib import Path
from tests.test_sdd_composy import assert_schema_valid

ROOT = Path(__file__).parents[1]
FLEET = ROOT / "plugins/sdd-composy/scripts/fleet"
OBSERVER = FLEET / "interactive_observer.py"

class FleetRunnerTest(unittest.TestCase):
    def observer(self):
        self.assertTrue(OBSERVER.is_file(), "production observer is missing")
        spec=importlib.util.spec_from_file_location("sdd_fleet_interactive_observer",OBSERVER)
        module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        return module

    def source(self, runtime, code):
        script = FLEET / f"engine-{runtime}.sh"
        return subprocess.run(["bash", "-c", f'. "{script}"; {code}'], capture_output=True, text=True)

    def interactive_fixture(self, folder, *, loop_task="TASK-001", task_state="ready", loop_status="running"):
        root=Path(folder)/"repo"; work=root/"work"; work.mkdir(parents=True)
        contract=root/".planning/sdd-composy/tasks/demo.json"; contract.parent.mkdir(parents=True)
        contract.write_text(json.dumps({"schema_version":"1","prd_slug":"demo","updated_at":"2026-09-12T00:00:00Z","tasks":[{"id":"TASK-001","title":"Demo","state":task_state,"dependencies":[],"acceptance_criteria":["CA-001"],"verification_commands":["true"],"allowed_paths":["README"],"evidence_required":True}]}))
        loops=root/".planning/sdd-composy/loops"; loops.mkdir(parents=True)
        stamp="2026-09-12T00:00:00Z"; loop_id="loop-fleet-member"
        loop={"schema_version":"1","id":loop_id,"task_id":loop_task,"status":loop_status,"iteration":0,"max_iterations":3,"started_at":stamp,"updated_at":stamp,"stages":[{"name":name,"status":"pending"} for name in ("EXECUTE","QA","EVIDENCE","REVIEW","VERIFY")]}
        if loop_status != "running": loop.update(stop_reason="Completed",finished_at=stamp)
        (loops/f"{loop_id}.json").write_text(json.dumps(loop))
        member=root/"member.json"
        digest=__import__("hashlib").sha256(contract.read_bytes()).hexdigest()
        member.write_text(json.dumps({"schema_version":"2","id":"member-1","task_id":"TASK-001","slug":"member-1","status":"pending","runtime":"codex","ui":"cmux","branch":"fleet/member-1","worktree_path":str(work),"repository_root":str(root),"started_at":stamp,"updated_at":stamp,"owner":{"kind":"sdd-composy-fleet","fleet_id":"fleet-1","member_id":"member-1"},"resources":{"branch":"fleet/member-1","worktree_path":str(work),"port":43001,"compose_project":"fleet-1-member-1","compose_file":".planning/sdd-composy/fleet/fleet-1/docker-compose.yml","compose_allocated":False},"contract_path":str(contract),"contract_sha256":digest,"interaction":{"state":"starting","started_at":stamp,"updated_at":stamp,"loop":{"id":loop_id,"task_id":"TASK-001"},"transport":{"session_name":"fleet-session","pane_id":"%7","handle":"owned-handle"}},"evidence":{"path":"evidence/kept.json","sha256":"abc"},"x-preserved":{"yes":True}}))
        return root,work,member

    def run_interactive(self, folder, **fixture):
        root,work,member=self.interactive_fixture(folder,**fixture); fake=Path(folder)/"bin"; fake.mkdir()
        capture=Path(folder)/"prompt"; (fake/"codex").write_text("#!/bin/sh\nfor value do last=$value; done\nprintf '%s' \"$last\" > \"$CAPTURE\"\n")
        (fake/"codex").chmod(0o755)
        result=subprocess.run([str(FLEET/"interactive-run.sh"),str(member),str(work)],env={**os.environ,"PATH":str(fake)+":"+os.environ["PATH"],"CAPTURE":str(capture)},capture_output=True,text=True)
        return result,json.loads(member.read_text()),capture

    def test_interactive_wrapper_consumes_one_bound_loop_without_starting_another(self):
        with tempfile.TemporaryDirectory() as d:
            result,member,prompt=self.run_interactive(d)
            self.assertEqual(result.returncode,0,result.stderr); self.assertEqual(member["interaction"]["state"],"awaiting_human")
            self.assertEqual(member["interaction"]["loop"]["id"],"loop-fleet-member"); self.assertEqual(member["x-preserved"],{"yes":True})
            text=prompt.read_text(); self.assertIn("fleet-1",text); self.assertIn("member-1",text); self.assertIn("TASK-001",text); self.assertIn("loop-fleet-member",text)
            self.assertNotIn(" sdd-loop start ",text)

    def test_observer_publishes_at_exactly_300_with_live_original_parent_without_signals_or_terminal(self):
        with tempfile.TemporaryDirectory() as d:
            _,_,member=self.interactive_fixture(d); record=json.loads(member.read_text()); record["interaction"]["state"]="running"; member.write_text(json.dumps(record))
            class Clock:
                value=0.0
                def monotonic(self): return self.value
                def sleep(self,seconds): self.value += seconds
            clock=Clock(); checks=[]
            outcome=self.observer().observe(member,4242,clock=clock.monotonic,sleep=clock.sleep,parent_alive=lambda pid: checks.append(("alive",pid)) or True,parent_is_original=lambda pid: checks.append(("parent",pid)) or True)
            updated=json.loads(member.read_text())
            self.assertEqual(clock.value,300.0); self.assertEqual(outcome,"awaiting_human"); self.assertEqual(updated["interaction"]["state"],"awaiting_human")
            self.assertEqual(updated["interaction"]["next_action"],"resume-session"); self.assertNotIn("terminal",updated["interaction"]); self.assertNotIn("signal",updated["interaction"])
            self.assertTrue(all(pid==4242 for _,pid in checks))

    def test_observer_cancels_when_original_parent_relationship_ends(self):
        with tempfile.TemporaryDirectory() as d:
            _,_,member=self.interactive_fixture(d); record=json.loads(member.read_text()); record["interaction"]["state"]="running"; member.write_text(json.dumps(record)); before=member.read_bytes()
            outcome=self.observer().observe(member,4242,clock=lambda:0.0,sleep=lambda _:None,parent_alive=lambda _:True,parent_is_original=lambda _:False)
            self.assertEqual(outcome,"cancelled"); self.assertEqual(member.read_bytes(),before)

    def test_interactive_wrapper_rejects_pending_task_before_runtime(self):
        with tempfile.TemporaryDirectory() as d:
            result,member,prompt=self.run_interactive(d,task_state="pending")
            self.assertNotEqual(result.returncode,0); self.assertEqual(member["interaction"]["state"],"blocked"); self.assertFalse(prompt.exists())

    def test_interactive_wrapper_guards_sensitive_basename_patterns_before_read(self):
        source=(FLEET/"interactive-run.sh").read_text()
        self.assertIn("sensitive_contract_name",source)
        guard=source.index("sensitive_contract_name")
        read=source.index("contract.read_bytes()")
        self.assertLess(guard,read)
        for pattern in (".env", "credentials", "private-key", "certificate", "token", "secret"):
            self.assertIn(pattern,source[guard:read])

    def test_interactive_wrapper_requires_projection_filename_to_match_prd_slug(self):
        with tempfile.TemporaryDirectory() as d:
            root,work,member=self.interactive_fixture(d); record=json.loads(member.read_text()); old=Path(record["contract_path"]); renamed=old.with_name("sentinel-mismatch.json"); old.rename(renamed)
            record["contract_path"]=str(renamed); record["contract_sha256"]=__import__("hashlib").sha256(renamed.read_bytes()).hexdigest(); member.write_text(json.dumps(record))
            fake=Path(d)/"bin"; fake.mkdir(); called=Path(d)/"called"; (fake/"codex").write_text("#!/bin/sh\ntouch \"$CALLED\"\n"); (fake/"codex").chmod(0o755)
            result=subprocess.run([str(FLEET/"interactive-run.sh"),str(member),str(work)],env={**os.environ,"PATH":str(fake)+":"+os.environ["PATH"],"CALLED":str(called)},capture_output=True,text=True)
            self.assertNotEqual(result.returncode,0); self.assertFalse(called.exists()); self.assertEqual(json.loads(member.read_text())["interaction"]["state"],"blocked")

    def test_interactive_wrapper_rejects_cross_bound_loop(self):
        with tempfile.TemporaryDirectory() as d:
            result,member,prompt=self.run_interactive(d,loop_task="TASK-002")
            self.assertNotEqual(result.returncode,0); self.assertEqual(member["interaction"]["state"],"blocked"); self.assertFalse(prompt.exists())

    def test_interactive_wrapper_requires_loop_proof_for_completion(self):
        with tempfile.TemporaryDirectory() as d:
            result,member,_=self.run_interactive(d,loop_status="completed")
            self.assertNotEqual(result.returncode,0); self.assertEqual(member["interaction"]["state"],"inconclusive")

    def test_interactive_wrapper_interruption_preserves_member_and_loop(self):
        with tempfile.TemporaryDirectory() as d:
            root,work,member=self.interactive_fixture(d); fake=Path(d)/"bin"; fake.mkdir()
            (fake/"codex").write_text("#!/bin/sh\nkill -TERM $PPID\n") ; (fake/"codex").chmod(0o755)
            result=subprocess.run([str(FLEET/"interactive-run.sh"),str(member),str(work)],env={**os.environ,"PATH":str(fake)+":"+os.environ["PATH"]},capture_output=True,text=True)
            record=json.loads(member.read_text())
            self.assertNotEqual(result.returncode,0); self.assertEqual(record["interaction"]["state"],"running")
            self.assertTrue((root/".planning/sdd-composy/loops/loop-fleet-member.json").is_file()); self.assertTrue(work.is_dir())
            self.assertEqual(record["branch"],"fleet/member-1"); self.assertEqual(record["interaction"]["transport"],{"session_name":"fleet-session","pane_id":"%7","handle":"owned-handle"})
            self.assertEqual(record["evidence"],{"path":"evidence/kept.json","sha256":"abc"})

    def test_headless_runner_consumes_bound_loop_identity(self):
        text=(FLEET/"run.sh").read_text()
        self.assertIn('BOUND_LOOP_ID',text); self.assertIn('orchestrate(',text); self.assertNotIn('sdd_loop.start',text)

    def test_headless_bound_terminal_loop_does_not_run_distinct_fleet_lifecycle(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/"repo"; root.mkdir(); subprocess.run(["git","init","-q",str(root)],check=True)
            subprocess.run(["git","-C",str(root),"config","user.email","test@example.invalid"],check=True); subprocess.run(["git","-C",str(root),"config","user.name","Test"],check=True)
            (root/"README").write_text("x\n"); subprocess.run(["git","-C",str(root),"add","."],check=True); subprocess.run(["git","-C",str(root),"commit","-qm","base"],check=True)
            base=subprocess.check_output(["git","-C",str(root),"branch","--show-current"],text=True).strip(); contract=root/"contract.json"
            contract.write_text(json.dumps({"id":"TASK-001","state":"ready","dependencies":[],"acceptance_criteria":["CA-001"],"verification_commands":["true"],"allowed_paths":["README"]}))
            launched=subprocess.run([str(FLEET/"launch.sh"),"--prepare-only","--runtime","codex","--root",str(root),"--fleet-id","demo","--base-branch",base,"--task",str(contract)],capture_output=True,text=True); self.assertEqual(launched.returncode,0,launched.stderr)
            member=root/".planning/sdd-composy/fleet/demo/members/TASK-001.json"; record=json.loads(member.read_text()); work=Path(record["worktree_path"])
            loop_id="loop-demo-task-001"; loops=root/".planning/sdd-composy/loops"; loops.mkdir(parents=True); stamp="2026-09-12T00:00:00Z"
            (loops/f"{loop_id}.json").write_text(json.dumps({"schema_version":"1","id":loop_id,"task_id":"TASK-001","status":"environment_failure","iteration":0,"max_iterations":3,"started_at":stamp,"updated_at":stamp,"finished_at":stamp,"stop_reason":"environment_failure","stages":[{"name":name,"status":"pending"} for name in ("EXECUTE","QA","EVIDENCE","REVIEW","VERIFY")]}))
            record["interaction"]={"state":"starting","started_at":stamp,"updated_at":stamp,"loop":{"id":loop_id,"task_id":"TASK-001"}}; member.write_text(json.dumps(record))
            fake=Path(d)/"bin"; fake.mkdir(); called=Path(d)/"called"; (fake/"codex").write_text("#!/bin/sh\ntouch \"$CALLED\"\n"); (fake/"codex").chmod(0o755)
            result=subprocess.run([str(FLEET/"run.sh"),record["slug"],str(work)],env={**os.environ,"PATH":str(fake)+":"+os.environ["PATH"],"CALLED":str(called),"SDD_FLEET_RUNTIME":"codex","SDD_FLEET_MEMBER_FILE":str(member)},capture_output=True,text=True)
            self.assertNotEqual(result.returncode,0); self.assertFalse(called.exists(),result.stderr); self.assertFalse((work/".planning/sdd-composy/fleet-status.json").exists())

    def test_runtime_mismatch_is_rejected(self):
        runner = FLEET / "run.sh"
        r = subprocess.run([str(runner), "demo", "/tmp/no-such-worktree"], env={**os.environ, "SDD_FLEET_RUNTIME":"unknown"}, capture_output=True, text=True)
        self.assertNotEqual(r.returncode, 0); self.assertIn("unsupported fleet runtime", r.stderr)

    def test_missing_runtime_and_legacy_member_require_migration(self):
        runner = FLEET / "run.sh"
        r=subprocess.run([str(runner),"demo","/tmp/no-such-worktree"],env={k:v for k,v in os.environ.items() if k != "SDD_FLEET_RUNTIME"},capture_output=True,text=True)
        self.assertNotEqual(r.returncode,0); self.assertIn("runtime is required",r.stderr)

    def test_claude_code_record_selects_claude_adapter_only(self):
        runner=(FLEET/"run.sh").read_text()
        self.assertIn('claude-code) CLI_RUNTIME=claude',runner)
        self.assertIn('loop-engine-{runtime}.py',runner)

    def test_member_from_another_repository_is_rejected_before_provider(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/"repo"; root.mkdir(); subprocess.run(["git","init","-q",str(root)],check=True)
            subprocess.run(["git","-C",str(root),"config","user.email","test@example.invalid"],check=True); subprocess.run(["git","-C",str(root),"config","user.name","Test"],check=True)
            (root/"README").write_text("x\n"); subprocess.run(["git","-C",str(root),"add","."],check=True); subprocess.run(["git","-C",str(root),"commit","-qm","base"],check=True)
            base=subprocess.check_output(["git","-C",str(root),"branch","--show-current"],text=True).strip(); contract=root/"contract.json"
            contract.write_text(json.dumps({"id":"TASK-001","state":"ready","dependencies":[],"acceptance_criteria":["ok"],"verification_commands":["true"],"allowed_paths":["README"],"contract_path":str(contract)}))
            launched=subprocess.run([str(FLEET/"launch.sh"),"--prepare-only","--runtime","codex","--root",str(root),"--fleet-id","demo","--base-branch",base,"--task",str(contract)],capture_output=True,text=True); self.assertEqual(launched.returncode,0,launched.stderr)
            member=root/".planning/sdd-composy/fleet/demo/members/TASK-001.json"; record=json.loads(member.read_text()); record["repository_root"]=str(Path(d)/"foreign"); member.write_text(json.dumps(record))
            called=Path(d)/"called"; fake=Path(d)/"bin"; fake.mkdir(); (fake/"codex").write_text("#!/bin/sh\ntouch '"+str(called)+"'\n"); (fake/"codex").chmod(0o755)
            r=subprocess.run([str(FLEET/"run.sh"),record["slug"],record["worktree_path"]],env={**os.environ,"PATH":str(fake)+":/usr/bin:/bin","SDD_FLEET_RUNTIME":"codex","SDD_FLEET_MEMBER_FILE":str(member)},capture_output=True,text=True)
            self.assertNotEqual(r.returncode,0); self.assertFalse(called.exists())

if __name__ == "__main__": unittest.main()
