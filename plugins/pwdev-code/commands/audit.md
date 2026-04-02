---
description: Query the audit trail database for events, decisions, artifacts, and statistics
argument-hint: "[summary | events | decisions | artifacts | stats | query <SQL>]"
---

# /pwdev-code:audit — Audit Trail Query

## Role
Utility command that queries the SQLite audit database (`.planning/pwdev-audit.db`) and presents results in readable format.

## Pre-check

1. Read `.planning/config.json` — if `audit` is not `true`, stop with:
   - PT-BR: `Trilha de auditoria nao esta ativada. Execute /pwdev-code:init para habilitar.`
   - EN: `Audit trail is not enabled. Run /pwdev-code:init to enable it.`

2. Check if database exists:
   ```bash
   [ -f ".planning/pwdev-audit.db" ] || echo "NOT_FOUND"
   ```
   If NOT_FOUND, stop with:
   - PT-BR: `Banco de auditoria nao encontrado em .planning/pwdev-audit.db`
   - EN: `Audit database not found at .planning/pwdev-audit.db`

3. Verify `sqlite3` is available:
   ```bash
   command -v sqlite3 >/dev/null 2>&1 || echo "NO_SQLITE3"
   ```
   If NO_SQLITE3, stop with:
   - PT-BR: `sqlite3 nao encontrado. Instale o SQLite para usar este comando.`
   - EN: `sqlite3 not found. Install SQLite to use this command.`

## STEP 0 — Language Selection
Read `.planning/config.json` for the `lang` field (`pt-BR` or `en`).
If set, use it silently. If not set, detect from $ARGUMENTS or ask:
"Em qual idioma deseja seguir? / Which language would you like to use? 1. Portugues (PT-BR) 2. English (EN)"
Save choice to `.planning/config.json` (merge, do not overwrite other fields).
All subsequent output follows the resolved language. Technical terms stay in English.

## STEP 1 — Parse Sub-command

Parse `$ARGUMENTS` to determine the sub-command:

| Argument | Action |
|----------|--------|
| (empty) or `summary` | Go to STEP 2 — Summary Dashboard |
| `events` | Go to STEP 3 — Event Log |
| `decisions` | Go to STEP 4 — Decision Log |
| `artifacts` | Go to STEP 5 — Artifact Tracker |
| `stats` | Go to STEP 6 — Statistics |
| `query <SQL>` | Go to STEP 7 — Custom Query |

If unrecognized, show help:
```markdown
## /pwdev-code:audit

Available sub-commands:

  summary    — Dashboard with key metrics and recent activity (default)
  events     — Full event log with filters
  decisions  — All architectural/product decisions with rationale
  artifacts  — Files tracked by the framework
  stats      — Command frequency, durations, phase distribution
  query <SQL> — Run a custom SQL query against the audit database

Examples:
  /pwdev-code:audit
  /pwdev-code:audit events
  /pwdev-code:audit decisions
  /pwdev-code:audit stats
  /pwdev-code:audit query "SELECT * FROM events WHERE action='failed'"
```

---

## STEP 2 — Summary Dashboard (default)

Run the following queries:

```bash
# Total events
sqlite3 .planning/pwdev-audit.db "SELECT COUNT(*) FROM events;"

# Events by action
sqlite3 .planning/pwdev-audit.db "SELECT action, COUNT(*) as count FROM events GROUP BY action ORDER BY count DESC;"

# Last 10 events
sqlite3 -header -column .planning/pwdev-audit.db "SELECT timestamp, plugin, command, agent, action, target FROM events ORDER BY timestamp DESC LIMIT 10;"

# Total decisions
sqlite3 .planning/pwdev-audit.db "SELECT COUNT(*) FROM decisions;"

# Active artifacts count
sqlite3 .planning/pwdev-audit.db "SELECT COUNT(*) FROM artifacts WHERE status='active';"

# Failed commands (if any)
sqlite3 -header -column .planning/pwdev-audit.db "SELECT timestamp, plugin, command, detail FROM events WHERE action='failed' ORDER BY timestamp DESC LIMIT 5;"

# Config changes count
sqlite3 .planning/pwdev-audit.db "SELECT COUNT(*) FROM config_changes;"
```

Present as:
```markdown
## Audit Trail — Summary

**Total events:** N | **Decisions:** N | **Active artifacts:** N | **Config changes:** N

### Events by Action
| Action | Count |
|--------|-------|
| completed | N |
| started | N |
| ... | ... |

### Last 10 Events
| Timestamp | Plugin | Command | Agent | Action | Target |
|-----------|--------|---------|-------|--------|--------|
| ... | ... | ... | ... | ... | ... |

### Failed Commands (last 5)
[None | table]
```

---

## STEP 3 — Event Log

```bash
sqlite3 -header -column .planning/pwdev-audit.db "
  SELECT id, timestamp, plugin, command, agent, model, phase, action, target,
         SUBSTR(detail, 1, 80) as detail_preview
  FROM events
  ORDER BY timestamp DESC
  LIMIT 50;
"
```

Present as a formatted table. If there are more than 50 events, note:
- PT-BR: `Mostrando os 50 eventos mais recentes. Use /pwdev-code:audit query para consultas customizadas.`
- EN: `Showing the 50 most recent events. Use /pwdev-code:audit query for custom queries.`

---

## STEP 4 — Decision Log

```bash
sqlite3 -header -column .planning/pwdev-audit.db "
  SELECT d.id, d.timestamp, d.phase, d.decision, d.rationale,
         d.alternatives, CASE d.reversible WHEN 1 THEN 'Yes' ELSE 'No' END as reversible
  FROM decisions d
  ORDER BY d.timestamp DESC;
"
```

