# Task 07 — independent review

SPEC: FAIL

QUALITY: FAIL

FINDINGS:

1. **Important — the documented Compose ownership record does not identify the Compose file that the launcher actually starts.** `references/fleet.md:42-45` and both READMEs say teardown stops only the exact plugin-owned Compose resource recorded in the member. However, `launch.sh:127-140` records `resources.compose_file` as `docker-compose.yml` relative to each member worktree while it copies and starts the actual file at `.planning/sdd-composy/fleet/<fleet-id>/docker-compose.yml` in the central repository. `teardown.sh:50-67` then resolves the recorded value as `$worktree/docker-compose.yml`, defaults a missing `compose_allocated` flag to `true`, and may either refuse cleanup because that unrelated path is absent or run `docker compose down` against a repository file that was never the launched fleet file. The documentation therefore overstates exact ownership and safe recovery. It must describe the current limitation, or the implementation/record must first be corrected and verified.

2. **Important — the package still advertises Hermes Kanban despite the five revised documents declaring it unavailable.** `README.md:45-48`, `README.pt-BR.md`, `references/runtime.md:27-33`, and `references/fleet.md:37-40` correctly say Hermes Kanban is not implemented. The bootstrap says it loads the documented tool mapping, but `references/hermes-tools.md:10` still maps task tracking to “Hermes task tracker or `hermes kanban`”. This contradicts the required no-promise limitation and makes the package documentation internally inconsistent. The Task 07 five-file restriction does not make the contradictory referenced document safe to publish; reconcile it before approval.

3. **Minor — `references/status.md` lists a closed set of canonical statuses that the implementation does not enforce.** The document lists only `uninitialized`, `active`, `blocked`, `divergent`, `looping`, `fleet`, and `malformed` at lines 28-30. In `sdd_status.py:59-61`, a valid global state's arbitrary schema stage is lowercased directly into `status`; when there is no active task or task bundle, values such as `init`, `map`, or `prd` remain in the result. Either document stage-derived statuses or normalize the implementation to the documented set.

Verified claims: the three provider vectors match the LOOP/fleet adapters (`claude -p`, `codex exec`, `hermes -z ... --in`); Hermes automation checks isolation or specific consent; schema v2 uses the three runtime enum values, absolute repository/worktree paths, owner, and nested resources; v1 migration is explicit, limited to Claude Code/Codex, preserves unknown fields, and publishes atomically; init distinguishes `symlink` and `existing_directory`; operational task JSON uses a nested `tasks` array and status falls back to Markdown only when the operational tasks directory is absent; status itself is read-only; the revised five files do not claim that real-provider acceptance passed.

Verification evidence:

- `python3 scripts/validate_readme_plugins.py` — PASS (`validated 16 plugins in both READMEs`).
- `python3 -m unittest tests.test_sdd_composy tests.test_readme_marketplace -v` — PASS (58 tests).
- `git diff --check ef59026..dbd05f6` — PASS.

REVIEW: REJECTED

The two Important documentation/implementation contradictions must be resolved before Task 07 proceeds. Passing README and foundation tests establish structure and selected textual contracts, not semantic correctness of Compose ownership or consistency of the Hermes tool mapping. No real Hermes, Codex, or Claude Code acceptance is claimed by the reviewed five documents or implementation report.
