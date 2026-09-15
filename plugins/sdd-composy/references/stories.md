# SDD Composy user-story contract

The stories stage consumes a human-approved `tasks/prd-<slug>/prd.md`, the current
`.planning/sdd-composy/context/domain.md`, and, when relevant, optional
`.planning/sdd-composy/context/project.md`. It produces the sole human story contract at
`tasks/prd-<slug>/stories.md`. Product documents describe observable behavior and must not
make architecture decisions.

## Applicability

Stories are required for user-facing behavior and externally consumed APIs. Such work must
not use `NOT_APPLICABLE`, even when the change is small or its implementation is mostly
internal. `NOT_APPLICABLE` is permitted only for pure internal work with no user-facing or
externally consumed behavior, and it requires a specific, non-empty justification.

Applicability is a human gate. An agent may recommend `REQUIRED` or `NOT_APPLICABLE`, but
only an explicit human decision resolves it. File existence, metadata, inferred intent, or
agent confidence never establishes approval or non-applicability.

## Story content and traceability

Identify actors before journeys. Each actor records goals, context, capabilities, and
constraints. Journeys record a trigger, ordered interaction, outcome, alternate or recovery
paths, participating actors, and linked stories.

User stories use globally unique, stable `US-NNN` identifiers within the PRD bundle.
Scenarios use globally unique, stable `SC-NNN` identifiers within the same bundle. Never
renumber, reuse, or silently replace assigned identifiers; retain obsolete items and record
their lifecycle. Every US links to one or more approved `RF-NNN` requirements, and every SC
links to one or more approved `CA-NNN` acceptance criteria. Missing or ambiguous RF/CA links
block publication and return the work to the PRD owner.

Record dependencies with owners and affected US/SC identifiers. Record edge cases and
failure, empty, boundary, permission, interruption, and recovery behavior where applicable,
with their expected outcomes and US/SC links. Do not invent technical components or tests in
this product contract.

## OKF v0.2 and lifecycle

Stories are an OKF v0.2 `STORIES` concept with the frontmatter defined in [okf.md](okf.md) plus
an `applicability` field.

A draft begins with `lifecycle.status: DRAFT`, `applicability: REQUIRED`,
`human_approval: PENDING`, and no invented verification event. Approval requires a human to
approve the exact stories, set `lifecycle.status: APPROVED` and `human_approval: APPROVED`,
and append a `verified` event
with the human actor in `by` and decision timestamp in `at`. A justified `NOT_APPLICABLE`
decision sets `lifecycle.status: NOT_APPLICABLE`, `applicability: NOT_APPLICABLE`, and
`human_approval: APPROVED`; it requires a non-empty justification and the same human-recorded
verification event. Rejection sets `lifecycle.status: REJECTED` and
`human_approval: REJECTED`. These are the only stories lifecycle combinations, as defined by
`references/workflow.md`. Rejection blocks TechSpec generation until the story gate is resolved.
