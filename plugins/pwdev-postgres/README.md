# PWDEV Postgres — Queries, Schema & Safe Mutations

> [Versão em Português](./README.pt-BR.md)

Claude Code plugin that operates PostgreSQL through
[`@soarescbm/postgres-mcp`](https://github.com/soarescbm/postgres-mcp) — a
purpose-built MCP server (stdio, spawned via `npx`) exposing 14 tools:
AST-validated read-only SELECT, schema inspection, and DML/DDL with a
mandatory dry-run (preview before execute).

## What's inside

| Piece | Purpose |
|---|---|
| MCP `postgres` | `npx -y @soarescbm/postgres-mcp@1.0.0` — `run_select` (read-only, AST-validated), schema inspection (tables, indexes, constraints), DML (`insert_row`/`update_rows`/`delete_rows`) and DDL (`create/alter/drop table`, indexes), all mutations gated by dry-run + `confirm: true` |
| Skill `postgres` | Day-to-day database work in natural conversation — intent→tool map, safety rules (two-phase mutations, always `LIMIT`, never bypass the mass-update guards) |
| `/pwdev-postgres:init` | Guided setup: connection string stored in the macOS Keychain, connection test, project context |
| `/pwdev-postgres:status` | Diagnosis: env vars, connection test, npm package, live MCP probe |
| `/pwdev-postgres:esquema` | Database overview — schemas, tables, indexes, constraints, actionable findings; read-only |

## Requirements

- PostgreSQL **13–16** (the server's CI matrix).
- A connection string (`postgresql://user:pass@host:5432/db`); for shared
  databases, use a least-privilege database user — the server is **v1,
  dev/local oriented**.
- Node.js **20+** (`npx` downloads the published server on first run).

## Setup

Run `/pwdev-postgres:init` and follow the steps. In short:

```sh
# ~/.zshrc
export PG_MCP_DATABASE_URL="$(security find-generic-password -s pwdev-postgres -w 2>/dev/null)"
# export PG_MCP_STATEMENT_TIMEOUT_MS="30000"   # optional (default 10000)
# export PG_MCP_POOL_MAX="10"                  # optional (default 5)
```

The plugin's `.mcp.json` maps `PG_MCP_DATABASE_URL` to the server's
`DATABASE_URL`. The env var is **deliberately namespaced**: many projects
export `DATABASE_URL` in the shell, and a direct passthrough would silently
connect the MCP to whatever database the current project uses.

**Restart the Claude Code session** after setting the vars. Note: without a
connection string the server **exits at boot** (no placeholder mode) — `/mcp`
will show the server as failed until the var reaches the session;
`/pwdev-postgres:status` is the real proof.

The npm version is **pinned** (`@1.0.0`) for reproducibility and npx cache
hits; server releases arrive as plugin patch bumps.

## Secret security

- The connection string (it contains the password) lives in the Keychain
  (service `pwdev-postgres`), never in a repository file and never in the
  conversation — `check-setup.sh --store` reads it with masked input.
- Diagnostics always print the URL with the password masked
  (`postgresql://user:***@host:5432/db`).

## Safety model

Every mutation is two-phase: the tool call with `confirm: false` returns a
preview (`sql`, `estimatedRows`, `warnings`) and executes nothing; only a
second call with `confirm: true` — after your explicit confirmation — runs
it. `update_rows`/`delete_rows` refuse empty `where` (anti mass-mutation),
and the dry-run cannot be disabled.

## Limits

Single database per instance · no multi-statement transactions · no
migrations, roles/GRANT, TRUNCATE/COPY · btree indexes only ·
`run_select` has no automatic row limit (the skill always adds `LIMIT`) ·
BIGINT beyond 2^53 arrives as `Number` with a warning.

## Troubleshooting

| Symptom | Cause / fix |
|---|---|
| `/mcp` shows the server failed | Missing `PG_MCP_DATABASE_URL` in the session → export + restart (no placeholder mode) |
| Tools fail, `check-setup.sh` green | Session started before the env vars → restart |
| `password authentication failed` | Wrong user/password in the URL → re-run `check-setup.sh --store` |
| `ECONNREFUSED` | Wrong host/port or Postgres down (`docker compose up -d` if local) |
| `no pg_hba.conf entry … no encryption` | Server requires SSL → append `?sslmode=require` |
| `canceling statement due to statement timeout` | Query over 10 s → optimize or raise `PG_MCP_STATEMENT_TIMEOUT_MS` |
| First session slow to connect | npx downloading the package (first run only) |
