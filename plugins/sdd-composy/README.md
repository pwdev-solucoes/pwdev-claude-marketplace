# SDD Composy — Portable Spec-Driven Development

> [Versão em português](./README.pt-BR.md)

## Origin and adaptation

This plugin is a fork of the Spec-Driven Development methodology implemented by
[Rodrigo Branas](https://github.com/rodrigobranas) and
[Pedro Nauck](https://github.com/pedronauck). It is adapted to the PWDEV workflow
and intended for use with [Compozy](https://github.com/compozy/compozy).

SDD Composy is an approval-gated workflow packaged for Claude Code, Codex, and Hermes Agent.
All three runtimes use the same lifecycle, schemas, skills, references, scripts, and templates;
a workflow can move between hosts without changing its meaning. Packaged support and offline
adapter tests do not constitute real-provider acceptance. Real acceptance for all three
runtimes is pending the acceptance harness; unavailable, unauthorized, or unaffordable runs
must be reported as `BLOCKED` or `NOT_RUN`, never as `PASS`.

Human-readable contracts live under `tasks/prd-<slug>/`. Operational state lives under
`.planning/sdd-composy/`. Generated project Markdown targets OKF v0.2, requires a non-empty
`type`, and permits unknown extension fields. Supported JSON and Markdown updates preserve
unknown fields.

## Artifact language

Run `/sdd-composy:init` with `pt-BR` or `en-US` to select the language for human-facing
artifacts. If the language is omitted, init asks you to choose and writes no artifacts until a
choice is made. The selection is persisted in `.planning/sdd-composy/config.json`; all
downstream skills consume it without asking again. Before initialization they return
`{"status":"not_initialized","next_action":"run_init"}`.

PRDs, stories, TechSpecs, task descriptions, QA/evidence reports, and status prose follow the
selected language. Machine keys, IDs, schemas, filenames, lifecycle values, command names, and
user evidence remain unchanged. Invalid language values fail without changing the existing
configuration. See the [language and workflow contract](./references/workflow.md).

## Runtime entry points

Claude Code discovers `.claude-plugin/plugin.json` and exposes thin command adapters as
`/sdd-composy:<name>`. Codex discovers `.codex-plugin/plugin.json` and its `skills` root, then
exposes shared skills as `$sdd-composy-<name>`. Hermes discovers `.hermes-plugin/plugin.yaml`;
its bootstrap registers the same skills and loads the documented tool mapping on the first
turn.

Automated Hermes LOOP/fleet execution uses `hermes -z <prompt> --in <worktree>` only after
independent isolation is established or the user gives specific consent. There is no
Claude/Codex fallback. Hermes Kanban integration is not implemented and is unavailable in this
release. The shared core remains authoritative for lifecycle gates, artifacts, state
transitions, safety, and orchestration. See the exact [runtime contract](./references/runtime.md).

## Workflow

```text
INIT -> MAP -> PRD -> STORIES -> TECHSPEC -> TASKS
                                            |
                              EXECUTE -> QA -> EVIDENCE -> REVIEW -> VERIFY -> COMPLETE
```

Product and execution gates require explicit human approval; editing operational JSON is not a
way to simulate approval. Verification reproduces fresh evidence. Reduced `QUICK`, bounded
`LOOP`, and isolated `FLEET` paths retain the same durable contracts and safety rules. Fleet
launch accepts only ready tasks, creates an owned branch and independent Git worktree per
member, can start the selected provider through cmux, tmux, or headless UI, and never merges
automatically. Optional Compose resources are plugin-owned and are stopped only from the
validated member ownership record; cleanup failure preserves recovery state.

## State, compatibility, and recovery

Human intent and approval records live in Markdown under `tasks/prd-<slug>/`; validated JSON
under `.planning/sdd-composy/` is authoritative for current operational state. Operational task
bundles use an object containing a `tasks` array, not a flat task object. Synchronization reports
Markdown/JSON divergence and requires an explicit authority choice. Legacy fleet member schema
v1 is diagnosed and refused during normal execution; eligible records are migrated explicitly
with `scripts/fleet/run.sh --migrate-member MEMBER.json --root ROOT`.

Init never replaces an existing `.claude`. A compatible `.claude -> .agents` link is reported
as `claude_compatibility: "symlink"`; an existing real directory is preserved and bridged by
the regular `.claude/AGENTS.md` file, reported as `"existing_directory"`. Other links or
collisions are conflicts. Status inspection is read-only: it creates or modifies no project
file. Provider-native logs, if a provider is invoked elsewhere, are accounted for separately
from that guarantee. See [status](./references/status.md), [fleet](./references/fleet.md), and
the [runtime contract](./references/runtime.md).

## Independence and security

SDD Composy has no runtime dependency on `pwdev-flow` or `pwdev-feat`. It never infers
approval, reads secrets or fleet environment files, or merges fleet branches automatically.
Full contracts are in [`references/`](./references/).

## License

Apache-2.0. See [LICENSE](../../LICENSE).

## Setup

Run `/sdd-composy:init` before generating artifacts and choose the project language.

## Safety

Do not skip approval, QA, evidence, or verification gates.
