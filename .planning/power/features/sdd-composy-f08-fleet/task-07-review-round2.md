# Task 07 review — round 2 — REJECTED

## Verification

```text
python3 -m unittest tests.test_sdd_composy_fleet tests.test_sdd_composy_fleet_runner
Ran 39 tests in 8.091s
OK
```

The commit binding is now correct: the result commit is compared with both
the member worktree `HEAD` and the registered branch tip. A direct symlink
worktree regression, Compose failure preservation, lock-release failure, and
no-`--volumes` assertion were added.

## Remaining findings

### MEDIUM — successful authorized merge is not tested

The test matrix covers refusals and conflict abort, but does not exercise the
positive path: completed member, exact confirmation, valid result tip,
successful `--no-ff` merge, post-merge verification, worktree removal, and
member metadata removal. Add this regression before approving the task.

### MEDIUM — parent-component symlink safety is still incomplete

The new guard checks `[[ ! -L "$candidate" ]]` before canonicalization, but it
does not inspect each parent component of the candidate. A metadata path such
as `symlink-parent/worktree` can therefore pass the direct check and be
canonicalized through a symlink. The Compose path similarly checks only the
final file with `! -L`, not symlinked parent components. Reject symlinks in
every component of the worktree and recorded Compose path, and add nested
symlink regressions.

## Disposition

**REJECTED** — add the successful authorized merge test and complete
component-wise symlink protection.
