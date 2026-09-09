# F04 Task 04 — Review round 1

## SPEC

PASS. The implementation now includes the previously missing optional
`qa_required -> review_required` route, requires non-empty rejection reasons,
records rejection stage/reason and invalidation time, and requires/stores skip
justification plus human authority. The timestamp guard rejects evidence older
than the projection baseline and evidence newer than the transition clock.

## QUALITY

FAIL. The focused suite passes (`python3 -m unittest tests.test_sdd_composy_tasks`:
13 tests), but the added tests do not yet cover every Task 04 case or assert all
new metadata. They cover missing tests, blocking QA, stale verify evidence,
missing rejection reason, unjustified skip/no authority, valid completion, and
the optional no-dossier route. However, they do not cover:

- blocking or unapproved review evidence;
- rejected verification with a valid reason and assertions for
  `rejection_stage`, `rejection_reason`, and `evidence_invalidated_at`;
- a valid skipped transition with assertions for justification and authority;
- future timestamps and explicit trace inconsistency/unapproved review/verify
  predicates.

The implementation itself preserves unknown fields and atomic writes from the
earlier coverage, and no regression was observed in the focused run.

## FINDINGS

1. **[MAJOR] Required guard coverage remains incomplete.** Add focused tests
   for the omitted review/trace/verify predicates, future timestamps, valid
   rejection metadata, and valid skip metadata. The current green suite cannot
   establish the full brief's evidence matrix.

## REVIEW

`REJECTED`

The lifecycle implementation addresses the prior blockers, but round-1 review
does not approve until the missing tests and metadata assertions are added.
No HEAD movement or commit was performed.
