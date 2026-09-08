# SDD Composy — Portable Spec-Driven Development

> [Versão em português](./README.pt-BR.md)

SDD Composy is an approval-gated workflow that runs on Claude Code and Codex from one portable package. Both runtimes use the same lifecycle, schemas, skills, references, scripts, and templates; a workflow can move between hosts without changing its meaning.

Human-readable contracts live under `tasks/prd-<slug>/`. Operational state lives under `.planning/sdd-composy/`. Generated project Markdown targets OKF v0.2, requires a non-empty `type`, and permits unknown extension fields. Supported JSON and Markdown updates preserve unknown fields.

## Runtime entry points

Claude Code discovers `.claude-plugin/plugin.json` and exposes thin command adapters as `/sdd-composy:<name>`. Codex discovers `.codex-plugin/plugin.json` and its `skills` root, then exposes the shared skills as `$sdd-composy-<name>`.

Claude commands contain no independent workflow policy. They select the matching portable skill, forward arguments and context, and map host tool names. The shared core remains authoritative for lifecycle gates, artifacts, state transitions, safety, and orchestration. See the exact [runtime contract](./references/runtime.md).

## Workflow

```text
INIT -> MAP -> PRD -> STORIES -> TECHSPEC -> TASKS
                                            |
                              EXECUTE -> QA -> EVIDENCE -> REVIEW -> VERIFY -> COMPLETE
```

Product and execution gates require explicit human approval. Verification reproduces fresh evidence. Reduced `QUICK`, bounded `LOOP`, and isolated `FLEET` paths retain the same durable contracts and safety rules.

## Independence and safety

SDD Composy has no runtime dependency on `pwdev-flow` or `pwdev-feat`. It never infers approval, reads secrets or fleet environment files, or merges fleet branches automatically. Full contracts are in [`references/`](./references/).

## License

Apache-2.0. See [LICENSE](../../LICENSE).
