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

## Review fix round 1

- RED: the three focused interactive tests failed because matrix rows lacked runner/driver observations, negative cases were lookup labels, and `auto` resolution evidence was absent.
- GREEN: `python3 -m unittest tests.test_sdd_composy_runtime_smoke` — 28 tests passed in 93.128s.
- Matrix rerun: 6/6 PASS, zero provider calls; every row reached `awaiting_human` through `interactive-run.sh` and obtained a live, recoverable observation through its real cmux/tmux driver function.
- Negative decisions now consume executable fixtures: terminal files are ignored as witness, witness SHA-256 is recomputed, pane liveness comes from driver-shaped observation, elapsed time is injected at the exact 300-second boundary, and member/LOOP IDs are read from durable JSON.
- Real `fleet_select_ui auto` resolved cmux, tmux, and headless under three fake availability environments before a mutation marker was created.

## Review fix round 2

- RED: the focused negative test failed because results carried no production-call provenance and were still classified by a smoke-local decision chain.
- GREEN: `python3 -m unittest tests.test_sdd_composy_runtime_smoke` — 28 tests passed in 152.274s.
- Fresh offline matrix: 6/6 PASS across Hermes/Codex/Claude × cmux/tmux; provider counters remained zero.
- Production authorities: terminal Markdown/JSON and divergent binding use `fleet/interactive-run.sh`; exact-300 timeout uses `interactive_observer.observe` with injected monotonic ticks; dead panes use both real UI inspect functions; tampered evidence uses canonical `sdd_loop.resume` digest validation.
- The smoke harness only translates returned production state/error into report vocabulary. Real human-assisted tests remain INCOMPLETE.

## Review fix round 3

- RED: the new outcome-injection regression failed because the runner result translator was absent and terminal/divergent cases returned fixed FAIL labels.
- GREEN: `python3 -m unittest tests.test_sdd_composy_runtime_smoke` — 29 tests passed in 140.300s.
- Fresh matrix: 6/6 PASS, zero provider calls.
- Markdown/terminal JSON now PASS only when the captured production run reaches durable `awaiting_human`, invokes the fake provider, leaves LOOP bytes/status/stages unchanged, and advances no evidence. Divergent LOOP now PASS only on nonzero, pre-provider `blocked` rejection with the original LOOP preserved.
- Regression injections for `completed`, advanced stages, zero exit, and provider invocation on divergence all produce FAIL. Real tests remain INCOMPLETE.

## Task 08 gate and one-attempt budget

Status: INCOMPLETE

- RED: the two focused gate tests errored because `run_acceptance` had no exact runtime+UI authorization input and no durable invocation budget.
- GREEN: three focused fake-launcher tests pass. Only `codex:cmux` was invoked in the six-row matrix; every other runtime/UI row was `NOT_RUN` with zero invocation.
- A generic fleet acknowledgement and the presence of a credential-shaped environment variable did not authorize the combination and did not consume budget.
- `invocation-budget.json` is atomically published in the run output before the fake external call. A fake failure consumed `codex:cmux`; a second run returned `NOT_RUN` without retry, and the separately authorized `codex:tmux` fallback was not invoked.
- Final suite: `python3 -m unittest discover -s tests -p 'test_sdd_composy*.py'` — 424 tests passed in 179.986s.
- No real provider, cmux session, tmux session, credentials, or protected file was used. All real runtime/UI combinations remain `INCOMPLETE`/`NOT_RUN` pending exact human authorization for each combination.
