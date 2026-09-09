# Task 06 report — Map skill and Claude adapter

## Status

Implemented the portable `$sdd-map` skill and `/sdd-composy:map` adapter.

## Delivered

- `plugins/sdd-composy/skills/sdd-map/SKILL.md`
  - Defines read-only scanning and the explicit `--write` publication boundary.
  - Documents the five context outputs under `.planning/sdd-composy/context/`.
  - Preserves source commit and staleness semantics from `sdd_map.py`.
  - Excludes sensitive paths, prohibits manifest command execution, and keeps
    the map observation-only.
  - Routes fresh evidence to PRD, STORIES, TECHSPEC, and TASKS; stale evidence
    returns to MAP before downstream reuse.
- `plugins/sdd-composy/skills/sdd-map/agents/openai.yaml`
- `plugins/sdd-composy/commands/map.md` as a thin Claude route.
- Structural adapter tests in `tests/test_sdd_composy.py`.

## Review follow-up

Added one shared `_validated_context` path in `sdd_map.py`. Both read-only
`build_map()` and publishing `write_map()` now reject resolved output paths
outside the repository before prior-map inspection or publication. A focused
fixture covers both modes with an invalid external prior map and verifies that
the external directory is not modified.

## Verification

`python3 -m unittest tests.test_sdd_composy tests.test_sdd_composy_runtime`

- 53 tests passed.

`python3 plugins/sdd-composy/scripts/sdd_map.py --repo-root .`

- Returned `schema: sdd-composy.codebase`.
- Returned `observation_only: true`.
- Reported source and mapped commit `acf19705da7abebbd3f445a47bc17313639c2827`.
- Reported `staleness.stale: false` without writing files.

Compilation was attempted with `py_compile`, but Python attempted to create its
cache outside the permitted worktree and the sandbox denied that directory
creation; no source error was reported.

## Commit

No commit was created because the worktree already contains other agents'
changes and the task brief requires explicit authorization before committing.
