# Task 05 — implementation report

Status: IMPLEMENTED
Date: 2026-09-09

## Scope and baseline

Implemented only the five declared Task 05 files. Before execution,
`tests/test_sdd_composy_hermes.py` was already modified and the planning bundle was untracked;
both were preserved and excluded from the implementation commit.

## TDD evidence

- RED: the focused regressions failed because emitted records lacked the v2 required fields,
  prepare-only accepted a missing runtime, rollback retained the registered worktree/branch,
  Compose resolved the wrong template level, and the runner defaulted to Codex.
- A second RED proved that a symlinked `.planning` ancestor allowed external state writes.
- GREEN: `python3 -m unittest tests.test_sdd_composy_fleet tests.test_sdd_composy_fleet_runner -v`
  passed 52 tests.
- Adjacent regression: adding `tests.test_sdd_composy_runtime_adapters` passed 60 tests.
- Static verification: `bash -n` for `launch.sh` and `run.sh`, plus `git diff --check`, passed.

## Result

- Fleet member schema v2 records `claude-code`, `codex`, or `hermes`, canonical absolute
  worktree/repository paths, canonical lifecycle status, timestamps, and explicit owner/resources.
- Launcher requires an explicit supported runtime even in prepare-only mode, normalizes only
  `claude` to `claude-code`, rejects unsafe state ancestors and non-exact Git roots before mutation,
  publishes JSON atomically, and resolves Compose from `HERE/../../templates`.
- Failure rollback uses the real created worktree/branch lists and removes both registrations and
  branches; empty Bash arrays no longer abort cleanup under nounset mode.
- Runner has no runtime fallback, maps `claude-code` back to the `claude` adapter only for CLI
  selection, rejects legacy records with an explicit migration diagnostic, and binds metadata to
  the exact Git repository/worktree before invoking a provider.

## Review round 1

Status: IMPORTANT_FIXED; CRITICAL_DEFERRED_BY_RULING; MINOR_NOT_TREATED.

- Replaced required-key/enum spot checks with the repository's dependency-free Draft 2020-12
  fixture validator. Launcher-produced pending records for all three runtimes now exercise `$ref`,
  nested constraints and types; a wrong nested port type is rejected.
- Added a real schema-v1 fixture and explicit `run.sh --migrate-member MEMBER.json --root ROOT`.
  The ordinary runner rejects the same record before provider dispatch. Migration requires a
  controlled central member path, exact Git root, registered worktree/branch, explicit runtime,
  UI, port and Compose ownership, and complete terminal evidence. It preserves unknown fields and
  uses fsync plus atomic replacement.
- The migration regression emits and validates v2 records for `completed`, `failed`, `blocked`
  and `cancelled`; atomic replacement and unknown-field preservation are asserted.
- Reconciled the two aggregate schema assertions under the explicit ledger ruling: fleet member
  uses schema v2 and the runtime enum includes Hermes.
- Fresh combined verification passed 117 tests:
  `tests.test_sdd_composy_fleet`, `tests.test_sdd_composy_fleet_runner`,
  `tests.test_sdd_composy_runtime_adapters`, and `tests.test_sdd_composy`.
- The Compose teardown Critical remains assigned to Task 06 by ledger ruling; `teardown.sh` was not
  changed. The stale-comment Minor was not treated.
