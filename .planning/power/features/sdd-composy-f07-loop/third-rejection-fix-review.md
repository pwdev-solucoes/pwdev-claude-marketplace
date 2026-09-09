# Review: F07 Third-Rejection Boundary Fix

## Scope

Read-only review of the targeted `orchestrate()` counter correction. The
approved contract requires the first two rejected runtime results to continue
bounded correction and the third rejected result to stop with
`third_rejection`.

## Findings

No blocking findings.

`orchestrate()` increments its local count for the current rejected result but
passes `rejections - 1` to `correction_decision()`. Therefore the second
rejection is evaluated with two prior rejections absent and continues until
the configured iteration cap; the third is evaluated with two prior
rejections and returns `needs_human/third_rejection`. The integration tests
assert both boundaries, including exact status, stop reason, and call count.

The public `correction_decision()` threshold remains `rejection_count >= 2`,
which is consistent with its documented meaning of prior rejected results and
preserves the direct API test.

## Verification

- `python3 -m unittest tests.test_sdd_composy_loop -v` — 30 tests passed.
- `python3 -m unittest discover -s tests -p 'test_sdd_composy*.py' -q` — 222 tests passed.
- `git diff --check` — passed.

## Disposition

**APPROVED.** The off-by-one defect is corrected, regression coverage is
present for both sides of the boundary, and the complete `sdd-composy` test
suite remains green. No commit was created.
