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

## Task 08 review fix round 1

- RED: the three focused review regressions failed: production rejected the injected interactive path parameter, a stale budget instance reused `codex:cmux`, and a symlinked budget was read.
- GREEN: six focused gate/budget tests pass in 0.129s using fake launchers only.
- Production now receives an exact reservation consumed by `run_acceptance` before its injected eventual external launch; retry and cross-UI fallback remain impossible.
- Reservation uses an exclusive sibling lock, re-reads and validates under lock, preserves unknown fields, atomically replaces and fsyncs both file and containing directory. Stale and spawned cross-process contenders produce exactly one consumption.
- Budget and lock paths, including ancestors, are rejected if symlinked before budget contents are read. Malformed state remains fail-closed and no launcher is called.
- All real combinations remain INCOMPLETE/NOT_RUN; no provider or real UI session was executed.
- Final suite: `python3 -m unittest discover -s tests -p 'test_sdd_composy*.py'` — 427 tests passed in 175.120s.

## Task 08 review fix round 2

- RED: real `ui=all` invoked the injected cmux path and could continue to tmux; the production identity probe likewise entered the first UI path.
- GREEN: four focused tests passed in 49.962s with fake injection only.
- Real `fleet-interactive` now accepts exactly one concrete `cmux`, `tmux`, or `headless` UI. `all` and `auto` produce `NOT_RUN` before reservation or launcher invocation; `all` remains valid for the offline matrix.
- A failed concrete `codex:cmux` run makes exactly one call and cannot continue to the separately authorized `codex:tmux` combination in the same invocation.
- All real runtime/UI rows remain INCOMPLETE/NOT_RUN; no real provider or UI was executed.
- Final suite: `python3 -m unittest discover -s tests -p 'test_sdd_composy*.py'` — 428 tests passed in 176.683s.

## Task 08 production interactive launcher

- RED: three focused tests failed because `production_interactive_launcher` did not exist and `main()` did not pass it into `run_acceptance`.
- GREEN: `python3 -m unittest tests.test_sdd_composy_runtime_smoke` — 39 tests passed in 137.914s using injected command runners only.
- `main()` now wires the production interactive launcher. After the exact reservation is consumed, it creates a confined recoverable Git/task/approval fixture under the requested run output and invokes existing `fleet/launch.sh` once with exactly one authorized runtime and concrete UI.
- The launch vector contains no compose, prepare-only, bypass, yolo, or full-auto flag. Runtime/UI command construction remains owned by the existing fleet adapters and drivers.
- Observation reads only durable member, LOOP, and handle JSON for the fixed 300-second window. Terminal stdout is ignored as evidence. PASS/BLOCKED/FAIL results carry repository, worktree, member, LOOP, and handle paths, with no merge, teardown, fallback, or retry.
- Full suite: `python3 -m unittest discover -s tests -p 'test_sdd_composy*.py'` — 431 tests passed in 172.945s.
- No real provider, cmux, or tmux process was invoked. Real combinations remain INCOMPLETE/NOT_RUN pending their individual human-authorized runs.

## Task 08 launcher fix round 3

- RED: adversarial tuple and injected-clock tests failed because the launcher accepted unbound JSON and returned immediately on `awaiting_human`.
- GREEN: three focused tests passed in 0.626s using injected runners and handle validators only.
- Member state is loaded through the canonical interactive-state validator, then bound to the exact fleet/member/task/runtime/UI/repository and matching registered worktree resource. The canonical worktree must remain inside the acceptance run area.
- LOOP IDs must satisfy the canonical safe-basename regex before path construction; the regular non-symlink LOOP remains confined to the fixture and its canonical validator must confirm internal ID/task identity.
- The fixed handle path must be confined, regular, non-symlinked, match driver/cwd/fleet/member ownership, and pass the existing cmux/tmux inspect or headless recoverability contract before classification.
- Adversarial member, owner, runtime, UI, worktree/resource, traversal/absolute LOOP, LOOP task, handle owner, and handle symlink cases all fail before PASS/BLOCKED classification.
- `awaiting_human` remains observed until a validated terminal transition or the exact monotonic 300-second boundary. Boundary classification is BLOCKED with no wall sleep; completion before the boundary is revalidated and PASS.
- No terminal output was used and no real provider or UI was invoked. All real combinations remain INCOMPLETE/NOT_RUN.
- Final suite: `python3 -m unittest discover -s tests -p 'test_sdd_composy*.py'` — 432 tests passed in 173.870s.

## Real acceptance `codex:cmux`

- Exactly one human-authorized call was consumed; verdict `BLOCKED` with reason `durable interaction blocked` before Codex provider execution.
- Durable member reason: the acceptance fixture placed `task-008.json` at repository root, outside the canonical `.planning/sdd-composy/tasks/` contract directory required by `interactive-run.sh`.
- cmux ownership was correct after `290f337`: handle `fleet_id` and `member_id` matched the member owner exactly.
- Session, handle, LOOP, branch and worktree were preserved. No retry, fallback, merge or teardown was performed.
- This is not a successful Codex/cmux acceptance result; the combination remains consumed for this run.

## Real acceptance — Hermes + cmux

- Exact human authorization: `hermes:cmux`, one call, `pt-BR`, 300-second observation window.
- Command completed with verdict `FAIL` before human interaction: `UI handle identity or ownership mismatch`.
- Invocation budget was durably consumed once; no retry or UI fallback was attempted.
- The cmux workspace, handle, LOOP, branch, and worktree were preserved for diagnosis. `runtime.env` was not read.
- Root cause was a launcher/driver arity and identity mismatch: the command path was shifted into the handle's member ownership, then the first correction used the lowercase slug instead of canonical `member.owner.member_id`.
- Corrective commits: `7ca8822` (arity) followed by `290f337` (canonical ownership). Independent re-review: SPEC PASS / QUALITY PASS, 87 offline tests.
- This failed attempt is not acceptance evidence for Hermes or cmux and will not be retried automatically.

## Task 08 production fixture fix round 4

- RED: the actual-launch regression failed because the root `task-008.json` was rejected by the real interactive wrapper preflight and the fleet launcher rolled back its pre-resource state.
- GREEN: the fixture publishes `.planning/sdd-composy/tasks/task-008.json` as a complete validated projection and passes that exact path to `fleet/launch.sh`.
- The regression uses only fake Codex/tmux executables, runs actual `launch.sh` plus actual `interactive-run.sh`, reaches durable `awaiting_human`, and verifies the member path and digest remain bound to the canonical projection.
- Focused result: 4 tests passed in 2.498s. Full suite: 434 tests passed in 298.112s.
- The fix was reverted once and the regression failed again before restoration. No real provider/UI was invoked; the consumed Hermes/cmux and Codex/cmux combinations were not retried.
