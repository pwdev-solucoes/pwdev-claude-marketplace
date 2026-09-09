---
name: sdd-techspec
description: >
  Create or revise an SDD Composy technical specification from approved PRD,
  applicability-resolved stories, and current mapped codebase evidence, with
  stable architecture and test traceability and an explicit human gate.
metadata:
  version: 0.1.0
---

# SDD TechSpec

Create or revise the sole human technical contract at
`tasks/prd-<slug>/techspec.md`. Read `references/specification.md` for the
complete architecture, conditional-detail, upstream-gate, and traceability
contract; read `references/workflow.md` for lifecycle rules. Use
`templates/techspec.md` as the document shape. This skill is runtime-neutral
and does not depend on runtime-specific tools.

## Inputs and upstream gates

- Require the PRD in the same bundle to have `human_approval: APPROVED`, the
  exact `lifecycle.status: APPROVED`, and a matching human event in `verified`.
  Artifact existence does not imply approval.
- Inspect stories applicability: user-facing behavior and externally consumed APIs require
  approved stories with `lifecycle.status: APPROVED` and the same explicit human gate. Internal
  work may use `NOT_APPLICABLE` only with a non-empty
  `applicability_justification`, `lifecycle.status: NOT_APPLICABLE`,
  `human_approval: APPROVED`, and a matching human verification event.
- Stop if upstream state is missing, pending, rejected,
  stale, contradictory, or unsupported by the required human event.
- Consume current relevant mapped context from `project.md`, `stack.md`, and
  `codebase.json`. Treat it as observed evidence, not an architecture decision.
- Require the configured OKF actor identifier and an ISO 8601 timestamp with
  explicit UTC offset for generated metadata.

## Procedure

1. Resolve the PRD bundle and validate every upstream field and human event
   before designing. Read an existing TechSpec before revision; preserve
   assigned identifiers and useful human-authored content.
2. Read only the mapped context relevant to the approved change. If context is
   missing or stale, stop rather than make an unsupported design claim.
3. Inventory affected components and define producer/consumer boundaries,
   interfaces, failures, recovery, and compatibility. Reuse evidenced
   repository conventions unless an explicit decision justifies a departure.
4. Record material decisions as stable `DEC-NNN` entries and risks as stable
   `RISK-NNN` entries. Link decisions and components to applicable `RF-NNN`,
   `US-NNN`, and `SC-NNN` identifiers without changing upstream product scope.
5. Consult the conditional-detail sections in `references/specification.md`
   only when persistence changes and only when an API changes. Otherwise
   record `NOT_APPLICABLE` with a concrete justification; do not invent data
   or API design.
6. Define stable, unique `TU-NNN`, `TI-NNN`, and `E2E-NNN` cases linked to
   approved `CA-NNN` identifiers. Explicitly consider every test level and
   justify `NOT_APPLICABLE` levels instead of silently omitting them.
7. Render `templates/techspec.md` as an OKF v0.2 `TECHSPEC`, listing only
   sources actually consumed. A new or revised artifact starts at `DRAFT`,
   with `human_approval: PENDING` and no invented verification event.
8. Write only `tasks/prd-<slug>/techspec.md`. Do not alter the PRD, stories,
   acceptance criteria, mapped context, or product scope.
9. Present an exact draft artifact reference, unresolved decisions, risks, and
   trace summary for human review. Approval of this exact document updates its
   lifecycle to `APPROVED`, sets `human_approval: APPROVED`, and appends the matching human
   event; rejection sets both fields to `REJECTED` and records its human event, while upstream
   staleness blocks downstream task generation.

## Output

Return exactly: path, slug, consumed sources, generated actor and timestamp,
lifecycle status, human approval value, exact draft artifact reference, trace
summary, unresolved decisions, risks, and next permitted lifecycle stage.
Do not duplicate the TechSpec body in this return summary. When the gate is
not approved, state that downstream task generation remains blocked.

## Boundaries

The specification reference owns architecture and gate semantics; the
template owns document shape. Do not duplicate these contracts in runtime
adapters, infer approval, mutate upstream product contracts, or name or depend
on runtime-specific tools. Runtime entry points only route to this skill.
