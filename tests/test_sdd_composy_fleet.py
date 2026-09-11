import hashlib, importlib.util, json, os, subprocess, tempfile, unittest
from pathlib import Path
from tests.test_sdd_composy import assert_schema_valid

ROOT = Path(__file__).parents[1]
LAUNCH = ROOT / "plugins/sdd-composy/scripts/fleet/launch.sh"
INTERACTIVE_STATE_PATH = ROOT / "plugins/sdd-composy/scripts/fleet/interactive_state.py"

def _load_interactive_state():
    spec = importlib.util.spec_from_file_location("sdd_fleet_interactive_state", INTERACTIVE_STATE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

class FleetInteractiveStateTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "member.json"
        self.member = {
            "schema_version": "2", "id": "TASK-001", "task_id": "TASK-001",
            "owner": {"kind": "sdd-composy-fleet", "fleet_id": "demo", "member_id": "TASK-001"},
            "interaction": {
                "state": "starting", "started_at": "2026-09-11T12:00:00Z",
                "updated_at": "2026-09-11T12:00:00Z"
            },
            "extension": {"preserve": True}
        }
        self.path.write_text(json.dumps(self.member))

    def tearDown(self):
        self.tmp.cleanup()

    def test_load_rejects_missing_interaction_fields_and_symlink(self):
        state = _load_interactive_state()
        for missing in ("state", "started_at", "updated_at"):
            with self.subTest(missing=missing):
                broken = json.loads(json.dumps(self.member)); del broken["interaction"][missing]
                self.path.write_text(json.dumps(broken))
                with self.assertRaises(state.InteractiveStateError): state.load_member(self.path)
        real = Path(self.tmp.name) / "real.json"; real.write_text(json.dumps(self.member))
        self.path.unlink(); self.path.symlink_to(real)
        with self.assertRaises(state.InteractiveStateError): state.load_member(self.path)

    def test_load_rejects_symlinked_ancestor(self):
        state = _load_interactive_state()
        real = Path(self.tmp.name) / "real"; real.mkdir()
        member = real / "member.json"; member.write_text(json.dumps(self.member))
        linked = Path(self.tmp.name) / "linked"; linked.symlink_to(real, target_is_directory=True)
        with self.assertRaises(state.InteractiveStateError): state.load_member(linked / "member.json")

    def test_schema_accepts_interaction_contract_and_rejects_missing_state(self):
        schema = json.loads((ROOT / "plugins/sdd-composy/schemas/fleet-member.schema.json").read_text())
        # Existing v2 records remain compatible; interaction is additive.
        legacy = json.loads(json.dumps(self.member)); legacy.pop("interaction")
        legacy.update({
            "status": "running", "runtime": "codex", "ui": "headless", "branch": "fleet/task-001",
            "worktree_path": "/tmp/task-001", "repository_root": "/tmp/repo",
            "started_at": "2026-09-11T12:00:00Z", "updated_at": "2026-09-11T12:00:00Z",
            "resources": {"branch": "fleet/task-001", "worktree_path": "/tmp/task-001", "port": 43001,
                          "compose_project": "fleet-demo", "compose_file": "fleet/docker-compose.yml",
                          "compose_allocated": False}
        })
        assert_schema_valid(self, schema, legacy)
        current = json.loads(json.dumps(legacy)); current["interaction"] = self.member["interaction"]
        assert_schema_valid(self, schema, current)
        del current["interaction"]["state"]
        with self.assertRaises(AssertionError): assert_schema_valid(self, schema, current)

    def test_transition_rejects_invalid_edge_and_preserves_unknown_fields(self):
        state = _load_interactive_state()
        with self.assertRaises(state.InteractiveStateError):
            state.transition(self.path, "starting", "completed", {}, "2026-09-11T12:01:00Z")
        result = state.transition(
            self.path, "starting", "running", {"handle": {"driver": "tmux", "id": "pane-1"}},
            "2026-09-11T12:01:00Z")
        self.assertEqual(result["extension"], {"preserve": True})
        self.assertEqual(result["interaction"]["handle"]["id"], "pane-1")
        self.assertEqual(json.loads(self.path.read_text()), result)

    def test_transition_is_compare_and_set(self):
        state = _load_interactive_state()
        with self.assertRaises(state.InteractiveStateError):
            state.transition(self.path, "running", "awaiting_human", {}, "2026-09-11T12:01:00Z")
        self.assertEqual(json.loads(self.path.read_text()), self.member)

    def test_bind_loop_is_immutable_and_rejects_task_divergence(self):
        state = _load_interactive_state()
        with self.assertRaises(state.InteractiveStateError):
            state.bind_loop(self.path, "loop-task-001", "TASK-002", "2026-09-11T12:01:00Z")
        bound = state.bind_loop(self.path, "loop-task-001", "TASK-001", "2026-09-11T12:01:00Z")
        self.assertEqual(bound["interaction"]["loop"], {"id": "loop-task-001", "task_id": "TASK-001"})
        self.assertEqual(bound["extension"], {"preserve": True})
        with self.assertRaises(state.InteractiveStateError):
            state.bind_loop(self.path, "loop-second", "TASK-001", "2026-09-11T12:02:00Z")
        self.assertEqual(json.loads(self.path.read_text()), bound)

class FleetLaunchTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.repo = Path(self.tmp.name)
        subprocess.run(["git","init","-q",str(self.repo)],check=True)
        subprocess.run(["git","-C",str(self.repo),"config","user.email","test@example.invalid"],check=True)
        subprocess.run(["git","-C",str(self.repo),"config","user.name","Test"],check=True)
        (self.repo/"src").mkdir(); (self.repo/"src/app.py").write_text("x\n")
        subprocess.run(["git","-C",str(self.repo),"add","."],check=True)
        subprocess.run(["git","-C",str(self.repo),"commit","-qm","base"],check=True)
        self.base=subprocess.check_output(["git","-C",str(self.repo),"branch","--show-current"],text=True).strip()
        self.contract=self.repo/"contract.json"
    def tearDown(self): self.tmp.cleanup()
    def task(self, **kw):
        d={"id":"TASK-001","state":"ready","dependencies":[],"acceptance_criteria":["CA-1"],"verification_commands":["true"],"allowed_paths":["src/app.py"],"contract_path":str(self.contract)}; d.update(kw); self.contract.write_text(json.dumps(d)); return d
    def invoke(self,*tasks, extra=None, runtime="codex"):
        args=[str(LAUNCH),"--prepare-only","--runtime",runtime,"--root",str(self.repo),"--fleet-id","demo","--base-branch",self.base]
        for t in tasks: args += ["--task",str(t)]
        return subprocess.run(args,capture_output=True,text=True,env={**os.environ,**(extra or {})})
    def test_ready_contract_hash_and_central_preserved(self):
        self.task(); before=(self.repo/"src/app.py").read_bytes()
        r=self.invoke(self.contract); self.assertEqual(r.returncode,0,r.stderr)
        member=self.repo/".planning/sdd-composy/fleet/demo/members/TASK-001.json"; d=json.loads(member.read_text())
        self.assertEqual(d["contract_sha256"],hashlib.sha256(self.contract.read_bytes()).hexdigest()); self.assertEqual(d["state"],"locked")
        self.assertEqual((self.repo/"src/app.py").read_bytes(),before)

    def test_emitted_members_validate_against_v2_schema_for_all_runtimes(self):
        schema=json.loads((ROOT/"plugins/sdd-composy/schemas/fleet-member.schema.json").read_text())
        for requested,stored in (("claude","claude-code"),("codex","codex"),("hermes","hermes")):
            with self.subTest(runtime=requested):
                self.task(); r=self.invoke(self.contract,runtime=requested); self.assertEqual(r.returncode,0,r.stderr)
                record=json.loads((self.repo/".planning/sdd-composy/fleet/demo/members/TASK-001.json").read_text())
                assert_schema_valid(self,schema,record)
                self.assertEqual(record["schema_version"],"2"); self.assertEqual(record["runtime"],stored)
                self.assertEqual(Path(record["worktree_path"]),Path(record["worktree_path"]).resolve())
                self.assertEqual(record["repository_root"],str(self.repo.resolve()))
                broken=json.loads(json.dumps(record)); broken["resources"]["port"]="43000"
                with self.assertRaises(AssertionError): assert_schema_valid(self,schema,broken)
                self.tearDown(); self.setUp()

    def test_prepare_only_requires_known_explicit_runtime_without_mutation(self):
        self.task()
        for runtime in (None,"unknown"):
            args=[str(LAUNCH),"--prepare-only","--root",str(self.repo),"--fleet-id","demo","--base-branch",self.base,"--task",str(self.contract)]
            if runtime: args[2:2]=["--runtime",runtime]
            r=subprocess.run(args,capture_output=True,text=True)
            self.assertNotEqual(r.returncode,0); self.assertFalse((self.repo/".planning").exists())

    def test_symlinked_state_ancestor_is_rejected_without_external_write(self):
        self.task(); outside=Path(self.tmp.name+"-outside"); outside.mkdir(); (self.repo/".planning").symlink_to(outside,target_is_directory=True)
        r=self.invoke(self.contract); self.assertNotEqual(r.returncode,0); self.assertEqual(list(outside.iterdir()),[])
        (self.repo/".planning").unlink(); outside.rmdir()

    def test_rollback_uses_real_git_registration_and_removes_created_branch(self):
        self.task(); before=subprocess.check_output(["git","-C",str(self.repo),"worktree","list","--porcelain"],text=True)
        r=self.invoke(self.contract,extra={"SDD_FLEET_FAIL_AFTER_WORKTREE":"1"}); self.assertNotEqual(r.returncode,0)
        after=subprocess.check_output(["git","-C",str(self.repo),"worktree","list","--porcelain"],text=True)
        self.assertEqual(after,before)
        self.assertNotEqual(subprocess.run(["git","-C",str(self.repo),"show-ref","--verify","--quiet","refs/heads/sdd-fleet/demo/TASK-001"]).returncode,0)

    def test_compose_template_and_member_ownership_are_recorded(self):
        launch=LAUNCH.read_text()
        self.assertIn('$HERE/../../templates/docker-compose.sdd-fleet.yml',launch)
        self.assertNotIn('$HERE/../../../templates/docker-compose.sdd-fleet.yml',launch)
        self.task(); r=self.invoke(self.contract); self.assertEqual(r.returncode,0,r.stderr)
        record=json.loads((self.repo/".planning/sdd-composy/fleet/demo/members/TASK-001.json").read_text())
        self.assertEqual(record["owner"],{"kind":"sdd-composy-fleet","fleet_id":"demo","member_id":"TASK-001"})
        self.assertEqual(record["resources"]["port"],record["port"])
        self.assertEqual(record["resources"]["branch"],record["branch"])
        self.assertFalse(record["resources"]["compose_allocated"])
        self.assertEqual(record["resources"]["compose_file"],".planning/sdd-composy/fleet/demo/docker-compose.yml")

    def test_compose_record_binds_the_actual_central_file_and_digest(self):
        self.task(); fake=Path(self.tmp.name)/"bin"; fake.mkdir(); docker=fake/"docker"; docker.write_text("#!/bin/sh\nexit 0\n"); docker.chmod(0o755)
        args=[str(LAUNCH),"--prepare-only","--runtime","codex","--compose","--root",str(self.repo),"--fleet-id","demo","--base-branch",self.base,"--task",str(self.contract)]
        r=subprocess.run(args,capture_output=True,text=True,env={**os.environ,"PATH":str(fake)+":/usr/bin:/bin"}); self.assertEqual(r.returncode,0,r.stderr)
        state=self.repo/".planning/sdd-composy/fleet/demo"; record=json.loads((state/"members/TASK-001.json").read_text()); resources=record["resources"]
        actual=self.repo/resources["compose_file"]; self.assertEqual(actual.resolve(),(state/"docker-compose.yml").resolve()); self.assertTrue(resources["compose_allocated"])
        self.assertEqual(resources["compose_sha256"],hashlib.sha256(actual.read_bytes()).hexdigest())
        assert_schema_valid(self,json.loads((ROOT/"plugins/sdd-composy/schemas/fleet-member.schema.json").read_text()),record)

    def test_members_have_distinct_worktrees_branches_and_ports(self):
        self.task(); other=self.repo/'other.json'
        other.write_text(json.dumps({'id':'TASK-002','state':'ready','acceptance_criteria':['ok'],'verification_commands':['true'],'allowed_paths':['other']}))
        result=self.invoke(self.contract,other)
        self.assertEqual(result.returncode,0,result.stderr)
        records=[json.loads(p.read_text()) for p in (self.repo/'.planning/sdd-composy/fleet/demo/members').glob('*.json')]
        for key in ('worktree','branch','port'):
            self.assertEqual(len({r[key] for r in records}),2,key)

    def test_launch_dispatches_real_runner_to_mock_provider_without_metadata_rewrite(self):
        import time
        phase=self.repo/'.planning/sdd-composy/phases/task-001'; phase.mkdir(parents=True)
        for name in ('spec.md','decisions.md'): (phase/name).write_text('Status: APPROVED\n')
        subprocess.run(['git','-C',str(self.repo),'add','.'],check=True)
        subprocess.run(['git','-C',str(self.repo),'commit','-qm','approved phase'],check=True)
        self.task(); fake=self.repo/'bin'; fake.mkdir(); called=self.repo/'provider-called'
        (fake/'codex').write_text('#!/bin/sh\nprintf "%s\\n" "$@" > "'+str(called)+'"\nexit 7\n'); (fake/'codex').chmod(0o755)
        result=subprocess.run([str(LAUNCH),'--runtime','codex','--ui','headless','--root',str(self.repo),'--fleet-id','demo','--base-branch',self.base,'--task',str(self.contract)],capture_output=True,text=True,env={**os.environ,'PATH':str(fake)+':/usr/bin:/bin'})
        self.assertEqual(result.returncode,0,result.stderr)
        state=self.repo/'.planning/sdd-composy/fleet/demo'; member=json.loads((state/'members/TASK-001.json').read_text()); work=Path(member['worktree'])
        deadline=time.monotonic()+10
        while time.monotonic()<deadline:
            status=work/'.planning/sdd-composy/fleet-status.json'
            if status.exists() and json.loads(status.read_text()).get('status')=='NEEDS_HUMAN': break
            time.sleep(.05)
        self.assertTrue(called.exists())
        args=called.read_text(); self.assertIn('TASK-001',args); self.assertIn(str(self.contract),args)
        self.assertNotIn('--dangerously-bypass',args)
        self.assertEqual(json.loads(status.read_text())['status'],'NEEDS_HUMAN')
    def test_eligibility_and_required_contract_fields(self):
        for key,val in (("state","pending"),("acceptance_criteria",[]),("verification_commands",[]),("dependencies_complete",False)):
            self.task(**{key:val}); self.assertNotEqual(self.invoke(self.contract).returncode,0)
    def test_symlink_dirty_and_collision_rejected(self):
        self.task(allowed_paths=["link.py"]); (self.repo/"link.py").symlink_to(self.repo/"src/app.py"); self.assertNotEqual(self.invoke(self.contract).returncode,0)
        self.contract.unlink(); self.contract.symlink_to(self.repo/"src/app.py"); self.assertNotEqual(self.invoke(self.contract).returncode,0)
        self.contract.unlink(); self.task(id="A",allowed_paths=["src/app.py"]); other=self.repo/"other.json"; other.write_text(json.dumps(self.task(id="B",allowed_paths=["src/app.py"]))); self.assertNotEqual(self.invoke(self.contract,other).returncode,0)
    def test_branch_collision_and_partial_failure_preserves_branch_or_central(self):
        self.task(); self.assertEqual(self.invoke(self.contract).returncode,0)
        self.assertNotEqual(self.invoke(self.contract).returncode,0)
        self.assertTrue((self.repo/".planning/sdd-composy/fleet/demo").exists())
    def test_post_worktree_failure_rolls_back_worktree_and_preserves_source(self):
        self.task(); source=(self.repo/"src/app.py").read_bytes()
        r=self.invoke(self.contract, extra={"SDD_FLEET_FAIL_AFTER_WORKTREE":"1"})
        self.assertNotEqual(r.returncode,0)
        self.assertEqual((self.repo/"src/app.py").read_bytes(),source)
        self.assertEqual(subprocess.run(["git","-C",str(self.repo),"worktree","list"],capture_output=True,text=True).stdout.count(".sdd-fleet-demo-"),0)
    def test_lock_timeout_and_hash_binding_reject_mutation(self):
        self.task(); lock=self.repo/"lock"; lock.write_text("owner")
        common=ROOT/"plugins/sdd-composy/scripts/fleet/common.sh"
        r=subprocess.run(["bash","-c",f'. "{common}"; fleet_lock "$1" 0', "", str(lock)],capture_output=True,text=True)
        self.assertNotEqual(r.returncode,0)
        self.assertEqual(self.invoke(self.contract).returncode,0)
        record=self.repo/".planning/sdd-composy/fleet/demo/members/TASK-001.json"; self.contract.write_text(self.contract.read_text()+"\n")
        r=subprocess.run(["bash","-c",f'. "{common}"; fleet_verify_binding "$1"', "", str(record)],capture_output=True,text=True)
        self.assertNotEqual(r.returncode,0)

    def test_invalid_range_and_occupied_slot_are_rejected(self):
        self.task(); env={"SDD_FLEET_PORT_START":"43100","SDD_FLEET_PORT_END":"43000"}
        self.assertNotEqual(self.invoke(self.contract,extra=env).returncode,0)
        env={"SDD_FLEET_PORT_START":"43100","SDD_FLEET_PORT_END":"43100"}
        state=self.repo/".planning/sdd-composy/fleet/demo"; state.mkdir(parents=True,exist_ok=True)
        (state/"port-43100").write_text("other\n")
        self.assertNotEqual(self.invoke(self.contract,extra=env).returncode,0)

    def test_existing_runtime_file_is_never_adopted(self):
        self.task(); state=self.repo/".planning/sdd-composy/fleet/demo"; state.mkdir(parents=True,exist_ok=True)
        (state/"runtime.env").write_text("SECRET=do-not-read\n")
        r=self.invoke(self.contract); self.assertNotEqual(r.returncode,0)
        self.assertEqual((state/"runtime.env").read_text(),"SECRET=do-not-read\n")

    def test_compose_mode_fails_closed_without_compose_and_rolls_back_allocation(self):
        self.task(); env={"PATH":"/usr/bin:/bin","SDD_FLEET_PORT_START":"43200","SDD_FLEET_PORT_END":"43200"}
        args=[str(LAUNCH),"--root",str(self.repo),"--fleet-id","demo","--base-branch",self.base,"--task",str(self.contract),"--compose"]
        r=subprocess.run(args,capture_output=True,text=True,env={**os.environ,**env})
        self.assertNotEqual(r.returncode,0)
        state=self.repo/".planning/sdd-composy/fleet/demo"
        self.assertFalse((state/"port-43200").exists()); self.assertFalse((state/"runtime.env").exists())

    def test_allocated_runtime_env_is_mode_restricted_and_recorded(self):
        self.task(); env={"SDD_FLEET_PORT_START":"43201","SDD_FLEET_PORT_END":"43201"}
        self.assertEqual(self.invoke(self.contract,extra=env).returncode,0)
        state=self.repo/".planning/sdd-composy/fleet/demo"; runtime=state/"runtime.env"
        self.assertEqual(runtime.stat().st_mode & 0o777,0o600)
        self.assertIn("SDD_FLEET_PORT=43201",runtime.read_text())

    def test_concurrent_port_allocators_get_distinct_slots(self):
        common=ROOT/"plugins/sdd-composy/scripts/fleet/common.sh"
        state=self.repo/"ports"; state.mkdir()
        code=f'. "{common}"; fleet_allocate_port "$1" 43300 43301'
        procs=[subprocess.Popen(["bash","-c",code,"",str(state)],stdout=subprocess.PIPE,text=True) for _ in range(2)]
        values=[p.communicate(timeout=10)[0].strip() for p in procs]
        self.assertEqual(sorted(values),["43300","43301"])

    def test_failed_compose_launch_removes_all_generated_bookkeeping(self):
        self.task(); env={"PATH":"/usr/bin:/bin","SDD_FLEET_PORT_START":"43302","SDD_FLEET_PORT_END":"43302"}
        args=[str(LAUNCH),"--root",str(self.repo),"--fleet-id","demo","--base-branch",self.base,"--task",str(self.contract),"--compose"]
        r=subprocess.run(args,capture_output=True,text=True,env={**os.environ,**env}); self.assertNotEqual(r.returncode,0)
        state=self.repo/".planning/sdd-composy/fleet/demo"
        self.assertFalse((state/"fleet.json").exists())
        self.assertEqual(list((state/"members").glob("*.json")),[])
        self.assertFalse((state/"docker-compose.yml").exists())

    def test_failure_preserves_preexisting_fleet_metadata_and_compose(self):
        self.task(); state=self.repo/".planning/sdd-composy/fleet/demo"; members=state/"members"; members.mkdir(parents=True)
        fleet=b'{"old":true}\n'; member=b'{"id":"OLD"}\n'; compose=b"services: {}\n"
        (state/"fleet.json").write_bytes(fleet); (members/"OLD.json").write_bytes(member); (state/"docker-compose.yml").write_bytes(compose)
        r=self.invoke(self.contract,extra={"SDD_FLEET_FAIL_AFTER_WORKTREE":"1"}); self.assertNotEqual(r.returncode,0)
        self.assertEqual((state/"fleet.json").read_bytes(),fleet); self.assertEqual((members/"OLD.json").read_bytes(),member); self.assertEqual((state/"docker-compose.yml").read_bytes(),compose)

    def test_preexisting_member_without_fleet_metadata_is_preserved(self):
        self.task(); state=self.repo/".planning/sdd-composy/fleet/demo"; members=state/"members"; members.mkdir(parents=True)
        original=b'{"id":"TASK-001","recoverable":true}\n'; (members/"TASK-001.json").write_bytes(original)
        r=self.invoke(self.contract,extra={"SDD_FLEET_FAIL_AFTER_WORKTREE":"1"}); self.assertNotEqual(r.returncode,0)
        self.assertEqual((members/"TASK-001.json").read_bytes(),original)
        self.assertFalse((state/"fleet.json").exists())

    def test_mixed_member_collision_writes_no_partial_records(self):
        self.task(id="TASK-A"); first=self.contract
        second=self.repo/"second.json"; second.write_text(json.dumps(self.task(id="TASK-B")))
        state=self.repo/".planning/sdd-composy/fleet/demo"; members=state/"members"; members.mkdir(parents=True)
        original=b'{"id":"TASK-B","old":true}\n'; (members/"TASK-B.json").write_bytes(original)
        r=self.invoke(first,second); self.assertNotEqual(r.returncode,0)
        self.assertFalse((members/"TASK-A.json").exists())
        self.assertEqual((members/"TASK-B.json").read_bytes(),original)
        self.assertFalse((state/"fleet.json").exists())

    def _launched_member(self, status="running"):
        self.task(); self.assertEqual(self.invoke(self.contract).returncode, 0)
        state=self.repo/".planning/sdd-composy/fleet/demo"; mf=state/"members/TASK-001.json"
        d=json.loads(mf.read_text()); d["status"]=status; d["worktree_path"]=d["worktree"]; d.setdefault("resources", {}).update(compose_allocated=False, compose_file="", compose_project="")
        mf.write_text(json.dumps(d)); return state,mf,d,Path(d["worktree"])

    def _teardown(self, *extra):
        return subprocess.run([str(ROOT/"plugins/sdd-composy/scripts/fleet/teardown.sh"), "--root",str(self.repo),"--fleet-id","demo","--member-id","TASK-001",*extra], capture_output=True,text=True)

    def test_teardown_refuses_nonterminal_and_missing_or_wrong_confirmation(self):
        state,mf,d,work=self._launched_member("running")
        r=self._teardown("--merge","--confirm","CONFIRM-SDD-MERGE"); self.assertNotEqual(r.returncode,0); self.assertTrue(mf.exists()); self.assertTrue(work.exists())
        d["status"]="completed"; mf.write_text(json.dumps(d))
        r=self._teardown("--merge"); self.assertNotEqual(r.returncode,0)
        r=self._teardown("--merge","--confirm","WRONG"); self.assertNotEqual(r.returncode,0)

    def test_teardown_validates_result_identity_and_commit(self):
        state,mf,d,work=self._launched_member("completed"); result=state/"result.json"; d["result_path"]=str(result); mf.write_text(json.dumps(d))
        result.write_text(json.dumps({"member_id":"OTHER","status":"completed","commit":"0"*40})); self.assertNotEqual(self._teardown("--merge","--confirm","CONFIRM-SDD-MERGE").returncode,0)
        result.write_text(json.dumps({"member_id":"TASK-001","status":"completed","commit":"bad"})); self.assertNotEqual(self._teardown("--merge","--confirm","CONFIRM-SDD-MERGE").returncode,0)
        (self.repo/"central.txt").write_text("unrelated\n"); subprocess.run(["git","-C",str(self.repo),"add","."],check=True); subprocess.run(["git","-C",str(self.repo),"commit","-qm","unrelated"],check=True)
        result.write_text(json.dumps({"member_id":"TASK-001","status":"completed","commit":subprocess.check_output(["git","-C",str(self.repo),"rev-parse","HEAD"],text=True).strip()})); self.assertNotEqual(self._teardown("--merge","--confirm","CONFIRM-SDD-MERGE").returncode,0); self.assertTrue(mf.exists())

    def test_teardown_nonmerge_stops_and_preserves_recoverable_worktree(self):
        state,mf,d,work=self._launched_member("running"); unknown=work/"unknown.txt"; unknown.write_text("keep")
        r=self._teardown(); self.assertEqual(r.returncode,0,r.stderr); self.assertFalse(mf.exists()); self.assertTrue(work.exists()); self.assertTrue(unknown.exists()); self.assertEqual(subprocess.run(["git","-C",str(self.repo),"show-ref","--verify","--quiet","refs/heads/"+d['branch']]).returncode,0)

    def test_merge_executes_bound_checks_and_keeps_recovery_on_failure(self):
        for command,success in [('printf verified > verification.txt',True),('exit 1',False)]:
            with self.subTest(command=command):
                self.task(verification_commands=[command])
                result=self.invoke(self.contract); self.assertEqual(result.returncode,0,result.stderr)
                state=self.repo/'.planning/sdd-composy/fleet/demo'; mf=state/'members/TASK-001.json'; d=json.loads(mf.read_text()); d['resources']['compose_allocated']=False; d['resources']['compose_file']=''; d['resources']['compose_project']=''; work=Path(d['worktree'])
                (work/'src/app.py').write_text('changed\n'); subprocess.run(['git','-C',str(work),'add','.'],check=True); subprocess.run(['git','-C',str(work),'commit','-qm','change'],check=True)
                tip=subprocess.check_output(['git','-C',str(work),'rev-parse','HEAD'],text=True).strip()
                report=state/'result.json'; report.write_text(json.dumps({'member_id':'TASK-001','status':'completed','commit':tip})); d.update(status='completed',result_path=str(report)); mf.write_text(json.dumps(d))
                result=self._teardown('--merge','--confirm','CONFIRM-SDD-MERGE')
                self.assertEqual(result.returncode==0,success,result.stderr)
                self.assertEqual(work.exists(),not success); self.assertEqual(mf.exists(),not success)
                if success: self.assertEqual((self.repo/'verification.txt').read_text(),'verified')
            self.tearDown(); self.setUp()

    def test_teardown_merge_conflict_aborts_and_preserves_state(self):
        state,mf,d,work=self._launched_member("completed"); (work/"src/app.py").write_text("branch\n")
        subprocess.run(["git","-C",str(work),"add","."],check=True); subprocess.run(["git","-C",str(work),"commit","-qm","fleet"],check=True)
        (self.repo/"src/app.py").write_text("central\n"); subprocess.run(["git","-C",str(self.repo),"add","."],check=True); subprocess.run(["git","-C",str(self.repo),"commit","-qm","central"],check=True)
        result=state/"result.json"; result.write_text(json.dumps({"member_id":"TASK-001","status":"completed","commit":subprocess.check_output(["git","-C",str(work),"rev-parse","HEAD"],text=True).strip()})); d["result_path"]=str(result); mf.write_text(json.dumps(d))
        r=self._teardown("--merge","--confirm","CONFIRM-SDD-MERGE"); self.assertNotEqual(r.returncode,0); self.assertTrue(mf.exists()); self.assertTrue(work.exists()); self.assertNotEqual(subprocess.run(["git","-C",str(self.repo),"rev-parse","-q","--verify","MERGE_HEAD"],capture_output=True).returncode,0)

    def test_teardown_authorized_merge_is_noff_and_removes_owned_state(self):
        state,mf,d,work=self._launched_member("completed"); (work/"src/app.py").write_text("merged\n"); subprocess.run(["git","-C",str(work),"add","."],check=True); subprocess.run(["git","-C",str(work),"commit","-qm","fleet change"],check=True)
        tip=subprocess.check_output(["git","-C",str(work),"rev-parse","HEAD"],text=True).strip(); result=state/"result.json"; result.write_text(json.dumps({"member_id":"TASK-001","status":"completed","commit":tip})); d["result_path"]=str(result); mf.write_text(json.dumps(d))
        r=self._teardown("--merge","--confirm","CONFIRM-SDD-MERGE"); self.assertEqual(r.returncode,0,r.stderr); self.assertFalse(mf.exists()); self.assertFalse(work.exists()); merge_head=subprocess.check_output(["git","-C",str(self.repo),"rev-parse","HEAD"],text=True).strip(); self.assertEqual(int(subprocess.check_output(["git","-C",str(self.repo),"rev-list","--count","--merges","HEAD"],text=True)),1); self.assertIn(tip,subprocess.check_output(["git","-C",str(self.repo),"show","-s","--format=%P",merge_head],text=True))

    def test_teardown_rejects_symlinked_member_and_worktree(self):
        state,mf,d,work=self._launched_member("running"); backup=mf.with_suffix(".real"); mf.rename(backup); mf.symlink_to(backup); self.assertNotEqual(self._teardown().returncode,0); mf.unlink(); backup.rename(mf)
        outside=Path(self.tmp.name)/"outside"; outside.mkdir(); d["worktree_path"]=str(outside); mf.write_text(json.dumps(d)); self.assertNotEqual(self._teardown().returncode,0)

    def test_teardown_rejects_symlink_worktree_and_preserves_state(self):
        state,mf,d,work=self._launched_member("running"); link=Path(self.tmp.name)/"linked-worktree"; link.symlink_to(work); d["worktree_path"]=str(link); mf.write_text(json.dumps(d)); r=self._teardown(); self.assertNotEqual(r.returncode,0); self.assertTrue(mf.exists()); self.assertTrue(work.exists())

    def test_teardown_rejects_nested_symlink_worktree_parent(self):
        state,mf,d,work=self._launched_member("running"); parent=Path(self.tmp.name)/"nested-target"; parent.mkdir(); link=Path(self.tmp.name)/"nested-link"; link.symlink_to(parent); d["worktree_path"]=str(link/"child"); mf.write_text(json.dumps(d)); r=self._teardown(); self.assertNotEqual(r.returncode,0); self.assertTrue(mf.exists())

    def test_teardown_uses_owned_central_compose_and_rejects_worktree_homonym(self):
        state,mf,d,work=self._launched_member("running")
        compose=state/"docker-compose.yml"; compose.write_text("services:\n  central: {}\n")
        relative=".planning/sdd-composy/fleet/demo/docker-compose.yml"
        homonym=work/relative; homonym.parent.mkdir(parents=True); homonym.write_text("services:\n  impostor: {}\n")
        d["resources"].update(compose_allocated=True,compose_file=relative,compose_project="sdd_fleet_demo",compose_sha256=hashlib.sha256(compose.read_bytes()).hexdigest())
        mf.write_text(json.dumps(d)); bind=Path(self.tmp.name)/"bin"; bind.mkdir(); log=Path(self.tmp.name)/"docker.log"
        (bind/"docker").write_text("#!/bin/sh\nprintf '%s\\n' \"$*\" >> '"+str(log)+"'\nexit 1\n"); (bind/"docker").chmod(0o755)
        r=subprocess.run([str(ROOT/"plugins/sdd-composy/scripts/fleet/teardown.sh"),"--root",str(self.repo),"--fleet-id","demo","--member-id","TASK-001"],env={**os.environ,"PATH":str(bind)+":"+os.environ.get("PATH","")},capture_output=True,text=True)
        self.assertNotEqual(r.returncode,0); self.assertTrue(mf.exists()); self.assertTrue(work.exists())
        self.assertTrue(log.exists(),r.stderr); invocation=log.read_text(); self.assertIn("-f "+str(compose.resolve()),invocation); self.assertNotIn(str(homonym.resolve()),invocation); self.assertNotIn("--volumes",invocation)

    def test_teardown_rejects_foreign_compose_project_before_docker_and_preserves_recovery(self):
        state,mf,d,work=self._launched_member("running"); compose=state/"docker-compose.yml"; compose.write_text("services: {}\n")
        d["resources"].update(compose_allocated=True,compose_file=".planning/sdd-composy/fleet/demo/docker-compose.yml",compose_project="foreign-project",compose_sha256=hashlib.sha256(compose.read_bytes()).hexdigest())
        mf.write_text(json.dumps(d)); bind=Path(self.tmp.name)/"bin"; bind.mkdir(); log=Path(self.tmp.name)/"docker.log"
        (bind/"docker").write_text("#!/bin/sh\nprintf '%s\\n' \"$*\" >> '"+str(log)+"'\nexit 0\n"); (bind/"docker").chmod(0o755)
        r=subprocess.run([str(ROOT/"plugins/sdd-composy/scripts/fleet/teardown.sh"),"--root",str(self.repo),"--fleet-id","demo","--member-id","TASK-001"],env={**os.environ,"PATH":str(bind)+":"+os.environ.get("PATH","")},capture_output=True,text=True)
        self.assertNotEqual(r.returncode,0); self.assertFalse(log.exists()); self.assertTrue(mf.exists()); self.assertTrue(work.exists())

    def test_teardown_legacy_compose_mirror_cannot_override_central_resource(self):
        state,mf,d,work=self._launched_member("running"); (work/"docker-compose.yml").write_text("services: {}\n"); (work/"other.yml").write_text("services: {}\n"); d["resources"].update(compose_allocated=True,compose_file="docker-compose.yml",compose_project=d["resources"].get("compose_project", "owned-project"))
        d["compose_file"]="other.yml"; mf.write_text(json.dumps(d)); bind=Path(self.tmp.name)/"bin"; bind.mkdir(); log=Path(self.tmp.name)/"docker.log"; (bind/"docker").write_text("#!/bin/sh\nprintf '%s\\n' \"$*\" >> '"+str(log)+"'\nexit 1\n"); (bind/"docker").chmod(0o755)
        r=subprocess.run([str(ROOT/"plugins/sdd-composy/scripts/fleet/teardown.sh"),"--root",str(self.repo),"--fleet-id","demo","--member-id","TASK-001"],env={**os.environ,"PATH":str(bind)+":"+os.environ.get("PATH","")},capture_output=True,text=True); self.assertNotEqual(r.returncode,0); self.assertFalse(log.exists()); self.assertTrue(mf.exists())

    def test_teardown_missing_central_compose_preserves_metadata(self):
        state,mf,d,work=self._launched_member("running"); d["resources"]["compose_allocated"]=True; mf.write_text(json.dumps(d)); r=self._teardown(); self.assertNotEqual(r.returncode,0); self.assertTrue(mf.exists()); self.assertTrue(work.exists())

    def test_teardown_requires_explicit_compose_allocation_and_ignores_worktree_homonym(self):
        state,mf,d,work=self._launched_member("running"); relative=".planning/sdd-composy/fleet/demo/docker-compose.yml"
        homonym=work/relative; homonym.parent.mkdir(parents=True); homonym.write_text("services: {}\n")
        d["resources"].update(compose_file=relative,compose_project="owned-project",compose_sha256=hashlib.sha256(homonym.read_bytes()).hexdigest()); del d["resources"]["compose_allocated"]
        mf.write_text(json.dumps(d)); bind=Path(self.tmp.name)/"bin"; bind.mkdir(); log=Path(self.tmp.name)/"docker.log"
        (bind/"docker").write_text("#!/bin/sh\nprintf '%s\\n' \"$*\" >> '"+str(log)+"'\nexit 0\n"); (bind/"docker").chmod(0o755)
        r=subprocess.run([str(ROOT/"plugins/sdd-composy/scripts/fleet/teardown.sh"),"--root",str(self.repo),"--fleet-id","demo","--member-id","TASK-001"],env={**os.environ,"PATH":str(bind)+":"+os.environ.get("PATH","")},capture_output=True,text=True)
        self.assertNotEqual(r.returncode,0); self.assertTrue(mf.exists()); self.assertTrue(work.exists()); self.assertFalse(log.exists())

    def test_teardown_lock_release_failure_preserves_recovery_state(self):
        state,mf,d,work=self._launched_member("running"); lock=state/".TASK-001.runner.lock"; lock.mkdir(); (lock/"owner").write_text("keep"); r=self._teardown(); self.assertNotEqual(r.returncode,0); self.assertTrue(mf.exists()); self.assertTrue(work.exists()); self.assertTrue((lock/"owner").exists())

    def test_ui_headless_preserves_argv_and_returns_teardown_handle(self):
        ui=ROOT/"plugins/sdd-composy/scripts/fleet/ui-headless.sh"
        with tempfile.TemporaryDirectory() as tmp:
            tmp=Path(tmp); out=tmp/"args.json"; handle=tmp/"handle.json"
            command=["python3","-c", "import json,sys; json.dump(sys.argv[1:],open(sys.argv[1],'w'))", str(out), "a b", "$(literal)"]
            r=subprocess.run(["bash","-c",f'source "{ui}"; fleet_ui_headless_start "$1" "$2" "$3" "$4" "$5" "$6" "$7" "$8"',"",str(handle),str(tmp),*command],capture_output=True,text=True)
            self.assertEqual(r.returncode,0,r.stderr)
            self.assertEqual(json.loads(out.read_text()),[str(out),"a b","$(literal)"])
            d=json.loads(handle.read_text()); self.assertEqual(d["driver"],"headless"); self.assertIn("pid",d)
            self.assertEqual(subprocess.run(["bash","-c",f'source "{ui}"; fleet_ui_teardown "$1"',"",str(handle)]).returncode,0)
            self.assertFalse(handle.exists())

    def test_ui_tmux_collision_and_missing_tool_are_explicit(self):
        ui=ROOT/"plugins/sdd-composy/scripts/fleet/ui-tmux.sh"
        with tempfile.TemporaryDirectory() as tmp:
            tmp=Path(tmp); fake=tmp/"tmux"; log=tmp/"log"
            fake.write_text("#!/bin/sh\nprintf '%s\\n' \"$*\" >> \"$UI_LOG\"\ncase $1 in has-session) exit ${UI_COLLISION:-1};; esac\n") ; fake.chmod(0o755)
            env={**os.environ,"PATH":str(tmp)+":"+os.environ["PATH"],"UI_LOG":str(log)}
            h=tmp/"h.json"
            r=subprocess.run(["bash","-c",f'source "{ui}"; fleet_ui_tmux_start "$1" "$2" "$3" "$4"',"",str(h),str(tmp),"fleet-demo","printf hi"],capture_output=True,text=True,env=env)
            self.assertEqual(r.returncode,0,r.stderr); self.assertIn("new-session",log.read_text()); self.assertEqual(json.loads(h.read_text())["driver"],"tmux")
            r=subprocess.run(["bash","-c",f'source "{ui}"; fleet_ui_tmux_start "$1" "$2" "$3" "$4"',"",str(tmp/"x.json"),str(tmp),"fleet-demo","printf hi"],capture_output=True,text=True,env={**env,"UI_COLLISION":"0"})
            self.assertNotEqual(r.returncode,0); self.assertIn("collision",r.stderr)

    def test_ui_selection_matrix_and_missing_tool_fallback(self):
        common=ROOT/"plugins/sdd-composy/scripts/fleet/common.sh"
        with tempfile.TemporaryDirectory() as tmp:
            tmp=Path(tmp)
            def select(requested, tools=()):
                for old in (tmp/"cmux", tmp/"tmux"):
                    old.unlink(missing_ok=True)
                for name in tools:
                    p=tmp/name; p.write_text("#!/bin/sh\n"); p.chmod(0o755)
                env={**os.environ,"PATH":str(tmp)+":/usr/bin:/bin"}
                return subprocess.run(["bash","-c",f'source "{common}"; fleet_select_ui "$1"',"",requested],capture_output=True,text=True,env=env)
            self.assertEqual(select("headless").stdout.strip(),"headless")
            self.assertEqual(select("cmux",("cmux",)).stdout.strip(),"cmux")
            self.assertEqual(select("cmux").stdout.strip(),"headless")
            self.assertEqual(select("auto").stdout.strip(),"headless")
            self.assertNotEqual(select("tmux").returncode,0)

    def test_headless_teardown_proves_process_is_gone(self):
        ui=ROOT/"plugins/sdd-composy/scripts/fleet/ui-headless.sh"
        with tempfile.TemporaryDirectory() as tmp:
            tmp=Path(tmp); h=tmp/"handle.json"
            r=subprocess.run(["bash","-c",f'source "{ui}"; fleet_ui_headless_start "$1" "$2" sleep 30',"",str(h),str(tmp)],capture_output=True,text=True)
            self.assertEqual(r.returncode,0,r.stderr); pid=json.loads(h.read_text())["pid"]
            self.assertEqual(subprocess.run(["bash","-c",f'source "{ui}"; fleet_ui_teardown "$1"',"",str(h)]).returncode,0)
            self.assertFalse(h.exists()); self.assertNotEqual(subprocess.run(["kill","-0",str(pid)]).returncode,0)

    def test_tmux_teardown_removes_session_and_handle(self):
        ui=ROOT/"plugins/sdd-composy/scripts/fleet/ui-tmux.sh"
        with tempfile.TemporaryDirectory() as tmp:
            tmp=Path(tmp); fake=tmp/"tmux"; state=tmp/"session"; log=tmp/"log"
            fake.write_text("#!/bin/sh\nprintf '%s\\n' \"$*\" >> \"$UI_LOG\"\ncase $1 in has-session) test -f \"$UI_STATE\";; new-session) touch \"$UI_STATE\";; kill-session) rm -f \"$UI_STATE\";; esac\n") ; fake.chmod(0o755)
            env={**os.environ,"PATH":str(tmp)+":/usr/bin:/bin","UI_LOG":str(log),"UI_STATE":str(state)}; h=tmp/"h.json"
            self.assertEqual(subprocess.run(["bash","-c",f'source "{ui}"; fleet_ui_tmux_start "$1" "$2" "$3" "$4"',"",str(h),str(tmp),"fleet-demo","printf hi"],env=env,capture_output=True,text=True).returncode,0)
            self.assertEqual(subprocess.run(["bash","-c",f'source "{ui}"; fleet_ui_teardown "$1"',"",str(h)],env=env,capture_output=True,text=True).returncode,0)
            self.assertFalse(state.exists()); self.assertFalse(h.exists()); self.assertIn("kill-session",log.read_text())

    def test_launch_persists_selected_ui_without_changing_member_lifecycle(self):
        self.task(); env={**os.environ,"PATH":"/usr/bin:/bin","SDD_FLEET_PORT_START":"43400","SDD_FLEET_PORT_END":"43400"}
        r=self.invoke(self.contract,extra=env); self.assertEqual(r.returncode,0,r.stderr)
        state=self.repo/".planning/sdd-composy/fleet/demo"; fleet=json.loads((state/"fleet.json").read_text()); member=json.loads((state/"members/TASK-001.json").read_text())
        self.assertEqual(fleet["ui"],"headless"); self.assertEqual(member["state"],"locked"); self.assertNotIn("pid",member)

    def test_cmux_mock_matrix_ownership_handles_and_no_foreign_mutation(self):
        ui=ROOT/"plugins/sdd-composy/scripts/fleet/ui-cmux.sh"
        common=ROOT/"plugins/sdd-composy/scripts/fleet/common.sh"
        with tempfile.TemporaryDirectory() as td:
            td=Path(td); log=td/"calls"; fake=td/"cmux"
            fake.write_text("""#!/usr/bin/env python3
import json, os, sys
log=os.environ['CMUX_LOG']; a=sys.argv[1:]
with open(log,'a') as f: f.write(json.dumps(a)+'\\n')
if a[:1]==['new-workspace']: print(json.dumps({'id':'ws-1'}))
elif a[:1]==['new-split']: print(json.dumps({'surface_id':'surf-1'}))
elif a[:1]==['list-workspaces']:
 print(json.dumps({'workspaces':[{'id':'ws-1','owner':'sdd-composy','sdd_composy_fleet':'demo'}]}))
elif a[:1] in (['set-workspace-meta'],['set-status'],['flash'],['close-surface']): print('{}')
else: print('{}')
"""); fake.chmod(0o755)
            env={**os.environ,"SDD_CMUX_BIN":str(fake),"CMUX_LOG":str(log)}; h=td/"handle.json"
            r=subprocess.run(["bash","-c",f'source "{ui}"; fleet_ui_cmux_start "$1" "$2" demo echo hi',"",str(h),str(td)],env=env,capture_output=True,text=True)
            self.assertEqual(r.returncode,0,r.stderr); d=json.loads(h.read_text()); self.assertEqual(d["workspace_id"],"ws-1"); self.assertEqual(d["surface_id"],"surf-1")
            self.assertEqual(subprocess.run(["bash","-c",f'source "{ui}"; fleet_ui_cmux_status "$1" ok green; fleet_ui_cmux_flash "$1"; fleet_ui_cmux_teardown "$1"',"",str(h)],env=env,capture_output=True,text=True).returncode,0)
            calls=''.join(log.read_text().splitlines()); self.assertIn('set-workspace-meta',calls); self.assertIn('set-status',calls); self.assertIn('flash',calls); self.assertIn('close-surface',calls); self.assertFalse(h.exists())
            h.write_text(json.dumps({'driver':'cmux','workspace_id':'foreign','surface_id':'s'}))
            self.assertNotEqual(subprocess.run(["bash","-c",f'source "{ui}"; fleet_ui_cmux_flash "$1"',"",str(h)],env=env,capture_output=True,text=True).returncode,0)
            before=log.read_text(); self.assertNotEqual(subprocess.run(["bash","-c",f'source "{ui}"; fleet_ui_cmux_teardown "$1"',"",str(h)],env=env,capture_output=True,text=True).returncode,0); after=log.read_text(); self.assertEqual([x for x in after.splitlines() if 'close-surface' in x],[x for x in before.splitlines() if 'close-surface' in x])
            self.assertEqual(subprocess.run(["bash","-c",f'source "{common}"; fleet_select_ui cmux',""],env={**env,"PATH":"/usr/bin:/bin"},capture_output=True,text=True).stdout.strip(),"cmux")

    def test_cmux_stale_handle_and_override_fallback(self):
        ui=ROOT/"plugins/sdd-composy/scripts/fleet/ui-cmux.sh"; common=ROOT/"plugins/sdd-composy/scripts/fleet/common.sh"
        with tempfile.TemporaryDirectory() as td:
            td=Path(td); h=td/"stale.json"; h.write_text(json.dumps({'driver':'cmux','workspace_id':'gone','surface_id':'s'}))
            fake=td/"cmux"; fake.write_text("#!/bin/sh\nexit 0\n"); fake.chmod(0o755); env={**os.environ,"SDD_CMUX_BIN":str(fake)}
            self.assertNotEqual(subprocess.run(["bash","-c",f'source "{ui}"; fleet_ui_cmux_flash "$1"',"",str(h)],env=env,capture_output=True,text=True).returncode,0)
            self.assertEqual(subprocess.run(["bash","-c",f'source "{common}"; fleet_select_ui auto',""],env={**env,"PATH":"/usr/bin:/bin"},capture_output=True,text=True).stdout.strip(),"cmux")

    def test_cmux_cross_fleet_handle_is_rejected(self):
        ui=ROOT/"plugins/sdd-composy/scripts/fleet/ui-cmux.sh"
        with tempfile.TemporaryDirectory() as td:
            td=Path(td); log=td/"calls"; fake=td/"cmux"
            fake.write_text("#!/bin/sh\n[ \"$1\" = list-workspaces ] && echo '{\\\"workspaces\\\":[{\\\"id\\\":\\\"ws-1\\\",\\\"owner\\\":\\\"sdd-composy\\\",\\\"sdd_composy_fleet\\\":\\\"fleet-a\\\"}]}' || echo '{}'\n") ; fake.chmod(0o755)
            env={**os.environ,"SDD_CMUX_BIN":str(fake)}; h=td/"h.json"; h.write_text(json.dumps({"driver":"cmux","workspace_id":"ws-1","surface_id":"s","fleet_id":"fleet-b"}))
            r=subprocess.run(["bash","-c",f'source "{ui}"; fleet_ui_cmux_status "$1" nope red',"",str(h)],env=env,capture_output=True,text=True)
            self.assertNotEqual(r.returncode,0)

    def test_dashboard_rejects_malformed_members_and_confines_output(self):
        dashboard = ROOT / "plugins/sdd-composy/scripts/fleet/dashboard.sh"
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); members = root/".planning/sdd-composy/fleet/demo/members"; members.mkdir(parents=True)
            (members/"bad.json").write_text('{broken\n')
            r = subprocess.run([str(dashboard), "--root", str(root), "--fleet-id", "demo"], capture_output=True, text=True)
            self.assertNotEqual(r.returncode, 0); self.assertIn("malformed", r.stderr)
            (members/"bad.json").unlink()
            (members/"one.json").write_text(json.dumps({"id":"TASK-001","status":"running","message":"x"*1000,"worktree_path":"../../escape"}))
            r = subprocess.run([str(dashboard), "--root", str(root), "--fleet-id", "demo"], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr); self.assertNotIn("escape", r.stdout); self.assertLess(len(r.stdout), 600)

    def test_dashboard_aggregates_status_and_marks_attention_transitions(self):
        dashboard = ROOT / "plugins/sdd-composy/scripts/fleet/dashboard.sh"
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); state = root/".planning/sdd-composy/fleet/demo"; members = state/"members"; members.mkdir(parents=True)
            (state/"fleet.json").write_text(json.dumps({"fleet_id":"demo","members":["TASK-001","TASK-002"]}))
            (members/"TASK-001.json").write_text(json.dumps({"id":"TASK-001","status":"completed","message":"done"}))
            (members/"TASK-002.json").write_text(json.dumps({"id":"TASK-002","status":"failed","message":"needs review"}))
            r = subprocess.run([str(dashboard), "--root", str(root), "--fleet-id", "demo", "--json"], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr); d=json.loads(r.stdout)
            self.assertEqual(d["counts"]["completed"], 1); self.assertEqual(d["counts"]["failed"], 1)
            self.assertTrue(d["attention"]); self.assertEqual(d["members"][1]["status"], "failed")
            status = subprocess.run(["python3", str(ROOT/"plugins/sdd-composy/scripts/sdd_status.py"), str(root), "--fleet", "--json"], capture_output=True, text=True)
            self.assertEqual(status.returncode, 0, status.stderr); snapshot=json.loads(status.stdout)
            self.assertEqual(snapshot["status"], "fleet"); self.assertTrue(snapshot["fleet_summary"])

if __name__ == "__main__": unittest.main()
