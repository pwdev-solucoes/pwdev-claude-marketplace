# Task 01 Review — Round 1

## Verification

- `plugins/sdd-composy/references/fleet.md` now exists and documents the provider-neutral
  ownership/invariants.
- `python3 -m unittest tests.test_sdd_composy_fleet` passed: 4 tests, 4 OK.

## Findings

### Important — focused matrix still does not cover all required behaviors

The brief requires coverage for eligibility, symlinks, collisions, dirty contracts, hash
binding, partial launch, and central-worktree preservation. The suite covers the named areas
in broad form, but `test_branch_collision_and_partial_failure_preserves_branch_or_central`
only exercises a second launch rejected by an existing branch. It does not induce a failure
after `git worktree add` succeeds, so the rollback/partial-launch path is untested.

Lock ownership is also implemented but has no focused test proving concurrent/duplicate lock
handling or timeout behavior. Hash binding is checked for the initial digest, but no test
checks that a contract mutation is detected or that the published binding remains coherent
after launch.

These gaps matter because the task explicitly calls for safety validation, not only syntax and
happy-path launch validation.

## Verdict

SPEC: REJECTED — the required partial-launch and lock-ownership acceptance coverage is not
complete.

QUALITY: REJECTED — the focused suite passes, but does not exercise the failure paths that
protect worktree cleanup and serialized fleet state.

Disposition: add tests that force a post-worktree-creation failure and verify cleanup/central
worktree preservation, plus lock ownership/timeout behavior; then rerun review.
