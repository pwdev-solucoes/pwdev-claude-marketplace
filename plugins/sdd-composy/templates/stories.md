---
type: STORIES
okf_version: "0.2"
sources:
  - resource: "tasks/prd-{{SLUG}}/prd.md"
  - resource: ".planning/sdd-composy/context/domain.md"
  - resource: ".planning/sdd-composy/context/project.md"
generated:
  by: "{{ACTOR_ID}}"
  at: "{{GENERATED_AT}}"
lifecycle:
  status: DRAFT
applicability: REQUIRED
applicability_justification: ""
human_approval: PENDING
verified: []
---

# {{PRODUCT_NAME}} — User Stories

## Actors

### Actor-001 — Primary actor

Describe this actor's goal, relevant context, capabilities, and constraints.

### Actor-002 — Supporting actor

Describe this actor's goal, relevant context, capabilities, and constraints, including how
the actor participates in or is affected by the journey.

## User Journeys

### Journey-001 — Primary outcome

Describe the trigger, ordered interaction, expected outcome, and recovery path. Link the
participating actors and applicable stories.

### Journey-002 — Alternate or recovery outcome

Describe the trigger, ordered interaction, expected outcome, and alternate or recovery path.
Link the participating actors and applicable stories.

## User Stories

### US-001 — RF-001 — Primary actor achieves the required outcome

As Actor-001, I want the behavior required by RF-001 so that I achieve the documented
product outcome.

#### SC-001 — CA-001 — Successful outcome

Given the documented starting context, when Actor-001 performs the behavior, then the
observable outcome required by CA-001 occurs.

Repeat the US/SC block only for identifiers present in the approved PRD. Allocate the next
stable US/SC identifiers and replace RF/CA references from the actual upstream IDs; do not
retain an example whose target does not exist.

## Dependencies

- DEP-001 — Identify the product, organizational, regulatory, or external dependency,
  its owner, and the US/SC identifiers it affects.

## Edge Cases

- EDGE-001 — Describe the boundary or failure condition, expected behavior, and linked
  US/SC identifiers.

## Gate

For user-facing behavior or externally consumed APIs, `applicability` remains `REQUIRED`
and this document requires explicit human approval. It remains unapproved while
`human_approval` is `PENDING`; approval requires a human to set it and `lifecycle.status` to
`APPROVED` and append a matching human event with `by` and `at` to `verified`. Rejection sets
both values to `REJECTED` and records the matching human event.

For pure internal work only, a human may set `applicability` to `NOT_APPLICABLE`, record a
non-empty `applicability_justification`, set `lifecycle.status: NOT_APPLICABLE` and
set `human_approval` to `APPROVED`, and append the matching human verification event. Artifact
existence, generated metadata, or agent confidence never
records either gate decision.
