# Task 04 review — Core schemas

## Verdict

- SPEC: FAIL
- QUALITY: FAIL
- Findings: 1 major, 1 minor

## Findings

### [MAJOR] `skipped` task state does not require its contract-mandated justification

`plugins/sdd-composy/schemas/tasks.schema.json:18-34` includes `skipped` in the durable task-state enum and defines an optional `justification`, but has no conditional requirement tying the two together. Consequently, a task document with `state: "skipped"` and no `justification` validates. This contradicts the consumed Task 02 state contract, which says that `skipped` is terminal and requires an explicit justification, and means the version-1 task-state schema does not enforce a required core field for one of its guarded states. Add a Draft 2020-12 `if`/`then` constraint (while retaining extension-safe objects) and valid/invalid fixtures for the invariant.

### [MINOR] Invalid-fixture tests can pass without exercising most advertised constraints

`tests/test_sdd_composy.py:218-227` supplies one fixture per schema containing several simultaneous defects and only asserts that validation fails somewhere. The custom validator stops at the first failing property, so the config fixture proves the actor pattern but not either root constant; the state fixture proves the stage enum but not other constraints; the tasks fixture fails at `prd_slug` before reaching task IDs, state, collection minima, or paths; and the trace fixture fails at `sequence` before checking the event ID, actor, type, stage, or task ID. Removing most advertised constraints would therefore leave the suite green. Use one isolated invalid fixture/subtest per constraint (and include the guarded `skipped` case), so failures identify the contract that regressed.

## Verification

- `python3 -m unittest tests.test_sdd_composy`: 12 tests passed.
- `git diff --check 2367299..2408b85`: passed.
- The four schema files parse as JSON through the focused suite.
- No implementation files were changed during review.

## Re-review round 1 — scoped major finding

### `skipped` requires justification: ADDRESSED

`review-2408b85..4711add.diff` adds a Draft 2020-12 `if`/`then` constraint to the task definition so `state: "skipped"` requires `justification`. The existing `minLength: 1` rejects an empty value, while `additionalProperties: true` remains intact for extension preservation. Focused coverage now accepts a justified skipped task with an unknown extension and rejects both missing and empty justification. `python3 -m unittest tests.test_sdd_composy` passes all 13 tests.

This re-review is limited to the original major finding. The deferred minor finding was not reassessed.
