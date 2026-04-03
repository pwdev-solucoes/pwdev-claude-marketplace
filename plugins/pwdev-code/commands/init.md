---
description: Initialize the PWDEV-CODE framework, map existing codebases, configure MCP servers, detect stack, or generate CLAUDE.md
argument-hint: "[map | mcp | stack | claude] (default: initialize folders)"
---

# /pwdev-code:init — Framework Initialization & Setup

## Role
Multi-purpose initialization and setup utility. Routes to the appropriate flow based on $ARGUMENTS.

## Input
$ARGUMENTS: subcommand (optional).
- (empty) or `greenfield` or `brownfield` → initialize .planning/ structure (default)
- `map` → analyze existing codebase (brownfield documentation)
- `mcp` → configure MCP servers (.mcp.json)
- `stack` → detect and configure project stack
- `claude` → generate CLAUDE.md operational memory file

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

### STEP 1 — Route Subcommand

Parse $ARGUMENTS:

- **`map`** → go to STEP 5 (Codebase Mapping)
- **`mcp`** → go to STEP 6 (MCP Server Configuration)
- **`stack`** → go to STEP 7 (Stack Detection & Config)
- **`claude`** → go to STEP 8 (Generate CLAUDE.md)
- **empty, `greenfield`, or `brownfield`** → go to STEP 2 (Framework Initialization)

---

## STEP 2 — Framework Initialization (default)

### STEP 2.0.1 — Model Profile Configuration

Model profile configuration is **mandatory** during initialization.

1. Read `.planning/config.json` — if `model_profile` already exists, show current setting and ask:
   - PT-BR: `Perfil de modelo atual: {model_profile}. Deseja manter? (s/n)`
   - EN: `Current model profile: {model_profile}. Keep it? (y/n)`
   If yes → proceed. If no → go to step 2.

2. If no config or user wants to change, present the profiles:

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

### STEP 2.1 — Detection
```bash
if [ -f ".planning/state.md" ]; then
  echo "Already initialized. Use /pwdev-code:session to see current state."
  exit 0
fi

FILE_COUNT=$(find . -maxdepth 2 -type f \( -name "*.ts" -o -name "*.js" -o -name "*.php" -o -name "*.py" -o -name "*.vue" -o -name "*.jsx" \) -not -path "*/node_modules/*" -not -path "*/vendor/*" 2>/dev/null | wc -l)
[ "$FILE_COUNT" -gt 5 ] && TYPE="brownfield" || TYPE="greenfield"
```

