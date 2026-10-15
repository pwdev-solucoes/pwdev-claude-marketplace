# Runtimes

pwdev-video-remotion ships portable skills (`skills/vrm-*/SKILL.md`), thin adapters per runtime, a
project template (`templates/projeto-remotion/`) and no MCP servers or subagents. The work is done by
two command-line tools:

- `pwdev-media` (plugin pwdev-media): transcription, cut by the waveform, captions, render plan, gate;
- `build.py` inside each project: writes the render data and drives the pinned Remotion CLI.

| | Claude Code | Codex | Hermes Agent |
|---|---|---|---|
| Entry point | `commands/<name>.md` (wrapper) + skills | `skills/<name>/agents/openai.yaml` | `.hermes-plugin/` registration |
| Invocation | `/pwdev-video-remotion:<cmd>` | `$vrm-<name>` | `skill_view("pwdev-video-remotion:vrm-<name>")` |
| Manifest | `.claude-plugin/plugin.json` | `.codex-plugin/plugin.json` | `.hermes-plugin/plugin.yaml` |

Commands map to skills: `init → vrm-setup`, `status → vrm-setup`, `editar → vrm-editar`,
`corte → vrm-corte`, `plano → vrm-plano`, `cenas → vrm-cenas`, `som → vrm-som`,
`revisar → vrm-revisar`, `versoes → vrm-variacoes`.

## Plugin-relative paths

`<plugin-root>/...` in a skill is the plugin root:

- Claude Code: `${CLAUDE_PLUGIN_ROOT}`.
- Codex and Hermes: the installed plugin directory (the parent of `skills/`).

## Placeholders used in the skills

| Placeholder | Meaning |
|---|---|
| `<VIDEOS>` | folder with the raw recordings (never modified) |
| `<EDIT>` | `<VIDEOS>/edit`: transcription, phrases, EDL, `cut.mp4`, timeline, captions |
| `<PROJ>` | `<VIDEOS>/<short-video-name>`: the Remotion project created from the template |

Every path passed to a command is absolute and in single quotes.

## Tools

| Action | Claude Code | Codex | Hermes |
|---|---|---|---|
| Run `pwdev-media`, `python3 build.py`, `npm` | `Bash` | `exec_command` | `terminal` |
| Read a file | `Read` | `exec_command` (`sed`) | `read_file` |
| Write / edit a file (`projeto.json`, scenes) | `Write` / `Edit` | `apply_patch` | `write_file` / `patch` |
| Look at a frame (PNG from `build.py quadro`) | `Read` on the image | attach or describe | `read_file` / vision tool |
| Ask the human | plain text or `AskUserQuestion` | end the turn and wait | end the turn and wait |

**Never invent a tool call.** Long steps (`instalar`, first render, transcription) may exceed a
runtime's command timeout: run them in the background when the runtime supports it, otherwise tell
the person how long it takes and use a long timeout. `npm install` needs network: a sandbox without
network must be reported, not worked around.

## Official Remotion skills

Custom scenes are written with the official skills from `remotion-dev/skills`, installed by
`vrm-setup` with `npx --yes skills add remotion-dev/skills`. Load them before writing a scene.

## Quoting

Text that comes from the person goes in single quotes in bash, zsh and PowerShell: double quotes turn
`$97` into an empty variable. A single quote inside the text is `'\''` in bash/zsh and `''` in
PowerShell. Long text with `$` goes in a file.

## Hermes constraint on skill bodies

Hermes silently drops any skill whose body contains the literal filenames of the project
instructions files. Skill bodies never name them.
