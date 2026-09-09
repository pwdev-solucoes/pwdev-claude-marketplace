# Task 03 — User-story contract and skill implementation report

Status: DONE
Sources: `.planning/power/features/sdd-composy-f03-product/task-03-brief.md`,
`.planning/power/features/sdd-composy-f03-product/plan.md`, approved
`plugins/sdd-composy/templates/prd.md`, and
`plugins/sdd-composy/references/product.md`
Date: 2026-09-08

## Delivered

- Added the OKF v0.2 `STORIES` template with consumed-source provenance,
  generated actor/timestamp, lifecycle state, one pending human approval field,
  and verified gate events.
- Added actors, journeys, stable unique `US-NNN` and `SC-NNN` examples, RF/CA
  links, dependencies, and edge-case contracts.
- Defined the applicability gate: stories are required for user-facing behavior
  and externally consumed APIs; `NOT_APPLICABLE` is limited to pure internal
  work with a specific justification and an explicit human-recorded decision.
- Added the portable `$sdd-stories` skill and Codex metadata. The skill consumes
  an explicitly approved `prd.md`, required `domain.md`, and optional
  `project.md`, writes only `tasks/prd-<slug>/stories.md`, and blocks downstream
  work until a human resolves the gate.
- Added product tests covering actors, journeys, US/SC uniqueness, RF/CA links,
  dependencies, edge cases, OKF provenance/lifecycle, applicability, upstream
  inputs, and explicit human approval.

## TDD evidence

RED: `python3 -m unittest tests.test_sdd_composy_product` ran 10 tests and
failed the five new story-contract tests because the template, reference,
skill, and metadata did not exist.

GREEN: `python3 -m unittest tests.test_sdd_composy_product` passed 10 tests.

Regression: `python3 -m unittest tests.test_sdd_composy` ran 36 tests with one
expected sequencing failure: the shared registration check reports
`sdd-stories` without a Claude adapter. The adapter belongs to approved Task 04
and is outside this task's file scope. Full discovery ran 67 tests with the same
single failure and no additional regression.

## Commit

No commit was created because the brief permits committing only with explicit
authorization, and none was provided. Existing unrelated and prior-task
worktree changes were preserved.

## Review round 1

- Strengthened the actor/journey product test to inspect every template entry rather than
  only checking headings. Every actor must include goal, context, capabilities, and
  constraints; every journey must include trigger, ordered interaction, outcome,
  participating actors, and applicable story links.
- Updated `Actor-002` and `Journey-002` so both examples satisfy the complete normative
  shapes in `references/stories.md`, including the alternate or recovery path for the
  second journey.
- RED: the focused actor/journey test failed two subtests on the expected omissions:
  `Actor-002` lacked `goal`, and `Journey-002` lacked `trigger`.
- GREEN: `python3 -m unittest tests.test_sdd_composy_product` passed all 10 tests.
- Structural regression remains 35/36 with only the planned Task 04 adapter-registration
  failure for `sdd-stories`; no new structural regression was introduced.

## Review round 2

- Extended the all-entry journey assertion so every journey must explicitly include an
  alternate or recovery path, matching the normative story reference.
- Confirmed both `Journey-001` and `Journey-002` already include the required recovery or
  alternate path guidance; no template correction was necessary in this round.
- `python3 -m unittest tests.test_sdd_composy_product` passed all 10 tests.
- `git diff --check` passed.
