# SDD Composy — Portable Spec-Driven Development

> [Versão em português](./README.pt-BR.md)

SDD Composy is an approval-gated workflow that runs on Claude Code and Codex from one portable package. Both runtimes use the same lifecycle, schemas, skills, references, scripts, and templates; a workflow can move between hosts without changing its meaning.

Human-readable contracts live under `tasks/prd-<slug>/`. Operational state lives under `.planning/sdd-composy/`. Generated project Markdown targets OKF v0.2, requires a non-empty `type`, and permits unknown extension fields. Supported JSON and Markdown updates preserve unknown fields.

## Artifact language

Run `/sdd-composy:init` with `pt-BR` or `en-US` to select the language for human-facing
artifacts. If the language is omitted, init asks you to choose and writes no artifacts
until a choice is made. The selection is persisted in `.planning/sdd-composy/config.json`;
all downstream skills consume it without asking again. Before initialization they return
`{"status":"not_initialized","next_action":"run_init"}`.

PRDs, stories, TechSpecs, task descriptions, QA/evidence reports, and status prose follow
the selected language. Machine keys, IDs, schemas, filenames, lifecycle values, and command
names remain English, preserving compatibility across Claude Code and Codex. Invalid
language values fail without changing the existing configuration. See the full [language
and workflow contract](./references/workflow.md).

## Runtime entry points

Claude Code discovers `.claude-plugin/plugin.json` and exposes thin command adapters as `/sdd-composy:<name>`. Codex discovers `.codex-plugin/plugin.json` and its `skills` root, then exposes the shared skills as `$sdd-composy-<name>`.

Claude commands contain no independent workflow policy. They select the matching portable skill, forward arguments and context, and map host tool names. The shared core remains authoritative for lifecycle gates, artifacts, state transitions, safety, and orchestration. See the exact [runtime contract](./references/runtime.md).

## Workflow

```text
INIT -> MAP -> PRD -> STORIES -> TECHSPEC -> TASKS
                                            |
                              EXECUTE -> QA -> EVIDENCE -> REVIEW -> VERIFY -> COMPLETE
```

Product and execution gates require explicit human approval. Verification reproduces fresh evidence. Reduced `QUICK`, bounded `LOOP`, and isolated `FLEET` paths retain the same durable contracts and safety rules. Fleet launch accepts only ready tasks, preserves recoverable branches, uses cmux for presentation when available, and never merges automatically.

## Independence and safety

SDD Composy has no runtime dependency on `pwdev-flow` or `pwdev-feat`. It never infers approval, reads secrets or fleet environment files, or merges fleet branches automatically. Full contracts are in [`references/`](./references/).

## License

Apache-2.0. See [LICENSE](../../LICENSE).
# Setup

Execute `/sdd-composy:init` antes de gerar artefatos e escolha o idioma do projeto.

# Segurança

Não pule gates de aprovação, QA, evidência ou verificação.
