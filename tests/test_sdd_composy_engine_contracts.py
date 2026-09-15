"""Runtime engine contracts pinned to the real provider output formats.

The fixtures below reproduce what the installed CLIs actually emit (captured on
2026-09-15 from claude 2.1.272 and opencode 1.18.31), not the shape the adapters
happen to expect.
"""

import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "sdd-composy"
SCRIPTS = PLUGIN / "scripts"
sys.path.insert(0, str(SCRIPTS))
import sdd_loop  # noqa: E402


def load(name):
    spec = importlib.util.spec_from_file_location(name.replace("-", "_") + "_contract", SCRIPTS / name)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CLAUDE = load("loop-engine-claude.py")
CODEX = load("loop-engine-codex.py")
HERMES = load("loop-engine-hermes.py")
OPENCODE = load("loop-engine-opencode.py")
ENGINES = (CLAUDE, CODEX, HERMES, OPENCODE)


def result(stage="EXECUTE", **extra):
    value = {"stage": stage, "status": "completed", "message": "done",
             "verdict": "passed", "evidence": {"status": "passed"}}
    value.update(extra)
    return value


def claude_envelope(payload, **overrides):
    """Every key `claude -p --output-format json` 2.1.272 emits."""
    envelope = {
        "api_error_status": None, "duration_api_ms": 2100, "duration_ms": 2400,
        "fast_mode_disabled_reason": None, "fast_mode_state": "off", "first_content_frame_ms": 900,
        "is_error": False, "modelUsage": {}, "num_turns": 1, "permission_denials": [],
        "queued_turn_count": 0, "result": payload, "result_index": 0, "session_id": "s-1",
        "stop_reason": "end_turn", "subagent_stats": {}, "subtype": "success",
        "terminal_reason": "completed", "time_to_request_ms": 12, "total_cost_usd": 0.01,
        "ttft_ms": 800, "ttft_stream_ms": 810, "type": "result", "usage": {}, "uuid": "u-1",
    }
    envelope.update(overrides)
    return envelope


def opencode_events(*texts):
    """NDJSON as `opencode run --format json` 1.18.31 emits it: text lives in part.text."""
    lines = [{"type": "step_start", "timestamp": 1, "sessionID": "ses_1",
              "part": {"id": "prt_0", "type": "step-start"}}]
    for index, text in enumerate(texts, start=1):
        lines.append({"type": "text", "timestamp": 1 + index, "sessionID": "ses_1",
                      "part": {"id": f"prt_{index}", "type": "text", "text": text,
                               "time": {"start": 1, "end": 2}}})
    lines.append({"type": "step_finish", "timestamp": 99, "sessionID": "ses_1",
                  "part": {"id": "prt_end", "type": "step-finish", "reason": "stop"}})
    return "\n".join(json.dumps(line) for line in lines) + "\n"


def fake(directory, name, stdout, capture):
    path = Path(directory) / name
    path.write_text(
        "#!/usr/bin/env python3\n"
        "import json, os, pathlib, sys\n"
        f"pathlib.Path({str(capture)!r}).write_text(json.dumps({{'argv': sys.argv[1:], 'env': dict(os.environ)}}))\n"
        f"sys.stdout.write({stdout!r})\n",
        encoding="utf-8")
    path.chmod(0o755)
    return path


class OpenCodeRealFormatTests(unittest.TestCase):
    def test_loop_engine_reads_part_text_from_real_event_stream(self):
        with tempfile.TemporaryDirectory() as directory:
            capture = Path(directory) / "capture.json"
            exe = fake(directory, "opencode", opencode_events(json.dumps(result())), capture)
            actual = OPENCODE.run({"stage": "EXECUTE", "task_id": "TASK-001", "automation_consent": True},
                                  Path(directory), executable=str(exe))
            self.assertEqual(actual, result())

    def test_loop_engine_uses_the_last_json_text_part_after_prose(self):
        events = opencode_events("I will now run the stage.", json.dumps(result()))
        self.assertEqual(OPENCODE.parse_envelope(events), result())

    def test_loop_engine_never_auto_approves_in_safe_mode(self):
        safe = OPENCODE.build_command({"stage": "EXECUTE", "automation_consent": True}, Path("/w"))
        self.assertNotIn("--auto", safe)
        elevated = OPENCODE.build_command({"stage": "EXECUTE", "automation_consent": True,
                                           "permission_mode": "danger-full-access"}, Path("/w"))
        self.assertIn("--auto", elevated)


