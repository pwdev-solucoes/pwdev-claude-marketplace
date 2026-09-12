# Task 08 — Restore root README contracts

## Context

The user approved expanding the quality-gates work to repair the two root README files after the
full suite exposed regressions introduced by commit `c9a5524`.

## Scope

Modify exactly:

- `README.md`
- `README.pt-BR.md`

Do not modify tests, manifests, plugin-local READMEs, or implementation files.

## Root cause and required behavior

The compact marketplace README redesign removed machine-checked structures and the public dual
runtime examples. Restore them without discarding the newer concise introduction:

1. Every plugin shipped by `.claude-plugin/marketplace.json` has a table row matching the regex in
   `tests/test_marketplace_readmes.py`, including the exact manifest version.
2. Every shipped plugin has a `### <plugin-name>` section, its own
   `claude plugin install <plugin-name>@pwdev-claude-marketplace` command, a link containing
   `./plugins/<plugin-name>/`, and an inventory line whose counts/features match the filesystem.
3. Both translations cover the same plugin set.
4. Both READMEs document `pwdev-flow`, contain literal examples using `claude -p` and `codex exec`,
   and mention every public command asserted by
   `ClaudeCompatibilityTests.test_public_docs_describe_dual_runtime_commands`.
5. Preserve clear English in `README.md` and Brazilian Portuguese in `README.pt-BR.md`.

Use `git show c9a5524^:README.md` and its Portuguese counterpart as known-good structural patterns,
but reconcile all inventory and versions with the current tree. Make the smallest coherent change.

## RED evidence

The following tests fail before this task because the required structures are missing:

```sh
python3 -m unittest \
  tests.test_flow_claude_compat.ClaudeCompatibilityTests.test_public_docs_describe_dual_runtime_commands \
  tests.test_marketplace_readmes.TestMarketplaceCoverage
```

## Verification

Run the RED command after editing and confirm it passes. Also run:

```sh
python3 -m unittest tests.test_readme_marketplace
```

Commit only the two scoped README files. Write the implementation report to
`.planning/power/features/quality-gates-skills/task-08-report.md` with the standard short status,
tests run, and commit range.
