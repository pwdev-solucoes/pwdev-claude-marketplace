import json, os, subprocess, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
FLEET = ROOT / "plugins/sdd-composy/scripts/fleet"

class FleetRunnerTest(unittest.TestCase):
    def source(self, runtime, code):
        script = FLEET / f"engine-{runtime}.sh"
        return subprocess.run(["bash", "-c", f'. "{script}"; {code}'], capture_output=True, text=True)

    def test_codex_vector_is_fixed_and_acknowledges_dangerous_mode(self):
        r = self.source("codex", 'sdd_engine_codex_stage_command /wt /schema /result PROMPT; printf "%s\\n" "${FLOW_ENGINE_COMMAND[@]}"')
        self.assertEqual(r.returncode, 0, r.stderr)
        args = r.stdout.splitlines()
        self.assertEqual(args[:4], ["codex", "exec", "--dangerously-bypass-approvals-and-sandbox", "--ephemeral"])
        self.assertIn("--output-schema", args); self.assertIn("--output-last-message", args)
        self.assertEqual(args[-1], "PROMPT")

    def test_claude_vector_is_fixed(self):
        r = self.source("claude", 'sdd_engine_claude_stage_command /wt /schema /result PROMPT; printf "%s\\n" "${FLOW_ENGINE_COMMAND[@]}"')
        self.assertEqual(r.returncode, 0, r.stderr)
        args = r.stdout.splitlines()
        self.assertEqual(args[:4], ["claude", "-p", "--dangerously-skip-permissions", "--no-session-persistence"])
        self.assertIn("--output-format", args)

    def test_claude_malformed_result_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            raw, out = Path(d)/"raw", Path(d)/"out"
            raw.write_text(json.dumps({"is_error": False, "result": "not json"}))
            r = self.source("claude", f'sdd_engine_claude_publish_result "{raw}" "{out}"')
            self.assertNotEqual(r.returncode, 0); self.assertFalse(out.read_text() if out.exists() else False)

    def test_runtime_mismatch_is_rejected(self):
        runner = FLEET / "run.sh"
        r = subprocess.run([str(runner), "demo", "/tmp/no-such-worktree"], env={**os.environ, "SDD_FLEET_RUNTIME":"unknown"}, capture_output=True, text=True)
        self.assertNotEqual(r.returncode, 0); self.assertIn("unsupported fleet runtime", r.stderr)

    def test_registered_worktree_reaches_provider_and_cleans_process_group(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "repo"; root.mkdir()
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            subprocess.run(["git", "-C", str(root), "config", "user.email", "test@example.invalid"], check=True)
            subprocess.run(["git", "-C", str(root), "config", "user.name", "Test"], check=True)
            (root / "README").write_text("x\n"); subprocess.run(["git", "-C", str(root), "add", "."], check=True); subprocess.run(["git", "-C", str(root), "commit", "-qm", "base"], check=True)
            contract = root / "contract.json"; contract.write_text(json.dumps({"id":"demo","state":"ready","dependencies":[],"acceptance_criteria":["ok"],"verification_commands":["true"],"allowed_paths":["README"],"contract_path":str(contract)}))
            launch = FLEET / "launch.sh"
            launched = subprocess.run([str(launch), "--root", str(root), "--fleet-id", "demo", "--base-branch", "master", "--task", str(contract)], capture_output=True, text=True)
            if launched.returncode != 0:
                # git's initial branch may be named main in the host image.
                base = subprocess.check_output(["git", "-C", str(root), "branch", "--show-current"], text=True).strip()
                launched = subprocess.run([str(launch), "--root", str(root), "--fleet-id", "demo", "--base-branch", base, "--task", str(contract)], capture_output=True, text=True)
            self.assertEqual(launched.returncode, 0, launched.stderr)
            state = root / ".planning/sdd-composy/fleet/demo/members"; record = json.loads((state / "demo.json").read_text()); work = Path(record["worktree"])
            phase = work / ".planning/sdd-composy/phases/demo"; phase.mkdir(parents=True)
            spec = phase / "spec.md"; decisions = phase / "decisions.md"
            spec.write_text("Status: APPROVED\n"); decisions.write_text("Status: APPROVED\n")
            import hashlib
            record.update({"spec_sha256":hashlib.sha256(spec.read_bytes()).hexdigest(), "decisions_sha256":hashlib.sha256(decisions.read_bytes()).hexdigest()})
            record.update({"id":"demo", "slug":"demo", "status":"ACTIVE", "runtime":"codex", "worktree":str(work), "worktree_path":str(work), "branch":"sdd-fleet/demo"}); (state / "demo.json").write_text(json.dumps(record))
            fake = Path(d) / "bin"; fake.mkdir(); called = Path(d) / "called"; child = Path(d) / "child.pid"
            fake.joinpath("codex").write_text("#!/bin/sh\nprintf x > '%s'\nsleep 60 & echo $! > '%s'\nexit 7\n" % (called, child)); fake.joinpath("codex").chmod(0o755)
            env = {**os.environ, "PATH": str(fake) + ":/usr/bin:/bin", "SDD_FLEET_RUNTIME":"codex"}
            result = subprocess.run([str(FLEET / "run.sh"), "demo", str(work)], env=env, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertTrue(called.exists(), result.stderr)
            self.assertFalse((root / ".planning/sdd-composy/fleet/demo/.demo.runner.lock").exists())
            self.assertTrue(child.exists())
            child_pid = int(child.read_text())
            self.assertNotEqual(subprocess.run(["kill", "-0", str(child_pid)]).returncode, 0)

if __name__ == "__main__": unittest.main()
