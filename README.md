# PWDEV Marketplace

*Leia em [Português Brasileiro](./README.pt-BR.md).*

Marketplace of plugins for Claude Code, Codex and compatible PWDEV runtimes.

## Install

```bash
claude plugin marketplace add /path/to/pwdev-claude-marketplace
claude plugin install <plugin>@pwdev-claude-marketplace
```

Restart the runtime after installation. Read each plugin README for its setup and permissions.

## Choose by goal

| Goal | Plugins |
|---|---|
| Spec-driven development | [pwdev-power](./plugins/pwdev-power/), [pwdev-flow](./plugins/pwdev-flow/), [sdd-composy](./plugins/sdd-composy/) |
| Coding and delegation | [pwdev-code](./plugins/pwdev-code/), [pwdev-feat](./plugins/pwdev-feat/) |
| Requirements and UI/UX | [pwdev-prd](./plugins/pwdev-prd/), [pwdev-uiux](./plugins/pwdev-uiux/) |
| Quality assurance | [pwdev-qa](./plugins/pwdev-qa/) |
| Copy and social content | [pwdev-copy](./plugins/pwdev-copy/), [pwdev-social-media](./plugins/pwdev-social-media/) |
| DevOps and operations | [pwdev-devops](./plugins/pwdev-devops/) |
| Knowledge and integrations | [pwdev-brain](./plugins/pwdev-brain/), [pwdev-glpi](./plugins/pwdev-glpi/), [pwdev-obsidian](./plugins/pwdev-obsidian/), [pwdev-postgres](./plugins/pwdev-postgres/), [pwdev-youtrack](./plugins/pwdev-youtrack/) |
| Terminal support | [pwdev-statusline](./plugins/pwdev-statusline/) |

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

## Plugins

| Plugin | Description | Version | License |
|--------|-------------|:-------:|:-------:|
| [**pwdev-flow**](./plugins/pwdev-flow/) | Portable spec-driven development for Claude Code **and** Codex — one `.planning/flow` contract, 17 commands, semantic opt-in audit, guarded external CLI delegation, isolated native fleets (`claude -p` / `codex exec`) | 0.6.0 | Apache-2.0 |
| [**sdd-composy**](./plugins/sdd-composy/) | Portable spec-driven development for Claude Code and Codex — shared contracts, durable state, OKF v0.2 artifacts, traceability, bounded loops, and isolated fleets | 0.1.0 | Apache-2.0 |
| [**pwdev-power**](./plugins/pwdev-power/) | Disciplined spec-driven development for Claude Code, Codex **and** Hermes Agent — brainstorm gate, plans with verbatim constraints, subagent-driven execution with a ledger and bounded fix loop, adversarial verification, codebase map, isolated cmux fleets as a visual panel or unattended | 0.1.0 | Apache-2.0 |
| [**pwdev-code**](./plugins/pwdev-code/) | Spec-driven development — 8 real subagents (incl. advisor), per-task model routing, memory graph, opt-in parallel waves, external CLI delegation (Codex/OpenCode/Kimi/Gemini/Kiro), 23 commands | 2.4.0 | Apache-2.0 |
| [**pwdev-uiux**](./plugins/pwdev-uiux/) | UI/UX engineering — 6 real subagents, 5-phase workflow with gates, Figma, WCAG 2.1 AA | 2.0.1 | Apache-2.0 |
| [**pwdev-feat**](./plugins/pwdev-feat/) | Simplified feature development — PWDEVIA 7-question plans inline + executor and advisor subagents | 2.1.1 | Apache-2.0 |
| [**pwdev-prd**](./plugins/pwdev-prd/) | Interview-driven PRD creation — 12-step inline interview, Markdown + canonical JSON | 2.0.1 | Apache-2.0 |
| [**pwdev-qa**](./plugins/pwdev-qa/) | Portable quality assurance for Claude Code, Codex and Hermes Agent — 10 workflows, 17 specialist guides, tool recommendation, auditable evidence, offline HTML and PDF reports | 0.1.0 | Apache-2.0 |
| [**pwdev-copy**](./plugins/pwdev-copy/) | Trainable copywriting framework — 20 skills across the full cycle (VOC research → copy → review → analysis), 5 real subagents | 1.1.0 | Apache-2.0 |
| [**pwdev-social-media**](./plugins/pwdev-social-media/) | AI creative generation for social — API orchestration (Ideogram, Leonardo, Flux, Runway, Freepik) with spend guard, 19 skills, 4 subagents | 2.0.1 | Apache-2.0 |
| [**pwdev-devops**](./plugins/pwdev-devops/) | Platform, operations & incident response — safe-execution posture with guard script, 24 skills, 4 subagents | 1.0.0 | Apache-2.0 |
| [**pwdev-youtrack**](./plugins/pwdev-youtrack/) | YouTrack management — official built-in MCP server (2025.3+) for issues, articles & work log; REST fallback for boards, sprints, time reports | 1.0.0 | Apache-2.0 |
| [**pwdev-glpi**](./plugins/pwdev-glpi/) | Multi-runtime GLPI 10/11 ITSM for Claude Code, Codex and Hermes — own MCP server via npx (@soarescbm/mcp-glpi): tickets CRUD, triage with MCP prompts, queue reports, assets & KB | 1.2.0 | Apache-2.0 |
| [**pwdev-postgres**](./plugins/pwdev-postgres/) | PostgreSQL — own MCP server via npx (@soarescbm/postgres-mcp): AST-validated read-only SELECT, schema inspection, DML/DDL with mandatory dry-run | 1.0.0 | Apache-2.0 |
| [**pwdev-obsidian**](./plugins/pwdev-obsidian/) | Obsidian vault — MCP server built into the Local REST API community plugin: read, write and structurally edit notes (heading/block/frontmatter), JsonLogic and free-text search, tags, active file, command palette | 1.0.0 | Apache-2.0 |
| [**pwdev-brain**](./plugins/pwdev-brain/) | Second brain as an LLM Wiki (Karpathy pattern) in Open Knowledge Format v0.2 — discussed ingest with per-claim citations, cited query, compliance lint; 2 subagents, embedded read-only MCP (6 tools) | 1.1.0 | Apache-2.0 |
| [**pwdev-statusline**](./plugins/pwdev-statusline/) | Rich terminal status line — dynamic colors, formatted tokens, fully configurable | 1.1.0 | Apache-2.0 |

