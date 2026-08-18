# Artifacts

Markdown artifacts are human-readable contracts; JSON is limited to configuration and
operational bookkeeping. Preserve unknown fields when updating existing files.

## Root

Everything lives under `.planning/power/` in the repository being worked on. Never write
plugin state anywhere else, and never write into the user's home directory.

## Configuration — `.planning/power/config.json`

```json
{
  "schema_version": 1,
  "language": "en",
  "runtime": "claude",
  "model_profile": "balanced",
  "audit": false
}
```

`runtime` records the adapter that last initialized state. It is descriptive: it must never
make artifacts unreadable elsewhere, and it never selects a fleet vector. Optional `fleet`
and `kanban` blocks are merged defaults-first, so every existing known or unknown field wins.

## State — `.planning/power/state.md`

```markdown
# PWDEV Power State

- Schema: 1
- Repository: brownfield
- Status: INITIALIZED
- Active feature: none
- Active artifact: none
- Last gate: none
- Correction cycles: 0
- Updated: 2026-08-18
- Next: define a bounded task or write a requirement
```

Update this file **only after a gate result is known**. Record the active slug, the phase and
status, the active artifact path, the last gate as `APPROVED`, `REJECTED` or `BLOCKED`, the
correction cycle count, and the exact next valid action.

**Never mark an artifact approved solely because it exists.**

## Tree

```text
.planning/power/
├── config.json
├── state.md
├── context/project.md
├── context/stack.md
├── context/domain.md
├── context/pitfalls.md
├── product/prd.md
├── product/roadmap/{ROADMAP,TRACEABILITY,RISKS,METRICS}.md
├── product/roadmap/<phase>/<epic>/<feature>.md
├── features/<slug>/spec.md
├── features/<slug>/plan.md
├── features/<slug>/ledger.md
├── features/<slug>/task-<NN>-brief.md
├── features/<slug>/task-<NN>-report.md
├── features/<slug>/task-<NN>-review.md
├── features/<slug>/verdict.md
├── features/<slug>/fix-<NN>.md
├── quick/<date>-<slug>/{contract,report}.md
├── fleet/<slug>.json
├── fleet/<slug>.pane.sh
├── fleet-status.json
├── fleet-logs/<stage>-<timestamp>.log
├── fleet-results/<stage>-<timestamp>.json
├── audit/pwdev-audit.db
└── memory/MEMORY.md
```

## Context

`.planning/power/context/` is the codebase map — what the repository is, before anyone changes it.
It is observation, never decision, and it is a snapshot: when it disagrees with the code, the code
is right. See [context](context.md).

## Conventions

- Slugs are stable, lowercase and hyphenated, with no accents.
- Task IDs are two digits (`01`, `02`) and are preserved from plan through execution and
  correction. A fix for task 03 is always about task 03.
- Every feature artifact opens with a title, a status, its source paths, and an ISO date.
- Do not duplicate full upstream documents. Link them and quote only the clauses the
  downstream contract requires.

## Prohibitions

- Never put secrets, raw credentials, environment dumps, or unnecessarily large command
  output into an artifact.
- Audit and archive paths are durable. Never treat them as disposable build output.
- Fleet paths are `.planning/power/fleet*`. Never translate them into another plugin's
  layout, and never read another plugin's fleet state as if it were yours.
- `.env.fleet` and `docker-compose.power-fleet.yml` are worktree runtime files, not portable
  contracts. Never read, display, or adopt an existing project `.env.fleet`; only the
  packaged fleet lifecycle may generate one.
