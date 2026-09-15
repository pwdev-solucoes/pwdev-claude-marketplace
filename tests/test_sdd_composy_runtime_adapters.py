import importlib.util
import hashlib
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "sdd-composy"


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CODEX = load(PLUGIN / "scripts/loop-engine-codex.py", "sdd_loop_codex_test")
HERMES = load(PLUGIN / "scripts/loop-engine-hermes.py", "sdd_loop_hermes_test")
OPENCODE = load(PLUGIN / "scripts/loop-engine-opencode.py", "sdd_loop_opencode_test")


def contract(stage="plan", **extra):
    value = {"stage": stage, "task_id": "TASK-004", "iteration": 1}
    value.update(extra)
    return value


def result(stage="plan", **extra):
    value = {"stage": stage, "status": "completed", "message": "done",
             "verdict": "passed", "evidence": {"status": "passed"}}
    value.update(extra)
    return value


def executable(directory, name, body):
    path = Path(directory) / name
    path.write_text("#!/usr/bin/env python3\n" + body, encoding="utf-8")
    path.chmod(0o755)
    return path


class LoopAdapterTests(unittest.TestCase):
    def test_codex_uses_final_message_file_and_ignores_jsonl_events(self):
        with tempfile.TemporaryDirectory() as directory:
            capture = Path(directory) / "capture.json"
            fake = executable(directory, "codex", f'''import json, os, pathlib, sys
pathlib.Path({str(capture)!r}).write_text(json.dumps({{"argv": sys.argv[1:], "cwd": os.getcwd()}}))
out = sys.argv[sys.argv.index("--output-last-message") + 1]
pathlib.Path(out).write_text(json.dumps({result()!r}))
print(json.dumps({{"type": "thread.started"}}))
print(json.dumps({{"type": "item.completed", "item": {{"text": "not the result"}}}}))
''')
            actual = CODEX.run(contract(), Path(directory), executable=str(fake))
            self.assertEqual(actual, result())
            called = json.loads(capture.read_text())
            self.assertEqual(Path(called["cwd"]).resolve(), Path(directory).resolve())
            self.assertIn("--sandbox", called["argv"])
            self.assertEqual(called["argv"][called["argv"].index("--sandbox") + 1], "workspace-write")
            self.assertIn("--output-last-message", called["argv"])
            self.assertNotIn("--dangerously-bypass-approvals-and-sandbox", called["argv"])

    def test_hermes_uses_confirmed_native_vector_and_preserves_prompt(self):
        with tempfile.TemporaryDirectory() as directory:
            capture = Path(directory) / "capture.json"
            wanted = contract(automation_consent=True, prompt="quote ' ; $(touch nope)")
            fake = executable(directory, "hermes", f'''import json, os, pathlib, sys
pathlib.Path({str(capture)!r}).write_text(json.dumps({{"argv": sys.argv[1:], "cwd": os.getcwd()}}))
print(json.dumps({result()!r}))
''')
            self.assertEqual(HERMES.run(wanted, Path(directory), executable=str(fake)), result())
            called = json.loads(capture.read_text())
            self.assertEqual(called["argv"][0], "-z")
            self.assertEqual(called["argv"][-2:], ["--in", directory])
            self.assertNotIn("run", called["argv"])
            self.assertNotIn("--yolo", called["argv"])
            self.assertIn(wanted["prompt"], called["argv"][1])

    def test_hermes_requires_isolation_or_specific_consent(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(HERMES.RuntimeError_, "isolation or automation consent"):
                HERMES.run(contract(), Path(directory), executable="must-not-run")

    def test_adapters_fail_closed_for_process_error_timeout_and_invalid_output(self):
        for adapter, permission in ((CODEX, {}), (HERMES, {"automation_consent": True}),
                                    (OPENCODE, {"automation_consent": True})):
            with self.subTest(adapter=adapter.__name__), tempfile.TemporaryDirectory() as directory:
                bad = executable(directory, "bad", "import sys; sys.exit(19)\n")
                with self.assertRaisesRegex(adapter.RuntimeError_, "status 19"):
                    adapter.run(contract(**permission), Path(directory), executable=str(bad))
                malformed = executable(directory, "malformed", "print('not json')\n")
                with self.assertRaisesRegex(adapter.RuntimeError_, "malformed JSON"):
                    adapter.run(contract(**permission), Path(directory), executable=str(malformed))
                slow = executable(directory, "slow", "import time; time.sleep(2)\n")
                with self.assertRaisesRegex(adapter.RuntimeError_, "timeout"):
                    adapter.run(contract(**permission), Path(directory), executable=str(slow), timeout=.05)
                with self.assertRaisesRegex(adapter.RuntimeError_, "runtime unavailable"):
                    adapter.run(contract(**permission), Path(directory), executable=str(Path(directory) / "missing"))

    def test_adapters_reject_stage_identity_and_synthetic_canonical_verify(self):
        for adapter in (CODEX, HERMES, OPENCODE):
            with self.subTest(adapter=adapter.__name__):
                with self.assertRaisesRegex(adapter.RuntimeError_, "requested stage"):
                    adapter.validate_result(result("qa"), "plan")
                false_verify = result("VERIFY", evidence={"status": "passed", "command_record": {
                    "path": "evidence/invented.json", "sha256": "0" * 64,
                    "command": ["python3", "-m", "unittest"], "exit_code": 0,
                }})
                with self.assertRaisesRegex(adapter.RuntimeError_, "VERIFY requires real command evidence"):
                    adapter.validate_result(false_verify, "VERIFY", root=Path("/tmp"),
                                            stage_contract=contract("VERIFY"))

    def test_adapters_verify_canonical_record_against_durable_loop(self):
        for adapter in (CODEX, HERMES, OPENCODE):
            with self.subTest(adapter=adapter.__name__), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                loops = root / ".planning/sdd-composy/loops"
                records = root / "evidence"
                loops.mkdir(parents=True); records.mkdir()
                command = {"task_id": "TASK-004", "loop_id": "loop-04", "status": "passed",
                           "exit_code": 0, "command": ["python3", "-m", "unittest"],
                           "stdout": "OK", "stderr": "", "started_at": 101, "ended_at": 102}
                command["sha256"] = hashlib.sha256(b"OK\n").hexdigest()
                raw = json.dumps(command, sort_keys=True).encode()
                (records / "verify.json").write_bytes(raw)
                loop = {"id": "loop-04", "task_id": "TASK-004", "status": "running",
                        "stages": [{"name": "REVIEW", "published_at": "1970-01-01T00:01:40Z"}]}
                (loops / "loop-04.json").write_text(json.dumps(loop), encoding="utf-8")
                verified = result("VERIFY", evidence={"status": "passed", "command_record": {
                    "path": "evidence/verify.json", "sha256": hashlib.sha256(raw).hexdigest()}})
                self.assertEqual(adapter.validate_result(
                    verified, "VERIFY", root=root, stage_contract=contract("VERIFY"), now=103), verified)


class FleetInteractiveAdapterTests(unittest.TestCase):
    FORBIDDEN = (
        "--yolo",
        "--accept-hooks",
        "--dangerously-bypass-approvals-and-sandbox",
        "--dangerously-skip-permissions",
    )

    def interactive_command(self, runtime, prompt="quote ' ; $HOME"):
        script = PLUGIN / "scripts/fleet" / f"engine-{runtime}.sh"
        with tempfile.TemporaryDirectory() as directory:
            prompt_file = Path(directory) / "prompt.txt"
            prompt_file.write_text(prompt, encoding="utf-8")
            shell = (f'source "{script}"\n'
                     f'sdd_engine_{runtime}_interactive_command "/work tree" '
                     f'"{prompt_file}" "/plugin root"\n'
                     'printf "cwd=%s\\n" "$SDD_ENGINE_CWD"\n'
                     'printf "%s\\n" "${SDD_ENGINE_COMMAND[@]}"\n')
            completed = subprocess.run(
                ["/bin/bash", "-c", shell], env=os.environ,
                text=True, capture_output=True, check=False)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        lines = completed.stdout.splitlines()
        return lines[0].removeprefix("cwd="), lines[1:]

    def assert_safe(self, argv):
        for flag in self.FORBIDDEN:
            self.assertNotIn(flag, argv)

    def test_hermes_interactive_vector_uses_query_file_and_worktree(self):
        cwd, argv = self.interactive_command("hermes")
        self.assertEqual(cwd, "")
        self.assertEqual(argv[:2], ["hermes", "chat"])
        self.assertEqual(argv[2], "--query-file")
        self.assertTrue(argv[3].endswith("/prompt.txt"))
        self.assertEqual(argv[4:], ["--cli", "--in", "/work tree"])
        self.assert_safe(argv)

    def test_codex_interactive_vector_uses_prompt_argument_and_safe_sandbox(self):
        cwd, argv = self.interactive_command("codex")
        self.assertEqual(cwd, "")
        self.assertEqual(argv, [
            "codex", "--cd", "/work tree", "--sandbox", "workspace-write",
            "quote ' ; $HOME",
        ])
        self.assert_safe(argv)

    def test_claude_interactive_vector_uses_prompt_argument_and_plugin_root(self):
        cwd, argv = self.interactive_command("claude")
        self.assertEqual(cwd, "")
        self.assertEqual(argv, [
            "claude", "--add-dir", "/work tree", "--plugin-dir", "/plugin root",
            "quote ' ; $HOME",
        ])
        self.assert_safe(argv)

    def test_opencode_interactive_vector_targets_worktree_with_prompt(self):
        cwd, argv = self.interactive_command("opencode")
        self.assertEqual(cwd, "")
        self.assertEqual(argv[:4], ["opencode", "/work tree", "--prompt", "quote ' ; $HOME"])
        self.assert_safe(argv)


class OpenCodeLoopAdapterTests(unittest.TestCase):
    def test_uses_confirmed_native_vector_with_consent_prompt_and_json_ndjson(self):
        with tempfile.TemporaryDirectory() as directory:
            capture = Path(directory) / "capture.json"
            wanted = contract(automation_consent=True, prompt="quote ' ; $(touch nope)")
            final = json.dumps(result())
            fake = executable(directory, "opencode", f'''import json, os, pathlib, sys
pathlib.Path({str(capture)!r}).write_text(json.dumps({{"argv": sys.argv[1:], "cwd": os.getcwd()}}))
print(json.dumps({{"type": "text", "part": {{"type": "text", "text": {final!r}}}}}))
''')
            self.assertEqual(OPENCODE.run(wanted, Path(directory), executable=str(fake)), result())
            called = json.loads(capture.read_text())
            argv, cwd = called["argv"], called["cwd"]
            self.assertEqual(argv[0], "run")
            self.assertEqual(argv[1:3], ["--dir", directory])
            self.assertEqual(Path(cwd).resolve(), Path(directory).resolve())
            self.assertIn("--format", argv)
            self.assertEqual(argv[argv.index("--format") + 1], "json")
            self.assertNotIn("--auto", argv)
            self.assertNotIn("--dangerously-skip-permissions", argv)
            self.assertIn(wanted["prompt"], argv[-1])

    def test_requires_isolation_or_specific_consent(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(OPENCODE.RuntimeError_, "isolation or automation consent"):
                OPENCODE.run(contract(), Path(directory), executable="must-not-run")


class HermesBootstrapTests(unittest.TestCase):
    def test_registers_exact_skills_as_paths_and_small_routing_context(self):
        module = load(PLUGIN / ".hermes-plugin/__init__.py", "sdd_hermes_bootstrap_test")
        class Context:
            def __init__(self): self.skills, self.hooks = [], {}
            def register_skill(self, name, path):
                self.assert_path(path); self.skills.append((name, path))
            def assert_path(self, path):
                if not isinstance(path, Path): raise AssertionError(type(path))
            def register_hook(self, name, hook): self.hooks[name] = hook
        ctx = Context()
        module.register(ctx)
        self.assertEqual(len(ctx.skills), 17)
        text = ctx.hooks["pre_llm_call"](is_first_turn=True)["context"]
        self.assertLess(len(text), 4000)
        self.assertIn("skill_view", text)
        self.assertNotIn("## Workflow", text)
        self.assertNotIn("hermes kanban", text)
        self.assertIsNone(ctx.hooks["pre_llm_call"](is_first_turn=False))


if __name__ == "__main__":
    unittest.main()
