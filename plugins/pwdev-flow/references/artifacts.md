# PWDEV Flow artifact protocol

Store portable project state under `.planning/flow/`. Markdown artifacts are human-readable contracts; JSON is limited to configuration. Preserve unknown fields when updating existing files.

## Configuration

`.planning/flow/config.json`:

```json
{
  "schema_version": 1,
  "language": "pt-BR",
  "runtime": "codex",
  "auto_commit": false,
  "audit": false
}
```

`language` follows the user's explicit preference or current conversation. `runtime` records the adapter that last initialized state; it must not make artifacts unreadable elsewhere. `auto_commit` defaults to `false` and never overrides an explicit user instruction.

`audit` is opt-in. When true, semantic events are appended through [audit](audit.md); Flow never promises complete tool telemetry.

Optional `fleet` and `external_models` blocks follow [fleet](fleet.md) and [delegation](delegation.md). Merge defaults without dropping unknown configuration fields.

## State

`.planning/flow/state.md`:

```markdown
# PWDEV Flow State

- Schema: 1
- Repository: brownfield
- Status: INITIALIZED
- Active workflow: none
- Active artifact: none
- Last gate: none
- Updated: 2026-08-16
- Next: define a bounded task or start discovery
```

Use ISO dates. Keep state concise; detailed analysis belongs in phase or report artifacts.

## Quick tasks

Store authorized quick artifacts under `.planning/flow/quick/<date>-<slug>/`:

- `contract.md`: objective, acceptance criteria, allowed files, prohibitions, verification commands;
- `report.md`: changed files, tests, review result, truth evidence, verdict, open concerns.

## Full lifecycle

```text
.planning/flow/
├── context/{project,requirements,domain,stack,pitfalls}.md
├── product/prd.md
├── product/roadmap/<phase>/<epic>/<feature>/<task>.md
├── phases/<slug>/spec.md
├── phases/<slug>/decisions.md
├── phases/<slug>/plans/<id>-<slug>.md
├── phases/<slug>/execution/<id>-summary.md
├── phases/<slug>/review/{code-review,qa-report,simplify-proposals}.md
├── phases/<slug>/verify/{verify,fix-<id>}.md
├── memory/MEMORY.md
├── memory/<type>-<slug>.md
├── audit/events.jsonl
├── fleet/<slug>.json
├── fleet/<slug>.pane.sh
├── fleet-status.json
├── fleet-logs/<stage>-<timestamp>.log
├── fleet-results/<stage>-<timestamp>.json
├── delegation/<timestamp>-<agent>.<unique>.md
├── delegation/.lock
├── archive/<date>/
├── migration.md
└── reports/{health,deps}/
```

Use stable lowercase hyphenated slugs. Use two-digit task IDs (`01`, `02`) and preserve them from plan through execution and correction artifacts.

Every phase artifact begins with a title, status, source paths, and ISO update date. Do not duplicate full upstream documents; link them and quote only the clauses required by the downstream contract.

## Gate persistence

Update `.planning/flow/state.md` only after the gate result is known. Record:

- active feature slug;
- current phase and status;
- active artifact path;
- last gate with `APPROVED`, `REJECTED`, or `BLOCKED`;
- correction cycle count;
- exact next valid action.

Never mark an artifact approved solely because it exists.

## Reports

Store standalone reports under `.planning/flow/reports/` only when the user requests persistence or an active Flow phase already authorizes it:

- `<date>-review-<slug>.md`;
- `<date>-verify-<slug>.md`.

Never put secrets, raw credentials, full environment dumps, or unnecessarily large command output into artifacts. Link to repository files and summarize evidence precisely.

Operational artifacts follow [health](health.md), [maintenance](maintenance.md), [audit](audit.md), and [migration](migration.md). Audit and archive paths are durable and must never be treated as disposable build output.

Fleet bookkeeping under `.planning/flow/fleet/` belongs to the initiating repository; each member binds the exact approved contract hashes, canonical initiating root, named base branch, and base commit. Fleet status, logs, and results belong to the isolated worktree and are atomically published only through validated non-symlink paths. Delegation capture and its write lock live under `.planning/flow/delegation/`. These are operational Flow paths and must never be translated into `.planning/fleet` or `.planning/delegation`.

`.env.fleet` and `docker-compose.flow-fleet.yml` are worktree runtime files, not portable contracts. The central `fleet/<slug>.pane.sh` is an executable lifecycle artifact, not worktree content. Never read, display, migrate, audit, or adopt an existing project `.env.fleet`; only the packaged fleet lifecycle may generate it.
