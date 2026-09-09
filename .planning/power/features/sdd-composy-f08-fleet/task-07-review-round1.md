# Task 07 review — round 1 — REJECTED

## Verification

```text
python3 -m unittest tests.test_sdd_composy_fleet tests.test_sdd_composy_fleet_runner
Ran 36 tests in 7.165s
OK

bash -n plugins/sdd-composy/scripts/fleet/teardown.sh
bash -n plugins/sdd-composy/scripts/fleet/common.sh
```

The new tests now cover the basic locked-to-completed handoff, confirmation,
identity/commit shape, non-merge preservation, merge conflict abort, and basic
symlink rejection. The lifecycle handoff is represented by manually setting
`status`, `worktree_path`, and `result_path` in the fixture.

## Findings

### HIGH — the result commit is not bound to the member branch/worktree

`teardown.sh` only checks that `result.commit` is a 40-character hexadecimal
string. It never verifies that it equals `git -C "$worktree" rev-parse HEAD`
(or the branch tip recorded by the member). A fabricated/stale result commit
can therefore authorize merging whatever currently points at `branch`. Add a
regression test with a valid but unrelated 40-character commit and reject it,
then bind the result commit to the exact member branch/worktree tip.

### MEDIUM — required failure/ownership matrix remains incomplete

The brief requires cleanup failure, foreign resource protection, recoverable
preservation, and no-volume-destruction coverage. The new tests do not invoke
Compose teardown at all, do not simulate a failing `docker compose down`, do
not assert that a foreign project/container is untouched, do not exercise
runner-lock release failure, and do not inspect the command line for absence
of `--volumes`. The report overstates the verified matrix. Add isolated fake
Docker tests and failure-preservation assertions.

### MEDIUM — symlink worktree path is resolved before symlink rejection

The implementation calls `fleet_abs` and then `cd ... && pwd -P` before
checking `! -L "$worktree"`. A metadata path that names a symlink can be
canonicalized to a real external Git worktree and evade the intended
symlink-path guard (the current test uses a plainly external directory, not a
symlink). Reject the metadata path and every parent component before
canonicalization, then add a symlink-worktree regression test.

## Disposition

**REJECTED** — rework the commit binding and complete the teardown safety test
matrix before approving Task 07.
