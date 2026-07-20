# Audit Trail Schema (SQLite)

Database: `.planning/pwdev-audit.db` — opt-in (`"audit": true` in `.planning/config.json`), never versioned (gitignored).

**How data gets here (v2.0):** mechanical events are recorded automatically by the plugin's hooks (`hooks/hooks.json` → `scripts/audit-hook.sh`): session start/stop, subagent started/completed with real `duration_ms`, and `.planning/` artifact writes. Semantic entries (phase gates, decisions) are recorded by commands calling `scripts/audit-log.sh`. Agents do NOT run inline INSERTs anymore.

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

## Action vocabulary

`session_start`, `turn_completed`, `started`, `completed`, `failed`, `gate_passed`, `gate_rejected`, `decision`, `artifact_created`, `commit`, `memory_captured`, `memory_forgotten`, `simplify_proposed`, `simplify_applied`, `advice_requested`, `advice_given`, `external_review`, `model_resolved`.

Note on `model_resolved`: the hook payload does NOT expose the subagent's
model, so the `model` column is populated semantically — orchestrator
commands call `audit-log.sh spawn <command> <phase> <agent> <model> [detail]`
right after each Task spawn (rule 3 of `references/spawn-contracts.md`).
Mechanical `started`/`completed` rows from the hooks keep `model` NULL.

## Rules

- All writes are best-effort: `2>/dev/null`, never block the main task, exit 0 on any failure.
- `.gitignore` must contain:

```gitignore
.planning/pwdev-audit.db
.planning/pwdev-audit.db-journal
.planning/pwdev-audit.db-wal
.planning/.audit-tmp/
.planning/audit-report.md
.planning/audit-report.pdf
```

## Useful queries

```sql
-- Recent activity
SELECT timestamp, command, agent, action, duration_ms FROM events ORDER BY id DESC LIMIT 50;
-- Average subagent duration
SELECT agent, COUNT(*) n, AVG(duration_ms) avg_ms FROM events
WHERE action='completed' AND duration_ms IS NOT NULL GROUP BY agent;
-- Decisions per phase
SELECT phase, decision, rationale FROM decisions ORDER BY id DESC;
-- Which model ran each spawn (per-task complexity routing evidence)
SELECT timestamp, command, agent, model, detail FROM events
WHERE action='model_resolved' ORDER BY id DESC;
```
