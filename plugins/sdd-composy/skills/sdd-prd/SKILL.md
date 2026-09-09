---
name: sdd-prd
description: >
  Create or revise the problem-first SDD Composy PRD from a required user
  problem and optional codebase or domain evidence, preserving stable RF and
  CA identifiers and stopping at an explicit human approval gate.
metadata:
  version: 0.1.0
---

# SDD PRD

Create or revise the human product contract at `tasks/prd-<slug>/prd.md`.
Read `references/product.md` for the complete product contract,
`templates/prd.md` for the document shape, and `references/workflow.md` for
the lifecycle rules. This skill interprets product evidence; it makes no architecture decisions
and does not depend on runtime-specific tools.

## Inputs

- A user problem is required. Establish who experiences it, its impact, and
  the available evidence before drafting the PRD.
- A short stable slug identifies the artifact directory. Reuse the existing
  slug when revising a PRD; do not silently create a second contract.
- Codebase and domain context are optional evidence sources. Consume them only
  when relevant and include only sources actually used.
- The configured OKF actor identifier and an ISO 8601 timestamp with an
  explicit UTC offset are required for generated metadata.

If the problem, intended outcomes, or product boundaries cannot be stated
without guessing, ask focused questions before writing. Technical uncertainty
does not belong in the PRD as a chosen solution.

## Procedure

1. Resolve `tasks/prd-<slug>/prd.md`. Read an existing PRD before revising it,
   preserve its assigned identifiers and useful human content, and do not
   overwrite unrelated artifacts in the directory.
2. Gather the user problem and any explicitly supplied codebase or domain
   evidence. Record the user-problem resource in `sources`; add optional
   context resources only when consumed.
3. Render `templates/prd.md` as an OKF v0.2 `PRD`. Replace its rendering
   markers and complete the problem, objectives, measurable success metrics,
   in-scope and out-of-scope boundaries, assumptions, dependencies, and open
   questions. Do not leave unused optional source entries in the result.
4. Assign stable `RF-NNN` identifiers to observable functional requirements
   and stable `CA-NNN` identifiers to acceptance criteria. Every CA identifies
   its applicable RF. Never renumber, reuse, or silently replace an assigned
   RF or CA; mark obsolete entries explicitly.
5. Exclude component, library, framework, interface, data-model, deployment,
   topology, and implementation choices. Product or externally imposed
   constraints may be recorded as constraints, but solution design belongs in
   the downstream TechSpec.
6. Write only `tasks/prd-<slug>/prd.md` as the human contract. A new or revised
   document starts with lifecycle status `DRAFT`, `human_approval: PENDING`,
   and no invented approval event. Artifact existence does not imply approval.
7. Present the draft and its unresolved questions to a human for review. Do
   not route stories, TechSpec, tasks, or implementation while approval is
   pending.
8. Only after a human explicitly approves this exact PRD, set
   `human_approval` to `APPROVED`, change lifecycle status to the canonical
   `APPROVED` state, and append a `verified` event with the human actor in `by`
   and the approval timestamp in `at`. Never use the generating agent as the
   approving human. If the human rejects it, set lifecycle and human approval to `REJECTED`
   and record the matching human event;
   rejection stops downstream generation until the PRD is revised and approved.

## Output

Return the PRD path, slug, consumed source resources, generated actor and
timestamp, lifecycle status, `human_approval` value, unresolved questions,
and the next permitted lifecycle stage. When the gate is not approved, state
that downstream generation remains blocked. Do not claim approval from file
existence, completeness, confidence, or an interview.

## Boundaries

The product reference owns content and gate semantics, and the template owns
the document shape. This skill must not duplicate those contracts in a
runtime adapter, infer approval, write architecture, or depend on
runtime-specific tools. Runtime entry points only route to this skill.
