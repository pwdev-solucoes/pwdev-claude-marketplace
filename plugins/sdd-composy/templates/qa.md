---
type: QA_REPORT
okf_version: "0.2"
title: "{{PRODUCT_NAME}} quality assurance report"
sources:
  - resource: "tasks/prd-{{SLUG}}/tasks.md"
  - resource: "tasks/prd-{{SLUG}}/stories.md"
generated:
  by: "{{ACTOR_ID}}"
  at: "{{GENERATED_AT}}"
verified: []
lifecycle:
  status: DRAFT
human_approval: PENDING
transition: evidence_required
---

# {{PRODUCT_NAME}} — Quality Assurance

## Scope and traceability

| Acceptance criterion | Story/scenario | Test IDs | Result | Evidence |
|---|---|---|---|---|
| CA-001 | US-001 / SC-001 | UNIT-001, INT-001, E2E-001 | PENDING | evidence/ |

Every approved CA must map to a SC and at least one executable test. Missing or
ambiguous mappings are blockers and cannot transition to `evidence_required`.

## Test results

### unit

| Test command | Environment | Result | Exit code | Evidence |
|---|---|---|---:|---|
| `{{UNIT_COMMAND}}` | {{ENVIRONMENT}} | PENDING | | |

### integration

| Test command | Environment | Result | Exit code | Evidence |
|---|---|---|---:|---|
| `{{INTEGRATION_COMMAND}}` | {{ENVIRONMENT}} | PENDING | | |

### End-to-end (E2E)

| Test command / browser | Environment | Result | Exit code | Evidence |
|---|---|---|---:|---|
| `{{E2E_COMMAND}}` / {{BROWSER}} | {{ENVIRONMENT}} | PENDING | | |

If browser capability is unavailable, record that fact and a blocker; do not
silently claim E2E coverage.

## Accessibility and responsiveness

- Accessibility standard/checks: {{ACCESSIBILITY_STANDARD}}
- Accessibility result: `PENDING`
- Responsive viewports tested: {{VIEWPORTS}}
- Responsive result: `PENDING`
- Known deviations and blockers: {{BLOCKERS}}

## Environment and regression evidence

- Runtime, OS, browser, versions, fixtures, and configuration: {{ENVIRONMENT}}
- Services started by this run and cleanup status: {{SERVICES}}
- Regression suite and result: {{REGRESSION_RESULT}}
- Evidence inventory (confined relative paths, type, SHA-256, result):
  {{EVIDENCE_INVENTORY}}

## Gate

Set `lifecycle.status: APPROVED`, `human_approval: APPROVED`, and append a
matching human event in `verified` only after every required CA is covered and
all required test, accessibility, responsiveness, environment, regression, and
evidence fields are verified. The permitted next transition is
`evidence_required`.

Any failed test, missing evidence, unavailable capability, unclean environment,
or unresolved accessibility/responsiveness issue sets `lifecycle.status:
REJECTED`, records a sanitized blocker and next action, and prevents the
transition. Agent confidence or artifact existence is never approval.
