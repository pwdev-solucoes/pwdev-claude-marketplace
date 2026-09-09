---
type: TECHSPEC
okf_version: "0.2"
sources:
  - resource: "tasks/prd-{{SLUG}}/prd.md"
  - resource: "tasks/prd-{{SLUG}}/stories.md"
  - resource: ".planning/sdd-composy/context/project.md"
  - resource: ".planning/sdd-composy/context/stack.md"
  - resource: ".planning/sdd-composy/context/codebase.json"
generated:
  by: "{{ACTOR_ID}}"
  at: "{{GENERATED_AT}}"
lifecycle:
  status: DRAFT
human_approval: PENDING
verified: []
---

# {{PRODUCT_NAME}} — Technical Specification

## Technical Context

Summarize relevant mapped constraints and conventions. Distinguish observed codebase facts
from decisions made by this specification, and cite their source resources.

## Component Inventory

| Component | Existing or new | Responsibility | Inputs | Outputs | RF/US links |
|---|---|---|---|---|---|
| `{{COMPONENT}}` | Existing / New | One bounded responsibility | Named inputs | Named outputs | RF-001; add US links only when stories are `REQUIRED` |

## Interfaces and Contracts

| Interface | Producer | Consumer | Input contract | Output contract | Failure behavior | Compatibility |
|---|---|---|---|---|---|---|
| `{{INTERFACE}}` | `{{PRODUCER}}` | `{{CONSUMER}}` | Shape and preconditions | Shape and guarantees | Errors and recovery | Compatibility rule |

## Data Model (Conditional)

Use the specification reference when persistent data changes. Otherwise record
`NOT_APPLICABLE` with a concrete justification.

## API Contracts (Conditional)

Use the specification reference for an externally consumed or internal API change.
Otherwise record `NOT_APPLICABLE` with a concrete justification.

## Decisions

### DEC-001 — {{DECISION_NAME}}

- Options: {{OPTIONS_CONSIDERED}}
- Choice: {{SELECTED_OPTION}}
- Rationale: {{WHY_THIS_OPTION}}
- Trade-offs: {{COSTS_AND_LIMITATIONS}}
- Reversible: {{YES_NO_AND_REVERSAL_CONDITIONS}}
- RF/US/SC links: RF-001; add US/SC links only when stories are `REQUIRED`

## Risks

### RISK-001 — {{RISK_NAME}}

- Likelihood: {{LOW_MEDIUM_HIGH}}
- Impact: {{LOW_MEDIUM_HIGH_AND_CONSEQUENCE}}
- Mitigation: {{PREVENTION_OR_REDUCTION}}
- Owner: {{ACTOR_ID}}
- Trigger or signal: {{OBSERVABLE_SIGNAL}}

## Test Cases

### TU-001 — CA-001 — {{UNIT_TEST_NAME}}

- Name: {{UNIT_TEST_NAME}}
- Level: Unit
- Setup: {{CONTROLLED_PRECONDITIONS}}
- Action: {{OPERATION}}
- Expected result: {{OBSERVABLE_RESULT_FOR_CA_001}}

### TI-001 — CA-001 — {{INTEGRATION_TEST_NAME}}

- Name: {{INTEGRATION_TEST_NAME}}
- Level: Integration
- Setup: {{REAL_BOUNDARIES_AND_PRECONDITIONS}}
- Action: {{INTERACTION}}
- Expected result: {{OBSERVABLE_RESULT_FOR_CA_001}}

### E2E-001 — CA-001 — {{END_TO_END_TEST_NAME}}

- Name: {{END_TO_END_TEST_NAME}}
- Level: End-to-end
- Setup: {{USER_VISIBLE_PRECONDITIONS}}
- Action: {{COMPLETE_USER_OR_CONSUMER_FLOW}}
- Expected result: {{OBSERVABLE_RESULT_FOR_CA_001}}

## Gate

This TechSpec remains unapproved while `human_approval` is `PENDING`. Approval requires a
human to approve the exact specification, set it and `lifecycle.status` to `APPROVED`, and
append a matching human event with `by` and `at` to `verified`. Rejection sets both values to
`REJECTED` and records the matching human event. Generation or existence never records a decision.
