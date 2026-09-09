# Task 04 review

## Disposition

**REJECTED — important findings remain.**

## Verification

Ran:

```text
python3 -m unittest tests.test_sdd_composy_observability -v
```

Result: 12 tests passed, but these are trace-only tests. No consolidated-status
contract tests were added for the required uninitialized, active, blocked,
divergent, looping, fleet, malformed, JSON/text, and byte-level no-write
scenarios.

## Findings

1. **Important — required Task 04 test matrix is absent.** The brief explicitly
   requires failing tests and focused coverage for every status and no-write
   behavior. `tests/test_sdd_composy_observability.py` imports only `sdd_trace`
   and contains no `sdd_status` tests. The implementation therefore has no
   regression protection for its public contract.

2. **Important — malformed task sources are silently discarded.**
   `_task_summary()` catches malformed Markdown/front matter and continues,
   while `status()` reports the tasks source as `missing` when no valid task was
   retained, or `valid` when at least one valid task remains. A malformed task
   can therefore produce `active`/`uninitialized` instead of the required
   fail-closed `malformed` status, and its source confidence is inaccurate.
   Symlink task files are also skipped rather than surfaced as an unsafe or
   malformed source. The task scanner needs to return both summaries and a
   source state (and status must include that state in malformed aggregation).

3. **Medium — the malformed-source behavior is not demonstrated at the CLI
   boundary.** The brief requires read-only text/JSON output and exact next
   action. There are no assertions that `main --json` is valid deterministic
   JSON, that text output is readable, or that either mode leaves all source
   bytes unchanged.

## Required follow-up

Add focused status tests and fix task-source aggregation before approval. At
minimum cover all canonical statuses, malformed JSON/Markdown and unsafe
symlinks, source confidence/state, exact `next_action`, both output modes,
determinism, and a byte-for-byte snapshot of all inputs before/after status.
