# Task 06 — implementation report

STATUS: IMPLEMENTED

## Scope

Implemented Claude native JSON envelope parsing with closed-field validation,
explicit error rejection, and strict final result validation. Fleet teardown now
requires the central `resources` ownership record, validates branch/worktree and
Compose identity, checks optional Compose hashes, invokes `docker compose down`
without volumes, and preserves recovery metadata on every failure path. Existing
legacy top-level Compose mirrors are used only for compatibility when they point
to an existing owned worktree file.

## Verification

`python3 -m unittest tests.test_sdd_composy_fleet tests.test_sdd_composy_loop -q`
contains 81 discovered tests after two new subprocess regressions for legacy
mirror bypass and missing central Compose resources. `git diff --check` and
`bash -n` passed, with all 81 passing. The suite covers real
subprocess fixtures, Compose failure preservation, merge failure preservation,
locks, cancellation, evidence freshness/tampering, and canonical loop gates.

## NOTE

The existing tests and planning files included pre-existing local changes; they
were preserved. Only the five authorized implementation/test files are intended
for the implementation commit.

## Addendum — residual Compose recovery correction

Teardown now resolves an allocated Compose resource exclusively from the
canonical `repository_root` and requires the exact fleet-owned relative path
`.planning/sdd-composy/fleet/<fleet-id>/docker-compose.yml`. It requires an
explicit boolean `resources.compose_allocated`; for allocated resources it also
requires the schema-form lowercase SHA-256, verifies the central regular file
and all path components, validates repository/owner/member/resource ownership,
and compares the digest before invoking Docker. Legacy top-level mirrors and a
same-named file inside the member worktree cannot substitute for the central
resource. Every rejection occurs before member metadata or the recoverable
worktree is removed.

TDD evidence: the two new subprocess regressions first failed against the old
consumer because it invoked the worktree homonym and defaulted a missing
allocation flag to true; they pass after the correction. Fresh verification:
`python3 -m unittest tests.test_sdd_composy_fleet tests.test_sdd_composy_loop -v`
passed 83 tests; `bash -n plugins/sdd-composy/scripts/fleet/teardown.sh` and
`git diff --check` also passed.
