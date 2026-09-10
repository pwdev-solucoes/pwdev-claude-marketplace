# Task 07 — implementation report

STATUS: DONE

## Scope

Updated only the five authorized plugin documentation files. The documentation now matches
the implemented Claude Code, Codex, and Hermes entry points and command vectors; replaces the
obsolete `hermes run` claim with `hermes -z <prompt> --in <worktree>`; and states that fleet
can start provider/UI processes after validation while the shared runner owns lifecycle truth.

The revised contracts document validated JSON as operational authority, nested task bundles,
explicit legacy fleet v1 migration and diagnosis, `symlink` versus `existing_directory` init
compatibility, governance language boundaries, status read-only semantics, mandatory worktree
isolation, nested Compose ownership and recovery behavior, and the absence of provider
fallback. Hermes Kanban is explicitly unavailable because it is not implemented.

Installed adapter support and offline regression coverage are separated from real-provider
acceptance. No real Hermes, Codex, or Claude Code acceptance is claimed before Task 08.

## Verification

- `python3 scripts/validate_readme_plugins.py` — PASS, 16 plugins validated without warnings.
- `python3 -m unittest tests.test_sdd_composy tests.test_readme_marketplace -v` — PASS, 58 tests.
- `python3 -m unittest tests.test_sdd_composy_fleet tests.test_sdd_composy_loop -q` — PASS,
  81 tests in 21.326s.
- `git diff --check` — PASS.

The first requested test run exposed one legacy textual expectation (`must not depend`) after
the runtime reference was rephrased. The wording was restored without changing semantics and
the complete requested command then passed.

## Traceability note

The Task 06 focused command discovers and executes 81 tests in the current repository. The
earlier value 88 was an estimate in the original brief, not observed test evidence. This report
retains 81 as the measured count and does not invent the seven absent tests or reinterpret the
estimate as a pass.

## Review

Semantic inspection checked the documented commands and paths against `sdd_init.py`,
`sdd_status.py`, the three LOOP/fleet engine adapters, `launch.sh`, `run.sh`, and `teardown.sh`.
Relative Markdown links are covered by the passing foundation test. Task 08 remains responsible
for real-provider acceptance.
