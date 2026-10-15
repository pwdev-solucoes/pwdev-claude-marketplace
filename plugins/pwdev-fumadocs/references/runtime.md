# Runtimes

pwdev-fumadocs ships portable skills (`skills/fumadocs-*/SKILL.md`) and thin adapters per
runtime. The skills are the single source of truth. There are no subagents and no hooks.

| | Claude Code | Codex | Hermes Agent | OpenCode |
|---|---|---|---|---|
| Entry point | `commands/<name>.md` (wrapper) + skills | `skills/<name>/agents/openai.yaml` | `.hermes-plugin/` registration | `.opencode-plugin/install.py` links |
| Invocation | `/pwdev-fumadocs:<cmd>` | `$fumadocs-<cmd>` | `skill_view("pwdev-fumadocs:fumadocs-<cmd>")` | `skill` tool, or `/fumadocs-<cmd>` |
| Manifest | `.claude-plugin/plugin.json` | `.codex-plugin/plugin.json` | `.hermes-plugin/plugin.yaml` | none (installer) |
| Fumadocs MCP | `.mcp.json` (automatic) | MCP config of Codex (`README.codex.md`) | `mcp_servers` in `~/.hermes/config.yaml` (`README.hermes.md`) | `mcp` in `opencode.json` (plugin README) |

Commands map 1:1 to skills: `setup → fumadocs-setup`, `content → fumadocs-content`,
`feature → fumadocs-feature`, `doctor → fumadocs-doctor`.

## Plugin-relative paths

`<plugin-root>/...`, `references/...` and `scripts/...` in a skill are relative to the plugin
root:

- Claude Code: `${CLAUDE_PLUGIN_ROOT}`.
- Codex and Hermes: the installed plugin directory (the parent of `skills/`).
- OpenCode: two levels above the resolved `SKILL.md` (skill folders are symlinks into the
  plugin checkout).

Everything else (`package.json`, `content/docs`, `lib/source.ts`) is relative to the project
root — the directory of the app's `package.json`, which may be a workspace package.

## Tools

| Action | Claude Code | Codex | Hermes | OpenCode |
|---|---|---|---|---|
| Run `python3 fdscan.py`, `npx`, `pnpm` | `Bash` | `exec_command` | `terminal` | `bash` |
| Read a file | `Read` | `exec_command` (`sed`) | `read_file` | `read` |
| Write / edit a file | `Write` / `Edit` | `apply_patch` | `write_file` / `patch` | `write` / `edit` |
| Fumadocs docs | MCP `fumadocs` tools, else `curl` | same | same | same |
| Ask the human | plain text or `AskUserQuestion` | end the turn and wait | end the turn and wait | end the turn and wait |

**Never invent a tool call.** Installing packages, running a generator (`create-fumadocs-app`,
`@fumadocs/cli`) and overwriting existing files need the human's explicit yes in the same
session. A sandbox that blocks network access (Codex `workspace-write` without network, for
example) must be reported, not worked around.

## Command form shown to the user

When a skill mentions another skill (`fumadocs-feature`, `fumadocs-doctor`...), show the form
of the runtime you are in: `/pwdev-fumadocs:feature`, `$fumadocs-feature`,
`skill_view("pwdev-fumadocs:fumadocs-feature")`, `/fumadocs-feature`.

## Hermes constraint on skill bodies

Hermes silently drops any skill whose body contains the literal filenames of the project
instructions files. Skill bodies never name them.
