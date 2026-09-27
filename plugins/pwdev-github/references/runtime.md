# Runtimes

pwdev-github ships portable skills (`skills/github-*/SKILL.md`) and thin adapters per runtime.
The skills are the single source of truth. There are no subagents and no hooks.

| | Claude Code | Codex | Hermes Agent | OpenCode |
|---|---|---|---|---|
| Entry point | `commands/<name>.md` (wrapper) + skills | `skills/<name>/agents/openai.yaml` | `.hermes-plugin/` registration | `.opencode-plugin/install.py` links |
| Invocation | `/pwdev-github:<cmd>` | `$github-<cmd>` | `skill_view("pwdev-github:github-<cmd>")` | `skill` tool, or `/github-<cmd>` |
| Manifest | `.claude-plugin/plugin.json` | `.codex-plugin/plugin.json` | `.hermes-plugin/plugin.yaml` | none (installer) |

Commands map 1:1 to skills: `init → github-init`, `project → github-project`,
`publish → github-publish`, `status → github-status`. `github-issues` has no command: it
triggers from the request ("fecha a issue #12", "move #14 para Em andamento").

## Plugin-relative paths

`<plugin-root>/...`, `references/...`, `scripts/...` and `templates/...` in a skill are
relative to the plugin root:

- Claude Code: `${CLAUDE_PLUGIN_ROOT}`.
- Codex and Hermes: the installed plugin directory (the parent of `skills/`).
- OpenCode: two levels above the resolved `SKILL.md` (skill folders are symlinks into the
  plugin checkout).

`.planning/github.json` and `.planning/github/` are always relative to the project root.

## Tools

| Action | Claude Code | Codex | Hermes | OpenCode |
|---|---|---|---|---|
| Run `gh` / `python3 ghp.py` | `Bash` | `exec_command` | `terminal` | `bash` |
| Read a file | `Read` | `exec_command` (`sed`) | `read_file` | `read` |
| Write a file | `Write` | `apply_patch` | `write_file` | `write` |
| Ask the human | plain text or `AskUserQuestion` | end the turn and wait | end the turn and wait | end the turn and wait |

**Never invent a tool call.** Every write to GitHub needs the human's explicit yes in the same
session; a sandbox that blocks network access (Codex `workspace-write` without network, for
example) must be reported, not worked around.

## Command form shown to the user

When a skill mentions another skill (`github-project`, `prd-publish`...), show the form of the
runtime you are in: `/pwdev-github:project`, `$github-project`,
`skill_view("pwdev-github:github-project")`, `/github-project`.

## Hermes constraint on skill bodies

Hermes silently drops any skill whose body contains the literal filenames of the project
instructions files. Skill bodies never name them.
