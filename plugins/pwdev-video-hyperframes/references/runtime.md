# Runtimes

pwdev-video-hyperframes ships portable skills (`skills/vhf-*/SKILL.md`), thin adapters per
runtime, a project template (`templates/projeto-hf/`) and no MCP servers or subagents. The work is
done by two command-line tools:

- `pwdev-media` (plugin pwdev-media): transcription, cut by the waveform, captions, checks, gate;
- `build.py` inside each project: builds `index.html` and drives the pinned HyperFrames CLI.

| | Claude Code | Codex | Hermes Agent |
|---|---|---|---|
| Entry point | `commands/<name>.md` (wrapper) + skills | `skills/<name>/agents/openai.yaml` | `.hermes-plugin/` registration |
| Invocation | `/pwdev-video-hyperframes:<cmd>` | `$vhf-<name>` | `skill_view("pwdev-video-hyperframes:vhf-<name>")` |
| Manifest | `.claude-plugin/plugin.json` | `.codex-plugin/plugin.json` | `.hermes-plugin/plugin.yaml` |

Commands map to skills: `init → vhf-setup`, `status → vhf-setup`, `editar → vhf-editar`,
`corte → vhf-corte`, `plano → vhf-plano`, `cenas → vhf-cenas`, `som → vhf-som`,
`revisar → vhf-revisar`, `versoes → vhf-variacoes`.

## Plugin-relative paths

`<plugin-root>/...` in a skill is the plugin root:

- Claude Code: `${CLAUDE_PLUGIN_ROOT}`.
- Codex and Hermes: the installed plugin directory (the parent of `skills/`).

## Placeholders used in the skills

| Placeholder | Meaning |
|---|---|
| `<VIDEOS>` | folder with the raw recordings (never modified) |
| `<EDIT>` | `<VIDEOS>/edit`: transcription, phrases, EDL, `cut.mp4`, timeline, captions |
| `<PROJ>` | `<VIDEOS>/<short-video-name>`: the HyperFrames project created from the template |

Every path passed to a command is absolute and in single quotes.

## Tools

| Action | Claude Code | Codex | Hermes |
|---|---|---|---|
| Run `pwdev-media`, `python3 build.py`, `npx` | `Bash` | `exec_command` | `terminal` |
| Read a file | `Read` | `exec_command` (`sed`) | `read_file` |
| Write / edit a file (`projeto.json`, scenes) | `Write` / `Edit` | `apply_patch` | `write_file` / `patch` |
| Look at a frame (PNG) | `Read` on the image | attach or describe from `hf snapshot` | `read_file` / vision tool |
| Ask the human | plain text or `AskUserQuestion` | end the turn and wait | end the turn and wait |

**Never invent a tool call.** Long steps (transcription on first run, render) may exceed a
runtime's command timeout: run them in the background when the runtime supports it, otherwise
tell the person how long it takes and run in the foreground with a long timeout.

## Official HyperFrames skills

Custom scenes are written with the official skills (`hyperframes-core`, `hyperframes-animation`,
`talking-head-recut`, `embedded-captions`…), installed by `vhf-setup` with
`npx hyperframes@<pinned> skills update`. Load them before writing a scene.

## Quoting

Text that comes from the person goes in single quotes in bash, zsh and PowerShell: double quotes
turn `$97` into an empty variable. A single quote inside the text is `'\''` in bash/zsh and `''`
in PowerShell. Long text with `$` goes in a file.

## Hermes constraint on skill bodies

Hermes silently drops any skill whose body contains the literal filenames of the project
instructions files. Skill bodies never name them.