### pwdev-power

Disciplined development that runs on **three runtimes** — Claude Code, Codex and
Hermes Agent — from one set of skills, with isolated autonomous fleets on
**cmux**.

```
[MAP] ─▶ PRD ─▶ ROADMAP ─▶ BRAINSTORM ─▶ PLAN ─▶ EXECUTE ─▶ VERIFY ─▶ FINISH
```

It pairs a product layer — a requirement, then a `Phase → Epic → Feature → Task`
roadmap with mandatory traceability — with subagent-driven execution: a durable
ledger, one brief per task, a fresh reviewer between tasks, and a fix loop capped
at five rounds with every judgement call recorded as a ruling.

Three rules hold throughout, each written against the rationalization that
defeats it: **no production code without a failing test observed failing**, **no
fix without root cause first**, and **no success claim without running the
command and reading its output**. Verification is adversarial — the verifier is
told to *refute* completion, not confirm it.

`init` maps the codebase into four context documents so a design does not
re-derive the architecture every phase. The privileged provider command exists in
exactly one adapter per runtime; the runtime is fixed by the launcher chosen
before any mutation, and a runner whose adapter disagrees refuses to start. With
Hermes present, approved phases can also be dispatched through its Kanban board.

Fleets are how several approved phases run at once, and how you watch them is
the choice. `/pwdev-power:fleet` opens a **visual cmux panel** by default — one
pane per phase, each an interactive session in its own worktree already reading
that phase's spec and plan, one to four members, one panel at a time. `--auto`
runs the unattended fleet instead, driving `plan → execute → review → verify` on
its own and reporting through the sidebar. Watching is not approving: both
vectors run with permissions bypassed, so both require you to acknowledge the
dangerous flag before anything launches. A member that stopped mid-flight
resumes with `--resume`, re-running the stage its runner status records rather
than starting over — and that flag is also the only thing that may restart a
member parked at `NEEDS_HUMAN`.

