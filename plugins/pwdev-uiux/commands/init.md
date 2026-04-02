---
description: Initialize the pwdev-uiux framework — detects project stack, creates .planning/ui/ workspace, checks Figma MCP.
---

# /pwdev-uiux:init — Framework Initialization

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

Agent-to-role mapping: orchestrator→opus(balanced), ux-analyst/ui-builder/design-bridge/theme-builder→sonnet(balanced), a11y-reviewer/ux-critic→sonnet(balanced), ui-scanner→haiku(balanced). Resolution order: (1) `model_overrides[agent-name]` → (2) profile lookup → (3) agent frontmatter `model:` default.

## STEP 1 — Check if already initialized

```bash
if [ -d ".planning/ui" ] && [ -f ".planning/ui/current-flow.md" ]; then
  echo "ALREADY_INITIALIZED"
else
  echo "NEW"
fi
```

If already initialized:
```
pwdev-uiux already initialized.
   Workspace: .planning/ui/
   Use /pwdev-uiux:status to see current state.
```
Stop unless user asks to reinitialize.

---

## STEP 2 — Detect project framework

```bash
node -e "
const p=require('./package.json');
const d={...p.dependencies,...p.devDependencies};
console.log('vue:', d.vue||'N/A');
console.log('nuxt:', d.nuxt||'N/A');
console.log('react:', d.react||'N/A');
console.log('next:', d.next||'N/A');
console.log('svelte:', d.svelte||'N/A');
console.log('tailwind:', d.tailwindcss||'N/A');
console.log('typescript:', d.typescript||'N/A');
// Component libraries
console.log('shadcn-vue:', d['shadcn-vue']||'N/A');
console.log('reka-ui:', d['reka-ui']||'N/A');
console.log('primevue:', d['primevue']||'N/A');
console.log('radix-ui:', d['@radix-ui/react-dialog']||'N/A');
console.log('headlessui:', d['@headlessui/react']||d['@headlessui/vue']||'N/A');
" 2>/dev/null
```

If no frontend framework detected:
```
No frontend framework detected in package.json.
pwdev-uiux works with Vue 3, React, Svelte, or any frontend framework.
Make sure you're in the right project directory.
```

---

## STEP 2.2 — Audit Trail (opt-in, disabled by default)

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

---

## STEP 3 — Create .planning/ui/ workspace

```bash
mkdir -p .planning/ui
touch .planning/ui/current-flow.md
touch .planning/ui/ux-spec.md
touch .planning/ui/figma-spec.md
touch .planning/ui/component-log.md
touch .planning/ui/review-findings.md
```

Write initial state to `.planning/ui/current-flow.md`:
```markdown
# pwdev-uiux — State

## Active flow
- Status: no active flow
- Phase: —
- Pending gate: —
- Initialized: [timestamp]
- Stack: not configured (run /pwdev-uiux:stack)

## History
- [timestamp]: Framework initialized
```

---

## STEP 4 — Configure UI stack

Prompt the user to configure the stack:

```
Which UI stack does this project use?

1. shadcn-vue      — Vue 3 + shadcn-vue + Reka UI v2 + Tailwind (default)
2. shadcn-react    — React + shadcn/ui + Radix UI + Tailwind
3. primevue        — Vue 3 + PrimeVue + Tailwind
4. untitled-ui     — React + Untitled UI + Radix UI + Tailwind
5. tailwind-plus   — Any framework + Tailwind Plus + Headless UI
6. custom          — I'll describe my stack

Pick a number or name (default: auto-detect):
```

If user picks or auto-detect succeeds → run `/pwdev-uiux:stack` logic to create `.planning/ui/stack.json`.

---

## STEP 5 — Check Figma MCP

Try `mcp:figma → whoami` to confirm connection.

If not configured:
```
Figma MCP: Not configured (optional)
To set up: /pwdev-uiux:setup-figma
```

---

## STEP 5.1 — Log Initialization (if audit enabled)

```bash
[ -f ".planning/pwdev-audit.db" ] && sqlite3 .planning/pwdev-audit.db "INSERT INTO events (plugin, command, action, detail) VALUES ('pwdev-uiux', 'init', 'completed', '{\"workspace\": \".planning/ui/\"}');" 2>/dev/null
```

## STEP 6 — Initialization report

```
pwdev-uiux initialized

Detected stack:
  Framework:    [Vue 3 / React / Svelte / ...]
  Components:   [shadcn-vue / shadcn/ui / PrimeVue / ...]
  Styling:      [Tailwind / ...]
  TypeScript:   [yes / no]

Workspace created:
  .planning/ui/
  ├── current-flow.md
  ├── ux-spec.md
  ├── figma-spec.md
  ├── component-log.md
  ├── review-findings.md
  └── stack.json

Integrations:
  Figma MCP:  [connected / not configured]

Next steps:
  /pwdev-uiux:stack          → Change UI stack configuration
  /pwdev-uiux:setup-figma    → Connect Figma
  /pwdev-uiux:scan           → Analyze existing UI
  /pwdev-uiux:start "task"   → Start new UI development
```

## Prohibitions
- NEVER overwrite existing `.planning/ui/` without confirmation
- NEVER read .env files
- NEVER install packages without asking
