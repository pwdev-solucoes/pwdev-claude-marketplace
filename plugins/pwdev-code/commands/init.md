---
description: Initialize the PWDEV-CODE v1.1.0 framework in a repository
---

# /pwdev-code:init — Framework Initialization

## Role
Utility agent that sets up the PWDEV-CODE v1.1.0 framework (3 layers) in a repository.

## Input
$ARGUMENTS: "greenfield" or "brownfield" (if empty, auto-detect).

## Procedure

### STEP 0 — Language Configuration

This is the initialization command, so language setup is **mandatory** here (not silent).

1. Read `.planning/config.json` — if `lang` already exists, show current setting and ask:
   ```
   Idioma atual / Current language: {lang}
   Deseja manter? / Keep it? (y/n)
   ```
   If yes → proceed. If no → go to step 2.

2. If no config or user wants to change, **always ask explicitly**:
   ```
   Em qual idioma deseja trabalhar? / Which language would you like to use?

   1. Portugues (PT-BR)
   2. English (EN)
   ```
   Wait for the user's response.

3. Save the choice to `.planning/config.json`:
   - If file exists, merge the `lang` field (do not overwrite other fields).
   - If file does not exist, create it:
     ```json
     {
       "lang": "pt-BR"
     }
     ```

4. Confirm:
   - `pt-BR`: "Idioma definido: **Portugues (PT-BR)**"
   - `en`: "Language set: **English (EN)**"

All subsequent output in this command must follow the resolved language.

Technical terms (API, CRUD, REST, endpoint) always stay in English regardless of language choice.

### STEP 0.1 — Model Profile Configuration

Model profile configuration is **mandatory** during initialization.

1. Read `.planning/config.json` — if `model_profile` already exists, show current setting and ask:
   - PT-BR: `Perfil de modelo atual: {model_profile}. Deseja manter? (s/n)`
   - EN: `Current model profile: {model_profile}. Keep it? (y/n)`
   If yes → proceed. If no → go to step 2.

2. If no config or user wants to change, present the profiles (use `{{LANG}}`):

   **PT-BR:**
   ```
   Qual perfil de modelo deseja usar para os agentes?

   1. Performance  — Opus para maioria dos agentes (melhor qualidade, maior custo)
   2. Balanced     — Opus para orquestracao, Sonnet para execucao, Haiku para scans (recomendado)
   3. Economy      — Sonnet para maioria, Haiku para scans (menor custo)

   Escolha (1-3, padrao: 2):
   ```

   **EN:**
   ```
   Which model profile would you like to use for agents?

   1. Performance  — Opus for most agents (best quality, highest cost)
   2. Balanced     — Opus for orchestration, Sonnet for execution, Haiku for scans (recommended)
   3. Economy      — Sonnet for most, Haiku for scans (lowest cost)

   Choose (1-3, default: 2):
   ```

3. Optionally ask about overrides:
   - PT-BR: `Deseja configurar overrides para agentes especificos? (s/n, padrao: n)`
   - EN: `Configure overrides for specific agents? (y/n, default: n)`

   If yes, list this plugin's agents with their profile-assigned model and let the user change individual ones.

4. Save `model_profile` (and `model_overrides` if any) to `.planning/config.json` — merge, do not overwrite.

5. Confirm:
   - PT-BR: `Perfil de modelo definido: **{profile}**`
   - EN: `Model profile set: **{profile}**`

Agent-to-role mapping: architect/planner/roadmap→sonnet(balanced), interviewer/prd→sonnet(balanced), executor/quick→sonnet(balanced), code-reviewer/qa→sonnet(balanced), researcher→sonnet(balanced), verifier→haiku(balanced). Resolution order: (1) `model_overrides[agent-name]` → (2) profile lookup → (3) agent frontmatter `model:` default.

### STEP 1 — Detection
```bash
if [ -f ".planning/state.md" ]; then
  echo "Already initialized. Use /pwdev-code:status to see current state."
  exit 0
fi

FILE_COUNT=$(find . -maxdepth 2 -type f \( -name "*.ts" -o -name "*.js" -o -name "*.php" -o -name "*.py" -o -name "*.vue" -o -name "*.jsx" \) -not -path "*/node_modules/*" -not -path "*/vendor/*" 2>/dev/null | wc -l)
[ "$FILE_COUNT" -gt 5 ] && TYPE="brownfield" || TYPE="greenfield"
```

### STEP 2 — Create Workspace Structure
```bash
# Layer 1-3 — Plugin structure
mkdir -p .claude/{commands,agents,skills}

# Context — project-level knowledge (discover + map-codebase)
mkdir -p .planning/context

# Product — PRD + Roadmap
mkdir -p .planning/product/roadmap

# Phases — one folder per phase (created dynamically by design command)
mkdir -p .planning/phases

# Quick — lightweight tasks outside phase workflow
mkdir -p .planning/quick

# Reports — health, deps, checklists
mkdir -p .planning/reports/{health,deps,checklists}

# Templates & Archive
mkdir -p .planning/{templates,archive}
```

### STEP 2.1 — Audit Trail (opt-in, disabled by default)

The audit trail records all commands, decisions, and artifacts in a local SQLite database.
It is **disabled by default** and the database file is **never versioned** (added to `.gitignore`).

1. Read `.planning/config.json` — if `audit` field already exists, show current setting and ask:
   - PT-BR: `Trilha de auditoria atual: {enabled/disabled}. Deseja manter? (s/n)`
   - EN: `Current audit trail: {enabled/disabled}. Keep it? (y/n)`
   If yes → proceed (skip to step 3 if disabled). If no → go to step 2.

