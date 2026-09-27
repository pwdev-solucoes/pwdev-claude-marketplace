# Runtimes

pwdev-feat ships one set of portable skills (`skills/feat-*/SKILL.md`) and thin adapters per
runtime. The skills are the single source of truth; an adapter only decides how a skill is
entered and which tool names its actions resolve to.

| | Claude Code | Codex | Hermes Agent | OpenCode |
|---|---|---|---|---|
| Entry point | `commands/<name>.md` (wrapper) | `skills/<name>/agents/openai.yaml` | `.hermes-plugin/` registration | `.opencode-plugin/install.py` links |
| Invocation | `/pwdev-feat:<cmd>` | `$<skill>` | `skill_view("pwdev-feat:<skill>")` | `skill` tool, or `/<skill>` |
| Manifest | `.claude-plugin/plugin.json` | `.codex-plugin/plugin.json` | `.hermes-plugin/plugin.yaml` | none (installer) |
| Hooks | `hooks/hooks.json` (audit, guard-secrets) | none | first-turn bootstrap only | none |
| Tool mapping | [claude-tools.md](claude-tools.md) | [codex-tools.md](codex-tools.md) | [hermes-tools.md](hermes-tools.md) | [opencode-tools.md](opencode-tools.md) |

Claude commands map 1:1 to skills (`<skill>` below is the name used by Codex, Hermes and
OpenCode, e.g. `$feat-exec`, `/feat-exec`): `init → feat-init`, `map-codebase → feat-map`, `setup → feat-setup`,
`feat → feat-feature`, `backend → feat-backend`, `frontend → feat-frontend`, `test → feat-test`,
`review → feat-review`, `exec → feat-exec`, `quick → feat-quick`, `status → feat-status`,
`audit → feat-audit`, `loop → feat-loop`.

## Identify yourself once

You are exactly one runtime for the whole session. Decide which from your own tool surface,
then use only that runtime's tool names. Read its mapping before dispatching anything.

## Plugin-relative paths

Paths written as `references/...`, `scripts/...`, `templates/...` or `schemas/...` in a skill are
relative to the plugin root:

- Claude Code: `${CLAUDE_PLUGIN_ROOT}`.
- Codex and Hermes: the installed plugin directory (the parent of `skills/`).
- OpenCode: the directory that contains `skills/` once the linked skill folder is resolved — two
  levels above the resolved `SKILL.md`.

Project artifacts (`.planning/feat/...`) are always relative to the project root, never to the
plugin.

## Subagent dispatch (executor, advisor)

- **Claude**: `Task`/`Agent` with `subagent_type` `pwdev-feat:executor` or `pwdev-feat:advisor`
  (the packaged `agents/*.md` carry tools and turn caps) and an explicit `model`.
- **Codex**: `spawn_agent` with `fork_turns: "none"` (the executor is deliberately fresh) and the
  full dispatch prompt; `wait_agent` with `timeout_ms` 300000–600000. Requires
  `[features] multi_agent = true`.
- **Hermes**: `delegate_task(goal=..., context=<dispatch prompt>, toolsets=[...], role="leaf")`.
- **OpenCode**: the `task` tool with the full dispatch prompt as explicit context.

The dispatch prompt is the same everywhere: [executor-contract.md](executor-contract.md) or
[advisor-contract.md](advisor-contract.md), filled per [spawn-contracts.md](spawn-contracts.md).

**Inline fallback.** If the runtime has no subagent mechanism available (or it is disabled), run
the contract inline yourself: follow the same steps, write the same artifacts, and produce the
same ≤10-line status block before presenting the result. Say that the run was inline.
**Never invent a tool call.**

## Human gates

A gate is a point where you stop, present, and wait for the human's answer. Ask in plain text
(or with the runtime's question tool, if it has one). Never infer approval from silence, from an
artifact existing, or from a previous run. Subagents never talk to the human — only the main
session does.

**Orchestrated mode.** When an Orca worker preamble is present (`feat-loop` dispatched by a
coordinator), every gate goes to the coordinator through the preamble's `ask` command instead —
[orchestrated-mode.md](orchestrated-mode.md).

## Hermes constraint on skill bodies

Hermes silently drops any skill whose body contains the literal filenames of the project
instructions files. Skill bodies refer to them indirectly ("the project instructions file");
[project-files.md](project-files.md) names them.

## Waiting for children

Never poll in a tight loop and never wait silently forever. Wait in bounded stretches with a
one-line status between them.