**Subagents:** mapper, roadmap, implementer, task-reviewer, verifier

**Ships:** 7 commands · 5 subagents · 15 skills · hooks

See the [full plugin documentation](./plugins/pwdev-power/README.md).

### pwdev-flow

Portable, approval-gated development that runs natively in **both Claude Code
and Codex** from one source package. The workflow contracts live in
runtime-neutral skills and references; each host gets a thin adapter.

```
DISCOVER ─▶ DESIGN ─▶ PLAN ─▶ EXECUTE ─▶ [SIMPLIFY] ─▶ REVIEW ─▶ VERIFY
```

A workflow started in one runtime can be continued in the other: both read and
write the same `.planning/flow` artifacts. Autonomous fleets run approved phases
in isolated Git worktrees with their own Docker stack and tmux pane, driven by
the runtime's own headless CLI — `claude -p` or `codex exec`. The two privileged
vectors are built in separate adapters and can never turn into one another.

**No subagents, no hooks, no MCP servers**, by design: the audit trail is a
semantic, opt-in JSONL log written only after an action actually happened, so it
stays meaningful in both hosts instead of being host-specific telemetry.

**Ships:** 17 commands · 17 skills · no subagents, no hooks, no MCP

See the [full plugin documentation](./plugins/pwdev-flow/README.md).

### sdd-composy

Portable spec-driven development for Claude Code and Codex from one shared contract set.
It keeps human contracts under `tasks/prd-<slug>/`, operational state under
`.planning/sdd-composy/`, and generated project Markdown aligned with OKF v0.2.

```
INIT ─▶ MAP ─▶ PRD ─▶ STORIES ─▶ TECHSPEC ─▶ TASKS ─▶ EXECUTE ─▶ QA ─▶ EVIDENCE ─▶ REVIEW ─▶ VERIFY
```

**Ships:** 17 commands · 17 skills · no subagents · no MCP

See the [full plugin documentation](./plugins/sdd-composy/README.md).

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

**Ships:** 23 commands · 8 subagents · 3 skills · hooks

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

**Ships:** 13 commands · 6 subagents · 10 skills · hooks

See the [full plugin documentation](./plugins/pwdev-uiux/README.md).

### pwdev-feat

Simplified AI-assisted feature development using the **PWDEVIA 7-question methodology**. Describe what you want, get a structured plan, execute it.

```
Describe ─▶ Plan (PWDEVIA, inline) ─▶ Execute (real subagent, IMPLEMENT/REPORT)
```

**Agents:** PWDEVIA (inline planner) + executor and advisor (real subagents); reads pwdev-code's curated project memory when present

**Plan types:** Feature, Backend, Frontend, Test, Review, Quick

**Ships:** 12 commands · 2 subagents · hooks

See the [full plugin documentation](./plugins/pwdev-feat/README.md).

### pwdev-prd

Interview-driven **PRD creation** with a 12-step structured process — run
inline (the interviewer talks to you; zero subagents by design).
Technology-agnostic, outputs Markdown + canonical JSON.

```
Interview (12 steps) ─▶ PRD.md ─▶ Export (JSON / GitHub Issue)
```

**Outputs:** Structured PRD with objectives, metrics, functional/non-functional requirements, architecture, risks, acceptance criteria

**Ships:** 6 commands · no subagents, by design · hooks

See the [full plugin documentation](./plugins/pwdev-prd/README.md).

### pwdev-qa

**Portable quality assurance** for Claude Code, Codex and Hermes Agent: intent
routing across ten QA workflows, specialist guidance for web, API, mobile, data,
accessibility, performance, security, automation and production, tool
recommendation from observed context, auditable evidence, and equivalent
offline HTML and PDF reports.

```
init ─▶ strategy ─▶ test / explore ─▶ bug ─▶ regression ─▶ review ─▶ release ─▶ report
```

**Skills:** qa (intent→workflow router), 17 qa-specialist-* guides, qa-tooling
**Key features:** evidence with SHA-256 digests, acceptance never inferred from confidence, offline HTML and PDF parity, no mandatory MCP server

**Ships:** 10 commands · 29 skills · no MCP

See the [full plugin documentation](./plugins/pwdev-qa/README.md).

### pwdev-copy

