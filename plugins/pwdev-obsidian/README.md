# PWDEV Obsidian — Notes, Search & Vault

> [Versão em Português](./README.pt-BR.md)

Claude Code plugin that manages an [Obsidian](https://obsidian.md) vault
through the **MCP server built into the "Local REST API" community plugin**
— reading, writing, and structurally editing notes (heading/block/frontmatter),
JsonLogic and free-text search, tags, the active file, and the command
palette.

## What's inside

| Piece | Purpose |
|---|---|
| MCP `obsidian` | Built into the Local REST API plugin, self-signed HTTPS at `https://127.0.0.1:27124/mcp/` — 16 tools: vault CRUD, structured patch, move/copy/delete, search (JsonLogic + free text), tags, active file, open file, commands |
| Skill `obsidian` | Day-to-day note management in natural conversation (intent → tool map, confirm-before-mutate, structured edits) |
| `/pwdev-obsidian:init` | Guided setup: Local REST API prerequisite check, API Key stored in the macOS Keychain, connection test, vault context |
| `/pwdev-obsidian:status` | Diagnosis: env vars, REST health check, MCP session connection |
| `/pwdev-obsidian:vault` | Read-only vault overview — folder structure, top tags, most recently modified notes |

## Requirements

- **Obsidian desktop app open**, with the vault you want to use loaded. The
  MCP server is the app itself running locally — not an always-on remote
  service.
- The **"Local REST API"** community plugin installed and enabled (Settings
  → Community plugins → Browse), with its built-in MCP endpoint exposed
  (check the plugin's own settings — older plugin versions only ship the
  classic REST API, without MCP).
- `curl`; macOS Keychain recommended for API Key storage (Linux: env var).

## Setup

Run `/pwdev-obsidian:init` and follow the steps. In short, it results in:

```sh
# ~/.zshrc
export OBSIDIAN_API_KEY="$(security find-generic-password -s pwdev-obsidian -w 2>/dev/null)"
# export OBSIDIAN_MCP_URL="https://127.0.0.1:<port>/mcp/"   # only if you changed the plugin's default port
```

The plugin's `.mcp.json` expands those env vars:

```json
{ "obsidian": { "type": "http",
  "url": "${OBSIDIAN_MCP_URL:-https://127.0.0.1:27124/mcp/}",
  "headers": { "Authorization": "Bearer ${OBSIDIAN_API_KEY:-}" } } }
```

**Restart the Claude Code session** after setting the env vars — the
environment is captured at launch. Verify with `/mcp` and
`/pwdev-obsidian:status`. Keep Obsidian open whenever you use this plugin.

## API Key security

- The key lives in the Keychain (service `pwdev-obsidian`), never in a file
  inside any repository and never in the conversation —
  `check-setup.sh --store` reads it with masked input.
- Diagnostics always print the key masked (`abc12***…wxyz`).
- The REST health check uses `curl -k` because the Local REST API plugin
  uses a self-signed certificate — expected, not a misconfiguration.

## Troubleshooting

| Symptom | Cause / fix |
|---|---|
| `REST … FALHOU — sem conexão` | Obsidian is closed, or the Local REST API plugin is disabled — not an API Key problem |
| `REST … FALHOU — API Key inválida` | Key invalid/rotated → recreate it in the plugin settings and re-run `check-setup.sh --store` |
| Script green, MCP not connected | Session started before the env vars → restart the session |
| `/mcp` shows `obsidian` failed after restart | Obsidian was closed or the plugin was disabled after `check-setup.sh` ran |
