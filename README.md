# PWDEV Marketplace

*Read this in [Português Brasileiro](./README.pt-BR.md)*

Plugin marketplace for [Claude Code](https://docs.anthropic.com/en/docs/claude-code).

---

## What is PWDEV

[Paulo Soares](https://github.com/soarescbm), CTO of PWDEV, a company focused on developing GovTech solutions, believes that artificial intelligence is fundamentally reshaping software development. More than a passing trend, this shift represents a new way to support professionals, extend capabilities, and bring greater consistency across the entire development lifecycle. Guided by this vision, PWDEV is making these solutions available to help teams work with more structure, quality, and predictability.

Our plugins turn Claude Code from a general-purpose coding assistant into a disciplined engineering partner through specialized agents, structured workflows, and domain-specific knowledge packs.

Core philosophy across all plugins:

> **Never execute without a plan. Never ship without verification.**

### PWDEV Flow — dual runtime

`pwdev-flow` is the portable PWDEV workflow for Claude Code and Codex. The
same approval-gated skills and `.planning/flow` artifacts work in both
runtimes; isolated fleets select an explicit native engine (`claude` or
`codex`) and keep privileged execution vectors separate.

Claude fleet members execute through `claude -p`; Codex members execute
through `codex exec`, with no cross-runtime fallback.

Commands: `/pwdev-flow:init`, `/pwdev-flow:discover`, `/pwdev-flow:design`,
`/pwdev-flow:plan`, `/pwdev-flow:execute`, `/pwdev-flow:review`,
`/pwdev-flow:verify`, `/pwdev-flow:simplify`, `/pwdev-flow:quick`,
`/pwdev-flow:product`, `/pwdev-flow:memory`, `/pwdev-flow:health`,
`/pwdev-flow:audit`, `/pwdev-flow:maintenance`, `/pwdev-flow:compat`,
`/pwdev-flow:delegate`, `/pwdev-flow:fleet`.

---

## What's New

### External CLI delegation — pwdev-code v2.3.0

Claude Code as an **orchestrator of other coding agents**: 6 new commands
(`/pwdev-code:codex`, `opencode`, `kimi`, `gemini`, `kiro`, and the smart
`/pwdev-code:delegate`) route tasks through a single hardened runner —
binary allowlist, 10-rule safety prompt, timeout, write-lock, read-only
verification (`gemini` defaults to read-only) — and Claude then reviews the
full `git diff`, runs the tests itself, and gives its own verdict (never
commits). Optional per-agent config via `external_models.<agent>`.

### Orchestration patterns — pwdev-code v2.2.0 & pwdev-feat v2.1.0

The development plugins absorbed three orchestration patterns — plan,
specialize, review is now also *ask the strong model at the moment of doubt*:

- **Advisor subagent** (both plugins) — an executor blocked on a hard
  decision emits `NEEDS_ADVICE`; the orchestrator consults the new `advisor`
  (Opus even in `balanced`, read-only, `effort: high`) and re-spawns the
  executor with the decision attached. Max 1 consultation per task.
- **Per-task model routing** (pwdev-code) — plans declare
  `Complexity: low|medium|high`; the executor's model is resolved per task
  (e.g. `balanced`: high → opus, low/medium → sonnet). Backward compatible.
- **Memory graph** (pwdev-code) — memories relate via `related:` / `[[name]]`
  / `[rel:]` index suffix; spawn selection expands 1 hop without opening
  files; new `memory link` and `memory graph` subcommands. pwdev-feat now
  consumes the shared memory read-only.
- **Opt-in parallel waves** (pwdev-code) — `Parallel-safe` tasks with
  disjoint files run as executor batches in isolated git worktrees, merged
  sequentially. Default remains serial.
- **Optional external reviewer CLI** (pwdev-code) — `/review` can collect an
  advisory second opinion from an allowlisted CLI (codex, gemini, opencode,
  qwen); external findings never block the gate.

> **Upgrading?** Installed plugins are cached copies — run
> `claude plugin marketplace update pwdev-claude-marketplace` +
> `claude plugin update <plugin>@pwdev-claude-marketplace`, then restart
> Claude Code so the new agents register.

### New plugins — marketing & operations

The marketplace now goes beyond the development workflow:

- **pwdev-copy v1.1.0** — trainable copywriting framework, expanded to
  **20 skills / 5 subagents / 9 commands**: new creation skills (hooks,
  repurposing), CRO page review, and an **analysis layer**
  (`perf-analyzer` / `perf-patterns` / `perf-optimize` + `analyst` subagent)
  that closes the loop: research → brief → copy → review → publish → analyze.
- **pwdev-social-media v2.0.0** *(new)* — AI creative generation for social
  media with **API orchestration at the center** (Ideogram, Leonardo, Flux,
  Runway, Freepik/Magnific) behind spend-guarded wrappers: cost triage,
  prompt engineering, visual consistency, and variation curation. Figma is an
  optional composition layer. 19 skills, 4 subagents.
- **pwdev-devops v1.0.0** *(new)* — platform, operations, and incident
  response with a **safe-execution posture**: reads are free, mutations
  require per-command confirmation, destructive operations are blocked by a
  guard script (a second barrier independent of skill instructions).
  19 skills covering AWS, Kubernetes, Docker, Linux, Nginx, PostgreSQL,
  observability, incident response, security, Proxmox, FinOps, and more;
  4 subagents.

### The v2 wave

The five original plugins were rebuilt on the modern Claude Code plugin system.
**No slash command was renamed or removed** — internals were restructured.

### Common to all workflow plugins (code / feat / prd / uiux)

- **Hybrid orchestration** — personas that interact with the human (interviews,
  approval gates) run INLINE in the main context; heavy work runs in **real
  subagents** spawned via the Task tool with official frontmatter, fresh
  context, and genuine parallelism. The old "assume the persona" prose is gone.
- **Deterministic audit via hooks** — the shared SQLite trail
  (`.planning/pwdev-audit.db`, rows distinguished by the `plugin` column) is
  now written by plugin hooks: real `duration_ms`/`session_id`,
  `config_changes` finally populated. A **secret-guard PreToolUse hook**
  blocks reads of `.env`/`*.pem`/`*.key`/`id_rsa*` in every plugin.
- **Packaged references** — language protocol, model profiles, spawn
  contracts, and audit schema live in each plugin's `references/` directory,
  resolved via `${CLAUDE_PLUGIN_ROOT}` (no more duplicated blocks or broken
  relative paths).
- **Hardened `/audit`** — single-statement SELECT-only query guard; portable
  POSIX shell throughout.

### pwdev-code v2.1.0

- **7 real subagents** (executor, simplifier, code-reviewer, qa, adversarial
  verifier, researcher, roadmap) + 5 inline personas; 16 commands.
- **Curated project memory** (`/pwdev-code:memory` + versioned
  `.planning/memory/`) feeding every spawn; lessons auto-captured from
  rejected verifications and blocked reviews.
- **Correction loops with hard stops** — `verify` → fix plans →
  `execute --fix` (max 2 iterations); review gate blocks verify;
  `verify --strict` runs 2 parallel verifiers (worst verdict wins).
- **`/pwdev-code:simplify`** — two-pass quality refactor (propose ≥80%
  confidence → human approves by ID → apply + refactor commit).
- **`skill-user-stories`** + `/pwdev-code:product stories` (INVEST, Gherkin
  ACs, definition of ready).

### pwdev-feat v2.0.0

- **Real executor subagent** with IMPLEMENT/REPORT modes (review plans report
  findings without committing); PWDEVIA planner inline
  (`references/pwdevia-method.md`); `/status` now detects FAILED/CAVEATS.

### pwdev-prd v2.0.0

- **Interviewer inline by design** (zero subagents); canonical `prd.json`
  structure finally defined; init no longer configures model profiles
  (nothing here resolves a model).

### pwdev-uiux v2.0.0

- **6 real subagents + 2 inline personas** (orchestrator and theme-builder
  hold the human gates); prohibited agent fields (`permissionMode`,
  `mcpServers`, non-official `skills:`) removed; skills passed as explicit
  SKILL.md paths in spawn prompts; namespaced model overrides
  (`uiux-<agent>`).

### pwdev-statusline v1.1.0

- **Configuration block** (toggles/colors/separator/dir depth as variables —
  `/customize` edits one line idempotently); **single jq pass** per render;
  dynamic context/rate colors; formatted tokens (`512k`/`1.2M`); truncated
  paths; safer install/uninstall.

---

## Plugins

| Plugin | Description | Version | License |
|--------|-------------|:-------:|:-------:|
| [**pwdev-code**](./plugins/pwdev-code/) | Spec-driven development — 8 real subagents (incl. advisor), per-task model routing, memory graph, opt-in parallel waves, external CLI delegation (Codex/OpenCode/Kimi/Gemini/Kiro), 22 commands | 2.3.0 | Apache-2.0 |
| [**pwdev-uiux**](./plugins/pwdev-uiux/) | UI/UX engineering — 6 real subagents, 5-phase workflow with gates, Figma, WCAG 2.1 AA | 2.0.1 | Apache-2.0 |
| [**pwdev-feat**](./plugins/pwdev-feat/) | Simplified feature development — PWDEVIA 7-question plans inline + executor and advisor subagents | 2.1.0 | Apache-2.0 |
| [**pwdev-prd**](./plugins/pwdev-prd/) | Interview-driven PRD creation — 12-step inline interview, Markdown + canonical JSON | 2.0.1 | Apache-2.0 |
| [**pwdev-copy**](./plugins/pwdev-copy/) | Trainable copywriting framework — 20 skills across the full cycle (VOC research → copy → review → analysis), 5 real subagents | 1.1.0 | Apache-2.0 |
| [**pwdev-social-media**](./plugins/pwdev-social-media/) | AI creative generation for social — API orchestration (Ideogram, Leonardo, Flux, Runway, Freepik) with spend guard, 19 skills, 4 subagents | 2.0.1 | Apache-2.0 |
| [**pwdev-devops**](./plugins/pwdev-devops/) | Platform, operations & incident response — safe-execution posture with guard script, 19 skills, 4 subagents | 1.0.0 | Apache-2.0 |
| [**pwdev-youtrack**](./plugins/pwdev-youtrack/) | YouTrack management — official built-in MCP server (2025.3+) for issues, articles & work log; REST fallback for boards, sprints, time reports | 1.0.0 | Apache-2.0 |
| [**pwdev-glpi**](./plugins/pwdev-glpi/) | GLPI 10.x ITSM — own MCP server via npx (@soarescbm/mcp-glpi): tickets CRUD, triage with MCP prompts, queue reports, assets & KB | 1.0.0 | Apache-2.0 |
| [**pwdev-postgres**](./plugins/pwdev-postgres/) | PostgreSQL — own MCP server via npx (@soarescbm/postgres-mcp): AST-validated read-only SELECT, schema inspection, DML/DDL with mandatory dry-run | 1.0.0 | Apache-2.0 |
| [**pwdev-brain**](./plugins/pwdev-brain/) | Second brain as an LLM Wiki (Karpathy pattern) in Open Knowledge Format v0.2 — discussed ingest with per-claim citations, cited query, compliance lint; 2 subagents, embedded read-only MCP (6 tools) | 1.1.0 | Apache-2.0 |
| [**pwdev-statusline**](./plugins/pwdev-statusline/) | Rich terminal status line — dynamic colors, formatted tokens, fully configurable | 1.1.0 | Apache-2.0 |

### pwdev-code

Spec-driven development with **hybrid orchestration**: interactive phases run
in the main conversation; heavy work is delegated to **8 real subagents**
across **6 phases** with correction loops and a **curated project memory
graph**.

```
PRD ─▶ ROADMAP ─▶ DISCOVER ─▶ DESIGN ─▶ PLAN ─▶ EXECUTE ─▶ [SIMPLIFY] ─▶ REVIEW ─▶ VERIFY
```

**Subagents:** executor, advisor, simplifier, code-reviewer, qa, adversarial verifier, researcher, roadmap
**Inline personas:** interviewer, architect, planner, product manager, quick engineer

See the [full plugin documentation](./plugins/pwdev-code/README.md).

### pwdev-uiux

Stack-agnostic UI/UX engineering: **6 real subagents + 2 inline personas**
across a 5-phase workflow with human gates.

```
UNDERSTAND ─▶ STRUCTURE ─▶ IMPLEMENT ─▶ REVIEW ─▶ HANDOFF
```

**Subagents:** UX Analyst, Design Bridge, UI Scanner, UI Builder, A11y Reviewer, UX Critic
**Inline personas:** Orchestrator (gates), Theme Builder (brand interview)

**Key features:** Figma MCP integration, WCAG 2.1 AA auditing, 7-axis UX review, project-specific contextual skills

See the [full plugin documentation](./plugins/pwdev-uiux/README.md).

### pwdev-feat

Simplified AI-assisted feature development using the **PWDEVIA 7-question methodology**. Describe what you want, get a structured plan, execute it.

```
Describe ─▶ Plan (PWDEVIA, inline) ─▶ Execute (real subagent, IMPLEMENT/REPORT)
```

**Agents:** PWDEVIA (inline planner) + executor and advisor (real subagents); reads pwdev-code's curated project memory when present

**Plan types:** Feature, Backend, Frontend, Test, Review, Quick

See the [full plugin documentation](./plugins/pwdev-feat/README.md).

### pwdev-prd

Interview-driven **PRD creation** with a 12-step structured process — run
inline (the interviewer talks to you; zero subagents by design).
Technology-agnostic, outputs Markdown + canonical JSON.

```
Interview (12 steps) ─▶ PRD.md ─▶ Export (JSON / GitHub Issue)
```

**Outputs:** Structured PRD with objectives, metrics, functional/non-functional requirements, architecture, risks, acceptance criteria

See the [full plugin documentation](./plugins/pwdev-prd/README.md).

### pwdev-copy

Trainable **copywriting framework** (docs in PT-BR): one context file defines
brand, ICP, and voice; **20 skills** produce consistent copy from it. The same
installation serves any client — you swap the training file.

```
treinar ─▶ voc ─▶ brief ─▶ copy ─▶ revisar ─▶ publicar ─▶ analisar ↺
```

**Subagents:** voc, copywriter, reviewer, adversarial-copy, analyst
**Key features:** 7-sweep anti-slop review, adversarial conversion review, Ogilvy brief gate, performance analysis loop

See the [full plugin documentation](./plugins/pwdev-copy/README.md) (PT-BR).

### pwdev-social-media

AI **creative generation** for social media (docs in PT-BR): API orchestration
at the center — Ideogram, Leonardo, Flux, Runway, Freepik/Magnific — behind
spend-guarded wrappers. Figma is an optional composition layer. Complements
`pwdev-copy`: there the text, here the piece.

```
concept ─▶ [COST CONFIRMATION] ─▶ prompt ─▶ API generation ─▶ curation ─▶ [figma] ─▶ review ─▶ export
```

**Subagents:** art-director, asset-generator, creative-reviewer, figma-builder
**Key features:** spend guard with cost triage, prompt-only mode without API keys, mandatory accessibility review

See the [full plugin documentation](./plugins/pwdev-social-media/README.md) (PT-BR).

### pwdev-devops

**Platform, operations, and incident response** (docs in PT-BR) with a
safe-execution posture: reads are free, mutations require per-command
confirmation, destructive operations are blocked by `scripts/guard.sh` — a
second barrier independent of skill instructions.

```
init (env mapping) ─▶ diagnosticar / incidente / auditar / custo / documentar
```

**Subagents:** incident-commander, infra-auditor, db-analyst, platform-documenter
**Key features:** 19 skills (AWS, Kubernetes, Docker, Linux, Nginx, PostgreSQL, observability, incident, security, Proxmox, FinOps, …), read-only audits, FinOps reports

See the [full plugin documentation](./plugins/pwdev-devops/README.md) (PT-BR).

### pwdev-youtrack

**YouTrack management** (docs in PT-BR) through JetBrains' official built-in
MCP server (YouTrack 2025.3+): issues CRUD, search with the query language,
comments, tags, knowledge-base articles, and work log — plus an authenticated
REST fallback for what the MCP does not cover (agile boards, sprints, time
reports, attachments, bulk commands).

```
init (token → Keychain) ─▶ natural conversation via MCP ─▶ sprint / report via REST
```

**Skills:** youtrack (official MCP), youtrack-rest (boards/sprints/reports)
**Key features:** guided setup with the token stored in the macOS Keychain, token never in files or transcripts, confirm-before-mutate

See the [full plugin documentation](./plugins/pwdev-youtrack/README.md).

### pwdev-glpi

**GLPI 10.x ITSM management** (docs in PT-BR) through a purpose-built MCP
server published on npm ([@soarescbm/mcp-glpi](https://github.com/soarescbm/mcp-glpi),
spawned via `npx`): tickets CRUD, followups, solution/close, plus read-only
users, groups, assets, projects and knowledge base. Queue triage is driven by
the server's own MCP prompts.

```
init (PAT → Keychain) ─▶ natural conversation via MCP ─▶ triagem / relatorio
```

**Skills:** glpi (intent→tool map, ITIL rules)
**Key features:** guided setup with the PAT in the macOS Keychain, triage via `triage_ticket` MCP prompt, confirm-before-mutate, pinned npm version

See the [full plugin documentation](./plugins/pwdev-glpi/README.md).

### pwdev-postgres

**PostgreSQL operations** (docs in PT-BR) through a purpose-built MCP server
published on npm ([@soarescbm/postgres-mcp](https://github.com/soarescbm/postgres-mcp),
spawned via `npx`): AST-validated read-only SELECT, schema inspection
(tables, indexes, constraints) and DML/DDL where every mutation is a
mandatory dry-run — preview first, execute only with `confirm: true`.

```
init (connection string → Keychain) ─▶ natural conversation via MCP ─▶ esquema / safe mutations
```

**Skills:** postgres (intent→tool map, two-phase mutation rules)
**Key features:** guided setup with the connection string in the macOS Keychain, dedicated `PG_MCP_DATABASE_URL` env var (no collision with project `DATABASE_URL`), mandatory dry-run on every mutation, pinned npm version

See the [full plugin documentation](./plugins/pwdev-postgres/README.md).

### pwdev-brain

**Second brain as a persistent LLM Wiki** (docs in PT-BR) — Markdown wiki in
the [Karpathy pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
kept as an [Open Knowledge Format v0.2](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)
bundle. Sources are read once, discussed with you, and integrated into
concept documents with per-claim citations; queries answer from the wiki and
feed durable syntheses back into it. Ships an embedded **read-only MCP
server** (zero-dependency Node stdio, 6 tools: info, index, list, ranked
search, get, log) usable from Claude Code and any MCP client — writes stay
exclusive to the discussed ingest flow. No API keys.

```
raw/ (immutable) ─▶ ingest (discussed) ─▶ wiki/ OKF v0.2 ─▶ query (cited) ─▶ output/ artifacts
                                          ├─▶ lint (report → approved fixes)
                                          └─▶ MCP brain (read-only, 6 tools)
```

**Skills:** brain (intent routing: "add this to my brain" / "what does my wiki say about X", intent→MCP-tool map)
**Key features:** guided setup (global or per-project brain), immutable `raw/`, nothing written without discussion, footnote citations resolving to `sources[].id`, append-only `wiki/log.md`, BR-nnn lint rule catalog with approved-only fixes, `brain-ingestor` + `brain-linter` subagents, embedded read-only MCP with path-traversal guards and graceful filesystem fallback

See the [full plugin documentation](./plugins/pwdev-brain/README.md).

### pwdev-statusline

Rich terminal **status line** for Claude Code. Displays model, git branch, context usage, rate limits, and token counts in a colorful single-line bar — every segment toggleable.

```
PWDEV | Paulo Soares | session | …/skills-ia/project | Fable 5 | main | ctx:████░░░░░░ 42% | tok:1.5k | 5h:15%
```

**Commands:** `install`, `uninstall`, `customize`, `preview`

**Sections:** Brand, User, Session, Directory (truncated), Model, Git Branch, Context Bar (dynamic color), Tokens (formatted), Rate Limit (3-tier color)

See the [full plugin documentation](./plugins/pwdev-statusline/README.md).

---

## Installation

### Prerequisites

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) installed
- Node.js 18+ (for MCP servers via npx)

### Add the marketplace

```bash
claude plugin marketplace add https://github.com/pwdev-solucoes/pwdev-claude-marketplace.git
```

### Install plugins

```bash
# Spec-driven development (8 subagents, 6 phases, memory graph)
claude plugin install pwdev-code@pwdev-claude-marketplace

# UI/UX engineering (6 subagents, Figma, WCAG, theming)
claude plugin install pwdev-uiux@pwdev-claude-marketplace

# Simplified feature development (7-question plans)
claude plugin install pwdev-feat@pwdev-claude-marketplace

# Interview-driven PRD creation (12-step process)
claude plugin install pwdev-prd@pwdev-claude-marketplace

# Trainable copywriting framework (20 skills, analysis loop)
claude plugin install pwdev-copy@pwdev-claude-marketplace

# AI creative generation for social media (API orchestration, spend guard)
claude plugin install pwdev-social-media@pwdev-claude-marketplace

# Platform, operations & incident response (safe-execution posture)
claude plugin install pwdev-devops@pwdev-claude-marketplace

# YouTrack management (official MCP + REST fallback)
claude plugin install pwdev-youtrack@pwdev-claude-marketplace

# GLPI ITSM management (own MCP server via npx)
claude plugin install pwdev-glpi@pwdev-claude-marketplace

# PostgreSQL operations (own MCP server via npx, mandatory dry-run)
claude plugin install pwdev-postgres@pwdev-claude-marketplace

# Second brain — LLM Wiki in Open Knowledge Format (embedded read-only MCP)
claude plugin install pwdev-brain@pwdev-claude-marketplace

# Rich terminal status line
claude plugin install pwdev-statusline@pwdev-claude-marketplace
```

Install only the plugins you need. Each one works independently.

---

## Configuration

All plugins share a unified configuration stored in `.planning/config.json`. This is set up during `/init` of any plugin.

### Language Selection

Every command supports **Portuguese (PT-BR)** and **English (EN)**. The language is configured once and applied across all plugins.

- During `/init`: you are prompted to choose your language
- During other commands: the saved preference is used silently
- Mid-conversation switch: if you change language, the agent detects it and offers to update your preference

```json
{
  "lang": "pt-BR"
}
```

Technical terms (API, CRUD, REST, endpoint) always stay in English regardless of language choice. File names and structured data keys also remain in English.

### Model Profiles

Only **subagents** resolve models — inline personas run on the session model.
Each plugin ships its own profile table in `references/model-profiles.md`
(single source of truth per plugin). The shared `model_profile`
(`performance` / `balanced` / `economy`) applies across plugins; overrides
are per-subagent, with namespaced keys where needed:

- pwdev-code: `"executor"`, `"advisor"`, `"verifier"`, `"simplifier"`, ...
  (the executor also routes per task via the plan's `Complexity:` header)
- pwdev-feat: `"feat-executor"`, `"feat-advisor"`
- pwdev-uiux: `"uiux-ui-builder"`, `"uiux-ux-critic"`, ...
- pwdev-prd: no subagents — nothing to configure

```json
{
  "lang": "pt-BR",
  "model_profile": "balanced",
  "model_overrides": {
    "executor": "opus",
    "uiux-ui-builder": "opus"
  }
}
```

---

## Audit Trail

All plugins share an optional SQLite audit database at `.planning/pwdev-audit.db`. It is **disabled by default** and configured during `/init`. The database file is never versioned (automatically added to `.gitignore`).

**How data gets here (v2 — deterministic, via hooks):** each plugin ships
`hooks/hooks.json` + POSIX scripts that record automatically — session
start/stop, subagent runs with real `session_id` and `duration_ms`,
`.planning/` artifact writes, command milestones, and configuration changes
(`config_changes`). No agent runs inline INSERTs anymore. A secret-guard
PreToolUse hook (every plugin) blocks reads of `.env`/`*.pem`/`*.key`/`id_rsa*`.

Rows are distinguished by the `plugin` column — filter with
`WHERE plugin='pwdev-code'` (or `pwdev-feat`, `pwdev-prd`, `pwdev-uiux`).

### Querying the Audit Trail

Every plugin includes an `/audit` command to query the database interactively:

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
/pwdev-code:audit              # summary dashboard
/pwdev-code:audit stats        # detailed statistics
/pwdev-code:audit export       # generate PDF report at .planning/audit-report.pdf
/pwdev-code:audit query "SELECT * FROM events WHERE action='failed'"
```

The `export` sub-command generates a comprehensive PDF report with executive summary, event log, decisions, artifacts, statistics, and configuration history. Supports pandoc, weasyprint, and wkhtmltopdf with automatic detection and graceful fallback to Markdown.

Add `.planning/pwdev-audit.db` to `.gitignore` (recommended).

---

## Updating

### Update the marketplace

Pull the latest changes from the marketplace repository:

```bash
claude plugin marketplace update
```

This runs `git pull` on the local copy at `~/.claude/plugins/marketplaces/pwdev-claude-marketplace/`.

### Update installed plugins

Reinstall each plugin you use to pick up the latest version:

```bash
claude plugin install pwdev-code@pwdev-claude-marketplace
claude plugin install pwdev-uiux@pwdev-claude-marketplace
claude plugin install pwdev-feat@pwdev-claude-marketplace
claude plugin install pwdev-prd@pwdev-claude-marketplace
claude plugin install pwdev-copy@pwdev-claude-marketplace
claude plugin install pwdev-social-media@pwdev-claude-marketplace
claude plugin install pwdev-devops@pwdev-claude-marketplace
claude plugin install pwdev-youtrack@pwdev-claude-marketplace
claude plugin install pwdev-glpi@pwdev-claude-marketplace
claude plugin install pwdev-postgres@pwdev-claude-marketplace
claude plugin install pwdev-statusline@pwdev-claude-marketplace
```

This copies the updated plugin files to the local cache. **Your project data (`.planning/`) is never touched** — only the plugin commands and agents are updated.

### Migrate your workspace (if needed)

After updating, run `/init` in your project to check for migration steps:

```
/pwdev-feat:init
/pwdev-code:init
/pwdev-uiux:init
/pwdev-prd:init
```

The `init` command detects existing workspaces and:
- Preserves all your data (plans, PRDs, specs, reports)
- Offers guided migration if the folder structure changed
- Asks to confirm or update language, model profile, and audit settings
- Never overwrites without your confirmation

### What gets updated vs. what stays

| Component | Location | On update |
|-----------|----------|-----------|
| Commands & agents | `~/.claude/plugins/cache/` | **Replaced** with new version |
| Plugin config | `~/.claude/plugins/installed_plugins.json` | **Updated** (version, commit SHA) |
| Project data | `.planning/` (your project) | **Untouched** — never modified by updates |
| config.json | `.planning/config.json` | **Preserved** — init uses merge, not overwrite |
| Audit database | `.planning/pwdev-audit.db` | **Preserved** — append-only, never reset |

### Version compatibility

Each plugin stores its version in `.claude-plugin/plugin.json`. After updating, you can check:

```bash
# Check installed version
cat ~/.claude/plugins/cache/pwdev-claude-marketplace/pwdev-feat/*/plugin.json | grep version
```

Breaking changes (major version bumps) are documented in each plugin's README under "What's New".

---

## License

Apache-2.0

*Maintained by [Paulo Soares](https://github.com/soarescbm)*