Present as:
```markdown
## Decisions

| # | Timestamp | Phase | Decision | Rationale | Alternatives | Reversible |
|---|-----------|-------|----------|-----------|--------------|------------|
| ... | ... | ... | ... | ... | ... | ... |
```

If no decisions, note:
- PT-BR: `Nenhuma decisao registrada na trilha de auditoria.`
- EN: `No decisions recorded in the audit trail.`

---

## STEP 5 — Artifact Tracker

```bash
# Active artifacts grouped by type
sqlite3 -header -column .planning/pwdev-audit.db "
  SELECT type, COUNT(*) as count
  FROM artifacts
  WHERE status='active'
  GROUP BY type
  ORDER BY count DESC;
"

# Full artifact list
sqlite3 -header -column .planning/pwdev-audit.db "
  SELECT id, path, type, phase, status, created_at, archived_at
  FROM artifacts
  ORDER BY created_at DESC;
"
```

Present as:
```markdown
## Artifacts

### By Type
| Type | Count |
|------|-------|
| ... | ... |

### All Artifacts
| Path | Type | Phase | Status | Created | Archived |
|------|------|-------|--------|---------|----------|
| ... | ... | ... | ... | ... | ... |
```

---

## STEP 6 — Statistics

```bash
# Command frequency
sqlite3 -header -column .planning/pwdev-audit.db "
  SELECT command, COUNT(*) as runs
  FROM events
  WHERE action='completed'
  GROUP BY command
  ORDER BY runs DESC;
"

# Average duration per command (when available)
sqlite3 -header -column .planning/pwdev-audit.db "
  SELECT command, COUNT(*) as runs,
         ROUND(AVG(duration_ms)/1000.0, 1) as avg_sec,
         ROUND(MIN(duration_ms)/1000.0, 1) as min_sec,
         ROUND(MAX(duration_ms)/1000.0, 1) as max_sec
  FROM events
  WHERE duration_ms IS NOT NULL AND action='completed'
  GROUP BY command
  ORDER BY avg_sec DESC;
"

# Events by phase
sqlite3 -header -column .planning/pwdev-audit.db "
  SELECT phase, COUNT(*) as count
  FROM events
  WHERE phase IS NOT NULL
  GROUP BY phase
  ORDER BY count DESC;
"

# Events by plugin
sqlite3 -header -column .planning/pwdev-audit.db "
  SELECT plugin, COUNT(*) as count
  FROM events
  GROUP BY plugin
  ORDER BY count DESC;
"

# Activity timeline (events per day, last 14 days)
sqlite3 -header -column .planning/pwdev-audit.db "
  SELECT DATE(timestamp) as day, COUNT(*) as events
  FROM events
  WHERE timestamp >= datetime('now', '-14 days')
  GROUP BY day
  ORDER BY day DESC;
"

# Success rate
sqlite3 .planning/pwdev-audit.db "
  SELECT
    ROUND(100.0 * SUM(CASE WHEN action='completed' THEN 1 ELSE 0 END) / COUNT(*), 1) as success_pct,
    SUM(CASE WHEN action='completed' THEN 1 ELSE 0 END) as completed,
    SUM(CASE WHEN action='failed' THEN 1 ELSE 0 END) as failed
  FROM events
  WHERE action IN ('completed', 'failed');
"
```

Present as:
```markdown
## Statistics

### Command Frequency
| Command | Runs |
|---------|------|
| ... | ... |

### Performance (avg duration)
| Command | Runs | Avg (s) | Min (s) | Max (s) |
|---------|------|---------|---------|---------|
| ... | ... | ... | ... | ... |

### Events by Phase
| Phase | Count |
|-------|-------|
| ... | ... |

### Events by Plugin
| Plugin | Count |
|--------|-------|
| ... | ... |

### Activity (last 14 days)
| Day | Events |
|-----|--------|
| ... | ... |

### Success Rate
**N%** (N completed / N failed)
```

---

## STEP 7 — Custom Query

Extract the SQL from `$ARGUMENTS` after `query `.

**Safety rules:**
- Only allow `SELECT` statements. If the query starts with `INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, `CREATE`, or `PRAGMA`, reject with:
  - PT-BR: `Apenas consultas SELECT sao permitidas. O banco de auditoria e somente leitura.`
  - EN: `Only SELECT queries are allowed. The audit database is read-only.`

Execute:
```bash
sqlite3 -header -column .planning/pwdev-audit.db "<USER_SQL>"
```

Present the raw result in a formatted table. If the query fails, show the SQLite error message.

### Quick Reference (show with results)

```markdown
### Tables: events, decisions, artifacts, config_changes

**events columns:** id, timestamp, session_id, plugin, command, agent, model, phase, action, target, detail, duration_ms
**decisions columns:** id, event_id, timestamp, phase, decision, rationale, alternatives, reversible
**artifacts columns:** id, event_id, path, type, phase, status, created_at, archived_at
**config_changes columns:** id, timestamp, field, old_value, new_value, changed_by
```

---

## STEP 8 — Audit Log (self-referential)

After presenting results, log this query:
```bash
[ -f ".planning/pwdev-audit.db" ] && sqlite3 .planning/pwdev-audit.db "INSERT INTO events (plugin, command, action, detail) VALUES ('pwdev-code', 'audit', 'completed', '{\"sub_command\": \"$SUB_COMMAND\"}');" 2>/dev/null
```
