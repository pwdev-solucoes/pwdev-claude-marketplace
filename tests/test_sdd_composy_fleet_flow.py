"""Fleet end to end from real SDD artifacts: approved TechSpec, task projection, launch, run, merge.

The previous fleet tests fabricated legacy `phases/<slug>/{spec,decisions}.md` files that no
skill produces, and edited member JSON by hand to reach a mergeable state.
"""

import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import textwrap
import time
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "sdd-composy"
FLEET = PLUGIN / "scripts" / "fleet"
sys.path.insert(0, str(PLUGIN / "scripts"))
sys.path.insert(0, str(FLEET))
sys.path.insert(0, str(ROOT / "tests"))
import interactive_state  # noqa: E402

TECHSPEC = """---
type: TECHSPEC
okf_version: "0.2"
sources:
  - resource: "tasks/prd-demo/prd.md"
generated:
  by: "agent:codex"
  at: "2026-09-15T10:00:00Z"
lifecycle:
  status: {status}
human_approval: {status}
verified:
  - by: "human:paulo"
    at: "2026-09-15T11:00:00Z"
---

# Demo — Technical Specification
"""

# A provider double that honours the stage contract: it edits the allowed file on EXECUTE and,
# on VERIFY, runs the task's verification command and writes the hashed command record the
# LOOP requires, below the LOOP root it receives in the contract.
FAKE_CLAUDE = textwrap.dedent('''\
    #!/usr/bin/env python3
    import hashlib, json, os, pathlib, subprocess, sys, time
    prompt = sys.argv[sys.argv.index("-p") + 1]
    contract = json.loads(prompt[prompt.index("{"):])
    stage = contract["stage"]
    evidence = {"status": "passed"}
    if stage == "EXECUTE":
        pathlib.Path("src/app.py").write_text("changed by the fleet\\n")
    if stage == "VERIFY":
        started = time.time()
        completed = subprocess.run(["true"], capture_output=True, text=True)
        record = {"task_id": contract["task_id"], "loop_id": contract["loop_id"], "status": "passed",
                  "exit_code": completed.returncode, "command": ["true"], "stdout": completed.stdout,
                  "stderr": completed.stderr, "started_at": started, "ended_at": time.time()}
        record["sha256"] = hashlib.sha256((record["stdout"] + "\\n" + record["stderr"]).encode()).hexdigest()
        relative = pathlib.Path(".planning/sdd-composy/evidence") / (contract["loop_id"] + "-verify.json")
        target = pathlib.Path(contract["loop_root"]) / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        raw = json.dumps(record).encode(); target.write_bytes(raw)
        evidence = {"status": "passed", "command_record": {"path": str(relative), "sha256": hashlib.sha256(raw).hexdigest()}}
    result = {"stage": stage, "status": "completed", "message": stage + " ok", "verdict": "passed", "evidence": evidence}
    print(json.dumps({"type": "result", "subtype": "success", "is_error": False, "result": json.dumps(result),
                      "session_id": "fake", "usage": {}}))
''')


def git(root, *args):
    return subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, text=True).stdout.strip()


