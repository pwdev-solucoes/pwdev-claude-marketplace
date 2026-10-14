# Runtimes

pwdev-media ships portable skills (`skills/media-*/SKILL.md`), thin adapters per runtime and one
CLI, `pwdev-media`, that does the real work. The skills are the single source of truth. There
are no subagents, hooks (besides the Hermes bootstrap) or MCP servers.

| | Claude Code | Codex | Hermes Agent |
|---|---|---|---|
| Entry point | `commands/<name>.md` (wrapper) + skills | `skills/<name>/agents/openai.yaml` | `.hermes-plugin/` registration |
| Invocation | `/pwdev-media:<cmd>` | `$media-<name>` | `skill_view("pwdev-media:media-<name>")` |
| Manifest | `.claude-plugin/plugin.json` | `.codex-plugin/plugin.json` | `.hermes-plugin/plugin.yaml` |

Commands map to skills: `init → media-setup`, `status → media-setup`, `catalogo → media-catalogo`,
`atualizar → media-atualizar`, `gerar → media-gerar`, `custo → media-custo`,
`formatos → media-formatos`.

## Plugin-relative paths

`<plugin-root>/...` in a skill is the plugin root:

- Claude Code: `${CLAUDE_PLUGIN_ROOT}`.
- Codex and Hermes: the installed plugin directory (the parent of `skills/`).

## The CLI

Every skill starts by checking the CLI:

```bash
pwdev-media versao || uv tool install --force <plugin-root>/engine
```

`uv tool install` puts `pwdev-media` in `~/.local/bin`. A shell that does not see it yet can call
`~/.local/bin/pwdev-media` (Windows: `%USERPROFILE%\.local\bin\pwdev-media.exe`). Add `--json` to any
command when you need to parse the output. Exit codes are in `<plugin-root>/references/provedores.md`.

## Tools

| Action | Claude Code | Codex | Hermes |
|---|---|---|---|
| Run `pwdev-media`, `uv` | `Bash` | `exec_command` | `terminal` |
| Read a file | `Read` | `exec_command` (`sed`) | `read_file` |
| Write / edit a file | `Write` / `Edit` | `apply_patch` | `write_file` / `patch` |
| Ask the human | plain text or `AskUserQuestion` | end the turn and wait | end the turn and wait |

**Never invent a tool call.** A paid generation (`pwdev-media gerar ... --confirmar`) needs the
human's explicit yes in the same session, after seeing the estimate. A sandbox that blocks network
access (Codex `workspace-write` without network) must be reported, not worked around.

## Secrets

An API key is typed by the human, never pasted in the conversation:

- Claude Code: ask them to run `! pwdev-media chaves guardar <provedor>` (hidden input).
- Codex and Hermes: ask them to run `pwdev-media chaves guardar <provedor>` in their own terminal.

Never print, echo or log a key value; `pwdev-media status` only says where a key was found.

## Command form shown to the user

When a skill mentions another one, show the form of the runtime you are in:
`/pwdev-media:gerar`, `$media-gerar`, `skill_view("pwdev-media:media-gerar")`.

## Hermes constraint on skill bodies

Hermes silently drops any skill whose body contains the literal filenames of the project
instructions files. Skill bodies never name them.

## Quoting

Text that comes from the person (prompts, paths) goes in single quotes in bash, zsh and
PowerShell: double quotes turn `$97` into an empty variable. A single quote inside the text is
`'\''` in bash/zsh and `''` in PowerShell. Long text with `$` goes in a file.
