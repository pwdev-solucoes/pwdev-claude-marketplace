# Runtimes

pwdev-prd ships one set of portable skills (`skills/prd-*/SKILL.md`) and thin adapters per
runtime. The skills are the single source of truth; an adapter only decides how a skill is
entered and which tool names its actions resolve to.

| | Claude Code | Codex | Hermes Agent | OpenCode |
|---|---|---|---|---|
| Entry point | `commands/<name>.md` (wrapper) | `skills/<name>/agents/openai.yaml` | `.hermes-plugin/` registration | `.opencode-plugin/install.py` links |
| Invocation | `/pwdev-prd:<cmd>` | `$prd-<cmd>` | `skill_view("pwdev-prd:prd-<cmd>")` | `skill` tool, or `/prd-<cmd>` |
| Manifest | `.claude-plugin/plugin.json` | `.codex-plugin/plugin.json` | `.hermes-plugin/plugin.yaml` | none (installer) |
| Hooks | `hooks/hooks.json` (audit, guard-secrets) | none | first-turn bootstrap only | none |
| Tool mapping | [claude-tools.md](claude-tools.md) | [codex-tools.md](codex-tools.md) | [hermes-tools.md](hermes-tools.md) | [opencode-tools.md](opencode-tools.md) |

Claude commands map 1:1 to skills: `init → prd-init`, `create → prd-create`,
`refine → prd-refine`, `list → prd-list`, `export → prd-export`, `roadmap → prd-roadmap`,
`stories → prd-stories`, `publish → prd-publish`, `audit → prd-audit`. When a skill names a command such as
`/pwdev-prd:roadmap`, show the user the form of the runtime you are in (`$prd-roadmap`,
`/prd-roadmap`, ...).

## Identify yourself once

You are exactly one runtime for the whole session. Decide which from your own tool surface,
then use only that runtime's tool names. Read its mapping before dispatching anything.

## Plugin-relative paths

Paths written as `<plugin-root>/...` — or `references/...`, `scripts/...`, `templates/...`
inside a skill — are relative to the plugin root:

- Claude Code: `${CLAUDE_PLUGIN_ROOT}`.
- Codex and Hermes: the installed plugin directory (the parent of `skills/`).
- OpenCode: two levels above the resolved `SKILL.md` (the skill folder is a symlink into the
  plugin checkout).

Project artifacts (`.planning/...`) are always relative to the project root.

## Arguments

Claude passes the command arguments as `$ARGUMENTS`; the other runtimes pass them in the
user's message. Skills call them "the arguments".

## Subagent dispatch (roadmap)

Only `prd-roadmap` dispatches a subagent: the roadmap writer, whose contract is
[roadmap-agent.md](roadmap-agent.md).

- **Claude**: `Task`/`Agent` with `subagent_type: "pwdev-prd:roadmap"` (the packaged
  `agents/roadmap.md` reads the same contract).
- **Codex**: `spawn_agent` with `fork_turns: "none"` and the full dispatch block; then
  `wait_agent` with `timeout_ms` 300000–600000. Requires `[features] multi_agent = true`.
- **Hermes**: `delegate_task(goal=..., context=<dispatch block>, toolsets=["file", "terminal"], role="leaf")`.
- **OpenCode**: the `task` tool with the full dispatch block as the prompt.

**Inline fallback.** Without a subagent mechanism, follow `roadmap-agent.md` yourself: write the
same files, run the same checker, produce the same ≤10-line summary, and say the run was
inline. **Never invent a tool call.**

## Calling another plugin

`prd-publish` hands over to the `github-publish` skill of **pwdev-github**: Claude `Skill`
tool (`pwdev-github:github-publish`) or `/pwdev-github:publish`; Codex `$github-publish`;
Hermes `skill_view("pwdev-github:github-publish")`; OpenCode the `skill` tool with
`github-publish`. If it is not installed, say how to install it and stop.

## Human gates

A gate is a point where you stop, present, and wait for the human's answer. Ask in plain text
(or with the runtime's question tool, if it has one). Never infer approval from silence, from an
artifact existing, or from a previous run. Subagents never talk to the human.

## Hermes constraint on skill bodies

Hermes silently drops any skill whose body contains the literal filenames of the project
instructions files. Skill bodies refer to them indirectly ("the project instructions file").

## Audit on other runtimes

Hooks exist only on Claude Code. Everywhere else the audit trail has only the milestone events
that skills record with `sh "<plugin-root>/scripts/audit-log.sh" ...`; that is expected.
