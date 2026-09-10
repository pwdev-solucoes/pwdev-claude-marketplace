# Task 06 — re-review round 1

## SPEC

The prior P1/P2 findings are addressed in `5fb1d77..ef59026`:

- Legacy top-level Compose mirrors no longer override `resources`; reproduction with
  central `docker-compose.yml` and legacy `other.yml` invokes only the central file and
  preserves metadata on Docker failure.
- Missing central Compose file now fails closed and preserves metadata/worktree.
- Explicit `resources.compose_allocated=false` with empty Compose fields is accepted as a
  no-Compose allocation and teardown completes safely.

The focused command ran successfully:

`python3 -m unittest tests.test_sdd_composy_fleet tests.test_sdd_composy_loop -q`

Result: **81 tests passed** in 14.305s. This reconciles the previously reported 79 by
adding the two targeted regressions, but remains below the original brief's 88 estimate.

## QUALITY

The teardown change is appropriately fail-closed for allocated resources and maintains
central ownership as the sole shutdown source. The new tests directly reproduce the prior
findings and verify no volume removal. Existing LOOP, Claude envelope, cancellation,
evidence, merge, and recovery tests remain green. The `kill: ... No such process` line is
fixture cleanup noise; unittest exits 0 and all cases pass.

## FINDINGS

No new P1/P2 findings. The only remaining traceability issue is that the brief says 88
focused tests while the repository currently contains and executes 81. This is a P2
documentation/scope discrepancy unless 88 refers to a broader, separately defined suite.

## REVIEW

**Verdict: APPROVED WITH TRACEABILITY NOTE.** Previous ownership-bypass and missing-Compose
recovery findings are resolved and independently reproduced. Accept the implementation if
the expected-test count is corrected/reconciled (or the additional seven tests are added),
then retain this 81-test fresh evidence in the final review.