2. If no config or user wants to change, ask:

   **PT-BR:**
   ```
   Deseja ativar a trilha de auditoria SQLite? (registra comandos, decisoes e artefatos)
   O arquivo .db nao e versionado (adicionado ao .gitignore).

   1. Sim — ativar auditoria
   2. Nao — desativar (padrao)

   Escolha (1-2, padrao: 2):
   ```

   **EN:**
   ```
   Enable SQLite audit trail? (records commands, decisions, and artifacts)
   The .db file is not versioned (added to .gitignore).

   1. Yes — enable audit
   2. No — disable (default)

   Choose (1-2, default: 2):
   ```

3. Save the choice to `.planning/config.json` — merge `"audit": true` or `"audit": false`.

4. If audit is **enabled** and `sqlite3` is available:

   ```bash
   if command -v sqlite3 >/dev/null 2>&1 && [ ! -f ".planning/pwdev-audit.db" ]; then
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
       CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp);
       CREATE INDEX IF NOT EXISTS idx_events_plugin ON events(plugin);
       CREATE INDEX IF NOT EXISTS idx_events_command ON events(command);
     "
   fi
   ```

   Ensure `.planning/pwdev-audit.db` is in `.gitignore`:
   ```bash
   if ! grep -q "pwdev-audit.db" .gitignore 2>/dev/null; then
     echo -e "\n# PWDEV audit trail (not versioned)\n.planning/pwdev-audit.db\n.planning/pwdev-audit.db-journal\n.planning/pwdev-audit.db-wal" >> .gitignore
   fi
   ```

5. If audit is **disabled**, skip silently. Confirm:
   - PT-BR: `Trilha de auditoria: **{ativada/desativada}**`
   - EN: `Audit trail: **{enabled/disabled}**`

### STEP 3 — Initial Files

**`.planning/config.json`:**
```json
{
  "lang": "[pt-BR|en — from STEP 0]",
  "model_profile": "[performance|balanced|economy — from STEP 0.1]",
  "model_overrides": {},
  "audit": false,
  "framework": "PWDEV-CODE",
  "version": "3.0",
  "architecture": "3-layer (commands, agents, skills)",
  "type": "[greenfield|brownfield]",
  "created": "[date]",
  "default_intensity": "standard",
  "branch_strategy": "feature-branch",
  "commit_convention": "conventional-commits"
}
```

**`.planning/state.md`:**
```markdown
# State

## Current Position
- Phase: NONE (freshly initialized)
- Active feature: —
- Status: Awaiting /pwdev-code:discover, /pwdev-code:prd or /pwdev-code:quick

## Decisions
- [date]: PWDEV-CODE v1.1.0 framework initialized — type [greenfield|brownfield]

## Blockers
- None
```

**`.claude/settings.json`:**
```json
{
  "permissions": {
    "allow": [
      "git add", "git commit", "git status", "git log", "git diff",
      "git tag", "git branch", "git checkout", "git stash",
      "mkdir -p", "cat", "ls", "find", "grep", "wc",
      "npm run", "npm test", "npm audit",
      "composer run", "composer test", "composer audit",
      "npx vitest", "npx playwright", "npx eslint", "npx tsc"
    ],
    "deny": [
      "rm -rf /", "git push --force", "git reset --hard",
      "cat .env", "cat .env.local", "cat .env.production",
      "cat *.pem", "cat *.key", "cat id_rsa*"
    ]
  }
}
```

### STEP 3.1 — Log Initialization (if audit enabled)

```bash
[ -f ".planning/pwdev-audit.db" ] && sqlite3 .planning/pwdev-audit.db "INSERT INTO events (plugin, command, action, detail) VALUES ('pwdev-code', 'init', 'completed', '{\"type\": \"$TYPE\", \"structure\": \"v1.1.0-organized\"}');" 2>/dev/null
```

### STEP 4 — If Brownfield
Suggest: "/pwdev-code:map-codebase to analyze existing repo."

### STEP 5 — Summary
```markdown
## ✅ PWDEV-CODE v1.1.0 Initialized

**Type:** [greenfield|brownfield]
**Architecture:** 3 layers (commands, agents, skills)

**Structure created:**
.claude/
├── commands/        # Orchestration (20 commands)
├── agents/          # Personas (11 agents)
├── skills/          # Knowledge packs
└── settings.json

.planning/
├── state.md, config.json
├── context/         # Project knowledge (discover + map-codebase)
├── product/         # PRD + Roadmap
├── phases/          # One folder per phase (F01-slug/, F02-slug/, ...)
│   └── F01-slug/
│       ├── spec.md, decisions.md
│       ├── plans/       # Execution plans
│       ├── execution/   # Summaries
│       ├── review/      # Code review + QA
│       └── verify/      # Acceptance verdict
├── quick/           # Lightweight tasks
├── reports/         # Health, deps, checklists
├── templates/
└── archive/

### Next steps:
1. [If brownfield] /pwdev-code:map-codebase
2. /pwdev-code:prd — create product PRD
3. /pwdev-code:roadmap — generate executable roadmap
4. /pwdev-code:discover — start first feature
```

## Prohibitions
- ❌ NEVER overwrite existing .planning/
- ❌ NEVER overwrite existing .claude/ without confirmation
- ❌ NEVER modify .gitignore without confirmation
- ❌ NEVER read .env
