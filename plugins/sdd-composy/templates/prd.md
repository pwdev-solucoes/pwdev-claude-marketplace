---
type: PRD
okf_version: "0.2"
sources:
  - resource: "{{USER_PROBLEM_RESOURCE}}"
  - resource: "{{CODEBASE_CONTEXT_RESOURCE}}"
  - resource: "{{DOMAIN_CONTEXT_RESOURCE}}"
generated:
  by: "{{ACTOR_ID}}"
  at: "{{GENERATED_AT}}"
lifecycle:
  status: DRAFT
human_approval: PENDING
verified: []
---

# {{PRODUCT_NAME}} — Product Requirements Document

## Problem

Describe the user or business problem, who experiences it, its impact, and the evidence
that establishes the problem. Keep implementation proposals out of this section.

## Objectives

- O-001 — State a desired product outcome.

## Success Metrics

| Objective | Metric | Baseline | Target | Measurement window |
|---|---|---:|---:|---|
| O-001 | Name a measurable outcome | Record the current value | Record the exact target | Record when it is measured |

## Scope

### In Scope

- State the product behavior or outcome included in this PRD.

### Out of Scope

- State an explicit product boundary.

## Assumptions

- A-001 — Record an unverified belief and how it will be validated.

## Dependencies

- D-001 — Record an external, organizational, regulatory, or product dependency and its owner.

## Open Questions

- Q-001 — Record an unresolved product question, its owner, and the decision deadline.

## Functional Requirements

### RF-001 — Name the required behavior

Describe observable behavior without choosing components, frameworks, data models, APIs,
or another implementation approach. Once assigned, this identifier is never renumbered or
reused.

## Acceptance Criteria

### CA-001 — RF-001 produces its expected outcome

Given the documented product context, when the required behavior occurs, then state the
observable and verifiable outcome. Once assigned, this identifier is never renumbered or
reused.

## Gate

This PRD remains unapproved while `human_approval` is `PENDING`. Approval requires a human
to set that single field and `lifecycle.status` to `APPROVED` and append a matching human
event to `verified` with `by` and `at`. Rejection sets both values to `REJECTED` and records
the human event; document generation or existence never records a decision.
