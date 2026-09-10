# Task 07 — documentation rereview round 1

SPEC: PASS

QUALITY: PASS

FINDINGS:

None.

The three prior findings are resolved:

- **Compose contract:** both READMEs plus `references/fleet.md` and `references/runtime.md` now describe the actual approved producer/consumer behavior: one central repository-relative file under the fleet state directory; exact `sdd_fleet_<fleet-id>` project; SHA-256 and explicit allocation flag in nested member resources; no Compose action when allocation is false; and teardown validation against repository root, ownership, path, project, digest, and symlink safety before shutdown. Successful non-merge cleanup removes the member record while preserving branch/worktree; failures preserve recovery state.
- **Hermes Kanban:** `references/hermes-tools.md` no longer advertises a task tracker or `hermes kanban`. It routes tracking to shared SDD Composy contracts/status and explicitly says Kanban integration is unavailable and must not be invoked as fallback. Repository-wide search found only the intended unavailability statements.
- **Status values:** `references/status.md` distinguishes overriding consolidated statuses from lowercase lifecycle-stage-derived values. Its examples exactly cover the `state.schema.json` stage enum lowercased by `sdd_status.py` when no task, loop, fleet, blocker, or divergence overrides it.

Verification evidence:

- `python3 scripts/validate_readme_plugins.py` — PASS (`validated 16 plugins in both READMEs`).
- `python3 -m unittest tests.test_sdd_composy tests.test_readme_marketplace -v` — PASS (58 tests).
- Dedicated relative-link/placeholder test — PASS (1 test).
- `git diff --check 70d1228..3e491f8` — PASS.

REVIEW: APPROVED

The revised documentation is consistent with the current scripts and schemas for all three reviewed findings. It continues to distinguish offline adapter coverage from real-provider acceptance and makes no claim that real Hermes, Codex, or Claude Code acceptance has passed.
