# F06 integrated final review

## Scope

Read-only review of the complete F06 implementation against
`.planning/power/features/sdd-composy-f06-observability/plan.md`, all task briefs,
reports, and review rounds. The reviewed surface includes semantic events,
deterministic trace projection, trace/status/quick skills and adapters,
consolidated read-only status, the quick five-file gate, OKF templates, and the
F06 test suite.

## Verification

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_sdd_composy*.py' -q
Ran 189 tests ... OK

PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_sdd_composy_observability -q
Ran 19 tests ... OK

PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_sdd_composy -q
Ran 52 tests ... OK

PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_sdd_composy_tasks -q
Ran 32 tests ... OK

git diff --check
passed
```

## SPEC verdict

**CHANGES_REQUESTED**

The normal symlink cases are fail-closed, append-only events are validated and
preserved, projection rebuilds are deterministic and hash-bound, status remains
read-only, quick eligibility is authoritative and side-effect-free, and the
runtime adapters are thin. However, broken symlink entries are still treated as
missing in multiple read paths because `Path.exists()` is checked before
`Path.is_symlink()`:

- `sdd_trace._target()` can treat a broken `trace/` symlink as absent and return
  an empty event history instead of rejecting the unsafe directory entry;
- `sdd_status._load()` classifies broken JSON symlinks as `missing`, and
  `_records()`/`_task_summary()` similarly allow broken state/task roots to be
  reported as missing rather than unsafe or malformed.

This violates the safe-directory-traversal and fail-closed symlink contract,
even though existing-target symlink tests pass. Add lexists-style checks and
regression tests for broken trace/state/task/fleet/loop symlinks before treating
F06 as fully approved.

## QUALITY verdict

**PASS WITH MINOR FOLLOW-UP**

The deferred Task 04 quality item remains: the focused status tests do not
explicitly assert malformed JSON input and the exact `next_action` for every
canonical state. Manual smoke verification confirms malformed JSON produces the
deterministic repair action and active state preserves its configured action,
but these assertions should be promoted to regression tests in the fix round.

No files other than this review report were modified and no commit or HEAD
movement was performed.
