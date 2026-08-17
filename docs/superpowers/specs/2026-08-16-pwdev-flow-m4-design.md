# PWDEV Flow Marco 4 Design

## Objective

Add the operational layer required to maintain, diagnose, audit, and migrate PWDEV Flow projects without introducing runtime hooks or destructive automation. Preserve the complete Marco 3 lifecycle and provide a compatibility route for supported PWDEV Code commands.

## Scope

Marco 4 adds four skills:

- `flow-health` — read-only project and Flow workspace diagnostics;
- `flow-maintenance` — inventory, approval-gated archival, and evidence-based changelog generation;
- `flow-audit` — enable, record, query, and verify a portable semantic audit trail;
- `flow-compat` — map supported `/pwdev-code:*` requests to canonical Flow skills.

`flow-init` gains a migration route for legacy `.planning/config.json`. Marco 4 also adds deterministic Python scripts for audit events and configuration migration.

Fleet orchestration, external coding CLI delegation, automatic worktrees, Docker isolation, and dashboards remain deferred to Marco 5.

## Operational architecture

```text
canonical Flow skills ──semantic event──▶ audit JSONL
        │                                  │
        ├── health reads workspace ◀───────┤
        ├── maintenance archives safely    │
        └── compat routes old intent       │

legacy .planning/config.json ──plan/apply──▶ .planning/flow/config.json
```

Skills describe user-facing workflows. Scripts own deterministic parsing, validation, append behavior, secret rejection, and migration conflict handling.

## Audit protocol

Audit is opt-in through `"audit": true` in `.planning/flow/config.json`. Events are appended to `.planning/flow/audit/events.jsonl` with:

- `schema_version`;
- UTC `timestamp`;
- `action` from a fixed vocabulary;
- `skill`;
- optional `phase`, `status`, `target`, and JSON `detail`.

The audit helper supports `record`, `summary`, `events`, and `verify`. Recording while disabled is a successful no-op. Malformed event files, unknown actions, non-object details, secret-like detail keys, and secret file targets fail explicitly. The script never reads repository secrets and never records model routing or hidden runtime events.

This is a semantic audit trail, not complete telemetry. Skills record meaningful gates and artifact transitions when audit is enabled; there are no hooks in the plugin manifest.

## Legacy migration

Migration is two-step:

1. `plan` reads `.planning/config.json` and reports mappings without writing.
2. `apply` creates `.planning/flow/config.json` only after user approval.

The source remains untouched. The migration refuses to overwrite an existing Flow config. Mappings include:

- `lang` → `language`;
- `audit` → `audit`;
- `type` → `repository_type`;
- safe operational preferences under a `legacy` object.

Flow always sets `schema_version: 1`, `runtime: "codex"`, and `auto_commit: false`. Provider/model routing, external agent configuration, credentials, token-like keys, and unknown values are not copied. A migration record names the source framework and version.

Legacy artifacts remain where they are. The migration reference explains how Flow can consult them and how to copy selected Markdown artifacts only after an explicit inventory and approval; automatic bulk moves are prohibited.

## Health contract

Health is read-only by default and evaluates:

- Flow structure, state, config, links, memory index, phase gates, and audit integrity;
- repository instructions and documentation;
- discovered test, lint, typecheck, build, and dependency commands;
- Git status and repository hygiene;
- locally available security and dependency checks.

It does not install tools, fetch vulnerability data without authorization, read secrets, or fix findings. Persist a report only when requested or when an active Flow workflow already authorizes reports.

## Maintenance contract

Maintenance supports:

- `inventory` — read-only classification of active, complete, stale, and archivable artifacts;
- `archive` — move only verified-complete phases or quick tasks into `.planning/flow/archive/<date>/` after exact-target approval;
- `changelog` — generate or merge entries from real Git history and verified Flow artifacts.

Never delete artifacts. Never archive active state, context, product contracts, memory, audit data, or an unverified phase. Never overwrite an existing changelog.

## Compatibility router

`flow-compat` recognizes supported legacy commands and follows the canonical skill:

- init/session, discover, design, plan, execute, quick, review, verify;
- product, memory, simplify;
- health, maintenance, audit.

It translates `.planning/` paths to `.planning/flow/` only for newly written Flow artifacts and never rewrites legacy data silently. Fleet and external CLI commands return `UNSUPPORTED_IN_M4` and point to Marco 5.

## Version and acceptance

The manifest base version becomes `0.4.0` and receives one local Codex cachebuster.

Marco 4 is accepted when:

- all fifteen canonical/compat skills pass the official validator;
- four new references and two scripts exist;
- audit tests prove append, summary, disabled no-op, malformed-log failure, and secret rejection;
- migration tests prove dry-run, safe mappings, source preservation, target conflict refusal, and secret-key exclusion;
- structural tests, plugin validation, content scans, and source/cache comparison pass;
- the marketplace is not hand-edited;
- unrelated existing changes remain untouched.
