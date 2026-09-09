---
type: QUICK_CONTRACT
okf_version: "0.2"
sources:
  - resource: "{{REQUEST_RESOURCE}}"
generated:
  by: "{{ACTOR_ID}}"
  at: "{{GENERATED_AT}}"
lifecycle:
  status: DRAFT
human_approval: PENDING
verified: []
quick:
  id: "Q-{{SEQUENCE}}"
  allowed_files: []
  verification_commands: []
---

# {{TITLE}}

This contract belongs to the `sdd-composy` bundle.

## Objective

{{BOUNDED_OBJECTIVE}}

## Acceptance criteria

- CA-001 — {{OBSERVABLE_OUTCOME}}

## Scope gate

This contract is eligible only when the implementation touches no more than five
files, has no architecture decision, migration, destructive operation, scope
expansion, or unknown verification. The allowed file list is closed before edits.

## TDD and evidence

Record a failing test before implementation. The final report must link the test,
review, verification, and evidence artifacts. Successful semantic events are then
registered for the normal `TASK-*` record and its `Q-*` quick contract.

## Escalation

If any gate fails, stop before editing and escalate to the standard/full SDD
workflow. Escalation is explicit and never silently converted into quick mode.
