# F04 Task 04 — Review

## SPEC

FAIL. The implementation adds timestamp/evidence predicates, but it does not
implement the full lifecycle contract in `references/states.md`. In particular,
`qa_required` can only transition to `evidence_required`; there is no guarded
`qa_required -> review_required` path for the explicitly supported
`evidence_required: false` case. Also, `verify_required -> rejected` accepts no
rejection reason, although the contract requires a rejection reason, stale
evidence invalidation, and producing stage to be recorded. `skipped` stores a
string justification, but does not capture the required human authority.

## QUALITY

FAIL. The focused suite passes (`python3 -m unittest tests.test_sdd_composy_tasks`:
10 tests), but those ten tests are Task 03 graph/transition tests and contain no
Task 04 evidence fixtures. None of the brief's required cases—stale evidence,
missing tests, blocking QA/review, rejected verification, unjustified skip, or
valid completion—is exercised. Thus the green result does not establish the
new completion guards. Unknown-field preservation and atomic replacement are
covered by the existing import tests and remain intact on inspection.

## FINDINGS

1. **[BLOCKER] Evidence guard coverage is absent.** Add failing-then-passing
   tests that construct complete evidence records and assert each required
   predicate and timestamp freshness boundary, including future and stale
   timestamps.
2. **[BLOCKER] `evidence_required: false` cannot bypass dossier state.** Add
   the legal `qa_required -> review_required` transition with its QA/test
   guards, or reject the contract field; currently valid no-dossier tasks are
   stranded.
3. **[BLOCKER] Rejected verification is under-guarded.** Require a non-empty
   rejection reason and persist the reason/stale invalidation metadata when
   entering `rejected` from a gated state. The current branch allows
   `verify_required -> rejected` with no reason and records nothing.
4. **[MAJOR] Skip authority is not represented.** The implementation only
   requires a non-empty string; the state contract requires explicit human
   authority. Add an authority field/API requirement and test it.

## REVIEW

`REJECTED`

Focused tests pass, but the implementation is not complete against the Task 04
brief and lifecycle contract. No HEAD movement or commit was performed.
