# F07 Integrated Re-review — Round 1

## Verification

```text
python3 -m unittest discover -s tests -p 'test_sdd_composy*.py' -q
Ran 220 tests ... OK

python3 -m unittest tests.test_sdd_composy_loop -q
Ran 28 tests ... OK

python3 -m unittest tests.test_sdd_composy tests.test_sdd_composy_tasks -q
Ran 85 tests ... OK

git diff --check
passed
```

## Re-review findings

The two prior findings are corrected:

- Orchestrated safety decisions now preserve the exact reason in `status` and
  `stop_reason`, including scope, architecture, destructive, repeated
  environment, and no-progress classifications.
- Runtime engine exceptions now terminate as `environment_failure`, with a
  stable `next_action`; no task/trace events are emitted and no stage is marked
  complete.

### Important — `third_rejection` is emitted after the second rejection

`orchestrate()` initializes `rejections` to zero and increments it before
calling `correction_decision()`. The decision uses `rejection_count >= 2`, so
the second rejected runtime result is classified as `third_rejection`. The
F07 plan requires stopping on the third rejection, and the durable state should
allow two bounded rejected corrections before that terminal reason. Existing
tests cover direct classification with an explicit count but do not exercise
the orchestrated two-versus-three rejection boundary.

## Disposition

**SPEC/QUALITY: REJECTED pending correction.**

The corrected findings are verified, but the rejection counter off-by-one must
be fixed and covered by an orchestrator integration test before F07 approval.
