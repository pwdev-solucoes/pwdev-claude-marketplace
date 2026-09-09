# F07 Task 04 — Runtime engines

## STATUS

PASS

## Scope

Added dedicated Codex and Claude Code runtime adapters with fixed provider command
vectors, repository-root working-directory isolation, a minimal deterministic
environment, timeout and non-zero exit handling, and strict validation of the
loop result contract. Added the portable `loop-result.schema.json` contract
requiring exactly `stage`, `status`, `message`, `verdict`, and `evidence`.

Focused tests cover vector shape and provider isolation, malformed and invalid
results, non-zero exits, and runtime timeouts.

## Verification

`python3 -m unittest tests.test_sdd_composy_loop` — 21 tests passed.

`git diff --check` passed.

No commit created; commit authority was not requested for this subtask.
