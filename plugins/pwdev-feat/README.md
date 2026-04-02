# PWDEV-FEAT v1.1.0

*Read this in [Português Brasileiro](./README.pt-BR.md)*

> **Simplified AI-Assisted Feature Development for Claude Code**

```
Describe what you want → get a structured plan → execute it.
```

PWDEV-FEAT uses the **PWDEVIA 7-question methodology** to generate structured action plans that an executor agent follows precisely. No complex ceremonies — just describe, plan, execute.

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

## What's New in v1.1.0

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

| Agent | Role | What it does |
|-------|------|-------------|
| **agent-planner** (PWDEVIA) | Prompt Engineer | Applies the 7 questions to create structured action plans. Never writes code. |
| **agent-executor** | Implementation Engineer | Follows plans step by step. Implements, tests, commits. Reports deviations. |

### Agent Boundaries

- **PWDEVIA** creates plans — never writes production code
- **Executor** follows plans — never deviates without asking
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

---

## Language & Model Configuration

### Language

All commands support **Portuguese (PT-BR)** and **English (EN)**. Configured during `/pwdev-feat:init` and stored in `.planning/config.json`.

- `/pwdev-feat:init` — always asks for language preference
- Other commands — use saved preference silently
- Override — switch language mid-conversation and confirm when prompted

### Model Profile

Agent models are configurable via profiles set during `/pwdev-feat:init`:

| Profile | agent-planner | agent-executor |
|---------|:------------:|:--------------:|
| **performance** | Opus | Opus |
| **balanced** | Sonnet | Sonnet |
| **economy** | Sonnet | Sonnet |

Override specific agents with `model_overrides` in `.planning/config.json`:

```json
{
  "lang": "pt-BR",
  "model_profile": "balanced",
  "model_overrides": {}
}
```

---

## Audit Trail

All plugins share an optional SQLite audit database at `.planning/pwdev-audit.db`. It is **disabled by default** and configured during `/init`. The database file is never versioned (automatically added to `.gitignore`).

The audit trail records:
- **Events** — every command execution (start, complete, fail) with timestamp, agent, model, and phase
- **Decisions** — architectural and product decisions with rationale and alternatives considered
- **Artifacts** — files created or modified by the framework, with status tracking
- **Config changes** — history of language, model profile, and other configuration changes

The audit database runs **in parallel** with Markdown files — agents continue to read and write Markdown as before. SQLite is a bonus layer for history and analysis.

### Querying the Audit Trail

```bash
# Last 20 events
sqlite3 .planning/pwdev-audit.db "SELECT timestamp, plugin, command, action, target FROM events ORDER BY timestamp DESC LIMIT 20;"

# All decisions with rationale
sqlite3 .planning/pwdev-audit.db "SELECT timestamp, phase, decision, rationale FROM decisions ORDER BY timestamp;"

# Command frequency
sqlite3 .planning/pwdev-audit.db "SELECT command, COUNT(*) as runs FROM events WHERE action='completed' GROUP BY command ORDER BY runs DESC;"
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
│   ├── auth-tests/
│   │   ├── plan.md
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
| **Agents** | 2 (planner + executor) | 11 specialized agents |
| **Commands** | 10 | 21 |
| **Best for** | Individual features, quick iterations, small teams | Complex projects, compliance, large teams |
| **Ceremony** | Minimal | Structured with gates |
| **Plan style** | 7-question action plan | SPEC.md (8 sections) + atomic tasks |

**Use pwdev-feat when** you want to ship fast with AI assistance.
**Use pwdev-code when** you need full traceability and verification.

---

## License

Apache-2.0 — See [LICENSE](./LICENSE)

*PWDEV-FEAT v1.1.0 — Describe, plan, execute. Ship.*
*Maintained by [Paulo Soares](https://github.com/soarescbm)*
