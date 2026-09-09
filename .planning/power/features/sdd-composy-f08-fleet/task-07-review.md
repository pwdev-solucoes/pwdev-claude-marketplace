# Task 07 review — REJECTED

## Scope

Read-only review of `teardown.sh`, `common.sh`, the Task 07 report, and both
fleet test modules. Executed:

```text
python3 -m unittest tests.test_sdd_composy_fleet tests.test_sdd_composy_fleet_runner
Ran 31 tests in 6.220s
OK
```

## Findings

### HIGH — required teardown/merge test matrix is absent

The Task 07 brief explicitly requires failing tests for non-terminal merge
refusal, missing authorization, conflict abort, cleanup failure, foreign
resource protection, and recoverable preservation. Neither
`tests/test_sdd_composy_fleet.py` nor `tests/test_sdd_composy_fleet_runner.py`
contains a teardown invocation or a merge/cleanup test; the 31 passing tests
cover launch, runner, UI, cmux, and dashboard behavior only. The report's
verification therefore does not demonstrate the new teardown contract.

Add executable regression tests covering at minimum:

- non-completed member and missing/incorrect `CONFIRM-SDD-MERGE` refusal;
- exact member/result identity and 40-character commit validation;
- dirty and detached central repositories;
- merge conflict and `git merge --abort` behavior;
- Compose shutdown failure and lock-release/metadata cleanup failure;
- foreign or symlinked worktree, metadata, lock, Compose file/project safety;
- no `--volumes` and no deletion of unknown files/volumes;
- preservation of branch, worktree, and metadata on every failure;
- successful non-merge teardown and authorized no-ff merge with post-merge
  verification.

### MEDIUM — launch/run/teardown lifecycle agreement is untested and currently
requires an external metadata transition

`launch.sh` writes member records with `id` and `state: locked`; `run.sh`
publishes per-worktree results/status but does not update the central member
record to `status: completed`. `teardown.sh --merge` requires the central
record's status/state to equal `completed`, and then requires a `result_path`
whose JSON contains `member_id`. This may be an intentional authorized
handoff boundary, but it is not documented or exercised end-to-end. Add a
fixture proving the intended transition and exact schema, or make the
handoff explicit in the lifecycle contract.

## Disposition

**REJECTED** — implementation may be retained, but Task 07 is not approved
until the required teardown tests and lifecycle handoff coverage are added and
both fleet suites are rerun.
