# SDD Composy PRD contract

The PRD converts a user problem and optional codebase or domain context into the human
contract at `tasks/prd-<slug>/prd.md`. This location is the only supported human output for
the PRD stage. Operational state under `.planning/sdd-composy/` cannot replace it.

## Product content

The document is problem-first and records objectives, measurable success metrics, explicit
in-scope and out-of-scope boundaries, assumptions, dependencies, and open questions.
Functional requirements use stable `RF-NNN` identifiers. Acceptance criteria use stable
`CA-NNN` identifiers and link to the applicable RF on the criterion heading. Assigned RF and
CA identifiers are never renumbered, reused, or silently replaced; obsolete items retain
their identifier and record their lifecycle explicitly.

Codebase and domain maps are evidence sources only. Product documents must not make architecture decisions.
A PRD may record genuine product or externally imposed constraints,
but it must not select components, libraries, frameworks, interfaces, data models, deployment
topology, or an implementation approach. Those decisions belong to the downstream TechSpec.

## OKF v0.2 metadata

The PRD is an OKF v0.2 `PRD` concept with the frontmatter defined in [okf.md](okf.md). The
user-problem source is required; codebase and domain resources appear only when consumed.

## Human gate

The template contains exactly one explicit `human_approval` field. It starts as `PENDING`.
Artifact existence, generated metadata, agent confidence, or completion of an interview must
never change it to `APPROVED`.

Only a human may approve the PRD. On approval, set `human_approval` to `APPROVED`, set the
lifecycle status to the canonical `APPROVED` state, and append a `verified` event containing
the human actor in `by` and the approval timestamp in `at`. Rejection is recorded explicitly
as `lifecycle.status: REJECTED` with `human_approval: REJECTED` and a matching human event,
and stops downstream generation. The only PRD lifecycle values are `DRAFT`, `APPROVED`, and
`REJECTED`, as defined by `references/workflow.md`. Stories and TechSpec must consume only a
human-approved PRD.