Trainable **copywriting framework** (docs in PT-BR): one context file defines
brand, ICP, and voice; **20 skills** produce consistent copy from it. The same
installation serves any client — you swap the training file.

```
treinar ─▶ voc ─▶ brief ─▶ copy ─▶ revisar ─▶ publicar ─▶ analisar ↺
```

**Subagents:** voc, copywriter, reviewer, adversarial-copy, analyst
**Key features:** 7-sweep anti-slop review, adversarial conversion review, Ogilvy brief gate, performance analysis loop

**Ships:** 9 commands · 5 subagents · 20 skills

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

**Ships:** 9 commands · 4 subagents · 19 skills · MCP

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
**Key features:** 24 skills (AWS, Kubernetes, Docker, Linux, Nginx, PostgreSQL, observability, incident, security, Proxmox, FinOps, …), read-only audits, FinOps reports

**Ships:** 7 commands · 4 subagents · 24 skills · MCP

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

**Ships:** 4 commands · 2 skills · MCP

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

**Ships:** 4 commands · 1 skill · MCP

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

**Ships:** 3 commands · 1 skill · MCP

See the [full plugin documentation](./plugins/pwdev-postgres/README.md).

### pwdev-obsidian

Manages an [Obsidian](https://obsidian.md) vault through the **MCP server built
into the "Local REST API" community plugin** — no separate server to install.

Reads, writes and structurally edits notes by heading, block or frontmatter
rather than rewriting whole files, and searches the vault with both JsonLogic and
free text. Also reaches tags, the active file, and the command palette.

**Ships:** 3 commands · 1 skill · MCP

See the [full plugin documentation](./plugins/pwdev-obsidian/README.md).

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

**Ships:** 5 commands · 2 subagents · 1 skill · embedded MCP (6 tools)

See the [full plugin documentation](./plugins/pwdev-brain/README.md).

### pwdev-statusline

Rich terminal **status line** for Claude Code. Displays model, git branch, context usage, rate limits, and token counts in a colorful single-line bar — every segment toggleable.

```
PWDEV | Paulo Soares | session | …/skills-ia/project | Fable 5 | main | ctx:████░░░░░░ 42% | tok:1.5k | 5h:15%
```

**Commands:** `install`, `uninstall`, `customize`, `preview`

**Sections:** Brand, User, Session, Directory (truncated), Model, Git Branch, Context Bar (dynamic color), Tokens (formatted), Rate Limit (3-tier color)

**Ships:** 4 commands · no subagents, no skills, no MCP

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
# Disciplined spec-driven development on Claude Code, Codex and Hermes (visual cmux fleet panels)
claude plugin install pwdev-power@pwdev-claude-marketplace

# Portable spec-driven development for Claude Code and Codex (17 commands, native fleets)
claude plugin install pwdev-flow@pwdev-claude-marketplace

# Portable SDD workflow with OKF v0.2 artifacts and traceable execution
claude plugin install sdd-composy@pwdev-claude-marketplace

# Spec-driven development (8 subagents, 6 phases, memory graph)
claude plugin install pwdev-code@pwdev-claude-marketplace

# UI/UX engineering (6 subagents, Figma, WCAG, theming)
claude plugin install pwdev-uiux@pwdev-claude-marketplace

# Simplified feature development (7-question plans)
claude plugin install pwdev-feat@pwdev-claude-marketplace

# Interview-driven PRD creation (12-step process)
claude plugin install pwdev-prd@pwdev-claude-marketplace

# Portable quality assurance (10 workflows, evidence, HTML/PDF reports)
claude plugin install pwdev-qa@pwdev-claude-marketplace

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

# Obsidian vault — notes, structural editing and search (MCP via Local REST API)
claude plugin install pwdev-obsidian@pwdev-claude-marketplace

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
claude plugin install pwdev-flow@pwdev-claude-marketplace
claude plugin install pwdev-code@pwdev-claude-marketplace
claude plugin install pwdev-uiux@pwdev-claude-marketplace
claude plugin install pwdev-feat@pwdev-claude-marketplace
claude plugin install pwdev-prd@pwdev-claude-marketplace
claude plugin install pwdev-qa@pwdev-claude-marketplace
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