class FleetRepository(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name).resolve() / "repo"
        self.repo.mkdir()
        git(self.repo, "init", "-q")
        git(self.repo, "config", "user.email", "test@example.invalid")
        git(self.repo, "config", "user.name", "Test")
        (self.repo / "src").mkdir()
        (self.repo / "src/app.py").write_text("base\n")
        (self.repo / "other").mkdir()
        (self.repo / "other/lib.py").write_text("base\n")
        self.techspec("APPROVED")
        self.projection()
        git(self.repo, "add", "."); git(self.repo, "commit", "-qm", "approved contracts")
        self.base = git(self.repo, "branch", "--show-current")
        self.bin = Path(self.tmp.name) / "bin"; self.bin.mkdir()
        claude = self.bin / "claude"; claude.write_text(FAKE_CLAUDE); claude.chmod(0o755)

    def tearDown(self):
        for line in git(self.repo, "worktree", "list", "--porcelain").splitlines():
            if line.startswith("worktree ") and Path(line[9:]).resolve() != self.repo:
                subprocess.run(["git", "-C", str(self.repo), "worktree", "remove", "--force", line[9:]], capture_output=True)
        self.tmp.cleanup()

    def techspec(self, status):
        path = self.repo / "tasks/prd-demo/techspec.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(TECHSPEC.format(status=status), encoding="utf-8")

    def projection(self, **overrides):
        base = {"dependencies": [], "acceptance_criteria": ["CA-001"], "verification_commands": ["true"],
                "evidence_required": False}
        tasks = [{**base, "id": "TASK-001", "title": "one", "state": "ready", "allowed_paths": ["src/app.py"]},
                 {**base, "id": "TASK-002", "title": "two", "state": "pending", "allowed_paths": ["other/lib.py"],
                  "dependencies": ["TASK-001"]}]
        tasks[0].update(overrides)
        self.contract = self.repo / ".planning/sdd-composy/tasks/demo.json"
        self.contract.parent.mkdir(parents=True, exist_ok=True)
        self.contract.write_text(json.dumps({"schema_version": "1", "prd_slug": "demo",
                                             "updated_at": "2026-09-15T12:00:00Z", "tasks": tasks}), encoding="utf-8")

    def env(self, **extra):
        return {**os.environ, "PATH": f"{self.bin}:{os.environ['PATH']}", "SDD_CLAUDE_ISOLATED": "1", **extra}

    def launch(self, *extra, fleet_id="demo", env=None):
        args = [str(FLEET / "launch.sh"), "--runtime", "claude", "--ui", "headless", "--root", str(self.repo),
                "--fleet-id", fleet_id, "--base-branch", self.base, "--task", str(self.contract), *extra]
        return subprocess.run(args, capture_output=True, text=True, env=env or self.env())

    def member_path(self, fleet_id="demo", member="TASK-001"):
        return self.repo / f".planning/sdd-composy/fleet/{fleet_id}/members/{member}.json"

    def wait_member(self, predicate, timeout=60):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            path = self.member_path()
            if path.exists():
                try: member = json.loads(path.read_text())
                except ValueError: member = None
                if member and predicate(member): return member
            time.sleep(0.1)
        log = self.repo / ".planning/sdd-composy/fleet/demo/task-001.log"
        self.fail("member never reached the expected state: " + (log.read_text() if log.exists() else "no log"))

    def no_fleet_leftovers(self):
        self.assertNotIn(".sddcomposy-fleet-", git(self.repo, "worktree", "list"))
        self.assertEqual(git(self.repo, "branch", "--list", "sdd-fleet/*"), "")


class LaunchGateTests(FleetRepository):
    def test_launch_requires_an_approved_techspec(self):
        self.techspec("DRAFT"); git(self.repo, "commit", "-qam", "draft")
        result = self.launch("--human-approved", "--approved-by", "human:paulo")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("techspec", result.stderr.lower())
        self.no_fleet_leftovers()

    def test_launch_requires_the_canonical_task_projection(self):
        elsewhere = self.repo / "contract.json"
        elsewhere.write_text(self.contract.read_text())
        result = subprocess.run([str(FLEET / "launch.sh"), "--runtime", "claude", "--ui", "headless", "--root", str(self.repo),
                                 "--fleet-id", "demo", "--base-branch", self.base, "--task", str(elsewhere),
                                 "--human-approved", "--approved-by", "human:paulo"],
                                capture_output=True, text=True, env=self.env())
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("projection", result.stderr)
        self.no_fleet_leftovers()

    def test_headless_launch_requires_recorded_human_approval(self):
        result = self.launch()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--human-approved", result.stderr)
        self.no_fleet_leftovers()
        refused = self.launch("--human-approved", "--approved-by", "not an actor")
        self.assertNotEqual(refused.returncode, 0)

    def test_mixed_bundle_selects_only_ready_tasks_and_reads_dependencies_from_it(self):
        prepared = self.launch("--prepare-only")
        self.assertEqual(prepared.returncode, 0, prepared.stderr)
        members = sorted(p.stem for p in self.member_path().parent.glob("*.json"))
        self.assertEqual(members, ["TASK-001"])

    def test_single_task_with_dependencies_outside_a_projection_is_refused(self):
        self.projection(dependencies=["TASK-002"])
        single = self.repo / "single.json"
        single.write_text(json.dumps(json.loads(self.contract.read_text())["tasks"][0]))
        result = subprocess.run([str(FLEET / "launch.sh"), "--prepare-only", "--runtime", "claude", "--root", str(self.repo),
                                 "--fleet-id", "demo", "--base-branch", self.base, "--task", str(single)],
                                capture_output=True, text=True, env=self.env())
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("dependencies", result.stderr)

    def test_unsafe_fleet_ids_are_rejected_before_any_write(self):
        for fleet_id in ("..", ".", "a/b"):
            with self.subTest(fleet_id=fleet_id):
                result = self.launch("--prepare-only", fleet_id=fleet_id)
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse((self.repo / ".planning/sdd-composy/members").exists())
                self.assertFalse((self.repo / ".planning/sdd-composy/fleet").exists())


