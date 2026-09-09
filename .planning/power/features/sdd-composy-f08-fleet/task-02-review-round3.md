# Task 02 review — round 3

## Verdict

**REJECTED — publication is not transactional during multi-task preflight.**

## Verification

Ran `python3 -m unittest tests.test_sdd_composy_fleet -v` — 14 tests passed.
Ran `git diff --check` — passed.

The requested member-destination refusal and member-only preservation regression
now pass. Existing fleet/member/Compose artifacts are protected in the covered
single-collision scenarios, and lock/race tests remain green.

## Finding

### MEDIUM — partial member publication can occur before a later collision

The Python publication loop checks and writes each member sequentially:

```python
for r in records:
    destination = out / (r['id'] + '.json')
    if destination.exists() ...: raise ...
    destination.write_text(...)
```

If a multi-task launch has a new first member and a pre-existing second member,
the first record is written before the second collision is discovered. The launch
process exits while the cleanup trap has not yet been installed (the trap is set
only after the Python block), leaving an orphaned new member record. Preflight all
member destinations before writing any record, or install ownership-aware cleanup
before publication and test this mixed collision case.

## Positive checks

- Lock lifetime and two-slot concurrent allocation pass.
- Invalid/occupied ports, existing runtime refusal, mode `0600`, Compose isolation,
  Compose overwrite refusal, and byte-level rollback preservation pass.
