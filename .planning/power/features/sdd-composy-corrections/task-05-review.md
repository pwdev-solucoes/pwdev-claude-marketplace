# Task 05 — review

Review range: `02a1ad8..331c85b`
Reviewer mode: read-only implementation review; no subagents
Date: 2026-09-09

## SPEC

FAIL.

The focused launcher/runner suite passes, and the implementation adds explicit runtime
selection, Hermes normalization, v2 fields, canonical repository/worktree binding,
symlink rejection, distinct allocations, and rollback of real Git worktrees/branches.
However, Compose ownership is not wired through to teardown, v1 migration behavior is
not exercised or implemented beyond rejection, emitted records are not actually
validated against the JSON Schema, and the existing aggregate schema contract is left
red.

## QUALITY

FAIL.

Fresh evidence:

- `python3 -m unittest tests.test_sdd_composy_fleet tests.test_sdd_composy_fleet_runner -v`
  — PASS, 52 tests.
- `python3 -m unittest tests.test_sdd_composy_runtime_adapters -v`
  — PASS, 8 tests.
- `python3 -m unittest tests.test_sdd_composy -v`
  — FAIL, 56 tests run, 2 failures:
  `test_fleet_runtime_ui_and_terminal_enums` and
  `test_operational_schemas_are_versioned_and_extension_safe`.
- `bash -n plugins/sdd-composy/scripts/fleet/launch.sh plugins/sdd-composy/scripts/fleet/run.sh`
  — PASS.
- `git diff --check 02a1ad8..331c85b` — PASS.
- Baseline remained present after review: pre-existing
  `tests/test_sdd_composy_hermes.py` modification and the untracked planning bundle.
- No provider was invoked, no real task/branch was changed, and no project file was
  modified except this required review artifact.

## FINDINGS

### Critical

1. Compose resources cannot be torn down from the v2 record. The launcher writes
   `resources.compose_project` and `resources.compose_file` and copies the Compose file
   to the central fleet state directory (`launch.sh:128`, `launch.sh:138`). The existing
   teardown reads only top-level `compose_file`/`compose_project` and resolves the file
   under the member worktree (`teardown.sh:48-53`). Consequently a v2 member emitted by
   this launcher skips `docker compose down`, then non-merge teardown removes member
   metadata (`teardown.sh:57`), orphaning the owned Compose project and losing the exact
   resource binding needed for recovery. The new test only inspects source text and two
   nested fields; it never starts or tears down Compose (`test_sdd_composy_fleet.py:65-73`).

### Important

1. The claimed schema-validation test does not validate emitted JSON against Draft
   2020-12. It manually checks required-key presence, one enum membership, and selected
   values (`test_sdd_composy_fleet.py:32-43`). It does not evaluate `$ref`, types,
   patterns, `if`/`then`, nested owner/resources constraints, or terminal-state required
   fields. The runtime paths also perform selected `jq` predicates rather than validate
   the full member schema. This does not satisfy the requirement to validate JSON
   actually emitted by the launcher against the schema, including terminal states.

2. The legacy-v1 requirement has no effective migration coverage. `run.sh:103` only
   rejects every non-v2 record with a generic diagnostic. The test named
   `test_missing_runtime_and_legacy_member_require_migration` exercises only a missing
   environment variable against `/tmp/no-such-worktree`; it never constructs, reads, or
   migrates a v1 member (`test_sdd_composy_fleet_runner.py:41-44`). Repository search
   found no fleet-member migration implementation. Thus preservation of unknown fields,
   pre-migration diagnosis, and a controlled v1-to-v2 path remain unproven.

3. The change leaves the repository's aggregate schema suite red. The two failures are
   direct incompatibilities between the v2/Hermes contract and the still-authoritative
   aggregate assertions in `tests/test_sdd_composy.py:702,720-723`. Recording this as a
   compatibility note does not make fresh failing verification evidence acceptable.
   The schema evolution and its tests must be reconciled before approval.

### Minor

1. The comment at `run.sh:14` says `EXPECTED_RUNTIME` is constrained to
   `codex|claude`, while the accepted persisted values are `codex|hermes|claude-code`.
   This is stale and makes the adapter boundary harder to audit.

## REVIEW

REJECTED.

The focused behavior is directionally correct, but the Critical Compose ownership leak
and the Important validation/migration/regression gaps block Task 05 from proceeding.
Required correction: make teardown consume and verify the exact nested v2 resources
and central Compose path; add real schema validation for emitted pending and terminal
records; add an actual v1 fixture and explicit migration/diagnostic path that preserves
unknown fields atomically; reconcile the aggregate schema suite; then rerun focused,
adapter, aggregate, symlink, two-member, binding, Compose, and rollback tests with fresh
evidence.
