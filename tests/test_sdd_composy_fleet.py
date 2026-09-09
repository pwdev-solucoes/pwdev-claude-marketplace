import hashlib, json, os, subprocess, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
LAUNCH = ROOT / "plugins/sdd-composy/scripts/fleet/launch.sh"

class FleetLaunchTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.repo = Path(self.tmp.name)
        subprocess.run(["git","init","-q",str(self.repo)],check=True)
        subprocess.run(["git","-C",str(self.repo),"config","user.email","test@example.invalid"],check=True)
        subprocess.run(["git","-C",str(self.repo),"config","user.name","Test"],check=True)
        (self.repo/"src").mkdir(); (self.repo/"src/app.py").write_text("x\n")
        subprocess.run(["git","-C",str(self.repo),"add","."],check=True)
        subprocess.run(["git","-C",str(self.repo),"commit","-qm","base"],check=True)
        self.contract=self.repo/"contract.json"
    def tearDown(self): self.tmp.cleanup()
    def task(self, **kw):
        d={"id":"TASK-001","state":"ready","dependencies":[],"acceptance_criteria":["CA-1"],"verification_commands":["true"],"allowed_paths":["src/app.py"],"contract_path":str(self.contract)}; d.update(kw); self.contract.write_text(json.dumps(d)); return d
    def run(self,*tasks, extra=None):
        args=[str(LAUNCH),"--root",str(self.repo),"--fleet-id","demo","--base-branch","master"]
        for t in tasks: args += ["--task",str(t)]
        return subprocess.run(args,capture_output=True,text=True,env={**os.environ,**(extra or {})})
    def test_ready_contract_hash_and_central_preserved(self):
        self.task(); before=subprocess.check_output(["git","-C",str(self.repo),"status","--porcelain"],text=True)
        r=self.run(self.contract); self.assertEqual(r.returncode,0,r.stderr)
        member=self.repo/".planning/sdd-composy/fleet/demo/members/TASK-001.json"; d=json.loads(member.read_text())
        self.assertEqual(d["contract_sha256"],hashlib.sha256(self.contract.read_bytes()).hexdigest()); self.assertEqual(d["state"],"locked")
        self.assertEqual(subprocess.check_output(["git","-C",str(self.repo),"status","--porcelain"],text=True),before)
    def test_eligibility_and_required_contract_fields(self):
        for key,val in (("state","pending"),("acceptance_criteria",[]),("verification_commands",[]),("dependencies_complete",False)):
            self.task(**{key:val}); self.assertNotEqual(self.run(self.contract).returncode,0)
    def test_symlink_dirty_and_collision_rejected(self):
        self.task(allowed_paths=["link.py"]); (self.repo/"link.py").symlink_to(self.repo/"src/app.py"); self.assertNotEqual(self.run(self.contract).returncode,0)
        self.contract.unlink(); self.contract.symlink_to(self.repo/"src/app.py"); self.assertNotEqual(self.run(self.contract).returncode,0)
        self.contract.unlink(); self.task(id="A",allowed_paths=["src/app.py"]); other=self.repo/"other.json"; other.write_text(json.dumps(self.task(id="B",allowed_paths=["src/app.py"]))); self.assertNotEqual(self.run(self.contract,other).returncode,0)
    def test_branch_collision_and_partial_failure_preserves_branch_or_central(self):
        self.task(); self.assertEqual(self.run(self.contract).returncode,0)
        self.assertNotEqual(self.run(self.contract).returncode,0)
        self.assertTrue((self.repo/".planning/sdd-composy/fleet/demo").exists())

if __name__ == "__main__": unittest.main()
