---
type: TASK
okf_version: "0.2"
sources:
  - resource: "tasks/prd-{{SLUG}}/prd.md"
  - resource: "tasks/prd-{{SLUG}}/stories.md"
  - resource: "tasks/prd-{{SLUG}}/techspec.md"
generated:
  by: "{{ACTOR_ID}}"
  at: "{{GENERATED_AT}}"
lifecycle:
  status: DRAFT
human_approval: PENDING
verified: []
task:
  id: TASK-001
  state: pending
  dependencies: []
  allowed_paths: ["path/to/file"]
  acceptance_criteria: [CA-001]
  verification_commands: ["python3 -m unittest"]
  evidence_required: true
---

# TASK-001 — {{TASK_TITLE}}

## Intent

Describe the implementation outcome and link the approved requirement(s): [RF-001](../prd-{{SLUG}}/prd.md#rf-001), story [US-001](../prd-{{SLUG}}/stories.md#us-001), scenario [SC-001](../prd-{{SLUG}}/stories.md#sc-001), and acceptance criterion [CA-001](../prd-{{SLUG}}/stories.md#ca-001).

## Dependencies

- `TASK-000` — dependency title, or `None` when independent.

Dependencies must be complete before this task may become `ready`; IDs remain stable once
approved.

## Allowed files

- `path/to/file` — explicitly permitted file or directory.

Do not edit files outside this allowlist. Keep paths repository-relative and free of `..`.

## Subtasks

- [ ] SUBTASK-001 — concrete bounded implementation step.
- [ ] SUBTASK-002 — concrete bounded verification or documentation step.

Use `None` only when the task genuinely has no decomposable subtask.

## Acceptance and verification

- **CA-001:** Describe the observable acceptance condition.
- **Tests:** `TEST-001` — [tests/test_sdd_composy_tasks.py::TaskContractTemplatesTest::test_task_contract_covers_trace_paths_subtasks_and_commands](../../tests/test_sdd_composy_tasks.py#test_task_contract_covers_trace_paths_subtasks_and_commands) proves CA-001.
- **Commands:**
  - `python3 -m unittest tests.test_sdd_composy_tasks`

Commands must be reproducible and non-empty. Completion requires fresh test evidence,
non-blocking QA, review, approved verification, and consistent trace links.

## Human gate

This contract is not approved by generation. A human must review the exact task and set
`lifecycle.status: APPROVED`, `human_approval: APPROVED`, and append a matching event to
`verified`. Revisions return it to `DRAFT`/`PENDING` until approved again.
