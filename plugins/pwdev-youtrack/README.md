# PWDEV YouTrack — Issues, Sprints & Time Tracking

> [Versão em Português](./README.pt-BR.md)

Claude Code plugin that manages [YouTrack](https://www.jetbrains.com/youtrack/)
through the **official built-in MCP server** (YouTrack 2025.3+), with an
authenticated REST fallback for what the MCP does not cover: agile boards,
sprints, time reports, attachments and bulk commands.

## What's inside

| Piece | Purpose |
|---|---|
| MCP `youtrack` | Official JetBrains server at `https://<instance>/mcp` — ~25 tools: issues CRUD, search, comments, tags, links, knowledge-base articles, `log_work` |
| Skill `youtrack` | Day-to-day issue management in natural conversation (query language, field schema discipline, confirm-before-mutate) |
| Skill `youtrack-rest` | Boards, sprints, work-item reads, attachments, bulk `/api/commands` via `scripts/yt-api.sh` |
| `/pwdev-youtrack:init` | Guided setup: instance URL, token stored in the macOS Keychain, connection test, project context |
| `/pwdev-youtrack:status` | Diagnosis: env vars, REST, MCP endpoint, session connection |
| `/pwdev-youtrack:sprint` | Sprint view, move issues between sprints, create sprints |
| `/pwdev-youtrack:report` | Time report (work items aggregated by person/day/issue) or sprint report |

## Requirements

- YouTrack **2025.3+** (Cloud or self-hosted) — the built-in MCP server ships
  from that version. Older instances still work in REST-only mode.
- A **permanent token** (Profile → Account Security → Tokens → New token,
  scope *YouTrack*).
- `curl`; macOS Keychain recommended for token storage (Linux: env var).

## Setup

Run `/pwdev-youtrack:init` and follow the steps. In short, it results in:

```sh
# ~/.zshrc
export YOUTRACK_BASE_URL="https://yourorg.youtrack.cloud"
export YOUTRACK_TOKEN="$(security find-generic-password -s pwdev-youtrack -w 2>/dev/null)"
```

The plugin's `.mcp.json` expands those env vars:

```json
{ "youtrack": { "type": "http",
  "url": "${YOUTRACK_BASE_URL:-https://example.youtrack.cloud}/mcp",
  "headers": { "Authorization": "Bearer ${YOUTRACK_TOKEN:-}" } } }
```

**Restart the Claude Code session** after setting the env vars — the
environment is captured at launch. Verify with `/mcp` and
`/pwdev-youtrack:status`.

## Token security

- The token lives in the Keychain (service `pwdev-youtrack`), never in a file
  inside any repository and never in the conversation — `check-setup.sh --store`
  reads it with masked input.
- All REST calls go through `scripts/yt-api.sh`, which builds the auth header
  internally; the token never appears in a command line or transcript.
- Diagnostics always print the token masked (`perm-***…abcd`).

## Troubleshooting

| Symptom | Cause / fix |
|---|---|
| `/mcp` shows `youtrack` failed | Env vars missing in the session → set exports, restart session |
| `MCP … 404` in status | Instance older than 2025.3 → REST-only mode |
| `REST 401` | Token invalid/expired → recreate and re-run `check-setup.sh --store` |
| Script green, MCP not connected | Session started before the env vars → restart |