class HeadlessRunAndMergeTests(FleetRepository):
    def test_headless_member_runs_the_loop_commits_allowed_paths_and_merges(self):
        launched = self.launch("--human-approved", "--approved-by", "human:paulo",
                               env=self.env(SDD_FLEET_UI_LOG=str(self.repo / ".planning/sdd-composy/fleet/demo/task-001.log")))
        self.assertEqual(launched.returncode, 0, launched.stderr)
        member = self.wait_member(lambda m: m["status"] in {"completed", "failed", "blocked"})
        self.assertEqual(member["status"], "completed", member)
        self.assertEqual(member["approval"]["by"], "human:paulo")
        self.assertEqual(member["interaction"]["state"], "completed")
        worktree = Path(member["worktree_path"])
        self.assertEqual(git(worktree, "rev-parse", "HEAD"), member["commit"])
        self.assertEqual(git(worktree, "status", "--porcelain"), "")
        result = json.loads((self.repo / member["result_path"]).read_text())
        self.assertEqual((result["member_id"], result["status"], result["commit"]), ("TASK-001", "completed", member["commit"]))
        schema = json.loads((PLUGIN / "schemas/fleet-result.schema.json").read_text())
        from test_sdd_composy import assert_schema_valid
        assert_schema_valid(self, schema, result)
        interactive_state.load_member(self.member_path())

        merged = subprocess.run([str(FLEET / "teardown.sh"), "--root", str(self.repo), "--fleet-id", "demo",
                                 "--member-id", "TASK-001", "--merge", "--confirm", "CONFIRM-SDD-MERGE"],
                                capture_output=True, text=True, env=self.env())
        self.assertEqual(merged.returncode, 0, merged.stderr)
        self.assertEqual((self.repo / "src/app.py").read_text(), "changed by the fleet\n")
        self.no_fleet_leftovers()
        self.assertFalse((self.repo / ".planning/sdd-composy/fleet/demo/task-001.ui.json").exists())

    def test_changes_outside_allowed_paths_block_the_member_without_a_commit(self):
        escaping = FAKE_CLAUDE.replace('pathlib.Path("src/app.py").write_text("changed by the fleet\\n")',
                                       'pathlib.Path("other/lib.py").write_text("out of scope\\n")')
        self.assertNotEqual(escaping, FAKE_CLAUDE)
        (self.bin / "claude").write_text(escaping)
        launched = self.launch("--human-approved", "--approved-by", "human:paulo")
        self.assertEqual(launched.returncode, 0, launched.stderr)
        member = self.wait_member(lambda m: m["status"] in {"completed", "failed", "blocked"})
        self.assertEqual(member["status"], "blocked")
        self.assertIn("other/lib.py", member["message"])
        self.assertEqual(git(Path(member["worktree_path"]), "rev-parse", "HEAD"), git(self.repo, "rev-parse", self.base))

    def test_merge_refuses_a_root_on_another_branch(self):
        launched = self.launch("--human-approved", "--approved-by", "human:paulo")
        self.assertEqual(launched.returncode, 0, launched.stderr)
        self.wait_member(lambda m: m["status"] == "completed")
        git(self.repo, "checkout", "-qb", "elsewhere")
        refused = subprocess.run([str(FLEET / "teardown.sh"), "--root", str(self.repo), "--fleet-id", "demo",
                                  "--member-id", "TASK-001", "--merge", "--confirm", "CONFIRM-SDD-MERGE"],
                                 capture_output=True, text=True, env=self.env())
        self.assertNotEqual(refused.returncode, 0)
        self.assertIn("base branch", refused.stderr)


