# F07 Third-Rejection Boundary Fix

## Root cause

`orchestrate()` incremented the rejection counter before calling
`correction_decision()`, while the decision API defines `rejection_count` as
the number of rejected results preceding the current result. Consequently,
the second rejected result was passed as `rejection_count=2` and incorrectly
stopped with `third_rejection`.

## Fix

The orchestrator now passes `rejections - 1` to `correction_decision()`. The
first and second rejected results therefore continue through bounded
correction, while the third rejected result receives `rejection_count=2` and
stops with the required `third_rejection` reason. The public decision API and
its existing unit contract remain unchanged.

## Regression coverage

- Added an integration test proving the second rejection continues correction
  and reaches the iteration cap rather than `third_rejection`.
- Added an integration test proving the third rejection stops with the exact
  `third_rejection` status and stop reason.

## Verification

`python3 -m unittest tests.test_sdd_composy_loop -q` — 30 tests passed.

`python3 -m unittest discover -s tests -p 'test_sdd_composy*.py' -q` — 222 tests passed.

`git diff --check` — passed.

No commit was created.
