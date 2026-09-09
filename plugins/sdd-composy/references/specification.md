# SDD Composy technical-specification contract

The TechSpec stage consumes an approved `prd.md`, approved stories or a human-resolved
`NOT_APPLICABLE` stories decision, and current codebase context. It produces the sole human
technical contract at `tasks/prd-<slug>/techspec.md`.

## Upstream gates

Validate metadata and the human event, not merely the files. The PRD must have
`human_approval: APPROVED`, `lifecycle.status: APPROVED`, and a matching human event in
`verified`. Required stories must satisfy the same approval conditions. Stories marked
`NOT_APPLICABLE` require `lifecycle.status: NOT_APPLICABLE`,
`human_approval: APPROVED`, a non-empty `applicability_justification`, and a matching human
verification event. Stop on pending, rejected, stale, contradictory, or missing upstream
state. Artifact existence and generated metadata never establish approval.

Read the mapped codebase sources relevant to the change, including project and stack context
and `codebase.json`. Treat mapped facts as observations rather than prior architecture
decisions. Missing or stale context blocks unsupported design claims.

## Architecture contract

Inventory every affected component with its responsibility, whether it is existing or new,
inputs, outputs, and product trace links. Define boundaries between producers and consumers,
including input/output shapes, preconditions, guarantees, failures, recovery, and
compatibility. Reuse evidenced repository conventions unless an explicit decision explains
the departure.

Record material decisions with stable `DEC-NNN` identifiers, options, choice, rationale,
trade-offs, reversibility, and RF/US/SC links. Record risks with stable `RISK-NNN`
identifiers, likelihood, impact, mitigation, owner, and observable trigger. Do not hide an
unresolved architectural choice inside prose; leave it open and block approval when it is
required for safe implementation.

## Conditional detail

When persistence changes, the data section defines entities, fields and types, constraints,
relationships, ownership, schema compatibility, migration and backfill order, rollback,
retention, and sensitive-data handling. When persistence does not change, record
`NOT_APPLICABLE` and why; do not invent a data model.

When an API changes, the API section defines each endpoint or callable contract, method or
operation, request and response schema, validation, authentication, authorization, error
semantics, idempotency when relevant, versioning, compatibility, and deprecation. Include
internal APIs when another component consumes them. When no API changes, record
`NOT_APPLICABLE` and why.

## Tests and traceability

Name planned test cases with stable, unique `TU-NNN`, `TI-NNN`, and `E2E-NNN` identifiers.
Each case records a human-readable name, level, setup, action, expected result, and one or
more approved `CA-NNN` links. Select the levels justified by risk and architecture, but the
plan must explicitly consider unit, integration, and end-to-end coverage; record why a level
is `NOT_APPLICABLE` rather than silently omitting it. Never renumber or reuse an assigned ID.

## Product boundary and lifecycle

Technical design must not change requirements, stories, acceptance criteria, or product
scope. If implementation constraints reveal a needed product change, stop and return it to
the owning upstream human gate; do not mutate product scope in the TechSpec.

TechSpec is an OKF v0.2 `TECHSPEC` concept. Frontmatter lists every consumed artifact in
`sources`, records the generating actor and timestamp under `generated`, begins with
`lifecycle.status: DRAFT`, contains exactly one `human_approval: PENDING`, and begins with no
invented `verified` events. Human approval of the exact document updates the lifecycle and
sets `lifecycle.status: APPROVED` and `human_approval: APPROVED`, then appends a matching
`verified` event with actor in `by` and an ISO 8601 timestamp in `at`. Rejection sets
`lifecycle.status: REJECTED` and `human_approval: REJECTED`, with a matching human event.
TechSpec supports only `DRAFT`, `APPROVED`, and `REJECTED`, as defined by
`references/workflow.md`. Rejection or upstream staleness blocks downstream task generation.
