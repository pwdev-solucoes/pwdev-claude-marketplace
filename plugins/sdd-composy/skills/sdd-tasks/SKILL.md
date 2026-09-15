---
name: sdd-tasks
description: >
  Generate and safely advance the SDD Composy task projection from approved PRD,
  stories, and TechSpec: import contracts, list/next/show, and guarded
  start/block/transition/verify. Use when work must be decomposed or a task's state
  inspected or moved — 'quebrar a spec em tarefas', 'listar as tarefas', 'qual a
  próxima task', 'mark TASK-003 blocked'. Do NOT use to implement a task (sdd-
  execute), reconcile Markdown and JSON (sdd-sync), or for a status overview (sdd-
  status).
metadata:
  version: 0.1.0
---

# SDD Tasks

Manage the durable task projection for `tasks/prd-<slug>/` through the bundled
`scripts/sdd_tasks.py` helper; never duplicate its validation or mutation logic, and never write
task JSON or Markdown directly from this skill.

Language: before writing human-facing prose, run `scripts/sdd_language.py <repo-root>` and use the persisted language; on `not_initialized`, return it with `next_action: run_init`. Localization rules: `references/language.md`.

## Gates

Require the exact PRD, Stories, and TechSpec in the bundle to be explicitly human-approved (or an
explicitly approved `NOT_APPLICABLE` disposition where the contract permits it), with matching
`verified` events. Existence, metadata, completeness, or model confidence never implies approval.
Stop on missing, pending, rejected, stale, contradictory, or untraceable upstream contracts.

## Operations

- `import <markdown-root> <state> [--prd-slug] [--root]` — reconcile task Markdown into the
  repository-bound JSON projection.
- `list <state>`, `next <state>`, `show <state> <TASK-ID>` — read-only; safe without approval.
- `start <state> <TASK-ID>`, `block <state> <TASK-ID> <reason>`, `transition <state> <TASK-ID>
  <target>` — mutating. Request explicit human approval immediately before each; never infer it.
  `block`, `rejected`, and `skipped` require a non-empty reason; `skipped` also requires human
  authority.
- `verify <state>` — read-only gate check: inspects fresh tests, QA, review, verification, and
  trace evidence and reports whether completion is permitted; it does not mutate the projection.

The helper enforces stable `TASK-NNN` IDs, acyclic dependencies, dependency completion before
`ready`/`running`, guarded lifecycle transitions, fresh evidence, unknown-field preservation,
repository confinement, and atomic replacement. Report Markdown/JSON conflicts and require an
explicit resolution; never overwrite silently.

## Read when

- `references/tasks.md` — running `import`, or a contract is rejected for its shape or links.
- `references/states.md` — requesting `transition` or `block`, or explaining a refused transition.
- `references/artifacts.md` — resolving where a human contract or operational file belongs.

## Output

Human contracts go only beneath the exact path `tasks/prd-<slug>/`; the projection stays under
`.planning/sdd-composy/`. For read-only operations, return the helper output unchanged. Otherwise
return the operation, paths, PRD slug, task ID and state, approval status, evidence/trace summary,
and next permitted lifecycle action. Do not duplicate task bodies.

Safety: Do not commit, push, or publish. Do not read or expose `.env`, credentials, tokens, private keys, certificates, or fleet environment files. Full contract: `references/safety.md`.
