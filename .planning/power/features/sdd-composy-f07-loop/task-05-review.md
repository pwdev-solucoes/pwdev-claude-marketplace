# F07 Task 05 — Read-only review

## Scope

Reviewed `sdd_loop.orchestrate` and the runtime adapters against
`.planning/power/features/sdd-composy-f07-loop/task-05-brief.md`. The review was
read-only; no HEAD movement or implementation changes were made.

## Verification

Command:

```text
python3 -m unittest tests.test_sdd_composy_loop
```

Result: 21 tests passed.

## Findings

### Important — publication occurs before successful stage completion

`orchestrate` invokes `task_publish` and `trace_publish` before checking the
runtime result's `status`/`verdict` and before `publish_stage`. The task brief
requires task and trace publications only after a successful canonical stage.
Failed, rejected, malformed-by-core, or otherwise non-successful results can
therefore be externally published even though the stage is not durably
completed. This violates the required publication boundary and makes a failed
correction observable as completed work.

### Important — required orchestrator lifecycle tests are absent

The brief explicitly requires failing/then-passing lifecycle tests for human
approval, one correction, iteration-cap exhaustion, cancellation, and resume.
`tests/test_sdd_composy_loop.py` covers primitives (`start`, `resume`,
`publish_stage`, `continue_loop`, and adapter validation), but contains no
`orchestrate` tests for those five paths. Consequently the publication-order
bug and resume behavior are not exercised by the focused suite.

### Important — orchestrate does not resume an existing loop

`orchestrate` always calls `start(...)`. Supplying an existing `loop_id` raises
`LoopError("loop already exists")`, so a process interrupted after durable stage
publication cannot be resumed through the orchestrator API. The task brief
lists resume as a required lifecycle behavior; the lower-level `resume` helper
alone does not satisfy that orchestration contract.

## Disposition

**REJECTED — round 1 fixes required.**

The implementation has a sound atomic publication primitive and the adapters
are provider-isolated, but the three findings above are in scope and prevent
approval of Task 05.
