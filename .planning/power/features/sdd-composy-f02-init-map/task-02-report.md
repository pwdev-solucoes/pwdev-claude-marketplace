# F02 Task 02 — Rule templates

## STATUS

PASS

## Scope

Added the four segmented `.agents/rules` templates and linked them from canonical
`AGENTS.md`: the rule index, architecture, testing, and workflow responsibilities.
The rules are concern-specific and defer repository-wide governance to `AGENTS.md`.
Added focused discovery and responsibility contract tests, including the failing-first
run before implementation.

Round 1 review remediation strengthens the tests to parse exact Markdown destinations,
resolve rule links against an installed `.agents/rules/` layout, require unique
responsibility markers, and reject cross-responsibility duplication.

Round 2 review remediation now builds a temporary installed layout with real canonical
and rule files, asserts every resolved target exists and is the canonical file, and
checks explicit owner-only policy phrases for architecture, testing, and workflow.

## Verification

`python3 -m unittest tests.test_sdd_composy_runtime` — 7 tests passed.

`git diff --check` passed. No secret or environment files were read.

## Commit

Not created: Git could not create the shared worktree index lock
(`.git/worktrees/sdd-composy/index.lock`, operation not permitted).
