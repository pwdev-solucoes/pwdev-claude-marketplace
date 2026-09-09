# Task 06 — independent review

## SPEC

PARTIAL. The requested focused suite was executed from the correction worktree:

`python3 -m unittest tests.test_sdd_composy_fleet tests.test_sdd_composy_loop -v`

Result: **79 tests, all passed**, in 14.196s. This does not match the brief's stated
88-test target; the missing nine tests are not present in the checked-out test modules.
The exercised coverage includes central resource records, Compose failure preservation,
locks/cancellation, Claude envelope validation, LOOP gates/dependencies/evidence, and
authorized merge/post-merge recovery paths. No real provider invocation was attempted;
the suite is offline/simulated, as permitted for regression evidence.

## QUALITY

The implementation diff is small and focused. `loop-engine-claude.py` now rejects
non-success/native envelopes and validates the decoded result. `teardown.sh` checks the
central `resources` ownership record, validates identity and optional Compose hash, uses
`docker compose ... down` without volumes, and keeps recovery state on command failure.
The focused suite and shell syntax/diff checks pass.

## FINDINGS

### P1 — central resource ownership can be bypassed by legacy mirrors

In `plugins/sdd-composy/scripts/fleet/teardown.sh`, after validating the central
`resources.compose_file` and `resources.compose_project`, the code replaces both values
with top-level legacy fields whenever the legacy file exists. This means a record with a
valid central resource and a different existing top-level file/project can shut down an
unowned Compose project. The comment says the central record is the ownership source, but
the assignment contradicts that claim. Legacy fields should be read-only compatibility
mirrors and rejected when they disagree (or ignored entirely).

### P2 — missing Compose file is treated as successful teardown

If the centrally owned Compose file does not exist, the `if [[ -f ... ]]` block is skipped,
then non-merge teardown removes member metadata and reports success. Given the contract's
requirement to preserve recovery metadata on validation/cleanup failure, a missing owned
resource should fail closed and retain metadata (unless the record explicitly proves no
Compose resource was allocated).

### P2 — acceptance count is incomplete

The implementation report claims 79 tests and the actual run confirms 79, while the Task
06 brief requests observation of 88 focused tests. This is a traceability/spec gap, not a
test failure; the report should explicitly reconcile the expected count or add the missing
regressions before completion.

## REVIEW

**Verdict: CHANGES_REQUESTED.** Core regressions pass, but the P1 ownership bypass is a
security/safety defect in the teardown boundary and the missing-resource behavior can erase
recovery metadata. Resolve those findings, add/reconcile the nine expected tests, then
rerun the complete focused suite and update the implementation report with fresh evidence.
