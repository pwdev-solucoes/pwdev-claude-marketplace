# Task 03 review — Runtime engines and runner

## Disposition

**REJECTED — important implementation blocker.**

## Verification performed

- `python3 -m unittest tests.test_sdd_composy_fleet_runner -v` — 4 tests passed.
- `bash -n plugins/sdd-composy/scripts/fleet/engine-codex.sh plugins/sdd-composy/scripts/fleet/engine-claude.sh plugins/sdd-composy/scripts/fleet/run.sh` — passed.
- Reviewed the task brief, report, both runtime adapters, and the shared runner.

## Findings

### Important — the runner cannot load either runtime adapter

`run.sh` constructs and sources:

```sh
ENGINE_ADAPTER=$SCRIPT_DIR/fleet-engine-$EXPECTED_RUNTIME.sh
```

The task implementation creates `engine-codex.sh` and `engine-claude.sh`, not
`fleet-engine-codex.sh` and `fleet-engine-claude.sh`. Consequently every valid
runtime invocation fails with `missing runtime adapter` before any stage is
executed. The focused tests do not exercise a valid registered worktree, so the
failure is currently hidden.

The adapter naming must be made consistent (and the resulting valid-run path
must be tested) before Task 03 can be approved. Do not paper over this with a
test-only alias: the source-of-truth adapter path and its compatibility checks
must agree.

## Scope notes

- The provider command vectors are isolated in the adapter files and the
  malformed Claude result path fails closed in the focused tests.
- The runner's process-group cleanup and correction-cap code should be covered
  by executable integration tests once the adapter-loading blocker is fixed;
  the current four tests do not establish those requirements.
- No files were changed other than this review report; no commit or HEAD
  movement was performed.
