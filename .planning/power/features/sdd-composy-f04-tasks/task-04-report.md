# Task 04 report

Implemented evidence and completion guards in `plugins/sdd-composy/scripts/sdd_tasks.py`.

- Evidence records are explicit under `task.evidence` for `tests`, `qa`, `review`, `verify`, and `trace`.
- RFC3339 timestamps are required and must be no newer than the transition clock and no older than the projection timestamp.
- QA blocking, missing or failed tests, unapproved review/verification, and inconsistent trace evidence reject progression.
- `complete` requires all five fresh predicates; `skipped` requires a non-empty justification.
- Task03 legal transitions, unknown fields, and atomic writes remain preserved.

Review-round fixes add 3 evidence-focused tests (13 total): stale/missing evidence,
blocking QA, rejection, valid completion, fresh timestamp boundary, skip authority,
and the `evidence_required: false` QA-to-review route. Rejections now require a
reason and record producing stage plus invalidation timestamp; skips require explicit
human authority and justification.

Round-2 coverage additionally proves rejected/unapproved review, inconsistent trace,
rejected verification, future timestamps, and valid rejection/skip metadata.

Focused verification: `python3 -m unittest tests.test_sdd_composy_tasks` (15 tests passed).
