# Task 03 — Runtime engines and runner

## Result
Implemented dedicated Codex and Claude fleet runtime adapters and a provider-neutral runner.

- Fixed provider command vectors are isolated in `engine-codex.sh` and `engine-claude.sh`.
- Dangerous-mode flags are explicit and runtime-specific.
- Runner validates runtime, member/worktree binding, contract identity, structured results, fresh artifacts, and process-group ownership.
- Provider groups are terminated and ownership is checked before cleanup continues.
- Invalid/malformed results fail closed; contract changes and missing artifacts halt execution.
- Correction loop is capped and terminal state is published only after verification.

## Verification
`python3 -m unittest tests.test_sdd_composy_fleet_runner -v` — 4 tests passed.
`bash -n plugins/sdd-composy/scripts/fleet/engine-codex.sh plugins/sdd-composy/scripts/fleet/engine-claude.sh plugins/sdd-composy/scripts/fleet/run.sh` — passed.
`git diff --check` — passed.

No commit created.

## Round 1 follow-up
- Aligned runner adapter discovery with the canonical `engine-{runtime}.sh` files.
- Added support for launch's fleet-id-scoped member records and canonicalized recorded worktree paths.
- Corrected schema discovery to `schemas/fleet-result.schema.json` and ensured phase contract directories are initialized before safety validation.
- Added a valid registered-worktree integration test proving the provider vector is reached and runner cleanup releases its lock after provider failure.
- `python3 -m unittest tests.test_sdd_composy_fleet_runner -v` — 5 tests passed.
- `bash -n plugins/sdd-composy/scripts/fleet/engine-codex.sh plugins/sdd-composy/scripts/fleet/engine-claude.sh plugins/sdd-composy/scripts/fleet/run.sh` — passed.
- `git diff --check` — passed.

## Round 2 follow-up
- Removed fabricated `Status: APPROVED` contract fallback; missing or unsafe `spec.md`/`decisions.md` now fails closed before provider execution.
- Integration fixture now creates real approved contracts and binds their SHA-256 hashes in the member record.
- Provider fixture launches a descendant process; the runner terminates the owned process group and the test verifies no orphan remains.
- `python3 -m unittest tests.test_sdd_composy_fleet_runner -v` — 5 tests passed.
- `bash -n plugins/sdd-composy/scripts/fleet/*.sh` and `git diff --check` — passed.
