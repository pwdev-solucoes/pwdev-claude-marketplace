# Runtimes

pwdev-video-tutorial ships portable skills (`skills/vtut-*/SKILL.md`), thin adapters per runtime and
one script, `scripts/tutorial.py` (standard library). It relies on:

- `playwright-cli` — exploration, login session, recording (`run-code` with `page.screencast`);
- `pwdev-media` — formats, captions, gate, paid TTS (ElevenLabs) with estimate and yes;
- the official HyperFrames CLI — local pt-BR text to speech (Kokoro) and, through
  `pwdev-video-hyperframes`, the final composition and render.

| | Claude Code | Codex | Hermes Agent |
|---|---|---|---|
| Entry point | `commands/<name>.md` (wrapper) + skills | `skills/<name>/agents/openai.yaml` | `.hermes-plugin/` registration |
| Invocation | `/pwdev-video-tutorial:<cmd>` | `$vtut-<name>` | `skill_view("pwdev-video-tutorial:vtut-<name>")` |
| Manifest | `.claude-plugin/plugin.json` | `.codex-plugin/plugin.json` | `.hermes-plugin/plugin.yaml` |

Commands map to skills: `init → vtut-setup`, `status → vtut-setup`, `explorar → vtut-explorar`,
`roadmap → vtut-roadmap`, `roteiro → vtut-roteiro`, `narrar → vtut-narrar`, `gravar → vtut-gravar`,
`montar → vtut-montar`, `revisar → vtut-revisar`.

## Paths

`<plugin-root>/...` is the plugin root (Claude Code: `${CLAUDE_PLUGIN_ROOT}`; Codex and Hermes: the
installed plugin directory). `<TUT>` is the tutorial workspace the person chooses, by default
`<projeto-do-sistema>/.pwdev-tutorial/` (add it to `.gitignore`: it holds the login session).
One folder per video inside it: `<TUT>/<video-id>/`.

| Placeholder | Meaning |
|---|---|
| `<TUT>` | workspace: `codigo.json`, `mapa-do-sistema.md`, `roadmap.json`, `sessao.json`, one folder per video |
| `<V>` | `<TUT>/<video-id>`: `roteiro.json/.md`, `narracao/`, `gravacao.webm`, `cenas.json`, `capturas/`, `tutorial.md` |
| `<EDIT>` | `<V>/edit`: `cut.mp4` (recording + narration), timeline, captions — what the video plugins read |
| `<PROJ>` | `<V>/projeto-hf`: the HyperFrames project created by `pwdev-video-hyperframes` |

## Tools

| Action | Claude Code | Codex | Hermes |
|---|---|---|---|
| Run `playwright-cli`, `python3 tutorial.py`, `pwdev-media` | `Bash` | `exec_command` | `terminal` |
| Read code / files | `Read`, `Grep` | `exec_command` (`rg`, `sed`) | `read_file`, `search_files` |
| Write `roteiro.json`, `roadmap.json`, `.md` | `Write` / `Edit` | `apply_patch` | `write_file` / `patch` |
| Look at a capture (PNG) | `Read` on the image | attach or describe | `read_file` / vision tool |
| Ask the human | plain text or `AskUserQuestion` | end the turn and wait | end the turn and wait |

**Never invent a tool call.** The login is done by the person in a visible browser; never ask for,
type or store a password. A sandbox without network or without a browser must be reported, not
worked around.

## Quoting

Text that comes from the person goes in single quotes in bash, zsh and PowerShell. A single quote
inside the text is `'\''` in bash/zsh and `''` in PowerShell.

## Hermes constraint on skill bodies

Hermes silently drops any skill whose body contains the literal filenames of the project
instructions files. Skill bodies never name them.
