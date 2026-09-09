---
type: REVIEW
title: "Task 07 — Quick adapter and integrated validation review, round 1"
task_id: TASK-007
status: CHANGES_REQUESTED
generated:
  by: codex:f06-task07-review
  at: 2026-09-09T00:00:00Z
sources:
  - resource: .planning/power/features/sdd-composy-f06-observability/task-07-brief.md
  - resource: .planning/power/features/sdd-composy-f06-observability/task-07-report.md
  - resource: plugins/sdd-composy/skills/sdd-quick/SKILL.md
  - resource: plugins/sdd-composy/commands/quick.md
  - resource: plugins/sdd-composy/skills/sdd-quick/agents/openai.yaml
  - resource: tests/test_sdd_composy_tasks.py
  - resource: tests/test_sdd_composy.py
  - resource: tests/test_sdd_composy_observability.py
---

# Review

## Verification performed

- `python3 -m unittest tests.test_sdd_composy_tasks.QuickBehaviorIntegrationTest tests.test_sdd_composy.SddComposyQuickAdapterTest tests.test_sdd_composy_observability.QuickContractTest` — 8 passed.
- `python3 -m unittest discover -s tests -p 'test_sdd_composy*.py'` — 189 passed.
- `git diff --check` — passed.

The new tests now exercise real `sdd_tasks.import_tasks`/`transition` behavior for normal
`TASK-*` registration and completion guards. The thin Claude route and Codex metadata remain
discoverable and runtime-neutral.

## Finding

### Important — escalation test is still a local test mirror, not the public quick route

`QuickBehaviorIntegrationTest.test_over_boundary_or_unknown_verification_escalates_before_edit`
calls `_quick_gate`, a helper implemented inside the test itself (lines 17–22), rather than a
production `sdd-quick` API, command entry point, or parser. Consequently the test will pass
even if the portable skill/adapter stops enforcing escalation entirely; it only proves that the
test's duplicate predicate returns `ESCALATE`. The quick command is intentionally a thin
Markdown route, so this repository needs either a documented executable/runtime-neutral quick
gate that the test invokes, or a structural contract test that proves the adapter delegates to
an authoritative gate without duplicating policy. Until that boundary is connected to the
implementation under test, the brief's required escalation integration evidence is not met.

The valid task registration and completion-refusal tests are otherwise adequate for their
respective public task API paths.

## Disposition

`CHANGES_REQUESTED`: add a production/public quick eligibility surface (or equivalent
authoritative contract function) and test the five-file, architecture, and unknown-verification
cases through it. Preserve the thin adapter and re-run the structural, task, and observability
suites.
