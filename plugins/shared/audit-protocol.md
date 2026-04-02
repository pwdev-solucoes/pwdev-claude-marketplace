# Audit Trail Protocol (SQLite)

> **INTERNAL REFERENCE** — This file is the canonical specification for the audit trail system.
> It is NOT shipped with individual plugins. Each plugin has self-contained inline instructions
> derived from this spec. Edit this file to update the spec, then sync to each plugin's init/agents.

The audit trail provides a persistent, queryable log of all actions taken by plugins.
It runs **in parallel** with the existing Markdown-based state — Markdown remains the
source of truth for agents; SQLite is the source of truth for history and analysis.

---

## Database Location

```
.planning/pwdev-audit.db
```

- **Disabled by default** — enabled via `"audit": true` in `.planning/config.json`
- Configured during any plugin's `/init` command (user chooses to enable or not)
- Created only when explicitly enabled by the user and `sqlite3` is available
- Shared across all plugins in the same project
- **Never versioned** — automatically added to `.gitignore` on creation
- If the file doesn't exist or `audit` is not `true`, logging is silently skipped (never blocks work)

---

## Schema

```sql
-- Event log (append-only) — every significant action
CREATE TABLE IF NOT EXISTS events (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp   TEXT    NOT NULL DEFAULT (datetime('now')),
    session_id  TEXT,
    plugin      TEXT    NOT NULL,
    command     TEXT    NOT NULL,
    agent       TEXT,
    model       TEXT,
    phase       TEXT,
    action      TEXT    NOT NULL,
    target      TEXT,
    detail      TEXT,
    duration_ms INTEGER
);

-- Decision log — architectural and product decisions with rationale
CREATE TABLE IF NOT EXISTS decisions (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id    INTEGER REFERENCES events(id),
    timestamp   TEXT    NOT NULL DEFAULT (datetime('now')),
    phase       TEXT    NOT NULL,
    decision    TEXT    NOT NULL,
    rationale   TEXT,
    alternatives TEXT,
    reversible  INTEGER DEFAULT 1
);

-- Artifact tracking — files created/modified by the framework
CREATE TABLE IF NOT EXISTS artifacts (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id    INTEGER REFERENCES events(id),
    path        TEXT    NOT NULL,
    type        TEXT    NOT NULL,
    phase       TEXT,
    status      TEXT    DEFAULT 'active',
    created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
    archived_at TEXT
);

-- Config change log — tracks changes to .planning/config.json
CREATE TABLE IF NOT EXISTS config_changes (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp   TEXT    NOT NULL DEFAULT (datetime('now')),
    field       TEXT    NOT NULL,
    old_value   TEXT,
    new_value   TEXT    NOT NULL,
    changed_by  TEXT
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_events_plugin ON events(plugin);
CREATE INDEX IF NOT EXISTS idx_events_command ON events(command);
CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp);
CREATE INDEX IF NOT EXISTS idx_events_phase ON events(phase);
CREATE INDEX IF NOT EXISTS idx_artifacts_status ON artifacts(status);
CREATE INDEX IF NOT EXISTS idx_artifacts_type ON artifacts(type);
```

---

## Action Types

| Action | When to log |
|--------|------------|
| `started` | Command/agent begins execution |
| `completed` | Command/agent finishes successfully |
| `failed` | Command/agent encounters an error |
| `skipped` | Step or command skipped (already done, not applicable) |
| `decision` | Architectural or product decision made |
| `artifact_created` | File created in .planning/ |
| `artifact_updated` | File updated in .planning/ |
| `artifact_archived` | File moved to archive/ |
| `config_changed` | config.json field modified |
| `gate_passed` | Phase gate approved by human |
| `gate_rejected` | Phase gate rejected by human |
| `commit` | Git commit made |

---

## How to Log (for agents)

After completing the main task, log the event using bash:

```bash
sqlite3 .planning/pwdev-audit.db "INSERT INTO events (plugin, command, agent, model, phase, action, target, detail) VALUES ('<plugin>', '<command>', '<agent>', '<model>', '<phase>', '<action>', '<target>', '<json-detail>');" 2>/dev/null
```

Rules:
- **Always use `2>/dev/null`** — never let audit failures block the main task
- **Check file exists first** — `[ -f ".planning/pwdev-audit.db" ] && sqlite3 ...`
- **Keep detail brief** — JSON with 2-3 key facts, not full content
- **Log at the END** of the task, not the beginning (so we know it completed)
- **One INSERT per significant action** — don't log every micro-step

### Detail JSON Examples

```json
{"requirements_count": 12, "nfr_count": 5}
{"spec_sections": 8, "decisions": 3}
{"tasks": 3, "waves": 2, "files_affected": 7}
{"files_created": 2, "files_modified": 3, "tests_passed": true, "commit": "abc1234"}
{"findings": 4, "critical": 0, "security": 1}
{"verdict": "APPROVED", "ac_pass_rate": "100%"}
{"skill_name": "skill-backend-laravel", "rules": 15}
```

---

## Init Step (for plugin init commands)

```bash
# Create audit database (if not exists)
if command -v sqlite3 >/dev/null 2>&1; then
  mkdir -p .planning
  sqlite3 .planning/pwdev-audit.db "
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
    CREATE INDEX IF NOT EXISTS idx_events_plugin ON events(plugin);
    CREATE INDEX IF NOT EXISTS idx_events_command ON events(command);
    CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp);
    CREATE INDEX IF NOT EXISTS idx_events_phase ON events(phase);
    CREATE INDEX IF NOT EXISTS idx_artifacts_status ON artifacts(status);
    CREATE INDEX IF NOT EXISTS idx_artifacts_type ON artifacts(type);
  "
  echo "AUDIT_DB_READY"
else
  echo "AUDIT_DB_SKIP (sqlite3 not found)"
fi
```

---

## Useful Queries (for debugging/analysis)

```sql
-- Last 20 events
SELECT timestamp, plugin, command, agent, action, target FROM events ORDER BY timestamp DESC LIMIT 20;

-- All decisions with rationale
SELECT timestamp, phase, decision, rationale FROM decisions ORDER BY timestamp;

-- Active artifacts by type
SELECT type, COUNT(*) as count FROM artifacts WHERE status='active' GROUP BY type;

-- Command frequency
SELECT command, COUNT(*) as runs FROM events WHERE action='completed' GROUP BY command ORDER BY runs DESC;

-- Average duration per command
SELECT command, ROUND(AVG(duration_ms)/1000.0, 1) as avg_seconds FROM events WHERE duration_ms IS NOT NULL GROUP BY command;

-- Config change history
SELECT timestamp, field, old_value, new_value, changed_by FROM config_changes ORDER BY timestamp;

-- Failed commands
SELECT timestamp, plugin, command, agent, detail FROM events WHERE action='failed' ORDER BY timestamp DESC;
```

---

## .gitignore

The audit database should be in `.gitignore` by default:

```
.planning/pwdev-audit.db
.planning/pwdev-audit.db-journal
.planning/pwdev-audit.db-wal
```
