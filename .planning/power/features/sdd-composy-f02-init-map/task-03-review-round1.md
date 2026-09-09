# F02 Task 03 — Round 1 Review

## SPEC

PASS for the round-1 changes covered by the brief. The implementation now
parses the reserved index frontmatter, requires the exact `type`, OKF version,
`generated.by`, and ISO timestamp, checks all four installed rules, and verifies
that `.claude` is a real relative `.agents` symlink to an existing directory.
The added tests cover malformed actor metadata, missing rules, wrong link
target, a destination directory conflict, saved plan-token application,
parent-symlink rejection, and temporary-file cleanup after an injected
publication failure.

## QUALITY

CHANGES_REQUESTED. The focused suite passes all 15 tests:

```text
python3 -m unittest tests.test_sdd_composy_runtime
Ran 15 tests in 0.898s — OK
```

The new tests materially close the prior review gaps. One remaining contract
gap is in the verifier: it checks `generated.by == actor` but does not require
the OKF top-level `actor_id` field to equal the same actor. Thus an index can
declare `actor_id: another:actor` while `generated.by: human:test` passes
verification, despite initialization's actor identity being recorded in both
places.

## FINDINGS

### P1 — `verify` does not validate the top-level OKF actor ID

`plugins/sdd-composy/scripts/sdd_init.py:251-258` parses `actor_id` into
`index_meta`, but `valid_index` only checks `type`, `okf_version`,
`generated.by`, and the timestamp. It never requires
`index_meta.get("actor_id") == actor`. A modified or mixed-provenance
`tasks/index.md` can therefore be reported as valid even though its recorded
OKF actor ID disagrees with the verifier's actor.

Require the exact top-level actor field in `valid_index`, and add a negative
test that changes only `actor_id` while leaving `generated.by` unchanged.

## REVIEW

`CHANGES_REQUESTED`

Round-1 safety coverage is otherwise present and passing. Do not approve until
the verifier enforces both actor declarations in the OKF index.

HEAD was not moved and no commit was created.
