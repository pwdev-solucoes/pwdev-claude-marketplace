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
