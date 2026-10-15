# Runtimes

pwdev-social-media ships portable skills (`skills/social-*/SKILL.md`), thin adapters per runtime, four
Claude Code subagents (`agents/`), two MCP servers (Figma, Notion) and no scripts. Every paid call goes
through the core CLI `pwdev-media` (plugin pwdev-media ≥ 0.4.0).

| | Claude Code | Codex | Hermes Agent |
|---|---|---|---|
| Entry point | `commands/<name>.md` (wrapper) + skills | `skills/<name>/agents/openai.yaml` | `.hermes-plugin/` registration |
| Invocation | `/pwdev-social-media:<cmd>` | `$social-<name>` | `skill_view("pwdev-social-media:social-<name>")` |
| Manifest | `.claude-plugin/plugin.json` | `.codex-plugin/plugin.json` | `.hermes-plugin/plugin.yaml` |
| Figma / Notion MCP | `.mcp.json` (automatic) | `.mcp.json` via the Codex manifest, or `codex mcp add` | `mcp_servers` in `~/.hermes/config.yaml` |

Commands map to skills: `init → social-contexto`, `status → social-contexto`, `criar → social-criar`,
`gerar → social-imagem`, `carrossel → social-carrossel`, `video → social-video`,
`revisar → social-revisao`, `exportar → social-entrega`, `custo → social-custo`,
`formatos → social-formatos`, `lote → social-lote`.

## Plugin-relative paths

`<plugin-root>/...` in a skill is the plugin root:

- Claude Code: `${CLAUDE_PLUGIN_ROOT}`.
- Codex and Hermes: the installed plugin directory (the parent of `skills/`).

Project files (`.claude/pwdev-social-context.md`, `.pwdev-social/...`) are relative to the project root
in every runtime.

## Subagents

Four roles keep long or costly work out of the main context: `art-director` (concept),
`asset-generator` (paid generation), `figma-builder` (composition), `creative-reviewer` (quality gate).

- **Claude Code:** dispatch the subagent in `agents/<name>.md`, passing `LANGUAGE`, `ASSET_LANGUAGE`
  and the inputs its contract lists.
- **Codex and Hermes:** no plugin subagents — run the same steps inline, following the skill the
  subagent follows (`social-conceito`, `social-imagem`/`social-video`, `social-figma`,
  `social-revisao`).

Skills say "subagent when the runtime has one, inline otherwise".

## Tools

| Action | Claude Code | Codex | Hermes |
|---|---|---|---|
| Run `pwdev-media` | `Bash` | `exec_command` | `terminal` |
| Read a file / look at an image | `Read` | `exec_command` (`sed`), attached image | `read_file` / vision tool |
| Write / edit a file | `Write` / `Edit` | `apply_patch` | `write_file` / `patch` |
| Comparison grid for curation | Artifact | HTML file in `.pwdev-social/curadoria/` | HTML file in `.pwdev-social/curadoria/` |
| Figma | MCP `figma` tools (load `/figma-use` first) | same MCP when configured | same MCP when configured |
| Ask the human | plain text or `AskUserQuestion` | end the turn and wait | end the turn and wait |

**Never invent a tool call.** Without the Figma MCP, composition is delivered as a layered
specification and the skill says so. A sandbox without network (Codex `workspace-write`) cannot
generate: report it and stay in prompt mode.

## Money and keys

- A paid generation is always two calls: `pwdev-media gerar <item> ... --estimar`, show the estimate,
  wait for the person's explicit yes in this session, then the same command with `--confirmar`.
- Keys are typed by the person, never pasted in the conversation:
  - Claude Code: ask them to run `! pwdev-media chaves guardar <provedor>` (hidden input);
  - Codex and Hermes: `pwdev-media chaves guardar <provedor>` in their own terminal.
- Exit codes of `pwdev-media gerar`: 3 needs the yes · 4 monthly budget · 5 provider/contract error
  (stop and report) · 6 no key (prompt mode) · 7 item without adapter.

## Quoting

Prompts and paths go in single quotes in bash, zsh and PowerShell: double quotes turn `$97` into an
empty variable. A single quote inside the text is `'\''` in bash/zsh and `''` in PowerShell. Long text
with `$` goes in a file.

## Command form shown to the user

When a skill mentions another one, show the form of the runtime you are in:
`/pwdev-social-media:gerar`, `$social-imagem`, `skill_view("pwdev-social-media:social-imagem")`.

## Hermes constraint on skill bodies

Hermes silently drops any skill whose body contains the literal filenames of the project instructions
files. Skill bodies never name them.