class ClaudeRealFormatTests(unittest.TestCase):
    def test_accepts_the_full_real_envelope(self):
        self.assertEqual(CLAUDE.parse_envelope(claude_envelope(json.dumps(result()))), result())

    def test_envelope_decoding_leaves_verify_evidence_to_the_contextual_check(self):
        verify = result("VERIFY", evidence={"status": "passed", "command_record": {"path": "e.json", "sha256": "0" * 64}})
        self.assertEqual(CLAUDE.parse_envelope(claude_envelope(json.dumps(verify))), verify)

    def test_rejects_provider_errors_and_missing_core_keys(self):
        with self.assertRaisesRegex(CLAUDE.RuntimeError_, "reported an error"):
            CLAUDE.parse_envelope(claude_envelope(json.dumps(result()), is_error=True))
        broken = claude_envelope(json.dumps(result()))
        del broken["result"]
        with self.assertRaisesRegex(CLAUDE.RuntimeError_, "envelope"):
            CLAUDE.parse_envelope(broken)

    def test_safe_vector_can_edit_and_danger_requires_consent(self):
        safe = CLAUDE.build_command({"stage": "EXECUTE"}, Path("/w"))
        self.assertEqual(safe[safe.index("--permission-mode") + 1], "acceptEdits")
        self.assertNotIn("--dangerously-skip-permissions", safe)
        self.assertEqual(safe[-2:], ["--add-dir", "/w"])
        with self.assertRaisesRegex(CLAUDE.RuntimeError_, "isolation or automation consent"):
            CLAUDE.build_command({"stage": "EXECUTE", "permission_mode": "danger-full-access"}, Path("/w"))
        elevated = CLAUDE.build_command({"stage": "EXECUTE", "permission_mode": "danger-full-access",
                                         "isolation_confirmed": True}, Path("/w"))
        self.assertIn("--dangerously-skip-permissions", elevated)
        self.assertNotIn("--permission-mode", elevated)

    def test_run_decodes_real_envelope_end_to_end(self):
        with tempfile.TemporaryDirectory() as directory:
            capture = Path(directory) / "capture.json"
            exe = fake(directory, "claude", json.dumps(claude_envelope(json.dumps(result()))), capture)
            self.assertEqual(CLAUDE.run({"stage": "EXECUTE", "task_id": "TASK-001"}, Path(directory),
                                        executable=str(exe)), result())


