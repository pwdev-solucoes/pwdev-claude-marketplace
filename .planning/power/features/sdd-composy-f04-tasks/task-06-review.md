# Task 06 review

## SPEC

**FAIL**. The implementation has the intended read-only shape, exact
`CONFIRM-SDD-SYNC` token, deterministic ID ordering, and no authority-selection
or write operation. It does not meet the repository-bound contract in
`references/synchronization.md`: the confinement check resolves paths and then
accepts symlinks whose targets remain inside the repository, while the reference
explicitly requires symlinks to be rejected. In addition, `CLASSIFICATIONS`
declares malformed classifications but malformed Markdown/JSON is returned only
as top-level errors with no malformed item classification. Most importantly,
the status comparison treats a missing/empty state on either side as
`no_change`; a present state versus absent state is a divergence and must not
be silently presented as synchronized.

## QUALITY

**PARTIAL**. `inspect` and `plan` are side-effect free and preserve source JSON
by never reconstructing or writing it; unknown fields therefore cannot be lost.
The plan has stable sorting and an empty, non-executable operations list.
Focused pre-existing task-runtime tests pass (`17 tests, OK`), but there is no
`tests/test_sdd_composy_tasks.py` coverage for the new synchronization API's
required no-change, one-sided, identity, status, malformed, token,
read-only, symlink, and deterministic-plan cases. The unused imports and
one-line compound statements also make this new module less maintainable, but
are secondary to the contract gaps.

## FINDINGS

1. **High — symlink safety is incomplete.** `_confined` only checks the
resolved target is under the root (`sdd_sync.py:16-18`); an internal symlink
for `markdown_root`, `state_path`, or a matched task file is accepted. The
reference says “symlinks and external paths are rejected.” Add explicit
`is_symlink()` checks for input paths and every discovered Markdown file, with
tests for both internal and external links.
2. **Medium — malformed classification is not exposed.** Parsing errors return
`items: []` and an error string (`sdd_sync.py:56-61`) even though the required
classification vocabulary includes `malformed_markdown` and
`malformed_json`. Return deterministic malformed items (or revise the contract
and tests consistently), while retaining useful errors.
3. **Medium — missing status is silently equal.** The truthiness guard at
`sdd_sync.py:67` only detects divergence when both states are non-empty. A
state present on one source and absent on the other needs an explicit
`status_divergence` (or malformed classification), never `no_change`.
4. **Medium — required test file/coverage is absent.** The brief names
`tests/test_sdd_composy_tasks.py`, but the checked-out file contains only
`sdd_tasks` runtime tests and no import/tests for `sdd_sync`; the required Task
06 matrix is therefore unverified.

## REVIEW

**CHANGES_REQUIRED**. Do not mark Task 06 complete until the three behavioral
gaps are fixed and the focused synchronization tests cover all required cases,
including byte-for-byte read-only checks and repository/symlink safety.
