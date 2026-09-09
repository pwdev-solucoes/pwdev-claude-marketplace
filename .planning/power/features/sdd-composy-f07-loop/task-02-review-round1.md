# Task 02 review — durable resume (round 1)

## Verification

`python3 -m unittest tests.test_sdd_composy_loop -v` — 14 tests passed.

The round-1 changes correctly reject backfill publication after a later
durable stage, cover resume after each publication boundary, and preserve the
existing state bytes when `os.replace` fails.

## Finding

### Important — publication does not validate the success status of prior evidence

The new pre-publication validation checks that prior completed records contain
matching artifact/evidence digests, but it does not validate that each prior
evidence object has an allowed successful status. I constructed a durable
`EXECUTE` record with a valid digest for `{"status":"failed"}`; publishing
`QA` was accepted. `resume()` would reject that state later, but the write
boundary has already advanced the loop while a failed prerequisite remains
durable. The same stage-evidence success predicate used by `resume()` must be
applied to every prior completed record before publishing the next stage.

## Disposition

**REJECTED** pending this fail-closed validation fix and a focused regression
test. The other round-1 corrections are verified and behave as required.
