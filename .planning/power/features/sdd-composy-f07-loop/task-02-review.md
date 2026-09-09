# Task 02 review — durable resume

## Scope

Read-only review of the Task 02 brief/report and the `sdd_loop.py` durable
publication/resume implementation. Checked interruption and publication
boundaries, artifact/evidence digest binding, stage ordering, stale-state and
conflict handling, replay behavior, atomic write behavior, and symlink safety.

## Verification

`python3 -m unittest tests.test_sdd_composy_loop -v` — 11 tests passed.

An additional adversarial check reproduced an out-of-order publication: a
state file with `EVIDENCE` already marked complete was accepted by
`publish_stage(..., "EXECUTE", ...)` even though earlier stages were pending.

## Findings

### Important — `publish_stage` accepts stale out-of-order durable state

The publication guard only checks whether *preceding* records are pending:

```python
if any(r.get("status") == "pending" for r in records[:index]):
    raise LoopError(...)
```

It does not reject a state in which any later stage is already complete. An
interrupted or externally mutated state can therefore publish an earlier stage
after a later stage has already been durably recorded. `resume()` would reject
the resulting state later, but the corrupting publication has already happened,
so the write boundary itself is not fail-closed. `publish_stage` must reject
any later completed stage (and preferably validate all existing completed
records' bindings) before mutating the current record.

### Minor — required interruption matrix is not represented by the focused tests

The brief calls for interruption fixtures before/after each publication
boundary. The focused suite covers interruption before the first publication
and resume after `EXECUTE`, but does not exercise every boundary through
`QA`, `EVIDENCE`, `REVIEW`, and `VERIFY`, nor does it verify that a failed
atomic publication leaves the prior bytes unchanged. Add the matrix once the
ordering guard is corrected.

## Disposition

**REJECTED** pending correction of the Important finding and expansion of the
durable-resume test matrix. The implementation otherwise provides deterministic
artifact/evidence digests, rejects digest mutation during `resume()`, allows
same-payload idempotent replay only, uses atomic temporary-file replacement,
and rejects symlinked state paths.
