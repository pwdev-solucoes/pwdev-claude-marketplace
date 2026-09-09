# F02 Task 01 — Governance root templates

## STATUS

PASS

## Scope

Implemented the canonical governance template pair and focused runtime contract tests:

- `plugins/sdd-composy/templates/AGENTS.md`
- `plugins/sdd-composy/templates/CLAUDE.md`
- `tests/test_sdd_composy_runtime.py`

`AGENTS.md` covers codebase structure, commands, lifecycle workflow, approval gates,
human and operational artifact roots, OKF v0.2 requirements, and safety boundaries.
`CLAUDE.md` is intentionally a short compatibility pointer to canonical `AGENTS.md`.
Both templates use explicit uppercase render variables; the tests verify a representative
render leaves no scaffold placeholders unresolved.

## Verification

```text
python3 -m unittest tests.test_sdd_composy_runtime
.....
OK
```

`git diff --check` also passed.

## COMMITS

None. No commit was created because this task brief authorizes leaving files ready but
does not explicitly authorize committing.

## NOTE

The task brief and F01 context files were available in the linked `sdd-composy` worktree;
the implementation follows those exact contracts. No secret or environment files were
read.
