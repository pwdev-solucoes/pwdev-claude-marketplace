# Task 02 review — round 2

## Verdict

**REJECTED — pre-existing member records are not fully protected.**

## Verification

Ran `python3 -m unittest tests.test_sdd_composy_fleet -v` — 13 tests passed.
Ran `git diff --check` — passed.

The round-1 fixes correctly preserve a pre-existing `fleet.json`, member record,
and Compose file in the added combined regression test. Compose overwrite is also
refused explicitly, and generated Compose/runtime/port artifacts are removed on a
failed invocation.

## Finding

### MEDIUM — pre-existing member-only state can still be overwritten/deleted

The implementation refuses an existing `fleet.json`, but it does not refuse an
existing `members/*.json` when no `fleet.json` is present. The Python publication
loop writes `members/<task-id>.json` with `write_text`, so a task ID collision can
overwrite a pre-existing member. If the later launch fails, cleanup treats the
fleet as having no pre-existing fleet metadata and deletes all member JSON files,
including the original record. This violates preservation of recoverable fleet
state and rollback ownership.

Refuse any pre-existing member destination before publication (or snapshot and
restore exact bytes), and add a regression test with a pre-existing member but no
`fleet.json` that forces failure and asserts byte-for-byte preservation.

## Positive checks

- Lock lifetime and concurrent allocation are now correct; the two-slot race test
  passes.
- Existing `fleet.json` and Compose metadata are preserved/refused.
- Existing runtime env is never adopted.
- Generated environment is mode `0600`.
- Invalid/occupied ranges, symlink safety, Compose absence, and generated-state
  rollback pass.
