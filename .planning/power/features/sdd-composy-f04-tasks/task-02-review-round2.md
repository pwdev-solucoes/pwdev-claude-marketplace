# Task 02 review — round 2

STATUS: rejected

## SPEC

The new runtime fixtures exercise import, load/list/show-equivalent reads, merge
preservation, deterministic serialization, unsafe output/symlink rejection, ISO
validation, and temporary cleanup. Task 03 lifecycle transitions remain out of
scope.

## QUALITY

Focused tests pass: `python3 -m unittest tests.test_sdd_composy_tasks` (6 tests).
The repository-bound output check, unknown-field merge, atomic replacement cleanup,
and deterministic JSON behavior are materially improved.

## FINDINGS

1. **P2 — timestamp validation still does not match the F01 JSON schema.**
   `datetime.fromisoformat()` accepts date-only values (for example
   `2026-01-01`) and naive timestamps without a timezone, while
   `schemas/tasks.schema.json` declares `format: date-time` (RFC3339 date-time).
   Thus `load`, `list`, and `show` can accept persisted state rejected by the
   published schema. Require a `T` time component and `Z` or an explicit offset,
   with a strict regex/date parse; add fixtures for both invalid forms.

2. **P2 — deterministic test is time-sensitive.** The test compares two imports
   and passes only while both generated timestamps fall in the same second. A
   boundary crossing can fail despite identical inputs. Freeze the clock or compare
   canonical payloads after normalizing `updated_at`.

## REVIEW

Task 02 remains not approved. Fix strict RFC3339 validation and stabilize the
determinism test, then request final review. No Task 03 work is required.
