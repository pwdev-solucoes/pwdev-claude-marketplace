---
type: TASKS
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
---

# {{PRODUCT_NAME}} — Tasks

This dependency-explicit index is the human contract for implementation. Task IDs are
stable after approval and must never be renumbered. Each row links to one per-task
contract in this exact bundle: `tasks/prd-{{SLUG}}/`.

## Task index

| ID | Title | State | Dependencies | Contract |
|---|---|---|---|---|
| TASK-001 | Replace with approved task title | pending | — | [TASK-001](task-001.md) |

State is operationally owned by the validated JSON projection; Markdown/JSON conflicts
must be reported and explicitly resolved. A task is not `ready` until every dependency is
`complete`.

## Traceability

Every task contract must link approved `RF-*`, `US-*`, `SC-*`, `CA-*`, and test IDs where
applicable. Every task must declare non-empty allowed paths, subtasks (or `None`), and
verification commands. Completion requires fresh tests, QA, review, verification, and
trace consistency.

## Human gate

Before implementation, a human reviews this index and all linked contracts, then sets
`lifecycle.status: APPROVED`, `human_approval: APPROVED`, and appends a matching human
event to `verified`.
