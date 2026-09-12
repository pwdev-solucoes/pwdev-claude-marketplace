# Task 07 evidence — interactive runtime smoke

Status: INCOMPLETE

Real human-assisted runtime tests remain INCOMPLETE and were not run. No provider,
credential, protected file, real terminal session, or approval was used as evidence.

## TDD and offline verification

- RED: `python3 -m unittest tests.test_sdd_composy_runtime_smoke.RuntimeSmokeContractTests.test_fleet_interactive_offline_covers_runtime_ui_matrix_without_providers tests.test_sdd_composy_runtime_smoke.RuntimeSmokeContractTests.test_fleet_interactive_negative_pty_content_never_becomes_a_witness` — failed because `run_acceptance` did not accept `ui` and `fleet-interactive` assessment was absent.
- GREEN: `python3 -m unittest tests.test_sdd_composy_runtime_smoke` — 28 tests passed in 85.596s.
- Matrix: `python3 scripts/sdd_runtime_smoke.py --mode offline --runtime all --language en-US --scenario fleet-interactive --ui all --output <temporary-directory>` — PASS, 6/6 runtime×UI rows passed, 0 provider calls, timeout 300 seconds.
- Matrix rows: Hermes/Codex/Claude × cmux/tmux. Separate focused coverage exercises `auto→cmux` resolution and `headless` without provider calls.
- Negative cases: Markdown, JSON encoded as terminal text, tampered witness, dead pane, timeout with a live process, and divergent LOOP binding. Terminal content is never accepted as witness; timeout is BLOCKED/`awaiting_human`; non-executed combinations remain NOT_RUN.

## Limitations

- All runtime and PTY executables are deterministic local fakes.
- Real approval prompts, TUI rendering, credentials, provider networking, and human completion are intentionally untested.
- Real tests remain INCOMPLETE and require a separately authorized human-assisted run.
