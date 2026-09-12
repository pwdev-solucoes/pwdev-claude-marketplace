import importlib.util
import json
import multiprocessing
import os
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]


def load_module():
    path = ROOT / "scripts" / "sdd_runtime_smoke.py"
    spec = importlib.util.spec_from_file_location("sdd_runtime_smoke_test", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


SMOKE = load_module()


def _consume_budget_process(output, ready, start, results):
    budget = SMOKE.InvocationBudget(28, Path(output))
    ready.put(True)
    start.wait()
    try:
        budget.consume("codex", "cmux")
        results.put("consumed")
    except SMOKE.SmokeBlocked:
        results.put("rejected")


class RuntimeSmokeContractTests(unittest.TestCase):
    def _fake_interactive_launch_runner(self, terminal_state, calls):
        def runner(command, cwd, timeout):
            calls.append((command, cwd, timeout))
            root = Path(command[command.index("--root") + 1])
            fleet_id = command[command.index("--fleet-id") + 1]
            state = root / ".planning/sdd-composy/fleet" / fleet_id
            members = state / "members"; members.mkdir(parents=True)
            worktree = root.parent / "preserved-member-worktree"; worktree.mkdir()
            loop_id = f"loop-{fleet_id}-task-008"
            loop = root / ".planning/sdd-composy/loops" / f"{loop_id}.json"
            loop.parent.mkdir(parents=True)
            stamp = "2026-09-12T00:00:00Z"
            loop.write_text(json.dumps({"schema_version": "1", "id": loop_id,
                "task_id": "TASK-008", "status": "completed" if terminal_state == "completed" else "running",
                "iteration": 0, "max_iterations": 3, "started_at": stamp, "updated_at": stamp,
                "stop_reason": "human completed" if terminal_state == "completed" else None,
                "finished_at": stamp if terminal_state == "completed" else None,
                "stages": []}))
            member = members / "TASK-008.json"
            record_runtime = "claude-code" if command[command.index("--runtime") + 1] == "claude" else command[command.index("--runtime") + 1]
            ui = command[command.index("--ui") + 1]
            member.write_text(json.dumps({"schema_version": "2", "id": "TASK-008",
                "task_id": "TASK-008", "slug": "task-008", "status": "pending",
                "runtime": record_runtime, "ui": ui, "branch": f"sdd-fleet/{fleet_id}/TASK-008",
                "worktree_path": str(worktree), "repository_root": str(root),
                "started_at": stamp, "updated_at": stamp,
                "owner": {"kind": "sdd-composy-fleet", "fleet_id": fleet_id, "member_id": "TASK-008"},
                "resources": {"branch": f"sdd-fleet/{fleet_id}/TASK-008",
                    "worktree_path": str(worktree), "port": 43008,
                    "compose_project": f"sdd_fleet_{fleet_id}",
                    "compose_file": f".planning/sdd-composy/fleet/{fleet_id}/docker-compose.yml",
                    "compose_allocated": False},
                "interaction": {"state": terminal_state, "started_at": stamp, "updated_at": stamp,
                    "loop": {"id": loop_id, "task_id": "TASK-008"}}}))
            handle = state / "task-008.ui.json"
            handle.write_text(json.dumps({"driver": ui, "fleet_id": fleet_id,
                "member_id": "TASK-008", "cwd": str(worktree), "recoverable": True}))
            return {"status": "PASS", "exit_code": 0, "stdout": "terminal ignored",
                    "stderr": "", "duration_seconds": 0.01}
        return runner

    def _real_fake(self, runtime, behavior="success", consent=True):
        with tempfile.TemporaryDirectory() as directory:
            binary = Path(directory) / runtime
            binary.write_text(f"#!{sys.executable}\n" + '''import hashlib,json,os,subprocess,sys
from pathlib import Path
args=sys.argv[1:]
if '--version' in args:
    print('fake-native 1.0'); raise SystemExit(0)
runtime=Path(sys.argv[0]).name
if runtime=='codex':
    assert args[args.index('--sandbox')+1]=='read-only'
    request=json.loads(args[-1])
elif runtime=='claude':
    assert '--plugin-dir' in args and '--dangerously-skip-permissions' not in args
    request=json.loads(args[args.index('-p')+1])
else:
    prompt=args[args.index('-z')+1]; request=json.loads(prompt[prompt.index('{'):])
status=json.loads(subprocess.check_output(request['helper_command'],text=True))
loaded={p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in request['resource_paths']}
result={'stage':'READ_ONLY','status':'completed','message':'Local status inspected',
        'verdict':'passed','evidence':{'status':status,'loaded_resources':loaded}}
''' + f"behavior={behavior!r}\n" + '''if behavior=='mutate': Path('project.sentinel').write_text('changed')
if behavior=='symlink': Path('new-link').symlink_to('README.md')
if behavior=='error': print('permission denied',file=sys.stderr); raise SystemExit(3)
if behavior=='lie': result['evidence']['loaded_resources']={}
if runtime=='codex':
    Path(args[args.index('--output-last-message')+1]).write_text(json.dumps(result))
    print(json.dumps({'type':'thread.started','thread_id':'fixture'}))
    if behavior!='no-witness': print(json.dumps({'type':'item.completed','item':{
        'type':'command_execution','command':' '.join(request['helper_command']),
        'exit_code':0,'aggregated_output':json.dumps(status)}}))
    print(json.dumps({'type':'turn.completed','usage':{'input_tokens':12}}))
elif runtime=='claude':
    print(json.dumps({'type':'system','subtype':'init','extra':'allowed'}))
    if behavior!='no-witness':
        print(json.dumps({'type':'assistant','message':{'content':[{'type':'tool_use',
          'id':'tool-1','name':'Bash','input':{'command':' '.join(request['helper_command'])}}]}}))
        print(json.dumps({'type':'user','message':{'content':[{'type':'tool_result',
          'tool_use_id':'tool-1','content':json.dumps(status),'is_error':False}]}}))
    print(json.dumps({'type':'result','subtype':'success','is_error':False,
       'result':json.dumps(result),'usage':{'input_tokens':12},'modelUsage':{},'permission_denials':[]}))
else: print(json.dumps(result))
''')
            binary.chmod(0o755)
            with patch.dict(os.environ, {"PATH": directory + os.pathsep + os.environ["PATH"]}):
                return SMOKE.run_acceptance(mode="real", runtime=runtime, language="en-US",
                    scenario="read-only", output=Path(directory)/"output",
                    plugin_root=ROOT/"plugins/sdd-composy",
                    provider_launcher=SMOKE.production_provider_launcher,
                    hermes_automation_acknowledged=consent)

    def test_real_entry_uses_actual_native_executable_for_all_three_runtimes(self):
        for runtime in SMOKE.RUNTIMES:
            with self.subTest(runtime=runtime):
                summary=self._real_fake(runtime)
                row=summary['scenarios'][0]
                self.assertEqual(row['status'], 'NOT_RUN' if runtime=='hermes' else 'PASS', row['reason'])
                self.assertEqual(summary['provider_calls'][runtime], 1)
                self.assertEqual(row['snapshot_before'], row['snapshot_after'])
                self.assertEqual(row['version'], 'fake-native 1.0')
                self.assertEqual(len(row['loaded_resources']), 3)
                self.assertTrue(row['result_sha256'])
                self.assertNotIn('instructions', str(row['command']))

    def test_native_final_claim_without_command_witness_is_inconclusive(self):
        for runtime in ('codex', 'claude'):
            summary=self._real_fake(runtime, 'no-witness')
            self.assertEqual(summary['scenarios'][0]['status'], 'NOT_RUN')
            self.assertIn('witness', summary['scenarios'][0]['reason'])
            self.assertEqual(summary['provider_calls'][runtime], 1)

    def test_real_entry_rejects_mutation_symlink_false_hashes_and_provider_error(self):
        for behavior in ('mutate', 'symlink', 'lie', 'error'):
            with self.subTest(behavior=behavior):
                summary=self._real_fake('codex', behavior)
                row=summary['scenarios'][0]
                self.assertEqual(row['status'], 'FAIL')
                self.assertEqual(summary['provider_calls']['codex'], 1)
                if behavior=='error': self.assertIn('permission denied', row['stderr'])

    def test_hermes_without_consent_blocks_without_spending_invocation(self):
        summary=self._real_fake('hermes', consent=False)
        self.assertEqual(summary['scenarios'][0]['status'], 'BLOCKED')
        self.assertEqual(summary['provider_calls']['hermes'], 0)

    def test_production_unimplemented_scenarios_do_not_spend_budget(self):
        budget=SMOKE.InvocationBudget(1)
        result=SMOKE.production_provider_launcher(runtime='codex', language='en-US',
            scenario='lifecycle', plugin_root=ROOT/'plugins/sdd-composy', budget=budget)
        self.assertEqual(result['status'], 'NOT_RUN')
        self.assertEqual(budget.counts['codex'], 0)

    def test_witness_rejects_wrong_helper_and_failed_command(self):
        expected={'read_only':True}
        item={'type':'command_execution','command':'python /local/sdd_status.py',
              'exit_code':0,'aggregated_output':json.dumps(expected)}
        event={'type':'item.completed','item':item}
        self.assertTrue(SMOKE._helper_witness('codex',[event],Path('/local/sdd_status.py'),expected))
        self.assertFalse(SMOKE._helper_witness('codex',[event],Path('/corrected/sdd_status.py'),expected))
        item['exit_code']=1
        self.assertFalse(SMOKE._helper_witness('codex',[event],Path('/local/sdd_status.py'),expected))

    def test_runtime_smoke_cli_exists(self):
        self.assertTrue((ROOT / "scripts" / "sdd_runtime_smoke.py").is_file())

    def test_offline_all_never_invokes_a_provider_and_covers_the_matrix(self):
        with tempfile.TemporaryDirectory() as directory:
            def forbidden(*_args, **_kwargs):
                raise AssertionError("offline mode invoked a provider")

            summary = SMOKE.run_acceptance(
                mode="offline", runtime="all", language="both", scenario="all",
                output=Path(directory) / "run", plugin_root=ROOT / "plugins/sdd-composy",
                provider_launcher=forbidden,
            )
        self.assertEqual(summary["verdict"], "PASS")
        self.assertEqual(summary["provider_calls"], {"hermes": 0, "codex": 0, "claude": 0})
        covered = {(row["runtime"], row["language"], row["scenario"]) for row in summary["scenarios"]}
        for runtime in ("hermes", "codex", "claude"):
            for language in ("pt-BR", "en-US"):
                for scenario in ("read-only", "lifecycle", "fleet", "handoff", "evidence", "compose"):
                    self.assertIn((runtime, language, scenario), covered)
        self.assertTrue(all(row["status"] == "PASS" for row in summary["scenarios"]))
        self.assertTrue(all(row["resources"] for row in summary["scenarios"]))
        self.assertTrue(all(row["task_id"] == "TASK-008" for row in summary["scenarios"]))
        self.assertTrue(all(row["duration_seconds"] is not None for row in summary["scenarios"]))
        self.assertTrue(all(row["result_sha256"] for row in summary["scenarios"]))

    def test_fleet_interactive_offline_covers_runtime_ui_matrix_without_providers(self):
        with tempfile.TemporaryDirectory() as directory:
            def forbidden(*_args, **_kwargs):
                raise AssertionError("offline interactive mode invoked a real provider")

            summary = SMOKE.run_acceptance(
                mode="offline", runtime="all", language="en-US",
                scenario="fleet-interactive", ui="all",
                output=Path(directory) / "run", plugin_root=ROOT / "plugins/sdd-composy",
                provider_launcher=forbidden,
            )
        rows = summary["scenarios"]
        self.assertEqual(summary["verdict"], "PASS")
        self.assertEqual(summary["provider_calls"], {"hermes": 0, "codex": 0, "claude": 0})
        self.assertEqual({(row["runtime"], row["ui"]) for row in rows}, {
            (runtime, ui) for runtime in SMOKE.RUNTIMES for ui in ("cmux", "tmux")
        })
        self.assertTrue(all(row["status"] == "PASS" for row in rows))
        self.assertTrue(all(row["timeout_seconds"] == 300 for row in rows))
        self.assertTrue(all(row["runner_state"] == "awaiting_human" for row in rows))
        self.assertTrue(all(row["driver_observation"]["recoverable"] for row in rows))
        self.assertTrue(all(row["exercised_components"] == [
            "fleet/launch.sh", "fleet/interactive-run.sh", f"fleet/ui-{row['ui']}.sh"
        ] for row in rows))

    def test_fleet_interactive_negative_pty_content_never_becomes_a_witness(self):
        expected = {
            "markdown": "PASS", "json-string": "PASS", "tampered-witness": "FAIL",
            "dead-pane": "FAIL", "timeout": "BLOCKED", "divergent-loop": "PASS",
            "unsupported-combination": "NOT_RUN",
        }
        for case, status in expected.items():
            with self.subTest(case=case):
                with tempfile.TemporaryDirectory() as directory:
                    result = SMOKE._offline_interactive_negative_fixture(
                        Path(directory), case, timeout=300)
                self.assertEqual(result["status"], status)
                self.assertFalse(result["terminal_is_witness"])
                self.assertTrue(result["executed"])
                self.assertTrue(result["production_calls"])
                self.assertNotIn("smoke-classifier", result["production_calls"])
                if case == "timeout":
                    self.assertEqual(result["interaction_state"], "awaiting_human")
                    self.assertEqual(result["production_calls"], ["interactive_observer.observe"])

    def test_runner_negative_translation_fails_on_accepted_or_bypassed_outcomes(self):
        safe = {"provider_invoked": True, "loop_unchanged": True,
                "loop_status": "running", "stages_advanced": False}
        for case in ("markdown", "json-string"):
            self.assertEqual(SMOKE._runner_negative_translation(case, "awaiting_human", 0, safe)[0], "PASS")
            self.assertEqual(SMOKE._runner_negative_translation(case, "completed", 0, safe)[0], "FAIL")
            advanced = {**safe, "stages_advanced": True}
            self.assertEqual(SMOKE._runner_negative_translation(case, "awaiting_human", 0, advanced)[0], "FAIL")
        rejected = {"provider_invoked": False, "loop_unchanged": True,
                    "loop_status": "running", "stages_advanced": False}
        self.assertEqual(SMOKE._runner_negative_translation("divergent-loop", "blocked", 2, rejected)[0], "PASS")
        self.assertEqual(SMOKE._runner_negative_translation("divergent-loop", "blocked", 0, rejected)[0], "FAIL")
        self.assertEqual(SMOKE._runner_negative_translation(
            "divergent-loop", "blocked", 2, {**rejected, "provider_invoked": True})[0], "FAIL")

    def test_fleet_interactive_exercises_auto_resolution_and_headless_offline(self):
        for requested, resolved in (("auto", "cmux"), ("headless", "headless")):
            with self.subTest(ui=requested), tempfile.TemporaryDirectory() as directory:
                summary = SMOKE.run_acceptance(
                    mode="offline", runtime="codex", language="en-US",
                    scenario="fleet-interactive", ui=requested,
                    output=Path(directory) / "run", plugin_root=ROOT / "plugins/sdd-composy",
                    provider_launcher=lambda *_args, **_kwargs: self.fail("provider invoked"),
                )
                row = summary["scenarios"][0]
                self.assertEqual(row["status"], "PASS")
                self.assertEqual(row["requested_ui"], requested)
                self.assertEqual(row["ui"], resolved)
                self.assertEqual(row["auto_resolution"], {
                    "cmux": "cmux", "tmux": "tmux", "none": "headless"
                })
                self.assertTrue(row["selection_before_mutation"])

    def test_budget_is_per_runtime_hard_limit_and_has_no_automatic_retry(self):
        budget = SMOKE.InvocationBudget(2)
        budget.consume("codex")
        budget.consume("codex")
        with self.assertRaisesRegex(SMOKE.SmokeBlocked, "call budget"):
            budget.consume("codex")
        self.assertEqual(budget.counts, {"hermes": 0, "codex": 2, "claude": 0})

    def test_real_interactive_requires_exact_runtime_ui_authorization(self):
        with tempfile.TemporaryDirectory() as directory:
            calls = []
            def succeed(**kwargs):
                calls.append(kwargs)
                return {"status": "PASS"}
            summary = SMOKE.run_acceptance(
                mode="real", runtime="codex", language="en-US",
                scenario="fleet-interactive", ui="cmux",
                output=Path(directory) / "run", plugin_root=ROOT / "plugins/sdd-composy",
                provider_launcher=succeed,
                authorized_runtime_uis={"codex:cmux"},
            )
            durable = json.loads((Path(directory) / "run" / "invocation-budget.json").read_text())
        self.assertEqual([(row["runtime"], row["ui"], row["status"])
                          for row in summary["scenarios"]], [("codex", "cmux", "PASS")])
        self.assertEqual([(call["runtime"], call["ui"]) for call in calls], [("codex", "cmux")])
        self.assertEqual(durable["consumed"], ["codex:cmux"])

    def test_real_interactive_rejects_multi_ui_before_reservation_or_fake_launch(self):
        for launcher in (lambda **kwargs: self.fail(f"injected launcher called: {kwargs}"),
                         SMOKE.production_provider_launcher):
            with self.subTest(production=launcher is SMOKE.production_provider_launcher):
                with tempfile.TemporaryDirectory() as directory:
                    output = Path(directory) / "run"
                    external_calls = []
                    summary = SMOKE.run_acceptance(
                        mode="real", runtime="codex", language="en-US",
                        scenario="fleet-interactive", ui="all", output=output,
                        plugin_root=ROOT / "plugins/sdd-composy", provider_launcher=launcher,
                        production_interactive_launcher=lambda **kwargs: external_calls.append(kwargs),
                        authorized_runtime_uis={"codex:cmux", "codex:tmux"},
                    )
                    self.assertFalse((output / "invocation-budget.json").exists())
                self.assertEqual(external_calls, [])
                self.assertEqual(summary["provider_calls"], {"hermes": 0, "codex": 0, "claude": 0})
                self.assertEqual(len(summary["scenarios"]), 1)
                self.assertEqual(summary["scenarios"][0]["status"], "NOT_RUN")
                self.assertIn("concrete", summary["scenarios"][0]["reason"])

    def test_generic_acknowledgement_and_credentials_do_not_authorize_a_combination(self):
        with tempfile.TemporaryDirectory() as directory, patch.dict(
                os.environ, {"CODEX_API_KEY": "present-but-not-authority"}):
            calls = []
            summary = SMOKE.run_acceptance(
                mode="real", runtime="codex", language="en-US",
                scenario="fleet-interactive", ui="cmux",
                output=Path(directory) / "run", plugin_root=ROOT / "plugins/sdd-composy",
                provider_launcher=lambda **kwargs: calls.append(kwargs),
                fleet_acknowledged=True,
            )
        self.assertEqual(calls, [])
        self.assertEqual(summary["scenarios"][0]["status"], "NOT_RUN")
        self.assertEqual(summary["provider_calls"]["codex"], 0)

    def test_real_interactive_budget_is_durable_before_failure_and_cannot_retry_or_fallback(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "run"
            calls = []
            def failing(**kwargs):
                budget = json.loads((output / "invocation-budget.json").read_text())
                self.assertIn(f'{kwargs["runtime"]}:{kwargs["ui"]}', budget["consumed"])
                calls.append((kwargs["runtime"], kwargs["ui"]))
                raise OSError("fake provider failed")
            first = SMOKE.run_acceptance(
                mode="real", runtime="codex", language="en-US",
                scenario="fleet-interactive", ui="cmux", output=output,
                plugin_root=ROOT / "plugins/sdd-composy", provider_launcher=failing,
                authorized_runtime_uis={"codex:cmux", "codex:tmux"},
            )
            second = SMOKE.run_acceptance(
                mode="real", runtime="codex", language="en-US",
                scenario="fleet-interactive", ui="cmux", output=output,
                plugin_root=ROOT / "plugins/sdd-composy", provider_launcher=failing,
                authorized_runtime_uis={"codex:cmux", "codex:tmux"},
            )
        self.assertEqual(calls, [("codex", "cmux")])
        self.assertEqual(first["scenarios"][0]["status"], "BLOCKED")
        self.assertEqual(second["scenarios"][0]["status"], "NOT_RUN")
        self.assertIn("already consumed", second["scenarios"][0]["reason"])

    def test_production_interactive_branch_reserves_exact_key_before_injected_launch(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "run"
            calls = []
            def injected(**kwargs):
                durable = json.loads((output / "invocation-budget.json").read_text())
                self.assertEqual(durable["consumed"], ["codex:cmux"])
                calls.append((kwargs["runtime"], kwargs["ui"]))
                raise OSError("injected failure")
            first = SMOKE.run_acceptance(
                mode="real", runtime="codex", language="en-US",
                scenario="fleet-interactive", ui="cmux", output=output,
                plugin_root=ROOT / "plugins/sdd-composy",
                provider_launcher=SMOKE.production_provider_launcher,
                production_interactive_launcher=injected,
                authorized_runtime_uis={"codex:cmux", "codex:tmux"},
            )
            retry = SMOKE.run_acceptance(
                mode="real", runtime="codex", language="en-US",
                scenario="fleet-interactive", ui="cmux", output=output,
                plugin_root=ROOT / "plugins/sdd-composy",
                provider_launcher=SMOKE.production_provider_launcher,
                production_interactive_launcher=injected,
                authorized_runtime_uis={"codex:cmux", "codex:tmux"},
            )
        self.assertEqual(calls, [("codex", "cmux")])
        self.assertEqual(first["scenarios"][0]["status"], "BLOCKED")
        self.assertEqual(retry["scenarios"][0]["status"], "NOT_RUN")

    def test_stale_and_cross_process_budget_instances_cannot_both_reserve(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            (output / "invocation-budget.json").write_text(json.dumps({
                "schema_version": 1, "consumed": [], "future": {"kept": True}}))
            first = SMOKE.InvocationBudget(28, output)
            stale = SMOKE.InvocationBudget(28, output)
            first.consume("codex", "cmux")
            with self.assertRaisesRegex(SMOKE.SmokeBlocked, "already consumed"):
                stale.consume("codex", "cmux")
            self.assertEqual(json.loads((output / "invocation-budget.json").read_text())["future"],
                             {"kept": True})

        with tempfile.TemporaryDirectory() as directory:
            context = multiprocessing.get_context("spawn")
            ready, results, start = context.Queue(), context.Queue(), context.Event()
            processes = [context.Process(target=_consume_budget_process,
                args=(directory, ready, start, results)) for _ in range(2)]
            for process in processes: process.start()
            ready.get(timeout=10); ready.get(timeout=10); start.set()
            outcomes = sorted(results.get(timeout=10) for _ in processes)
            for process in processes: process.join(10)
            self.assertEqual(outcomes, ["consumed", "rejected"])
            self.assertTrue(all(process.exitcode == 0 for process in processes))

    def test_budget_symlink_is_rejected_before_read_or_launcher(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "run"; output.mkdir()
            target = Path(directory) / "benign.json"
            target.write_text('{"schema_version":1,"consumed":[]}')
            budget_path = output / "invocation-budget.json"
            budget_path.symlink_to(target)
            called = []
            original = Path.read_text
            def guarded(path, *args, **kwargs):
                if path == budget_path:
                    raise AssertionError("symlink budget was read")
                return original(path, *args, **kwargs)
            with patch.object(Path, "read_text", guarded):
                with self.assertRaisesRegex(SMOKE.SmokeBlocked, "symlink"):
                    SMOKE.run_acceptance(mode="real", runtime="codex", language="en-US",
                        scenario="fleet-interactive", ui="cmux", output=output,
                        plugin_root=ROOT / "plugins/sdd-composy",
                        provider_launcher=lambda **kwargs: called.append(kwargs),
                        authorized_runtime_uis={"codex:cmux"})
            self.assertEqual(called, [])

    def test_main_wires_the_production_interactive_launcher(self):
        captured = {}
        def acceptance(**kwargs):
            captured.update(kwargs)
            return {"verdict": "BLOCKED"}
        with tempfile.TemporaryDirectory() as directory, patch.object(
                SMOKE, "run_acceptance", side_effect=acceptance):
            code = SMOKE.main(["--mode", "real", "--runtime", "codex",
                "--language", "en-US", "--scenario", "fleet-interactive",
                "--ui", "cmux", "--provider-entry-point", "production",
                "--authorize-runtime-ui", "codex:cmux", "--output", directory])
        self.assertEqual(code, 2)
        self.assertIs(captured["provider_launcher"], SMOKE.production_provider_launcher)
        self.assertIs(captured["production_interactive_launcher"],
                      SMOKE.production_interactive_launcher)

    def test_production_interactive_launcher_uses_exact_fleet_argv_once_and_durable_pass(self):
        with tempfile.TemporaryDirectory() as directory:
            calls = []
            result = SMOKE.production_interactive_launcher(
                runtime="codex", language="en-US", scenario="fleet-interactive",
                ui="cmux", timeout=300, plugin_root=ROOT / "plugins/sdd-composy",
                output=Path(directory),
                command_runner=self._fake_interactive_launch_runner("completed", calls),
                handle_validator=lambda **_kwargs: {"recoverable": True, "driver": "cmux"},
                clock=lambda: 0.0, sleep=lambda _seconds: None)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(len(calls), 1)
        command, cwd, timeout = calls[0]
        self.assertEqual(command[0], str(ROOT / "plugins/sdd-composy/scripts/fleet/launch.sh"))
        self.assertEqual(command[command.index("--runtime") + 1], "codex")
        self.assertEqual(command[command.index("--ui") + 1], "cmux")
        self.assertEqual(timeout, 300)
        self.assertFalse({"--compose", "--prepare-only", "--dangerously-skip-permissions",
                          "--yolo", "--full-auto"}.intersection(command))
        self.assertTrue(all(result[key] for key in ("repository", "worktree", "member", "loop", "handle")))

    def test_production_interactive_launcher_rejects_unbound_or_escaping_durable_tuple(self):
        for case in ("member-id", "owner", "runtime", "ui", "worktree", "resource-worktree",
                     "loop-id", "absolute-loop-id", "loop-task", "handle-owner", "handle-symlink"):
            with self.subTest(case=case), tempfile.TemporaryDirectory() as directory:
                calls = []
                base = self._fake_interactive_launch_runner("completed", calls)
                def adversarial(command, cwd, timeout):
                    result = base(command, cwd, timeout)
                    root = Path(command[command.index("--root") + 1]); fleet_id = command[command.index("--fleet-id") + 1]
                    member_path = root / ".planning/sdd-composy/fleet" / fleet_id / "members/TASK-008.json"
                    member = json.loads(member_path.read_text())
                    if case == "member-id": member["id"] = "FOREIGN"
                    if case == "owner": member["owner"]["fleet_id"] = "foreign"
                    if case == "runtime": member["runtime"] = "hermes"
                    if case == "ui": member["ui"] = "tmux"
                    if case == "worktree":
                        member["worktree_path"] = "/outside/unowned"
                        member["resources"]["worktree_path"] = "/outside/unowned"
                    if case == "resource-worktree": member["resources"]["worktree_path"] += "-foreign"
                    if case == "loop-id": member["interaction"]["loop"]["id"] = "../../outside"
                    if case == "absolute-loop-id": member["interaction"]["loop"]["id"] = "/outside"
                    member_path.write_text(json.dumps(member))
                    if case == "loop-task":
                        loop_path = next((root / ".planning/sdd-composy/loops").glob("*.json"))
                        loop = json.loads(loop_path.read_text()); loop["task_id"] = "TASK-999"
                        loop_path.write_text(json.dumps(loop))
                    if case == "handle-owner":
                        handle = root / ".planning/sdd-composy/fleet" / fleet_id / "task-008.ui.json"
                        data = json.loads(handle.read_text()); data["member_id"] = "foreign"
                        handle.write_text(json.dumps(data))
                    if case == "handle-symlink":
                        handle = root / ".planning/sdd-composy/fleet" / fleet_id / "task-008.ui.json"
                        target = handle.with_name("benign-handle.json"); handle.replace(target)
                        handle.symlink_to(target)
                    return result
                result = SMOKE.production_interactive_launcher(runtime="codex", language="en-US",
                    scenario="fleet-interactive", ui="cmux", timeout=300,
                    plugin_root=ROOT / "plugins/sdd-composy", output=Path(directory),
                    command_runner=adversarial,
                    handle_validator=lambda **_kwargs: {"recoverable": True, "driver": "cmux"},
                    clock=lambda: 0.0, sleep=lambda _seconds: self.fail("invalid tuple was observed"))
                self.assertEqual(result["status"], "FAIL")

    def test_awaiting_human_observes_exact_boundary_and_completion_before_it(self):
        with tempfile.TemporaryDirectory() as directory:
            calls, clock_calls, sleeps = [], [], []
            ticks = iter((0.0, 300.0))
            def clock():
                value = next(ticks); clock_calls.append(value); return value
            result = SMOKE.production_interactive_launcher(runtime="claude", language="pt-BR",
                scenario="fleet-interactive", ui="tmux", timeout=300,
                plugin_root=ROOT / "plugins/sdd-composy", output=Path(directory),
                command_runner=self._fake_interactive_launch_runner("awaiting_human", calls),
                handle_validator=lambda **_kwargs: {"recoverable": True, "driver": "tmux"},
                clock=clock, sleep=lambda seconds: sleeps.append(seconds))
            self.assertEqual(result["status"], "BLOCKED")
            self.assertEqual(clock_calls, [0.0, 300.0])
            self.assertEqual(sleeps, [])

        with tempfile.TemporaryDirectory() as directory:
            calls = []
            def complete(_seconds):
                command = calls[0][0]; root = Path(command[command.index("--root") + 1])
                fleet_id = command[command.index("--fleet-id") + 1]
                member_path = root / ".planning/sdd-composy/fleet" / fleet_id / "members/TASK-008.json"
                member = json.loads(member_path.read_text()); member["interaction"]["state"] = "completed"
                member_path.write_text(json.dumps(member))
                loop_path = next((root / ".planning/sdd-composy/loops").glob("*.json"))
                loop = json.loads(loop_path.read_text()); loop.update(status="completed",
                    stop_reason="human completed", finished_at="2026-09-12T00:00:00Z")
                loop_path.write_text(json.dumps(loop))
            ticks = iter((0.0, 299.0))
            result = SMOKE.production_interactive_launcher(runtime="claude", language="pt-BR",
                scenario="fleet-interactive", ui="tmux", timeout=300,
                plugin_root=ROOT / "plugins/sdd-composy", output=Path(directory),
                command_runner=self._fake_interactive_launch_runner("awaiting_human", calls),
                handle_validator=lambda **_kwargs: {"recoverable": True, "driver": "tmux"},
                clock=lambda: next(ticks), sleep=complete)
            self.assertEqual(result["status"], "PASS")

    def test_production_fixture_actual_launch_and_wrapper_preflight_use_canonical_projection(self):
        with tempfile.TemporaryDirectory() as directory:
            fake = Path(directory) / "bin"; fake.mkdir()
            (fake / "codex").write_text("#!/bin/sh\nexit 0\n")
            (fake / "codex").chmod(0o755)
            (fake / "tmux").write_text(f"#!{sys.executable}\n" + '''import subprocess,sys
args=sys.argv[1:]
if 'has-session' in args: raise SystemExit(1)
if 'new-session' in args:
    split=args.index('--'); cwd=args[args.index('-c')+1]
    completed=subprocess.run(args[split+1:],cwd=cwd)
    print('sdd-composy-acceptance|%8')
    raise SystemExit(completed.returncode)
raise SystemExit(0)
''')
            (fake / "tmux").chmod(0o755)
            ticks = iter((0.0, 300.0))
            with patch.dict(os.environ, {"PATH": str(fake) + os.pathsep + os.environ["PATH"]}):
                result = SMOKE.production_interactive_launcher(runtime="codex", language="en-US",
                    scenario="fleet-interactive", ui="tmux", timeout=300,
                    plugin_root=ROOT / "plugins/sdd-composy", output=Path(directory),
                    handle_validator=lambda **_kwargs: {"recoverable": True, "driver": "tmux"},
                    clock=lambda: next(ticks), sleep=lambda _seconds: None)
            repository = Path(result["repository"])
            contract = repository / ".planning/sdd-composy/tasks/task-008.json"
            self.assertTrue(Path(result["member"]).is_file(), result)
            member = json.loads(Path(result["member"]).read_text())
            tasks = SMOKE._load_local(ROOT / "plugins/sdd-composy/scripts", "sdd_tasks.py",
                                      "acceptance_tasks_test").load(contract)
            self.assertEqual(result["status"], "BLOCKED")
            self.assertEqual(member["interaction"]["state"], "awaiting_human")
            self.assertEqual(Path(member["contract_path"]), contract)
            self.assertEqual(member["contract_sha256"], __import__("hashlib").sha256(contract.read_bytes()).hexdigest())
            self.assertEqual(tasks["prd_slug"], "task-008")
            self.assertEqual(tasks["tasks"][0]["id"], "TASK-008")

    def test_controlled_process_timeout_terminates_child_and_reports_timeout(self):
        with tempfile.TemporaryDirectory() as directory:
            marker = Path(directory) / "child-finished"
            code = (
                "import pathlib,subprocess,sys,time; "
                "subprocess.Popen([sys.executable,'-c',"
                f"\"import time,pathlib;time.sleep(2);pathlib.Path({str(marker)!r}).write_text('bad')\"]); "
                "time.sleep(2)"
            )
            result = SMOKE.run_process([sys.executable, "-c", code], Path(directory), timeout=0.05)
            self.assertEqual(result["status"], "BLOCKED")
            self.assertEqual(result["reason"], "timeout")
            import time
            time.sleep(2.2)
            self.assertFalse(marker.exists())

    def test_fixture_is_exclusive_cleaned_and_copied_plugin_has_no_operational_state(self):
        parent = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: parent.rmdir() if parent.exists() else None)
        with SMOKE.isolated_fixture(ROOT / "plugins/sdd-composy", base_dir=parent) as fixture:
            self.assertEqual(fixture.parent, parent)
            self.assertTrue((fixture / "plugin" / "skills" / "sdd-init" / "SKILL.md").is_file())
            self.assertTrue((fixture / ".git").is_dir())
            self.assertFalse((fixture / "plugin" / ".planning").exists())
            fixture_path = fixture
        self.assertFalse(fixture_path.exists())
        self.assertEqual(list(parent.iterdir()), [])

    def test_fixture_rejects_symlinks_and_excludes_secret_classes(self):
        with tempfile.TemporaryDirectory() as source_dir, tempfile.TemporaryDirectory() as parent_dir:
            source = Path(source_dir)
            (source / "skills").mkdir()
            (source / "skills/public.txt").write_text("ok")
            (source / "private.key").write_text("private")
            (source / "client.pem").write_text("certificate")
            (source / "credentials.json").write_text("credentials")
            (source / ".planning").mkdir()
            (source / ".planning/state.json").write_text("{}")
            (source / "outside-link").symlink_to(Path(parent_dir))
            with self.assertRaisesRegex(SMOKE.SmokeBlocked, "symlink"):
                with SMOKE.isolated_fixture(source, base_dir=Path(parent_dir)):
                    pass
            (source / "outside-link").unlink()
            with SMOKE.isolated_fixture(source, base_dir=Path(parent_dir)) as fixture:
                copied = fixture / "plugin"
                self.assertTrue((copied / "skills/public.txt").is_file())
                self.assertFalse((copied / "private.key").exists())
                self.assertFalse((copied / "client.pem").exists())
                self.assertFalse((copied / "credentials.json").exists())
                self.assertFalse((copied / ".planning").exists())

    def test_fixture_excludes_modern_auth_key_and_keystore_families_but_keeps_samples(self):
        sensitive = ("token.json", "auth.json", "id_ed25519", "id_ecdsa.pub",
                     "keystore.jks", "client.ckey", "truststore.p12", "private-keys.json",
                     "service-credentials.yaml", "server.cert")
        documented = ("token.example.json", "auth.sample.json", "credentials.example.yaml",
                      "keystore.sample.jks", "private-key.example.pem")
        with tempfile.TemporaryDirectory() as source_dir, tempfile.TemporaryDirectory() as parent_dir:
            source = Path(source_dir); (source / "skills").mkdir()
            (source / "skills/public.txt").write_text("ok")
            for name in sensitive + documented:
                (source / name).write_text(name)
            with SMOKE.isolated_fixture(source, base_dir=Path(parent_dir)) as fixture:
                copied = fixture / "plugin"
                self.assertTrue(all(not (copied / name).exists() for name in sensitive))
                self.assertTrue(all((copied / name).is_file() for name in documented))

    def test_handoff_uses_each_runtime_adapter_and_rejects_unscoped_approval(self):
        with tempfile.TemporaryDirectory() as directory:
            with SMOKE.isolated_fixture(ROOT / "plugins/sdd-composy",
                                        base_dir=Path(directory)) as fixture:
                outcome = SMOKE._offline_handoff(fixture, fixture / "plugin")
                self.assertTrue(outcome["passed"])
                self.assertEqual(outcome["adapters"], ["hermes", "codex", "claude", "hermes"])
                self.assertEqual(len(outcome["invocations"]), 4)
                for invocation in outcome["invocations"]:
                    self.assertEqual(Path(invocation["cwd"]).resolve(), fixture.resolve())
                    self.assertTrue(invocation["argv"])
                self.assertEqual([item["runtime"] for item in outcome["invocations"]], outcome["adapters"])
                for index, invocation in enumerate(outcome["invocations"][1:]):
                    self.assertEqual(Path(invocation["consumed"]), fixture / outcome["resources"][index])
                self.assertIn("--output-last-message", outcome["invocations"][1]["argv"])
                self.assertIn("--output-format", outcome["invocations"][2]["argv"])
                artifacts = [json.loads((fixture / resource).read_text())
                             for resource in outcome["resources"]]
                contracts = [item["result"]["evidence"]["handoff"] for item in artifacts]
                self.assertTrue(all(value["task_id"] == "TASK-008" for value in contracts))
                self.assertTrue(all(value["gate"] == "APPROVED" for value in contracts))
                self.assertTrue(all(value["approval"]["synthetic"] is True for value in contracts))
                self.assertTrue(all(value["requirement_id"] == "RF-010" for value in contracts))
                self.assertTrue(all(value["evidence"] == {"durable": True} for value in contracts))
                with self.assertRaisesRegex(SMOKE.SmokeBlocked, "invented approval"):
                    SMOKE._offline_handoff(fixture, fixture / "plugin",
                                           approval={"status": "APPROVED"})

    def test_fleet_mismatch_uses_canonical_runtime_and_exact_diagnostic(self):
        with tempfile.TemporaryDirectory() as directory:
            with SMOKE.isolated_fixture(ROOT / "plugins/sdd-composy",
                                        base_dir=Path(directory)) as fixture:
                outcome = SMOKE._offline_fleet(fixture, fixture / "plugin", "codex")
        self.assertTrue(outcome["passed"])
        self.assertEqual(outcome["mismatch_requested_runtime"], "hermes")
        self.assertIn("canonical Git worktree registration", outcome["mismatch_diagnostic"])
        self.assertNotIn("canonical Git worktree registration", outcome["matching_stderr"])
        self.assertFalse(outcome["mismatch_provider_invoked"])
        self.assertEqual(outcome["mismatch_diagnostic"], outcome["mismatch_stderr"])

    def test_handoff_cannot_pass_when_an_actual_adapter_run_is_skipped(self):
        original = SMOKE._load_local
        for skipped in range(4):
            loaded = []
            def load(scripts, filename, tag):
                module = original(scripts, filename, tag)
                loaded.append(filename)
                if len(loaded) - 1 == skipped:
                    module.run = lambda *args, **kwargs: {}
                return module
            with tempfile.TemporaryDirectory() as directory:
                with patch.object(SMOKE, "_load_local", side_effect=load):
                    with self.assertRaises((SMOKE.SmokeBlocked, KeyError, FileNotFoundError)):
                        SMOKE._offline_handoff(Path(directory), ROOT / "plugins/sdd-composy")

    def test_fleet_rejects_unrelated_runner_stderr_without_rewriting_it(self):
        original = subprocess.run
        diagnostic = "sdd-fleet-run: registered fleet member does not match canonical Git worktree registration\n"
        def run(command, *args, **kwargs):
            if str(command[0]).endswith("/fleet/run.sh"):
                return subprocess.CompletedProcess(command, 2, "", diagnostic)
            return original(command, *args, **kwargs)
        with SMOKE.isolated_fixture(ROOT / "plugins/sdd-composy") as fixture:
            with patch.object(SMOKE.subprocess, "run", side_effect=run):
                outcome = SMOKE._offline_fleet(fixture, fixture / "plugin", "codex")
        self.assertFalse(outcome["passed"])
        self.assertEqual(outcome["mismatch_diagnostic"], diagnostic)

    def test_sanitizer_redacts_secrets_and_sensitive_absolute_paths(self):
        raw = "token=secret-value Authorization: Bearer abc123 /Users/person/project"
        sanitized = SMOKE.sanitize(raw)
        self.assertNotIn("secret-value", sanitized)
        self.assertNotIn("abc123", sanitized)
        self.assertNotIn("/Users/person", sanitized)
        self.assertIn("[REDACTED]", sanitized)

    def test_fixture_approval_must_be_explicitly_synthetic_and_scoped(self):
        with self.assertRaisesRegex(SMOKE.SmokeBlocked, "invented approval"):
            SMOKE.validate_fixture_approval({"status": "APPROVED"})
        SMOKE.validate_fixture_approval({
            "status": "APPROVED", "synthetic": True, "scope": "task-08-runtime-smoke"
        })

    def test_real_fleet_is_blocked_without_external_acknowledgement(self):
        with tempfile.TemporaryDirectory() as directory:
            called = []
            summary = SMOKE.run_acceptance(
                mode="real", runtime="hermes", language="pt-BR", scenario="fleet",
                output=Path(directory) / "run", plugin_root=ROOT / "plugins/sdd-composy",
                provider_launcher=lambda *args, **kwargs: called.append((args, kwargs)),
                fleet_acknowledged=False,
            )
        self.assertEqual(called, [])
        self.assertEqual(summary["scenarios"][0]["status"], "BLOCKED")
        self.assertIn("acknowledgement", summary["scenarios"][0]["reason"])

    def test_launcher_measurements_are_preserved_in_real_records(self):
        with tempfile.TemporaryDirectory() as directory:
            summary = SMOKE.run_acceptance(
                mode="real", runtime="codex", language="en-US", scenario="read-only",
                output=Path(directory) / "run", plugin_root=ROOT / "plugins/sdd-composy",
                provider_launcher=lambda **_kwargs: {
                    "status": "PASS", "reason": None, "exit_code": 0,
                    "duration_seconds": 1.25, "result_sha256": "a" * 64,
                    "command": ["codex", "exec", "[REDACTED]"],
                    "resources": ["fixture-123"], "version": "test-version",
                    "provider": "fake", "model": None,
                })
        record = summary["scenarios"][0]
        self.assertEqual(record["duration_seconds"], 1.25)
        self.assertEqual(record["result_sha256"], "a" * 64)
        self.assertEqual(record["resources"], ["fixture-123"])
        self.assertEqual(record["version"], "test-version")

    def test_cli_writes_atomic_json_summary_with_null_unavailable_usage(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "offline"
            completed = subprocess.run([
                sys.executable, str(ROOT / "scripts/sdd_runtime_smoke.py"),
                "--mode", "offline", "--runtime", "all", "--language", "both",
                "--scenario", "all", "--output", str(output),
            ], cwd=ROOT, text=True, capture_output=True, check=False)
            self.assertEqual(completed.returncode, 0, completed.stderr)
            summary = json.loads((output / "summary.json").read_text())
            self.assertEqual(summary["verdict"], "PASS")
            self.assertIsNone(summary["usage"])
            self.assertFalse((output / "summary.json.tmp").exists())

    def test_output_and_fingerprint_reject_symlink_leaf_and_ancestors(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            real = root / "real"; real.mkdir()
            alias = root / "alias"; alias.symlink_to(real, target_is_directory=True)
            with self.assertRaisesRegex(SMOKE.SmokeBlocked, "symlink"):
                SMOKE.write_summary(alias / "child", {"verdict": "PASS"})
            source = root / "source"; source.mkdir()
            (source / "target").write_text("secret")
            (source / "linked").symlink_to(source / "target")
            with self.assertRaisesRegex(SMOKE.SmokeBlocked, "symlink"):
                SMOKE.tree_fingerprint(source)

    def test_failed_atomic_replace_preserves_existing_summary(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            target = output / "summary.json"
            target.write_text("original")
            with patch.object(SMOKE.os, "replace", side_effect=OSError("failure")):
                with self.assertRaises(OSError):
                    SMOKE.write_summary(output, {"verdict": "PASS"})
            self.assertEqual(target.read_text(), "original")
            self.assertEqual(list(output.iterdir()), [target])

    def test_real_cli_exposes_provider_entry_point_but_remains_gated(self):
        completed = subprocess.run([
            sys.executable, str(ROOT / "scripts/sdd_runtime_smoke.py"),
            "--mode", "real", "--runtime", "codex", "--language", "pt-BR",
            "--scenario", "fleet", "--provider-entry-point", "production",
            "--output", str(Path(tempfile.gettempdir()) / "sdd-real-gated-test"),
        ], cwd=ROOT, text=True, capture_output=True, check=False)
        self.assertEqual(completed.returncode, 2)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["verdict"], "BLOCKED")


if __name__ == "__main__":
    unittest.main()
