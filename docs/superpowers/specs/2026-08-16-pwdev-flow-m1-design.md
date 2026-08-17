# PWDEV Flow M1 Design

## Objective

Create a runtime-independent successor to PWDEV Code whose first release is a native Codex plugin. The first increment must be installable, preserve the existing `pwdev-code` plugin untouched, and prove the workflow through `init`, `quick`, `review`, and `verify` skills.

## Positioning

- Product name: **PWDEV Flow**
- Plugin identifier: `pwdev-flow`
- Tagline: **Plan once. Execute anywhere. Verify independently.**
- Runtime promise: methodology and `.planning/` artifacts are portable; orchestration adapters are runtime-specific.

## Architecture

The plugin has three layers:

1. **Codex adapter** — `.codex-plugin/plugin.json` and concise skills triggered by user intent.
2. **Runtime-neutral protocol** — artifact schemas, state transitions, safety rules, and collaboration contracts under `references/`.
3. **Project state** — versionable Markdown and JSON artifacts under the consuming project's `.planning/` directory.

The Codex skills use native planning and collaboration capabilities when available. They must fall back to inline execution when no collaboration tool is available. They must not name Claude models, depend on `${CLAUDE_PLUGIN_ROOT}`, or require Claude's `Task` tool, slash commands, hooks, or agent frontmatter.

## M1 Components

### `flow-init`

Initialize `.planning/flow/`, detect greenfield or brownfield projects, preserve existing configuration, and create a neutral state file. Do not create `CLAUDE.md`; inspect `AGENTS.md` first and treat `CLAUDE.md` as optional compatibility context.

### `flow-quick`

Handle a bounded change through inspect, mini-plan, implementation, tests, review, and verification. Escalate when scope exceeds five files, introduces an architectural decision, or changes a database schema. Never commit unless the user explicitly requests it.

### `flow-review`

Review a diff or explicit file set against acceptance criteria and project conventions. Prefer independent code-review and QA workers when the user requested delegation or the runtime permits it under active collaboration policy; otherwise execute the two lenses sequentially. Write a combined report.

### `flow-verify`

Build a truth list from the objective, acceptance criteria, definition of done, and prohibitions. Attempt to refute every truth with fresh evidence. Produce `APPROVED`, `WITH_CAVEATS`, or `REJECTED`; create correction plans for rejected truths.

## Shared Contracts

- `.planning/flow/config.json` stores language and policy.
- `.planning/flow/state.md` is the workflow source of truth.
- `.planning/flow/quick/` stores quick-task plans and reports.
- `.planning/flow/reports/` stores review and verification reports.
- Full reports live in files; user-facing responses remain concise and link to artifacts.
- File writes stay inside the active repository.
- Secrets, `.env` files, private keys, credentials, and tokens are never read or copied.
- `git commit`, `git push`, branch creation, and destructive cleanup require explicit user authorization.

## Plugin Distribution

The plugin is declared by `plugins/pwdev-flow/.codex-plugin/plugin.json`. A repository-local Codex marketplace at `.agents/plugins/marketplace.json` points to `./plugins/pwdev-flow` and is independent of `.claude-plugin/marketplace.json`.

## Validation

M1 is accepted when:

- the official Codex plugin validator accepts the plugin;
- every skill passes `quick_validate.py`;
- all skill frontmatter contains only `name` and `description`;
- all local Markdown links resolve;
- forbidden Claude-specific runtime terms do not appear in the Nexus implementation;
- the four M1 skills and shared references exist;
- the existing `plugins/pwdev-code` working tree is unchanged by this increment.

## Deferred Scope

Discovery, design, full planning/execution, product roadmaps, memory management, simplification, audit, external CLI delegation, and fleet orchestration are deferred to later increments.
