# Task 01 Review

## Review scope

Read-only review of the Task 01 fleet core against
`.planning/power/features/sdd-composy-f08-fleet/task-01-brief.md`.

## Verification

- `bash -n plugins/sdd-composy/scripts/fleet/common.sh plugins/sdd-composy/scripts/fleet/launch.sh` passed.
- `python3 -m unittest tests.test_sdd_composy_fleet` could not run: the required module does not exist (`ModuleNotFoundError: No module named 'tests.test_sdd_composy_fleet'`).
- The required `plugins/sdd-composy/references/fleet.md` file is also absent despite being listed as a Task 01 output.

## Findings

### Important — required behavioral test suite is absent

The brief explicitly requires failing tests and a focused rerun covering eligibility,
symlinks, collisions, dirty contracts, hash binding, partial launch, and central-worktree
preservation. There is no `tests/test_sdd_composy_fleet.py`, so none of these behaviors has
regression coverage or an executable acceptance signal. The implementation report confirms
this gap rather than resolving it.

### Important — required fleet reference is absent

`references/fleet.md` is listed in the task file set and the implementation report says it was
added, but the file is not present. The provider-neutral ownership and invariants therefore
are not documented in the shipped plugin.

### Review note — implementation needs test-driven validation

The shell syntax check is insufficient to establish safe path validation, lock ownership,
contract hash binding, rollback, or preservation of the central worktree. These must be
exercised by the missing focused test module before the task can be approved.

## Verdict

SPEC: REJECTED — required output `references/fleet.md` is missing.

QUALITY: REJECTED — the required focused test module is missing, so the acceptance matrix is
not executable and the safety claims are unverified.

Disposition: return to implementation for the missing reference and the complete focused test
matrix; then rerun this review read-only.
