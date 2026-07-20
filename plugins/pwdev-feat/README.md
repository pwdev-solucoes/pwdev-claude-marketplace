# PWDEV-FEAT v2.1.0

*Read this in [Português Brasileiro](./README.pt-BR.md)*

> **Simplified AI-Assisted Feature Development for Claude Code**

```
Describe what you want → get a structured plan → execute it.
```

PWDEV-FEAT uses the **PWDEVIA 7-question methodology** to generate structured
action plans — created inline while interviewing you (max 2 rounds) — that a
**real executor subagent** implements with fresh context. No complex
ceremonies — just describe, plan, execute.

---

## What's New in v2.1.0

- **Advisor subagent** (`pwdev-feat:advisor` + `NEEDS_ADVICE` status): when
  the executor hits a hard decision mid-plan (plan ambiguity, architectural
  fork, repeated verification failure with a concrete question), it stops and
  asks. `/pwdev-feat:exec` consults the advisor — the strong model (Opus even
  in `balanced`), read-only, `effort: high` — and re-spawns the executor with
  the decision attached. Max 1 consultation per plan; override key
  `feat-advisor` in the shared config.
- **Shared project memory (read-only)**: when the project keeps a curated
  memory (`.planning/memory/`, managed by pwdev-code), the PWDEVIA planner
  folds ≤3 relevant memories into the plan's Assumptions/Quality Criteria and
  `/pwdev-feat:exec` injects a RELEVANT MEMORY block into the executor spawn.
  pwdev-feat never writes to the memory — curation stays with pwdev-code.
- External reviewer CLI second opinion is a `/pwdev-code:review` feature —
  not available here (feat review plans run inside a subagent, with no
  channel to confirm an external command with the human).

## What's New in v2.0.0

Rebuilt on the modern Claude Code plugin system. No slash command was renamed
or removed; internals were restructured.

- **Real executor subagent** (`pwdev-feat:executor`): `/pwdev-feat:exec` now
  spawns an actual subagent via the Task tool with a self-contained prompt —
  fresh context per plan, official frontmatter, restricted tools.
- **PWDEVIA planner is inline by design** (`references/pwdevia-method.md`):
  it interviews you, and subagents cannot talk to the user. The old
  prose-persona agent files are gone.
- **IMPLEMENT / REPORT modes**: review plans (and report-only plans) run in
  REPORT mode — findings go to `report.md`, no code changes, no commit.
  Fixes the old conflict where executing a review plan tried to commit.
- **Deterministic audit via hooks**: session start/stop, executor runs with
  real `duration_ms`/`session_id`, and `.planning/` writes are recorded by
  plugin hooks — no more inline INSERTs. `config_changes` is now actually
  populated (via `audit-log.sh config`). Secret-guard PreToolUse hook blocks
  `.env`/`*.pem`/`*.key`/`id_rsa*` reads.
- **Packaged references** (`${CLAUDE_PLUGIN_ROOT}/references/`): PWDEVIA
  method, language protocol, model profiles (single source of truth),
  spawn contract, audit schema — replaces 11 duplicated Language blocks and
  6 divergent Model Resolution blocks.
- **Fixes**: `/pwdev-feat:status` now detects ❌ FAILED and ⚠️ WITH CAVEATS;
  audit custom-query guard hardened (single-statement SELECT only);
  verification reads CLAUDE.md commands first (no more `npm || composer`
  chains); `echo -e` and dead `$SUB_COMMAND` removed.
- **Shared config, namespaced**: `.planning/config.json` and the audit DB are
  shared with pwdev-code on purpose; pwdev-feat's model override key is
  `"feat-executor"`.

---

## Methodology

### The PWDEVIA 7 Questions

Every plan is built by answering 7 fundamental questions:

| # | Question | Purpose |
|---|----------|---------|
| 1 | **Persona & Scope** | Who should the executor be? What are the exact boundaries? |
| 2 | **Direct Objective** | What must exist when done? (1 clear sentence) |
| 3 | **Minimum Inputs** | What data, rules, files does the executor need? |
| 4 | **Output Format** | What files to create/modify? Expected structure? |
| 5 | **Quality Criteria** | What standards must be met? What tests? |
| 6 | **Ambiguity Handling** | What to do when something is unclear? |
| 7 | **Prohibitions** | What must NEVER be done? |

### How It Works

```
You describe                    PWDEVIA creates                Executor implements
─────────────                   ───────────────                ────────────────────
"User CRUD with          →      user-crud/plan.md        →     Code + Tests + Commit
 paginated listing"             (7 sections + steps)           user-crud/plan.done.md
```

