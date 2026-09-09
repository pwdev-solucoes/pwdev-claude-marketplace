# Task 05 — re-review round 1

Review range: `331c85b..0b2d6e2`
Reviewer mode: read-only; no subagents
Date: 2026-09-09

## Controller ruling

The prior Critical Compose/teardown finding is **DEFERRED_BY_RULING** to Task 06,
where `teardown.sh` is an explicit implementation file. It is load-bearing and remains
unresolved; no fleet acceptance may occur before Task 06 addresses it. It is not counted
as addressed by this re-review. The prior Minor finding was not reopened.

## Important findings

### 1. Draft 2020-12 validation of emitted pending and terminal records

**NOT ADDRESSED.**

The tests now route pending launcher records and migrated terminal records through
`assert_schema_valid`, but that function is a partial custom fixture checker, not a
Draft 2020-12 validator. A fresh adversarial reproduction supplied a member instance
with an extra property inside `owner`, despite `owner.additionalProperties: false`, and
with `resources.port: true`, despite `port` requiring an integer. The helper accepted
the invalid instance and printed `ACCEPTED_INVALID_DRAFT_INSTANCE`.

The helper does not enforce `additionalProperties` at all, and Python's
`assertIsInstance(True, int)` accepts booleans as integers. Therefore the green tests do
not prove Draft 2020-12 conformance for nested constraints. Use a conforming Draft
2020-12 validator (or make the repository validator semantically complete for every
keyword and JSON type used by this schema) and retain negative fixtures for nested
additional properties, boolean-as-integer, `$ref`, patterns, and terminal `if`/`then`.

### 2. Real v1 migration, unknown fields, and atomic replacement

**NOT ADDRESSED.**

The correction adds an explicit migration command, preserves unknown fields, rejects
unsafe relative evidence paths, writes through a same-directory temporary file, fsyncs
the file, and atomically replaces the member. Those portions are materially improved.

However, the migration's registration check accepts the initiating repository checkout
itself as a fleet member worktree. The new test deliberately uses
`worktree_path: "."`, the current base branch, and invokes migration with the repository
root; migration succeeds because the main checkout appears in `git worktree list`.
This can publish a v2 fleet member bound to the non-isolated central checkout, contrary
to the fleet member isolation/ownership contract and to the launcher, which creates a
distinct member worktree and branch. The test therefore does not reproduce migration
of a real independent legacy member; it blesses an unsafe topology. Require a registered
worktree distinct from `repository_root`, verify its exact branch, and reproduce the
migration using a real `git worktree add` member while retaining the unknown-field and
atomic-replacement assertions.

### 3. Aggregate schema-suite reconciliation

**ADDRESSED.**

The aggregate assertions now distinguish fleet-member schema v2 from the remaining v1
operational schemas, include Hermes in the fleet runtime enum, and use an absolute v2
fixture with owner/resources. Fresh combined verification completed 117 tests with no
failure.

## Fresh evidence

- `python3 -m unittest tests.test_sdd_composy_fleet tests.test_sdd_composy_fleet_runner tests.test_sdd_composy_runtime_adapters tests.test_sdd_composy -v`
  — PASS, 117 tests.
- Direct invalid-instance reproduction through `assert_schema_valid`
  — FAIL as Draft validation evidence: printed `ACCEPTED_INVALID_DRAFT_INSTANCE`.
- `bash -n plugins/sdd-composy/scripts/fleet/run.sh` — PASS.
- `git diff --check 331c85b..0b2d6e2` — PASS.
- Baseline preserved: pre-existing `tests/test_sdd_composy_hermes.py` modification and
  untracked planning bundle remain present.

## SPEC

**FAIL** for the authorized Task 05 implementation. Aggregate compatibility is fixed,
but conforming Draft 2020-12 validation and safe migration of an independent v1 member
remain unmet. The deferred Compose/teardown Critical is reported separately and is not
used as a claim that this round addressed it.

## QUALITY

**FAIL** for the authorized Task 05 implementation. The native suites are green, but
the fresh adversarial evidence shows the schema oracle accepts invalid Draft instances,
and the migration test validates a central checkout rather than an isolated member
worktree. Green coverage is therefore insufficient for the two affected contracts.

## REVIEW

**REJECTED — 1 ADDRESSED, 2 NOT ADDRESSED, 1 DEFERRED_BY_RULING.**

Task 05 should return for correction of the two remaining Important findings. Task 06
must independently close the deferred load-bearing Compose/teardown finding before any
fleet acceptance.

## Task 05 correction evidence

The two remaining Important findings are corrected: the fixture oracle now enforces the
Draft 2020-12 keywords used by these schemas, including nested `additionalProperties`,
strict integer-vs-boolean typing, `$ref`, regex patterns, and conditional `if`/`then`;
the migration rejects the initiating checkout and requires the registered independent
worktree to match the exact legacy branch. The migration test creates a real `git
worktree add` member and verifies unknown-field preservation and atomic inode replacement.

Focused verification: `python3 -m unittest tests.test_sdd_composy_fleet_runner tests.test_sdd_composy -v` — PASS, 66 tests.
