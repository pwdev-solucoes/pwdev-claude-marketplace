# F04 Task 04 — Review round 2

## SPEC

PASS. The transition engine now matches the Task 04 evidence/completion
contract: timestamps are RFC3339, bounded by the transition clock and the
projection timestamp; completion requires passing tests, non-blocking QA,
approved review and verification, and consistent trace evidence. The optional
`evidence_required: false` path is guarded and permits
`qa_required -> review_required`. Rejection requires a reason and records the
source stage plus invalidation timestamp. Skipping requires and records both a
non-empty justification and human authority.

## QUALITY

PASS. Focused verification is green:

```text
python3 -m unittest tests.test_sdd_composy_tasks
Ran 15 tests in 0.097s — OK
```

Coverage now includes missing tests, stale and future evidence, blocking QA,
blocking/unapproved review, rejected verification, inconsistent trace,
unapproved verification, valid completion, unjustified skip, missing human
authority, valid skip metadata, rejection metadata, and the optional no-dossier
route. Existing tests continue to cover unknown-field preservation and atomic
temporary-file cleanup.

## FINDINGS

None.

## REVIEW

`APPROVED`

No HEAD movement or commit was performed.
