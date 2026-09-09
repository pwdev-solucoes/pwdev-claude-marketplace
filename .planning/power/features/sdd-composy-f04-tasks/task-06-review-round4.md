# Task 06 review — round 4

## SPEC

**FAIL.** The one-sided fixture is corrected to a valid JSON projection and
missing-status, external-path, root-link, and unknown-field checks were added.
The matrix test passes, but the focused suite still fails: the test expects a
repository-root symlink to be rejected, while `inspect` resolves `root` and
does not reject it (`sdd_sync.py:59`). This violates the reference requirement
that symlinks be rejected.

## QUALITY

**FAIL.** `SynchronizationInspectionTest` results: 1 passed, 1 failed. The
failure is `test_malformed_and_read_only_and_symlink_safety` because no
`ValueError` is raised for `root_link`. The requested coverage is now present,
but verification is not green.

## REVIEW

**CHANGES_REQUIRED.** Reject a symlink repository root before resolving it (or
define and test an explicitly different contract), then rerun the focused
suite. No code or commit was modified by this review.
