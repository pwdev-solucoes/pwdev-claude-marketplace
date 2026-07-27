# PWDEV GLPI — Tickets, Triage & ITSM Queue

> [Versão em Português](./README.pt-BR.md)

Claude Code plugin that manages [GLPI](https://glpi-project.org/) 10.x through
[`@soarescbm/mcp-glpi`](https://github.com/soarescbm/mcp-glpi) — a purpose-built
MCP server (stdio, spawned via `npx`) exposing 20 tools, 2 prompts and
3 resources over the GLPI REST API.

## What's inside

| Piece | Purpose |
|---|---|
| MCP `glpi` | `npx -y @soarescbm/mcp-glpi@0.3.1` — tickets CRUD + followups + solution/close, document upload & linking, ticket validations, read-only users, groups, assets (Computer/Monitor/Phone/NetworkEquipment), projects and knowledge base |
| Skill `glpi` | Day-to-day ITSM in natural conversation — intent→tool map, ITIL rules (never set priority, close only with an approved solution text, confirm before mutate) |
| `/pwdev-glpi:init` | Guided setup: API URL, PAT stored in the macOS Keychain, connection test, project context |
| `/pwdev-glpi:status` | Diagnosis: env vars, REST handshake, npm package, live MCP probe |
| `/pwdev-glpi:triagem` | Queue triage driven by the server's `triage_ticket` MCP prompt; actions executed only after confirmation |
| `/pwdev-glpi:relatorio` | Queue overview via `summarize_tickets` — by status/urgency, stale P1/P2, recommended focus; read-only |

## Requirements

- GLPI **10.x** with the REST API enabled (Setup → General → API).
- A user **API token** (PAT, ≥16 chars): User Preferences → Remote access keys.
- Node.js **20+** (`npx` downloads the published server on first run).
- Optional `GLPI_APP_TOKEN` if your instance registers API clients.

## Setup

Run `/pwdev-glpi:init` and follow the steps. In short:

```sh
# ~/.zshrc
export GLPI_BASE_URL="https://your-glpi.example.com/apirest.php"
export GLPI_PAT="$(security find-generic-password -s pwdev-glpi -w 2>/dev/null)"
# export GLPI_APP_TOKEN="..."   # only if required by your instance
```

The plugin's `.mcp.json` spawns the server with those env vars. **Restart the
Claude Code session** after setting them. Note: the server boots even without
configuration (placeholder mode — tools list but fail on invoke), so
`/mcp` showing *connected* does not prove the setup; `/pwdev-glpi:status` does.

The npm version is **pinned** (`@0.3.1`) for reproducibility and npx cache
hits; server releases arrive as plugin patch bumps.

## Token security

- The PAT lives in the Keychain (service `pwdev-glpi`), never in a repository
  file and never in the conversation — `check-setup.sh --store` reads it with
  masked input.
- Diagnostics always print the PAT masked (`abc12***…wxyz`).

## Limits

No Problems/Changes, SLA/OLA or instance administration; writes only on
tickets (documents attached to a ticket/followup/task, plus validations —
users, groups, assets, projects and KB are read-only).

## Troubleshooting

| Symptom | Cause / fix |
|---|---|
| Tools fail, `check-setup.sh` green | Session started before the env vars → restart |
| `ERROR_GLPI_LOGIN` / 401 | PAT invalid → regenerate the API token in GLPI |
| `*APP_TOKEN*` error | Instance requires an App-Token → `export GLPI_APP_TOKEN` |
| HTML instead of JSON | URL missing `/apirest.php` or REST API disabled |
| First session slow to connect | npx downloading the package (first run only) |