### STEP 2.2 — Create Workspace Structure
```bash
# Layer 1-3 — Plugin structure
mkdir -p .claude/{commands,agents,skills}

# Context — project-level knowledge (discover + init map)
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

### STEP 2.3 — Audit Trail (opt-in, disabled by default)

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

### STEP 2.4 — Initial Files

**`.planning/config.json`:**
```json
{
  "lang": "[pt-BR|en — from STEP 0]",
  "model_profile": "[performance|balanced|economy — from STEP 2.0.1]",
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
- Status: Awaiting /pwdev-code:discover, /pwdev-code:product prd or /pwdev-code:quick

## Decisions
- [date]: PWDEV-CODE v1.2.0 framework initialized — type [greenfield|brownfield]

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

### STEP 2.5 — Log Initialization (if audit enabled)

```bash
[ -f ".planning/pwdev-audit.db" ] && sqlite3 .planning/pwdev-audit.db "INSERT INTO events (plugin, command, action, detail) VALUES ('pwdev-code', 'init', 'completed', '{\"type\": \"$TYPE\", \"structure\": \"v1.2.0-organized\"}');" 2>/dev/null
```

### STEP 2.6 — If Brownfield
Suggest: "/pwdev-code:init map to analyze existing repo."

### STEP 2.7 — Summary
```markdown
## ✅ PWDEV-CODE v1.2.0 Initialized

**Type:** [greenfield|brownfield]
**Architecture:** 3 layers (commands, agents, skills)

**Structure created:**
.claude/
├── commands/        # Orchestration (14 commands)
├── agents/          # Personas (11 agents)
├── skills/          # Knowledge packs
└── settings.json

.planning/
├── state.md, config.json
├── context/         # Project knowledge (discover + init map)
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
1. [If brownfield] /pwdev-code:init map
2. /pwdev-code:init claude — generate CLAUDE.md
3. /pwdev-code:product prd — create product PRD
4. /pwdev-code:product roadmap — generate executable roadmap
5. /pwdev-code:discover — start first feature
```

---

## STEP 5 — Codebase Mapping (Brownfield)

> Invoked with `/pwdev-code:init map`

### Role
You are a technical auditor. You analyze an existing repository and document everything
that PWDEV-CODE agents need to work without introducing inconsistencies.
You NEVER modify code. You generate DOCUMENTATION.

### STEP 5.1 — Stack and Infrastructure
```bash
cat package.json 2>/dev/null | head -40
cat composer.json 2>/dev/null | head -40
cat requirements.txt go.mod Cargo.toml Gemfile 2>/dev/null | head -30
node -v 2>/dev/null; php -v 2>/dev/null | head -1; python --version 2>/dev/null
cat docker-compose.yml Dockerfile 2>/dev/null | head -40
ls .github/workflows/ 2>/dev/null
```

### STEP 5.2 — Structure and Patterns
```bash
find . -maxdepth 2 -type d | grep -v node_modules | grep -v vendor | grep -v .git | sort
find . -type f | grep -v node_modules | grep -v vendor | grep -v .git | sed 's/.*\.//' | sort | uniq -c | sort -rn | head -15
cat routes/web.php routes/api.php 2>/dev/null
```

### STEP 5.3 — Conventions
```bash
cat .editorconfig .prettierrc* .eslintrc* phpcs.xml* tsconfig.json 2>/dev/null
git log --oneline -20
ls app/Models/ app/Http/Controllers/ src/components/ 2>/dev/null | head -10
```

### STEP 5.4 — Tests
```bash
cat phpunit.xml* jest.config* vitest.config* pytest.ini 2>/dev/null | head -20
find . -path "*/test*" \( -name "*.test.*" -o -name "*Test.php" -o -name "test_*.py" \) 2>/dev/null | wc -l
```

### STEP 5.5 — Dependencies and Risks
```bash
cat .env.example 2>/dev/null
npm audit --json 2>/dev/null | head -20
composer audit 2>/dev/null
ls database/migrations/ migrations/ 2>/dev/null | tail -10
grep -rl "auth\|login\|password\|payment\|stripe\|webhook" --include="*.php" --include="*.ts" --include="*.js" app/ src/ 2>/dev/null | head -15
```

### STEP 5.6 — Generate Documentation
Create `.planning/context/` with 4 files:

**`architecture.md`** — Stack, pattern, directory structure, inter-module dependencies.
**`conventions.md`** — Naming (classes, methods, files, tables), imports, commits, patterns.
**`dependencies.md`** — Production + dev (table: package, version, purpose), vulnerabilities, outdated.
**`concerns.md`** — Technical risks, technical debt, sensitive areas, observations.

### STEP 5.7 — Summary
```markdown
## 🗺️ Codebase Map

**Stack:** [X] [version]
**Pattern:** [architectural]
**Size:** ~[N] files, [N] tests
**Health:** vulnerabilities [N], coverage [low/medium/high], conventions [consistent/not]
**Risk areas:** [list]

📁 Documentation: .planning/context/
👉 Next: /pwdev-code:discover
```

### Codebase Mapping Prohibitions
- ❌ NEVER read .env (only .env.example)
- ❌ NEVER modify any file
- ❌ NEVER run destructive commands
- ❌ NEVER expose discovered secrets

---

## STEP 6 — MCP Server Configuration

> Invoked with `/pwdev-code:init mcp`

### STEP 6.1 — Detect Current State
```bash
if [ -f ".mcp.json" ]; then
  echo "EXISTING"
else
  echo "NEW"
fi
```

If `.mcp.json` exists → show current servers, ask: "Add servers to existing config or replace?"

### STEP 6.2 — Detect Stack (silent, ~10s)
```bash
cat package.json 2>/dev/null | head -30
cat composer.json 2>/dev/null | head -30
ls src/ app/ resources/ 2>/dev/null
cat CLAUDE.md .planning/phases/{active-phase-slug}/spec.md 2>/dev/null | head -50
```

### STEP 6.3 — Present Server Catalog

Show available servers organized by category. Mark recommended ones based on detected stack.

```
## MCP Server Catalog

### UI Frameworks
| Server | Package | Requires API Key | Recommended |
|--------|---------|:-:|:-:|
| primevue | @primevue/mcp | No | [if Vue detected] |
| shadcn | @anthropic/mcp-server-shadcn-ui | No | [if React detected] |
| chakra-ui | @anthropic/mcp-server-chakra-ui | No | [if React detected] |

### Documentation
| Server | Package | Requires API Key | Recommended |
|--------|---------|:-:|:-:|
| context7 | @upstash/context7-mcp | Yes | Always |

### DevOps & Integrations
| Server | Package | Requires API Key | Recommended |
|--------|---------|:-:|:-:|
| github | @modelcontextprotocol/server-github | Yes (PAT) | Always |
| supabase | @supabase/mcp-server-supabase@latest | Yes | [if Supabase detected] |

### Databases
| Server | Package | Requires API Key | Recommended |
|--------|---------|:-:|:-:|
| postgres | @modelcontextprotocol/server-postgres | Yes (conn string) | [if PG detected] |
| redis | @modelcontextprotocol/server-redis | No | [if Redis detected] |

### Design
| Server | Package | Requires API Key | Recommended |
|--------|---------|:-:|:-:|
| figma | @anthropic/mcp-server-figma | Yes | [if frontend project] |

### AI Providers
| Server | Package | Requires API Key | Recommended |
|--------|---------|:-:|:-:|
| openrouter | @openrouter/mcp-server | Yes | Optional |
| openai | @modelcontextprotocol/server-openai | Yes | Optional |
| google-ai | @anthropic/mcp-server-google-ai | Yes | Optional |
| ollama | @modelcontextprotocol/server-ollama | No (local) | Optional |

### Utilities
| Server | Package | Requires API Key | Recommended |
|--------|---------|:-:|:-:|
| sequential-thinking | @modelcontextprotocol/server-sequential-thinking | No | Always |
| memory | @modelcontextprotocol/server-memory | No | Always |
| fetch | @modelcontextprotocol/server-fetch | No | Always |
| filesystem | @modelcontextprotocol/server-filesystem | No | Optional |
| brave-search | @modelcontextprotocol/server-brave-search | Yes | Optional |
```

### STEP 6.4 — Selection

**If $ARGUMENTS has server names (e.g., `mcp primevue,context7`):** use them directly.
**If interactive:** ask the human to select which servers to configure.

Suggest a sensible default based on detected stack:
- **Always:** context7, github, sequential-thinking, memory, fetch
- **Vue project:** + primevue
- **React project:** + shadcn or chakra-ui
- **Laravel project:** + postgres
- **Frontend project:** + figma

Present selection and await approval.

### STEP 6.5 — Collect API Keys

For each selected server that requires an API key:
1. Ask the human for the key
2. If human says "skip" or "later" → use placeholder `"<your-KEY_NAME-here>"`
3. NEVER store real keys in files that will be committed

**Important:** Inform the human:
> "API keys will be written to `.mcp.json`. Make sure `.mcp.json` is in your `.gitignore` to avoid committing secrets."

### STEP 6.6 — Generate .mcp.json

Write `.mcp.json` to the **project root** (not the plugin directory).

Format:
```json
{
  "mcpServers": {
    "server-name": {
      "command": "npx",
      "args": ["-y", "@package/name"],
      "env": {
        "API_KEY": "value-or-placeholder"
      }
    }
  }
}
```

### STEP 6.7 — Ensure .gitignore

Check if `.mcp.json` is in `.gitignore`. If not, ask the human:
> ".mcp.json contains API keys. Add it to .gitignore? (recommended)"

If approved, append `.mcp.json` to `.gitignore`.

### STEP 6.8 — Summary

```markdown
## MCP Servers Configured

**File:** .mcp.json
**Servers:** [N] configured

| Server | Status |
|--------|--------|
| context7 | Configured |
| github | Placeholder key (update later) |
| primevue | Ready (no key needed) |

### Next steps:
1. Update placeholder API keys in `.mcp.json`
2. Restart Claude Code to load the new MCP servers
3. Verify with `/pwdev-code:health`
```

---

## STEP 7 — Stack Detection & Config

> Invoked with `/pwdev-code:init stack`

### STEP 7.1 — Detect Stack
```bash
cat package.json 2>/dev/null | head -40
cat composer.json 2>/dev/null | head -40
cat requirements.txt 2>/dev/null | head -20
cat go.mod 2>/dev/null | head -10
ls artisan nuxt.config.* next.config.* vite.config.* 2>/dev/null
```

### STEP 7.2 — Present Findings

Show detected stack and ask the human to confirm or adjust.

### STEP 7.3 — Save to config

Update `.planning/config.json` with detected stack info (merge, do not overwrite).

---

## STEP 8 — Generate CLAUDE.md

> Invoked with `/pwdev-code:init claude`

### Role
Generate the operational CLAUDE.md file — the central contract that governs all PWDEV-CODE agents.

### STEP 8.1 — Check Existing
```bash
[ -f "CLAUDE.md" ] && echo "EXISTS" || echo "NEW"
```

If EXISTS → ask:
- PT-BR: `CLAUDE.md ja existe. Deseja: 1. Sobrescrever  2. Atualizar (merge)  3. Cancelar`
- EN: `CLAUDE.md already exists. Would you like to: 1. Overwrite  2. Update (merge)  3. Cancel`

### STEP 8.2 — Collect Project Context
```bash
cat .planning/config.json 2>/dev/null
cat .planning/context/architecture.md 2>/dev/null | head -30
cat .planning/context/conventions.md 2>/dev/null | head -30
cat package.json composer.json requirements.txt 2>/dev/null | head -30
cat .editorconfig tsconfig.json 2>/dev/null | head -20
ls .claude/skills/*/SKILL.md 2>/dev/null
```

### STEP 8.3 — Generate from Template

Read the template from `.claude/templates/CLAUDE.template.md` (if it exists in the plugin) or use the built-in structure.

Fill in the sections using detected project data:
- Section 12 (Repository Conventions): stack, framework, database, test runner, linter
- Section 14 (Quick Commands): updated command names

If `.planning/context/` files exist (from `init map`), use them to populate:
- Stack details
- Naming conventions
- Available commands (npm scripts, composer scripts, etc.)

### STEP 8.4 — Present and Confirm

Show the generated CLAUDE.md to the human. Ask for approval before saving.

### STEP 8.5 — Save
```bash
cat > CLAUDE.md << 'EOF'
[content]
EOF
```

### STEP 8.6 — Summary
```markdown
## ✅ CLAUDE.md Generated

**Path:** CLAUDE.md
**Sections:** 14
**Stack:** [detected or placeholder]
**Skills:** [N] active

### Next steps:
  /pwdev-code:discover — start first feature
  /pwdev-code:init map — analyze codebase (if brownfield)
```

### CLAUDE.md Prohibitions
- ❌ NEVER include secrets or credentials
- ❌ NEVER overwrite without confirmation
- ❌ NEVER leave placeholder sections if data is available from context/

---

## General Prohibitions
- ❌ NEVER overwrite existing .planning/ without confirmation
- ❌ NEVER overwrite existing .claude/ without confirmation
- ❌ NEVER modify .gitignore without confirmation
- ❌ NEVER read .env
- ❌ NEVER commit `.mcp.json` with real API keys
- ❌ NEVER log or display API key values after writing
- ❌ NEVER write to the plugin directory — only to the project root