### Plan Types

| Type | Command | Scope |
|------|---------|-------|
| **Feature** | `/pwdev-feat:feat` | Full feature — backend + frontend + tests |
| **Backend** | `/pwdev-feat:backend` | API, services, models, migrations, backend tests |
| **Frontend** | `/pwdev-feat:frontend` | Components, pages, composables, E2E with Playwright |
| **Test** | `/pwdev-feat:test` | Unit, integration, E2E tests for existing code |
| **Review** | `/pwdev-feat:review` | Code review — security, performance, conventions |
| **Quick** | `/pwdev-feat:quick` | Direct execution, no plan file (1-3 files max) |

---

## What's New in v1.1.2

- **Per-feature folders** — Plans now live in `.planning/feat/features/{slug}/plan.md` instead of flat `plans/` directory. Each feature gets its own isolated folder.
- **Language Selection** — All commands support PT-BR and EN. Configured during `/pwdev-feat:init`.
- **Model Profiles** — Agent models configurable via `performance`, `balanced`, or `economy` profiles.
- **Audit Trail (opt-in)** — Optional SQLite logging of commands, decisions, and artifacts. Disabled by default.

---

## Quick Start

```bash
# 1. Initialize
/pwdev-feat:init

# 2. (Optional) Analyze existing codebase
/pwdev-feat:map-codebase

# 3. (Optional) Generate CLAUDE.md
/pwdev-feat:setup

# 4. Create a plan
/pwdev-feat:feat "User CRUD with paginated listing and search"

# 5. Execute the plan
/pwdev-feat:exec user-crud

# Or skip planning for simple tasks
/pwdev-feat:quick "Fix email validation in UserController"
```

---

## Agents

| Agent | Where it runs | What it does |
|-------|---------------|-------------|
| **PWDEVIA** (planner) | Inline, main context (`references/pwdevia-method.md`) | Applies the 7 questions, interviewing you (max 2 rounds). Never writes code. |
| **executor** (subagent) | Real subagent via Task tool, fresh context | Follows the plan step by step. IMPLEMENT: code + tests + commit + report. REPORT: findings only, no commit. |

### Agent Boundaries

- **PWDEVIA** creates plans — never writes production code
- **Executor** follows plans — never deviates without asking (STOPPED status)
- Both read CLAUDE.md and codebase.md for project context

---

## Commands

### Setup

| Command | What it does |
|---------|-------------|
| `/pwdev-feat:init` | Create `.planning/feat/` workspace, configure language and model profile |
| `/pwdev-feat:map-codebase` | Analyze codebase → generate `codebase.md` context |
| `/pwdev-feat:setup` | Generate `CLAUDE.md` with project conventions |

### Planning (PWDEVIA generates)

| Command | What it does |
|---------|-------------|
| `/pwdev-feat:feat "desc"` | Create full feature plan (backend + frontend + tests) |
| `/pwdev-feat:backend "desc"` | Create backend-focused plan (API, services, models) |
| `/pwdev-feat:frontend "desc"` | Create frontend-focused plan (components, E2E) |
| `/pwdev-feat:test "desc"` | Create test plan for existing code |
| `/pwdev-feat:review "scope"` | Create code review plan |

### Execution

| Command | What it does |
|---------|-------------|
| `/pwdev-feat:exec {slug}` | Execute a specific feature plan (or `latest`) |
| `/pwdev-feat:quick "desc"` | Direct execution — no plan file, for simple tasks |
| `/pwdev-feat:status` | Show pending, executed, and failed plans |
| `/pwdev-feat:audit` | Query the audit trail — summary, events, decisions, artifacts, stats, export PDF |

---

## Language & Model Configuration

### Language

All commands support **Portuguese (PT-BR)** and **English (EN)**. Configured during `/pwdev-feat:init` and stored in `.planning/config.json`.

- `/pwdev-feat:init` — always asks for language preference
- Other commands — use saved preference silently
- Override — switch language mid-conversation and confirm when prompted

### Model Profile

Only the **executor** subagent resolves a model (the PWDEVIA planner runs
inline on the session model). Single source of truth:
`references/model-profiles.md`.

| Profile | executor |
|---------|:--------:|
| **performance** | Opus |
| **balanced** (default) | Sonnet |
| **economy** | Sonnet |

Override with the **namespaced key `"feat-executor"`** in
`.planning/config.json` (the file is shared with pwdev-code — the plain
`"executor"` key belongs to it):

