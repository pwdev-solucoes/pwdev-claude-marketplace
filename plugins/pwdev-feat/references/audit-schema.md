# Audit Trail Schema (SQLite)

Database: `.planning/pwdev-audit.db` — opt-in (`"audit": true` in `.planning/config.json`), never versioned (gitignored).

**How data gets here (v3.0):**

- **Claude Code** — mechanical events are recorded automatically by the plugin's hooks
  (`hooks/hooks.json` → `scripts/audit-hook.sh`): session start/stop, executor/advisor
  started/completed with real `duration_ms`, and `.planning/` artifact writes.
- **All runtimes** — the skills call `scripts/audit-log.sh` at milestones (`event`), after each
  dispatch (`spawn`, with the model or `inherited`/`inline`) and for configuration changes
  (`config`). On Codex, Hermes and OpenCode these semantic rows are the whole trail — there are
  no hooks, so no `duration_ms` and no automatic artifact rows.
- `scripts/audit.py init` creates the schema (idempotent); every other `audit.py` command opens
  the database read-only. Agents never run inline INSERTs.

**Shared database.** `.planning/pwdev-audit.db` is shared by all PWDEV plugins
in the project. Rows are distinguished by the `plugin` column (`pwdev-feat` vs
`pwdev-code`). Either plugin's `init` may create the schema — it is identical.
Query this plugin's rows with `WHERE plugin='pwdev-feat'`. Note: an
`agent_type` without a plugin namespace could be logged by both plugins'
hooks; spawns always use `pwdev-feat:executor` / `pwdev-feat:advisor`, so
this is rare.

## Schema

```sql
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL DEFAULT (datetime('now')),
    session_id TEXT, plugin TEXT NOT NULL, command TEXT NOT NULL,
    agent TEXT, model TEXT, phase TEXT, action TEXT NOT NULL,
    target TEXT, detail TEXT, duration_ms INTEGER
);
CREATE TABLE IF NOT EXISTS decisions (
    id INTEGER PRIMARY KEY AUTOINCREMENT, event_id INTEGER REFERENCES events(id),
    timestamp TEXT NOT NULL DEFAULT (datetime('now')), phase TEXT NOT NULL,
    decision TEXT NOT NULL, rationale TEXT, alternatives TEXT, reversible INTEGER DEFAULT 1
);
CREATE TABLE IF NOT EXISTS artifacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT, event_id INTEGER REFERENCES events(id),
    path TEXT NOT NULL, type TEXT NOT NULL, phase TEXT, status TEXT DEFAULT 'active',
    created_at TEXT NOT NULL DEFAULT (datetime('now')), archived_at TEXT
);
CREATE TABLE IF NOT EXISTS config_changes (
    id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT NOT NULL DEFAULT (datetime('now')),
    field TEXT NOT NULL, old_value TEXT, new_value TEXT NOT NULL, changed_by TEXT
);
CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp);
CREATE INDEX IF NOT EXISTS idx_events_plugin ON events(plugin);
CREATE INDEX IF NOT EXISTS idx_events_command ON events(command);
```

## Action vocabulary (subset used by pwdev-feat)

`session_start`, `turn_completed`, `started`, `completed`, `failed`,
`advice_requested`, `advice_given`, `model_resolved`.

Note on `model_resolved`: the hook payload does NOT expose the subagent's
model, so the `model` column is populated semantically — `/pwdev-feat:exec`
calls `audit-log.sh spawn exec "" <agent> <model>` right after each dispatch
(rule 3 of `references/spawn-contracts.md`). Mechanical
`started`/`completed` rows from the hooks keep `model` NULL.

## Rules

- All writes are best-effort: `2>/dev/null`, never block the main task, exit 0 on any failure.
- `scripts/audit.py init` writes the ignore rules to `.planning/.gitignore` (never to the
  project's root `.gitignore`, so enabling the audit leaves no uncommitted change there):

```gitignore
pwdev-audit.db
pwdev-audit.db-journal
pwdev-audit.db-wal
.audit-tmp/
audit-report.md
audit-report.pdf
```

## Useful queries

```sql
-- This plugin's recent activity
SELECT timestamp, command, agent, action, duration_ms FROM events
WHERE plugin='pwdev-feat' ORDER BY id DESC LIMIT 50;
-- Executor average duration
SELECT AVG(duration_ms) avg_ms FROM events
WHERE plugin='pwdev-feat' AND action='completed' AND duration_ms IS NOT NULL;
-- Configuration history
SELECT timestamp, field, old_value, new_value, changed_by FROM config_changes ORDER BY id DESC;
```
