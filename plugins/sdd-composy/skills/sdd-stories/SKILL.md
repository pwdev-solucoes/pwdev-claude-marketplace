---
name: sdd-stories
description: >
  Create, revise, or resolve applicability for SDD Composy user stories from
  an approved PRD and domain evidence, preserving stable US/SC traceability
  and stopping at an explicit human gate.
metadata:
  version: 0.1.0
---

# SDD Stories

Create or revise `tasks/prd-<slug>/stories.md`. Read `references/stories.md` for the
complete story and applicability contract, `templates/stories.md` for the document shape,
and `references/workflow.md` for lifecycle rules. This skill is runtime-neutral and makes
no architecture decisions.

## Inputs

- A human-approved `prd.md` under the same PRD bundle is required. Confirm its explicit
  approval field and matching human event in `verified`; existence alone is insufficient.
- Consume the current `domain.md` as product-language and domain evidence.
- Consume optional `project.md` only when it materially informs actors or journeys, and
  omit it from rendered `sources` otherwise.
- Require the configured OKF actor identifier and an ISO 8601 timestamp with explicit UTC
  offset for generated metadata.

Stop if the PRD is missing, pending, rejected, stale, or lacks its matching human approval
event. Do not infer approval from completeness, metadata, or confidence.

## Procedure

1. Resolve the approved PRD and `tasks/prd-<slug>/stories.md`. Read an existing stories
   document before revision and preserve assigned identifiers and human-authored content.
2. Determine applicability from the approved scope. User-facing behavior and externally
   consumed APIs require stories. Recommend `NOT_APPLICABLE` only for pure internal work,
   provide a specific justification, and still stop for an explicit human decision.
3. For required stories, derive actors, end-to-end journeys, dependencies, and edge cases
   from approved RF and CA contracts plus domain evidence. Do not add scope or architecture.
4. Assign unique stable `US-NNN` identifiers and link every story to applicable `RF-NNN`
   identifiers. Assign unique stable `SC-NNN` identifiers and link every scenario to
   applicable `CA-NNN` identifiers. Never renumber, reuse, or silently replace an ID.
5. Render `templates/stories.md` with OKF v0.2 provenance, generated actor/timestamp,
   lifecycle state, applicability, approval field, and verification events. Record only
   sources actually consumed.
6. Write only `tasks/prd-<slug>/stories.md`. A required draft begins `DRAFT` and `PENDING`.
   A proposed internal exemption includes its justification but remains unresolved until a
   human records the decision.
7. Present the artifact, trace links, open issues, and applicability recommendation for
   human review. Do not route to TechSpec while the gate remains pending.
8. Only after a human explicitly approves this exact artifact or its justified
   `NOT_APPLICABLE` disposition, set required stories to lifecycle `APPROVED`, or the
   exemption to lifecycle `NOT_APPLICABLE`; in both cases set `human_approval: APPROVED`
   and append a `verified` event with the human actor and timestamp. Rejection sets lifecycle
   and human approval to `REJECTED` and records the matching human event
   and blocks downstream work.

## Output

Return the stories path, slug, consumed sources, generated actor and timestamp,
applicability and justification, lifecycle status, human approval value, RF/US and CA/SC
trace summary, unresolved issues, and next permitted lifecycle stage. State clearly when
downstream generation remains blocked.

## Boundaries

The story reference owns content and applicability semantics; the template owns document
shape. Do not duplicate them in runtime adapters, invent human approval, alter the approved
PRD, choose architecture, or depend on runtime-specific tool names.
