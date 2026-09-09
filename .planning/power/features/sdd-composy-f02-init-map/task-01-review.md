# F02 Task 01 — Review

## SPEC

Scope reviewed:

- `.planning/power/features/sdd-composy-f02-init-map/plan.md`
- `.planning/power/features/sdd-composy-f02-init-map/task-01-report.md`
- `plugins/sdd-composy/templates/AGENTS.md`
- `plugins/sdd-composy/templates/CLAUDE.md`
- `tests/test_sdd_composy_runtime.py`
- F01 contracts in `.planning/power/features/sdd-composy-f01-foundation/plan.md` and
  `.planning/power/features/sdd-composy/spec.md`

The implementation covers the requested governance-root template pair. `AGENTS.md`
contains the required Codebase, Commands, Workflow, Gates, Artifacts, and Safety
sections; `CLAUDE.md` is a short pointer to the canonical file. The templates expose
the expected uppercase render variables (`PROJECT_NAME`, `SOURCE_COMMIT`,
`GENERATED_AT`, `ACTOR_ID`, `STACK_SUMMARY`, and `COMMANDS`) and align with F01's
dual artifact roots, lifecycle, OKF v0.2, approval, and safety contracts. The
`<slug>`/`<prd-slug>` strings are path-pattern notation in the contract, not runtime
render variables.

## QUALITY

Verification performed:

```text
python3 -m unittest tests.test_sdd_composy_runtime
.....
OK

git diff --check
```

The focused suite has five useful contract tests and confirms the required headings,
canonical Claude pointer, representative variable substitution, F01 workflow/artifact
markers, and explicit safety language. No commit, branch movement, or external
mutation was performed.

## FINDINGS

### [P2] Render test does not reject undeclared placeholder forms

File: `tests/test_sdd_composy_runtime.py` (rendering test, approximately lines 45–57)

The post-render assertion only matches `{{[A-Z][A-Z0-9_]*}}`. A future template
placeholder such as `{{project_name}}`, `{{UNKNOWN-VAR}}`, or another non-uppercase
form would survive the test even though it violates the explicit-render-variable and
no-unresolved-placeholder contract. The test also does not compare the remaining
placeholder set against the declared variable set. Tighten the assertion to reject
any `{{...}}` token after replacement (while retaining the existing explicit-variable
check), or validate the complete placeholder set before and after rendering.

This is a test-quality gap; the current templates have no unresolved uppercase
scaffold variables after the representative substitution.

## REVIEW

Verdict: `CHANGES_REQUESTED`

The template content itself is aligned with the stated F01/F02 contract and the
focused tests pass, but the required rendering guarantee is not fully protected by
the test suite. Address the P2 test gap, then rerun the focused suite and `git diff
--check`.
