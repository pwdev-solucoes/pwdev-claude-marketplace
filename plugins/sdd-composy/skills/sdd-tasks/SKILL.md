---
name: sdd-tasks
description: Generate and safely advance the SDD Composy task projection from approved upstream contracts.
metadata:
  version: 0.1.0
---

# SDD Tasks

Manage the durable task projection for `tasks/prd-<slug>/`. Read
`references/tasks.md`, `references/states.md`, `references/workflow.md`, and
`references/safety.md` before acting. This skill is runtime-neutral and does
not depend on runtime-specific tools.

## Inputs and gates

Require the exact PRD, Stories, and TechSpec in the bundle to be explicitly
human-approved (or an explicitly approved `NOT_APPLICABLE` disposition where
the contract permits it), with matching `verified` events. Existence,
metadata, completeness, or model confidence never implies approval. Stop on
missing, pending, rejected, stale, contradictory, or untraceable upstream
contracts.

## Operations

Use the shared deterministic helper `${CLAUDE_PLUGIN_ROOT}/scripts/sdd_tasks.py`
for every projection operation; do not duplicate its validation or mutation
logic. The supported operations are:

- `import <markdown-root> <state> [--prd-slug] [--root]` to reconcile task
  Markdown into the repository-bound JSON projection.
- Read-only `list <state>`, `next <state>`, and `show <state> <TASK-ID>`.
  These never write files and are safe to use without approval.
- Mutating `start <state> <TASK-ID>`, `block <state> <TASK-ID> <reason>`, and
  `transition <state> <TASK-ID> <target>`. Request explicit human approval
  immediately before any state-changing command; never infer it. `block`,
  `rejected`, and `skipped` require a non-empty reason, and `skipped` also
  requires human authority.
- `verify` is a read-only gate check: inspect fresh tests, QA, review,
  verification, and trace evidence and report whether completion is permitted;
  it does not mutate the projection. If the installed helper exposes a
  verify subcommand, route to it; otherwise perform only the equivalent
  validation and do not invent state.

The helper enforces stable `TASK-NNN` IDs, acyclic dependencies, dependency
completion before `ready`/`running`, guarded lifecycle transitions, fresh
evidence, unknown-field preservation, repository confinement, and same-directory
temporary files with atomic replacement. Never write task JSON or Markdown
directly from this skill. Report Markdown/JSON conflicts and require an
explicit resolution; never overwrite silently.

## Output and boundaries

Write generated human contracts only beneath the exact path
`tasks/prd-<slug>/`; operational projection remains under its authorized
`.planning/sdd-composy/` location. Preserve stable IDs and unknown JSON fields.
Return exactly: operation, path(s), PRD slug, task ID/state when applicable,
consumed sources, approval status, evidence/trace summary, and next permitted
lifecycle action. Do not duplicate task bodies. Do not read or expose `.env`,
credentials, tokens, private keys, certificates, or fleet environment files.
Do not commit, push, publish, or mutate external services.