class TeardownResourceTests(FleetRepository):
    def test_teardown_stops_a_live_headless_runner(self):
        sleeper = self.bin / "claude"
        sleeper.write_text("#!/bin/sh\nsleep 30\n"); sleeper.chmod(0o755)
        launched = self.launch("--human-approved", "--approved-by", "human:paulo")
        self.assertEqual(launched.returncode, 0, launched.stderr)
        handle = self.repo / ".planning/sdd-composy/fleet/demo/task-001.ui.json"
        pid = json.loads(handle.read_text())["pid"]
        stopped = subprocess.run([str(FLEET / "teardown.sh"), "--root", str(self.repo), "--fleet-id", "demo",
                                  "--member-id", "TASK-001"], capture_output=True, text=True, env=self.env())
        self.assertEqual(stopped.returncode, 0, stopped.stderr)
        self.assertNotEqual(subprocess.run(["kill", "-0", str(pid)], capture_output=True).returncode, 0)
        self.assertFalse(handle.exists())
        self.assertEqual(subprocess.run(["pgrep", "-f", f"{self.bin}/claude"], capture_output=True).returncode, 1)

    def test_shared_compose_stays_up_until_the_last_member_is_torn_down(self):
        self.projection(); tasks = json.loads(self.contract.read_text())
        tasks["tasks"][1].update(state="ready", dependencies=[])
        self.contract.write_text(json.dumps(tasks))
        docker_log = Path(self.tmp.name) / "docker.log"
        docker = self.bin / "docker"
        docker.write_text(f"#!/bin/sh\nprintf '%s\\n' \"$*\" >> '{docker_log}'\nexit 0\n"); docker.chmod(0o755)
        prepared = self.launch("--prepare-only", "--compose")
        self.assertEqual(prepared.returncode, 0, prepared.stderr)
        docker_log.write_text("")
        teardown = lambda member: subprocess.run([str(FLEET / "teardown.sh"), "--root", str(self.repo), "--fleet-id", "demo",
                                                  "--member-id", member], capture_output=True, text=True, env=self.env())
        first = teardown("TASK-001"); self.assertEqual(first.returncode, 0, first.stderr)
        self.assertNotIn("down", docker_log.read_text())
        second = teardown("TASK-002"); self.assertEqual(second.returncode, 0, second.stderr)
        calls = docker_log.read_text()
        self.assertIn("down", calls)
        self.assertIn("--env-file", calls)


class PortLockTests(unittest.TestCase):
    def test_stale_port_lock_times_out_instead_of_spinning(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = Path(tmp)
            (state / ".ports.lock").write_text("12345")
            started = time.monotonic()
            result = subprocess.run(["bash", "-c", f'. "{FLEET}/common.sh"; port=$(fleet_allocate_port "$1" 43400 43401) || exit 9; echo "$port"', "", str(state)],
                                    capture_output=True, text=True, timeout=20, env={**os.environ, "SDD_FLEET_LOCK_TIMEOUT": "1"})
            self.assertEqual(result.returncode, 9, result.stdout + result.stderr)
            self.assertLess(time.monotonic() - started, 10)


class OpenCodeInteractiveTests(unittest.TestCase):
    def test_interactive_state_and_runner_accept_opencode_members(self):
        self.assertIn("opencode", interactive_state.RUNTIMES)
        runner = (FLEET / "interactive-run.sh").read_text()
        self.assertRegex(runner, r"case \$RUNTIME in [^)]*opencode")


class RunnerSurfaceTests(unittest.TestCase):
    def test_legacy_stage_machine_and_migration_are_gone(self):
        runner = (FLEET / "run.sh").read_text()
        for legacy in ("--migrate-member", "phases/", "flow_audit.py", "fleet-status.json", "git add -A", "ENGINE_ADAPTER"):
            self.assertNotIn(legacy, runner)
        self.assertNotIn("phases/", (FLEET / "launch.sh").read_text())
        for engine in FLEET.glob("engine-*.sh"):
            text = engine.read_text()
            self.assertNotRegex(text, r"_stage_command\(\)|_publish_result\(\)|_prompt_suffix\(\)")
        self.assertNotIn("human_approved=True", runner)


if __name__ == "__main__":
    unittest.main()
