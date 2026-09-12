# Task 08 report — authorization gate and invocation budget

Status: DONE

## Scope delivered

- Added exact `runtime:ui` authorization for real interactive smoke rows.
- Unauthorized rows are `NOT_RUN` and neither consume budget nor call a launcher.
- Added a durable, atomic per-run `invocation-budget.json`; the exact combination is consumed before the external launcher call, so failure cannot be retried.
- Duplicate attempts are `NOT_RUN`; authorization of another UI does not permit fallback.
- Preserved unknown durable-budget fields when publishing a later consumption.
- Added CLI `--authorize-runtime-ui` with only concrete Hermes/Codex/Claude and cmux/tmux/headless combinations. No conversation, artifact, generic acknowledgement, credential, or runtime availability inference grants authorization.

## Verification

- RED: two focused tests errored with `unexpected keyword argument 'authorized_runtime_uis'` before implementation.
- GREEN: focused exact-authorization, generic-acknowledgement, durable failure, duplicate, and no-fallback tests pass using fake launchers only.
- Full command: `python3 -m unittest discover -s tests -p 'test_sdd_composy*.py'`.
- Result: 424 tests passed in 179.986s.

## Real-run status

No real provider, cmux, or tmux session was executed. Every real runtime/UI combination remains INCOMPLETE/NOT_RUN and requires separate exact human authorization.

## Review fix round 1

- The production identity branch now carries the exact, already-consumed reservation into an injected interactive launch path.
- Durable reservation is serialized with an exclusive lock and a fresh under-lock read; publication preserves unknown fields and fsyncs the file and directory.
- Symlinked budget/lock paths and ancestors are rejected before reading durable budget content.
- Focused result: six gate/budget tests passed in 0.129s. Only fake launchers were used.
- Full result: 427 tests passed in 175.120s.

## Review fix round 2

- Real interactive invocation now requires exactly one concrete cmux, tmux, or headless UI; `all` and `auto` are rejected as `NOT_RUN` before reservation/call.
- Offline `all` remains supported. A failed concrete UI is terminal for that invocation and no cross-UI fallback can occur.
- Focused result: four fake-only tests passed in 49.962s.
- Full result: 428 tests passed in 176.683s.

## Production interactive launcher

- Implemented and wired `production_interactive_launcher` for the production CLI path.
- It prepares only a confined recoverable fixture beneath the requested output, calls the existing fleet launcher once with the exact runtime/UI, and observes durable member/LOOP/handle state for 300 seconds.
- It returns inspectable repository, worktree, member, LOOP, and handle paths and never treats terminal output as witness or performs cleanup, merge, retry, or fallback.
- Focused smoke module: 39 tests passed in 137.914s. Full suite: 431 tests passed in 172.945s.
- Verification used injected fake command runners only; all real combinations remain INCOMPLETE/NOT_RUN.

## Launcher fix round 3

- Added authoritative tuple validation using the existing member/LOOP validators and UI driver ownership/recoverability inspection contracts.
- Member, owner, task, runtime, UI, repository, registered worktree, LOOP binding/internal identity, and handle ownership are all bound and confined before PASS/BLOCKED classification.
- `awaiting_human` now remains under observation through the exact 300-second monotonic boundary; a validated completion before that boundary passes.
- Focused adversarial/timing result: three fake-only tests passed in 0.626s. Real rows remain INCOMPLETE/NOT_RUN.
- Full result: 432 tests passed in 173.870s.

## Production fixture fix round 4

- The production acceptance fixture now writes a complete `sdd_tasks` projection at `.planning/sdd-composy/tasks/task-008.json` and passes that canonical path to `fleet/launch.sh`.
- The ready task includes explicit dependencies, acceptance criterion, verification command, allowed path, and evidence requirement; the existing phase approvals remain explicit.
- A regression runs the actual fleet launcher and actual interactive wrapper preflight with fake Codex/tmux executables, reaches durable `awaiting_human`, and verifies the canonical member contract path and SHA-256 digest.
- Focused result: 4 tests passed in 2.498s. Full result: 434 tests passed in 298.112s.
- No real provider/UI was invoked and neither consumed real combination was retried.