```json
{
  "lang": "pt-BR",
  "model_profile": "balanced",
  "model_overrides": { "feat-executor": "opus" }
}
```

---

## Audit Trail

All plugins share an optional SQLite audit database at `.planning/pwdev-audit.db`. It is **disabled by default** and configured during `/init`. The database file is never versioned (automatically added to `.gitignore`).

**How data gets here (v2.0 — deterministic, via hooks):**
- `scripts/audit-hook.sh` (SessionStart, SubagentStart/Stop, PostToolUse,
  Stop) → session events, executor runs with real `session_id` and
  `duration_ms`, `.planning/` artifact writes
- `scripts/audit-log.sh` → command milestones (`event`) and configuration
  changes (`config` → the `config_changes` table, populated by `/init`)
- `scripts/guard-secrets.sh` (PreToolUse) → blocks reads of `.env`, `*.pem`,
  `*.key`, `id_rsa*` (`.env.example` allowed)

The database is **shared with pwdev-code** — rows are distinguished by the
`plugin` column (`WHERE plugin='pwdev-feat'`).

### Querying the Audit Trail

Use `/pwdev-feat:audit` to query the database interactively:

| Sub-command | What it does |
|-------------|-------------|
| `summary` (default) | Dashboard with key metrics and recent activity |
| `events` | Full event log (last 50 entries) |
| `decisions` | All architectural/product decisions with rationale |
| `artifacts` | Files tracked by the framework |
| `stats` | Command frequency, durations, phase distribution, success rate |
| `export` | Generate a full audit report as PDF + Markdown |
| `query <SQL>` | Run a custom read-only SQL query |

```bash
/pwdev-feat:audit              # summary dashboard
/pwdev-feat:audit stats        # detailed statistics
/pwdev-feat:audit export       # generate PDF report at .planning/audit-report.pdf
/pwdev-feat:audit query "SELECT * FROM events WHERE action='failed'"
```

Add `.planning/pwdev-audit.db` to `.gitignore` (recommended).

---

## Plan Structure

Every plan generated by PWDEVIA follows this structure:

```markdown
# Action Plan — {title}

## 1. Persona & Scope        ← who and what
## 2. Direct Objective        ← what must exist when done
## 3. Minimum Inputs          ← data, rules, files to read
## 4. Output Format           ← files to create/modify
## 5. Quality Criteria        ← tests, lint, standards
## 6. Ambiguity Handling      ← what to do when unsure
## 7. Prohibitions            ← what to NEVER do

## Execution Steps            ← concrete numbered steps
## Done                       ← single sentence = finished
## Commit                     ← conventional commit message
```

Plans are stored in `.planning/feat/features/{slug}/plan.md` and executed with `/pwdev-feat:exec {slug}`.

---

## Workspace

```
.planning/feat/
├── features/
│   ├── user-crud/
│   │   ├── plan.md                # Action plan
│   │   └── plan.done.md           # Execution report
│   ├── api-review/
│   │   ├── plan.md                # Review plan (Type: review)
│   │   ├── report.md              # Findings (REPORT mode — no commit)
│   │   └── plan.done.md
│   └── ...
└── codebase.md                    # Generated by /pwdev-feat:map-codebase
```

Each feature gets its own folder under `features/`. All artifacts related to a feature (plan, execution report, review findings) live inside that folder.

Optional context files:
- `.planning/feat/codebase.md` — generated by `/pwdev-feat:map-codebase`
- `CLAUDE.md` — generated by `/pwdev-feat:setup`

---

## pwdev-feat vs pwdev-code

| Aspect | pwdev-feat | pwdev-code |
|--------|-----------|------------|
| **Philosophy** | Fast and practical | Rigorous and traceable |
| **Phases** | Plan → Execute | DISCOVER → DESIGN → PLAN → EXECUTE → REVIEW → VERIFY |
| **Agents** | PWDEVIA inline + executor and advisor subagents | 8 real subagents + inline personas |
| **Commands** | 12 | 16 |
| **Best for** | Individual features, quick iterations, small teams | Complex projects, compliance, large teams |
| **Ceremony** | Minimal | Structured with gates |
| **Plan style** | 7-question action plan | SPEC.md (8 sections) + atomic tasks |

**Use pwdev-feat when** you want to ship fast with AI assistance.
**Use pwdev-code when** you need full traceability and verification.

---

## License

Apache-2.0 — See [LICENSE](./LICENSE)

*PWDEV-FEAT v2.1.0 — Describe, plan, execute. Ship.*
*Maintained by [Paulo Soares](https://github.com/soarescbm)*
