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
        for adapter, permission in ((CODEX, {}), (HERMES, {"automation_consent": True})):
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
        for adapter in (CODEX, HERMES):
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
        for adapter in (CODEX, HERMES):
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


class FleetHermesAdapterTests(unittest.TestCase):
    SCRIPT = PLUGIN / "scripts/fleet/engine-hermes.sh"

    def command(self, env=None):
        shell = (f'source "{self.SCRIPT}"\n'
                 'sdd_engine_hermes_stage_command "/work tree" "/schema" "/result" "quote \' ; \\$HOME"\n'
                 'printf "cwd=%s\\n" "$FLOW_ENGINE_CWD"\n'
                 'printf "stdout=%s\\n" "$FLOW_ENGINE_RESULT_FROM_STDOUT"\n'
                 'printf "%s\\n" "${FLOW_ENGINE_COMMAND[@]}"\n')
        return subprocess.run(["/bin/bash", "-c", shell], env={**os.environ, **(env or {})},
                              text=True, capture_output=True, check=False)

    def test_fleet_vector_is_native_and_requires_explicit_authorization(self):
        denied = self.command()
        self.assertNotEqual(denied.returncode, 0)
        allowed = self.command({"SDD_HERMES_AUTOMATION_CONSENT": "1"})
        self.assertEqual(allowed.returncode, 0, allowed.stderr)
        self.assertEqual(allowed.stdout.splitlines()[2:],
                         ["hermes", "-z", "quote ' ; $HOME", "--in", "/work tree"])


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
