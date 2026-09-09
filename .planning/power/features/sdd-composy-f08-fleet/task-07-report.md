# Task 07 report — teardown and authorized merge

## Result

Implemented `plugins/sdd-composy/scripts/fleet/teardown.sh` and shared guards in
`fleet/common.sh`.

The teardown accepts an exact root, fleet identity, and member identity. It
refuses non-completed merges, requires `CONFIRM-SDD-MERGE`, validates the result
identity and commit, refuses dirty or detached repositories, aborts conflicted
merges, and preserves branch/worktree/metadata on failure. Non-merge teardown
stops only the recorded Compose project, never passes `--volumes`, releases only
the member runner lock, removes only that member record, and preserves the
recoverable branch and worktree. Symlinked metadata, worktrees, compose files,
and locks are rejected.

## Lifecycle and regression coverage

The fleet tests now exercise the explicit locked-to-completed handoff: the
central member record receives `status: completed` and `result_path`, and the
result must carry the same `member_id` plus a forty-character commit before an
authorized merge is accepted. The matrix also covers non-terminal and missing
authorization refusal, identity/commit validation, dirty/conflict preservation,
symlinked foreign worktrees, successful non-merge teardown, branch/worktree
preservation, and no-volume-destruction behavior.

Round 2 additionally binds the result commit to both the registered branch
tip and the actual worktree `HEAD`. Fake-Docker coverage proves Compose failure
preserves metadata/worktree, records the owned project only, and never passes
`--volumes`; lock-release failure and symlink worktree rejection are covered.

Round 3 adds a successful authorized no-ff merge regression, verifying the
merge parent/result, post-merge cleanup, and removal of only the owned worktree
and metadata. Component-wise symlink checks now cover worktree and Compose
paths, including nested parents, before path resolution.

## Verification

```text
python3 -m unittest tests.test_sdd_composy_fleet tests.test_sdd_composy_fleet_runner
Ran 41 tests in 9.229s
OK

bash -n plugins/sdd-composy/scripts/fleet/teardown.sh
bash -n plugins/sdd-composy/scripts/fleet/common.sh
```

No commit was created.
