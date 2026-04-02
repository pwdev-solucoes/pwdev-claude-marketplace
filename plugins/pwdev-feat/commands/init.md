---
description: Initialize the pwdev-feat framework — creates .planning/feat/ workspace structure.
---

# /pwdev-feat:init — Initialize Framework

## STEP 0 — Language Configuration

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

## STEP 0.1 — Model Profile Configuration

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

Agent-to-role mapping: planner→sonnet(balanced), executor→sonnet(balanced). Resolution order: (1) `model_overrides[agent-name]` → (2) profile lookup → (3) agent frontmatter `model:` default.

## STEP 1 — Check if already initialized

```bash
if [ -d ".planning/feat" ] && [ -d ".planning/feat/features" ]; then
  echo "ALREADY_INITIALIZED"
else
  echo "NEW"
fi
```

If already initialized:
```
⚠️ pwdev-feat already initialized.
   Workspace: .planning/feat/
   Use /pwdev-feat:status to see current features.
```
Stop here unless the user explicitly asks to reinitialize.

## STEP 2 — Detect project

```bash
# Detect stack
cat package.json 2>/dev/null | head -20
cat composer.json 2>/dev/null | head -20
cat requirements.txt 2>/dev/null | head -10
ls src/ app/ lib/ resources/ 2>/dev/null
cat CLAUDE.md 2>/dev/null | head -30
```

## STEP 3 — Create workspace

```bash
mkdir -p .planning/feat/features
```

## STEP 3.1 — Audit Trail (opt-in, disabled by default)

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

   Log the initialization event:
   ```bash
   [ -f ".planning/pwdev-audit.db" ] && sqlite3 .planning/pwdev-audit.db "INSERT INTO events (plugin, command, action, detail) VALUES ('pwdev-feat', 'init', 'completed', '{\"workspace\": \".planning/feat/\"}');" 2>/dev/null
   ```

5. If audit is **disabled**, skip silently. Confirm:
   - PT-BR: `Trilha de auditoria: **{ativada/desativada}**`
   - EN: `Audit trail: **{enabled/disabled}**`

## STEP 4 — Summary

```
✅ pwdev-feat initialized

📁 Workspace created:
  .planning/feat/
  └── features/          # Feature folders will be stored here
      └── {slug}/
          ├── plan.md        # Action plan
          └── plan.done.md   # Execution report

📦 Detected stack: [stack info]

🚀 Next steps:
  /pwdev-feat:map-codebase  → Analyze existing codebase (recommended for existing projects)
  /pwdev-feat:setup         → Generate CLAUDE.md with project conventions
  /pwdev-feat:feat "desc"   → Create a feature plan
  /pwdev-feat:quick "desc"  → Quick task (no plan, direct execution)
```

## Prohibitions
- NEVER overwrite existing `.planning/feat/` without confirmation
- NEVER read .env files