class SharedEngineContractTests(unittest.TestCase):
    def test_all_engines_share_one_result_validator(self):
        validators = {engine.validate_result for engine in ENGINES}
        self.assertEqual(len(validators), 1)
        for engine in ENGINES:
            with self.assertRaisesRegex(engine.RuntimeError_, "requested stage"):
                engine.validate_result(result("QA"), "EXECUTE")

    def test_every_engine_prompt_asks_for_the_result_contract(self):
        contract = {"stage": "EXECUTE", "task_id": "TASK-001", "automation_consent": True}
        for engine in ENGINES:
            with self.subTest(engine=engine.__name__):
                argv = engine.build_command(contract, Path("/w"))
                prompt = next(item for item in argv if '"stage":"EXECUTE"' in item)
                self.assertIn("return exactly one JSON object with keys stage,status,message,verdict,evidence", prompt)

    def test_orchestrator_guard_keys_survive_engine_validation(self):
        flagged = result(destructive=True, diff="abc")
        for engine in ENGINES:
            self.assertEqual(engine.validate_result(flagged, "EXECUTE"), flagged)
            with self.assertRaises(engine.RuntimeError_):
                engine.validate_result(result(unexpected=1), "EXECUTE")

    def test_provider_environment_keeps_authentication_and_drops_unrelated_values(self):
        with tempfile.TemporaryDirectory() as directory:
            capture = Path(directory) / "capture.json"
            exe = fake(directory, "claude", json.dumps(claude_envelope(json.dumps(result()))), capture)
            wanted = {"HOME": "/home/me", "ANTHROPIC_API_KEY": "k", "XDG_CONFIG_HOME": "/x",
                      "CODEX_HOME": "/c", "LANG": "pt_BR.UTF-8", "DATABASE_URL": "postgres://secret"}
            old = {key: os.environ.get(key) for key in wanted}
            os.environ.update(wanted)
            try:
                CLAUDE.run({"stage": "EXECUTE", "task_id": "TASK-001"}, Path(directory), executable=str(exe))
            finally:
                for key, value in old.items():
                    if value is None: os.environ.pop(key, None)
                    else: os.environ[key] = value
            env = json.loads(capture.read_text())["env"]
            for key in ("HOME", "ANTHROPIC_API_KEY", "XDG_CONFIG_HOME", "CODEX_HOME", "LANG"):
                self.assertEqual(env.get(key), wanted[key])
            self.assertNotIn("DATABASE_URL", env)

    def test_verify_reads_the_loop_record_from_the_loop_root_not_the_worktree(self):
        with tempfile.TemporaryDirectory() as main, tempfile.TemporaryDirectory() as worktree:
            main_root = Path(main)
            loops = main_root / ".planning/sdd-composy/loops"
            loops.mkdir(parents=True)
            records = main_root / "evidence"
            records.mkdir()
            command = {"task_id": "TASK-004", "loop_id": "loop-04", "status": "passed", "exit_code": 0,
                       "command": ["python3", "-m", "unittest"], "stdout": "OK", "stderr": "",
                       "started_at": 101, "ended_at": 102}
            command["sha256"] = hashlib.sha256(b"OK\n").hexdigest()
            raw = json.dumps(command, sort_keys=True).encode()
            (records / "verify.json").write_bytes(raw)
            loop = {"id": "loop-04", "task_id": "TASK-004", "status": "running",
                    "stages": [{"name": "REVIEW", "published_at": "1970-01-01T00:01:40Z"}]}
            (loops / "loop-04.json").write_text(json.dumps(loop), encoding="utf-8")
            verified = result("VERIFY", evidence={"status": "passed", "command_record": {
                "path": "evidence/verify.json", "sha256": hashlib.sha256(raw).hexdigest()}})
            contract = {"stage": "VERIFY", "task_id": "TASK-004"}
            for engine in ENGINES:
                with self.subTest(engine=engine.__name__):
                    with self.assertRaises(engine.RuntimeError_):
                        engine.validate_result(verified, "VERIFY", root=Path(worktree),
                                               stage_contract=contract, now=103)
                    self.assertEqual(engine.validate_result(verified, "VERIFY", root=Path(worktree),
                                                            loop_root=main_root, stage_contract=contract,
                                                            now=103), verified)


class OrchestratorContractTests(unittest.TestCase):
    def test_contract_extra_reaches_the_engine(self):
        with tempfile.TemporaryDirectory() as directory:
            seen = []
            def engine(contract):
                seen.append(contract)
                return result(contract["stage"], status="failed", verdict="rejected")
            sdd_loop.orchestrate(Path(directory), "TASK-300", engine, human_approved=True, max_iterations=1,
                                 contract_extra={"automation_consent": True})
            self.assertTrue(seen)
            self.assertTrue(all(item["automation_consent"] is True for item in seen))
            self.assertEqual(seen[0]["stage"], "EXECUTE")

    def test_contract_extra_cannot_override_stage_identity(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(sdd_loop.LoopError):
                sdd_loop.orchestrate(Path(directory), "TASK-301", lambda contract: {}, human_approved=True,
                                     contract_extra={"stage": "VERIFY"})


if __name__ == "__main__":
    unittest.main()
