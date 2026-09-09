# Task 01 — Review

## Verdict

- SPEC: FAIL
- QUALITY: FAIL
- Findings: 1 critical, 1 important, 0 minor

## Scope reviewed

- Brief: `.planning/power/features/sdd-composy-f04-tasks/task-01-brief.md`
- Implementation report: `.planning/power/features/sdd-composy-f04-tasks/task-01-report.md`
- Plan/contracts: `.planning/power/features/sdd-composy-f04-tasks/plan.md`, `plugins/sdd-composy/schemas/tasks.schema.json`
- Implementation: `plugins/sdd-composy/templates/{tasks,task}.md`, `plugins/sdd-composy/references/tasks.md`
- Focused tests: `tests/test_sdd_composy_tasks.py`

## Findings

### Critical — per-task template cannot produce schema-valid task contracts

`plugins/sdd-composy/schemas/tasks.schema.json` requires every task to contain
`evidence_required` (boolean), and `references/tasks.md` explicitly repeats that
contract. `templates/task.md` has no `evidence_required` field in its frontmatter or
task block. A contract rendered from the shipped template therefore fails the existing
tasks schema and cannot participate in the later evidence/completion gates. Add an
explicit boolean placeholder/default and cover it with the focused structural test.

### Important — test traceability is asserted only as an unlinked placeholder

The brief requires RF/US/SC/CA/test links. The template body contains
`TEST-001` but only says “link the test that proves CA-001”; it does not provide a
repository-relative Markdown link or a concrete test path/anchor. This weakens the
required traceability contract and leaves generated tasks without a mechanically
reviewable test link. Provide a link placeholder (and define its expected shape in the
reference), then assert it in the focused test.

## Verification

`python3 -m unittest tests.test_sdd_composy_tasks` passes (3 tests), but the tests are
too weak to detect either finding: they do not check `evidence_required` or a linked
test target. No implementation files were changed by this review.

## Required follow-up

Update only the Task 01 contract/template/test scope to add the missing schema field and
explicit test-link shape, then rerun the focused suite and repeat review. Do not mark
Task 01 complete until generated task contracts are schema-valid and all requested trace
links are concrete.
