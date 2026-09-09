# Task 06 review — round 1

## SPEC

**PARTIAL / CHANGES_REQUIRED.** Round 1 fixes all three implementation gaps:
`_markdown`/`_json` and `inspect` reject symlinks; malformed inputs now produce
`malformed_markdown`/`malformed_json` items; and state presence/value mismatch
uses `status_divergence` (`sdd_sync.py:28-45, 53-78`). The API remains
read-only, repository-confined, authority-neutral, and uses the exact
confirmation token. However, the brief explicitly requires failing tests and a
focused synchronization test matrix. `tests/test_sdd_composy_tasks.py` still
contains only the 17 task-runtime tests and no `sdd_sync` import or cases.

## QUALITY

**PARTIAL.** `python3 -m unittest tests.test_sdd_composy_tasks -q` passes
(17 tests). The implementation changes are compact and deterministic, but the
new behavior is unverified by tests. A full `unittest discover` did not finish
within the review timeout, so no full-suite pass is claimed.

## FINDINGS

1. **Medium — required synchronization test matrix is still absent.** Add
focused tests for no-change, Markdown-only, JSON-only, identity change, status
divergence including missing status, malformed Markdown, malformed JSON, exact
confirmation token, deterministic `plan`, byte-for-byte read-only behavior,
unknown-field preservation, and internal/external symlink rejection.
2. **Low — malformed items use wildcard ID `*`.** This is deterministic and
acceptable if documented, but tests should pin the chosen representation.

## REVIEW

**CHANGES_REQUIRED** — implementation blockers are addressed, but Task 06 is
not complete until the required synchronization tests are added and pass.
