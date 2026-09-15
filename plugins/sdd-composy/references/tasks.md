# SDD Composy task contracts

The tasks stage consumes human-approved `tasks/prd-<slug>/prd.md`, `stories.md`, and
`techspec.md`, and writes only the human contracts under the exact root
`tasks/prd-<slug>/`. Operational state belongs under `.planning/sdd-composy/` and is
validated against `schemas/tasks.schema.json`.

Task IDs use `TASK-NNN` and are stable forever after approval: never renumber, reuse, or
silently replace an ID. A task cannot become `ready` until all listed dependencies are
`complete`. Dependencies must be unique, refer to known tasks, and be acyclic.

Each task declares at least one acceptance criterion (`CA-*`), verification command,
repository-relative allowed path, and explicit boolean `evidence_required` value. Its Markdown
contract also links upstream `RF-*`, `US-*`, `SC-*`, and `CA-*` concepts and the tests that
prove them. Every `TEST-*` trace must contain a concrete repository-relative Markdown link
to a test file and (when available) its test anchor; a prose placeholder is insufficient.
Subtasks are bounded checklist items; `None` is valid only when no decomposition
is appropriate. Verification commands must be reproducible and recorded before approval.

Generated Markdown is OKF v0.2 with the frontmatter defined in [okf.md](okf.md) and `sources`
for the approved PRD, stories, and TechSpec. New or changed contracts begin `DRAFT` and
`human_approval: PENDING`; only an explicit human approval may make them `APPROVED`.

The index `tasks.md` is a projection of linked `task-<id>.md` contracts. Markdown and JSON
are synchronized explicitly: conflicts are never overwritten silently, and unknown JSON
fields are preserved. Completion requires fresh tests, QA, review, verification, and trace
consistency. All human task writes stay beneath `tasks/prd-<slug>/` and use same-directory
temporary files followed by atomic replacement.
