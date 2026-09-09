# Task 02 report — durable resume

## Result

Implemented durable loop-stage publication and resume in `sdd_loop.py`.
Loops now persist the ordered EXECUTE → QA → EVIDENCE → REVIEW → VERIFY
stage ledger. Each completed stage atomically records its artifact, evidence,
publication timestamp, and deterministic content digests. Re-publication is
idempotent only for the same payload; conflicting or stale state fails closed.

`resume()` validates every durable boundary and returns the exact next
incomplete stage without replaying completed stages. Stage publication requires
a successful evidence status and all preceding stages to be complete.

## Verification

`python3 -m unittest tests.test_sdd_composy_loop` — 11 tests passed.

`git diff --check` — passed.

Coverage includes interruption before publication, successful durable resume,
artifact/evidence binding, stale-state mutation, stage ordering, and replay
protection.

No commit was created.

## Round 1 correction

`publish_stage()` now rejects any backfill when a later stage is already
durably complete and validates prior stage bindings before mutation. Added the
full interruption matrix after EXECUTE, QA, EVIDENCE, REVIEW, and VERIFY, plus
a failure-injection test proving failed atomic publication preserves the prior
state bytes.

`python3 -m unittest tests.test_sdd_composy_loop -v` — 14 tests passed.

## Round 2 correction

Later-stage publication now requires every prior completed stage to carry an
explicit successful evidence status (`passed`, `approved`, `complete`, or
`ok`). Failed or blocked prior evidence is rejected before mutation. Added a
regression test proving the persisted bytes remain unchanged on this failure.

`python3 -m unittest tests.test_sdd_composy_loop -v` — 15 tests passed.
