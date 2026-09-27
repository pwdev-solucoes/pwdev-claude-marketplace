# PWDEV-PRD v3.0.0

*Read this in [Português Brasileiro](./README.pt-BR.md)*

> **Interview-Driven PRD Creation for Claude Code, Codex, Hermes Agent and OpenCode**

```
Structured interview → Approved PRD → Roadmap with dependencies → GitHub Project
```

PWDEV-PRD guides you through a **12-step structured interview** to create complete, consistent, technology-agnostic Product Requirements Documents for features or entire systems.

---

## Methodology

### The Problem

PRDs are often incomplete, inconsistent, or biased toward a specific technology. Teams start building without clear objectives, metrics, acceptance criteria, or risk assessment. The result: scope creep, missed requirements, and features that don't solve the actual problem.

### The Solution

A specialized interviewer agent that:
- Asks **one question at a time** and waits for your answer
- Offers **2-3 options** when you don't know the answer
- Summarizes and confirms at the end of each stage
- Marks unknowns as **hypotheses** (never invents)
- Runs **consistency checks** before generating the final PRD
- Produces a **structured document** ready for execution

### Technology-Agnostic

PRDs created by this plugin describe **what** needs to be built and **why**, not **how**. Architecture sections capture decisions at a system level (monolith vs microservice, sync vs async) without specifying frameworks, libraries, or languages.

This makes PRDs compatible with any downstream workflow:
- `/pwdev-feat:feat` for simplified feature development
- `/pwdev-code:discover` for rigorous spec-driven development
- Manual handoff to engineering teams

---

## Installation

| Runtime | Install | Invoke |
|---|---|---|
| Claude Code | `claude plugin install pwdev-prd@pwdev-claude-marketplace` | `/pwdev-prd:create "…"` |
| Codex | add this repository as a marketplace and enable **pwdev-prd** (`.agents/plugins/marketplace.json`) | `$prd-create …` |
| Hermes Agent | `hermes plugins install pwdev-solucoes/pwdev-claude-marketplace --enable` (entry point `.hermes-plugin/`) | `skill_view("pwdev-prd:prd-create")` or just ask |
| OpenCode | `python3 plugins/pwdev-prd/.opencode-plugin/install.py [--project <dir>]` | `/prd-create …` or the `skill` tool |

The workflow lives in nine portable skills (`skills/prd-*`); each Claude command is a thin
wrapper over one of them (`create → prd-create`, `roadmap → prd-roadmap`, ...). The roadmap
writer is a subagent on every runtime that has one (Claude `Agent`, Codex `spawn_agent`, Hermes
`delegate_task`, OpenCode `task`) and runs inline otherwise; Codex subagents need
`[features] multi_agent = true` in `~/.codex/config.toml`. Hooks (audit, secret guard) are
Claude-only; elsewhere the audit trail has the milestone events only. Details:
[`references/runtime.md`](./references/runtime.md).

---

## What's New in v3.0.0

- **Portable to Codex, Hermes Agent and OpenCode** — nine `prd-*` skills are the single source
  of truth; Claude commands are wrappers; Codex manifest and `openai.yaml` per skill; Hermes
  adapter with a first-turn bootstrap; OpenCode installer that links the skills and writes one
  `/prd-<name>` command each.
- The roadmap writer's contract moved to `references/roadmap-agent.md`, shared by every runtime
  and by the inline fallback.
- **User stories, CA and RN per feature** — the PRD gains a `### Business Rules` section
  (`RN-xx`, captured in interview step 5); the roadmap writer drafts 1–3 user stories per feature
  ("Como…, quero…, para…", Gherkin CA with happy and error paths, the RN they apply); the new
  **`/pwdev-prd:stories {slug} [feature|next]`** evolves one feature at a time with you up to the
  Definition of Ready (INVEST, 3–8 CA, every RN verified by a CA). The checker enforces the
  standard (adapted from pwdev-code `skill-user-stories`, see `references/user-stories.md`) and
  generates `STORIES.md` and `stories/US-NN-*.md`. Publishing puts the stories in the feature
  issue or makes them sub-issues.

## What's New in v2.1.0

- **Roadmap with a dependency chain** — `/pwdev-prd:roadmap {slug}` decomposes an
  approved PRD into Phase → Epic → Feature → Task (same IDs as pwdev-power and
  pwdev-code) with explicit `depends_on` edges. The deterministic checker
  `scripts/roadmap-check.py` rejects cycles, dangling edges and orphan requirements, then
  generates `DEPENDENCIES.md`: Mermaid graph, **waves** (what can run in parallel) and the
  **critical path**. The roadmap is written by the plugin's first subagent,
  `pwdev-prd:roadmap`; the interview itself stays inline.
- **Publish to GitHub** — `/pwdev-prd:publish {slug}` hands the approved
  `roadmap.json` (`pwdev-roadmap/1`) to the **pwdev-github** plugin: GitHub Project from a
  customizable template, issues, sub-issues, milestones and native "blocked by" links.
- **Approval gate** — PRDs carry `Status: DRAFT | APPROVED`; only approved PRDs become
  roadmaps. `refine` bumps `Version`, keeps a `Change Log` and re-opens approval.
- **Traceable IDs** — `FR-xx`, `NFR-xx`, `AC-xx`; priority is MoSCoW everywhere
  (template and JSON used to disagree).
- **Safer `export --github`** — preflight for auth, repo, missing labels and the 65,536-char
  body limit, plus a preview before creating the issue.
- **`list`** shows status, version, roadmap state and the GitHub Project URL.

## What's New in v2.0.0

Rebuilt on the modern Claude Code plugin system. No slash command renamed or
removed.

- **Interviewer is inline by design** (`references/interview-method.md`): it
  talks to you one question at a time — subagents cannot do that, so this
  plugin has **zero subagents**. The old prose-persona agent file is gone,
  along with the dead "Model Resolution" blocks (nothing here resolves a
  model; the interview runs on the session model).
- **Canonical prd.json structure** finally defined (in
  `references/interview-method.md`) — `create` and `export` used to point at
  a JSON structure that didn't exist anywhere.
- **Deterministic audit via hooks** on the shared `.planning/pwdev-audit.db`
  (rows filtered with `WHERE plugin='pwdev-prd'`): session events with real
  `session_id`, `.planning/` artifact writes, command milestones and
  `config_changes` via `audit-log.sh`. Secret-guard PreToolUse hook included.
- **Fixes**: hardened audit query guard (single-statement SELECT only);
  `echo -e` → `printf`; dead `$SUB_COMMAND` removed; phantom model-profile
  roles (orchestrator/builder/scanner...) removed; wrong inherited audit
  examples (DISCOVER phases) removed; paths now resolve via
  `${CLAUDE_PLUGIN_ROOT}`.

## What's New in v1.1.2

- **Language Selection** — All commands support PT-BR and EN. Configured during `/pwdev-prd:init`.
- **Model Profiles** — Agent model configurable via `performance`, `balanced`, or `economy` profiles.
- **Audit Trail (opt-in)** — Optional SQLite logging of commands and decisions. Disabled by default.

---

## 12-Step Interview Process

| Step | Topic | What is captured |
|:----:|-------|-----------------|
| 1 | **Context & Overview** | Product, audience, deployment context, business objective |
| 2 | **Problem & Opportunity** | Current pain, real examples with numbers, failed attempts |
| 3 | **Objectives & Metrics** | Measurable goals with metric and target |
| 4 | **Scope** | What's in, what's explicitly out |
| 5 | **Functional Requirements and Business Rules** | Name, description, main flow, alternatives, errors, priority; business rules `RN-xx` with a testable statement and an example |
| 6 | **Non-Functional Requirements** | Performance, availability, security, observability, compliance |
| 7 | **Architecture & Approach** | Components, integrations, communication patterns |
| 8 | **Decisions & Trade-offs** | What's decided, why, what's the cost |
| 9 | **Dependencies** | Technical, organizational, external |
| 10 | **Risks & Mitigation** | Probability, impact, mitigation (multiple items), contingency |
| 11 | **Acceptance Criteria** | Objective, verifiable checklist |
| 12 | **Testing & Validation** | Test types, validation strategy |

### Consistency Checks

Before generating the final PRD, the agent validates:
- Every objective has a metric and target
- Every functional requirement has name, flow, and priority
- Every business rule has an `RN-xx` ID, a testable statement and an example
- NFRs include at least performance and availability
- Out of scope doesn't contradict in scope
- Architecture supports declared NFRs
- Every decision has justification and trade-off
- Every risk has probability, impact, mitigation, and contingency
- Acceptance criteria are objective and verifiable

---

## Agent

| Persona | Where it runs | What it does |
|---------|---------------|-------------|
| **PRD interviewer** | Inline, main context (`references/interview-method.md`) — it talks to you, so it is never a subagent | Conducts the 12-step interview, validates consistency, generates PRD.md + prd.json |
| **Roadmap** (`agents/roadmap.md`) | Subagent `pwdev-prd:roadmap`, dispatched by `/pwdev-prd:roadmap` — never talks to you | Writes the roadmap files and `roadmap.json` with the dependency chain; the command runs the checker and holds the approval gate |

### Agent Boundaries
- Never chooses specific technologies
- Never invents requirements (marks unknowns as hypotheses)
- Never asks double questions
- Always confirms understanding before moving on

---

## Commands

### Setup

| Command | What it does |
|---------|-------------|
| `/pwdev-prd:init` | Create `.planning/prds/` workspace, configure language and audit |

### PRD Creation

| Command | What it does |
|---------|-------------|
| `/pwdev-prd:create "desc"` | Start structured interview → generate PRD.md + optional prd.json |
| `/pwdev-prd:refine {slug}` | Update specific sections of an existing PRD (bumps version, re-opens approval) |

### Roadmap and GitHub

| Command | What it does |
|---------|-------------|
| `/pwdev-prd:roadmap {slug}` | Approved PRD → roadmap with dependency chain, waves, critical path, traceability and draft user stories |
| `/pwdev-prd:stories {slug} [feature\|next]` | Evolve one feature at a time: user stories, acceptance criteria (CA) and business rules (RN) up to the Definition of Ready |
| `/pwdev-prd:publish {slug}` | Approved roadmap → GitHub Project, issues, sub-issues and blocked-by (needs pwdev-github) |

### Management

| Command | What it does |
|---------|-------------|
| `/pwdev-prd:list` | List all PRDs with status |
| `/pwdev-prd:export {slug}` | Export as JSON or GitHub issue |
| `/pwdev-prd:export {slug} --json` | Regenerate prd.json |
| `/pwdev-prd:export {slug} --github` | Create one GitHub issue from the PRD (preflight + preview) |
| `/pwdev-prd:audit` | Query the audit trail — summary, events, decisions, artifacts, stats, export PDF |

---

## Language & Model Configuration

### Language

All commands support **Portuguese (PT-BR)** and **English (EN)**. Configured during `/pwdev-prd:init` and stored in `.planning/config.json`.

- `/pwdev-prd:init` — always asks for language preference
- Other commands — use saved preference silently
- Override — switch language mid-conversation and confirm when prompted

### Model

The interview runs inline on the session model. The single subagent,
`pwdev-prd:roadmap`, declares `model: inherit`, so it also follows the session
model — there is nothing to configure. `model_profile` in the
shared `.planning/config.json` belongs to the plugins with subagents
(pwdev-code, pwdev-feat) and is left untouched by `/pwdev-prd:init`.

The shared config still holds `lang` and `audit`:

```json
{
  "lang": "pt-BR",
  "audit": false
}
```

---

## Audit Trail

All plugins share an optional SQLite audit database at `.planning/pwdev-audit.db`. It is **disabled by default** and configured during `/init`. The database file is never versioned (automatically added to `.gitignore`).

**How data gets here (v2.0 — deterministic, via hooks):**
- `scripts/audit-hook.sh` (SessionStart, PostToolUse, Stop) → session events
  with real `session_id`, `.planning/` artifact writes
- `scripts/audit-log.sh` → command milestones (`event`) and configuration
  changes (`config` → the `config_changes` table, populated by `/init`)
- `scripts/guard-secrets.sh` (PreToolUse) → blocks reads of `.env`, `*.pem`,
  `*.key`, `id_rsa*` (`.env.example` allowed)

The database is **shared with pwdev-code/pwdev-feat** — filter this plugin's
rows with `WHERE plugin='pwdev-prd'`.

The audit database runs **in parallel** with Markdown files — agents continue to read and write Markdown as before. SQLite is a bonus layer for history and analysis.

### Querying the Audit Trail

Use `/pwdev-prd:audit` to query the database interactively:

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
/pwdev-prd:audit              # summary dashboard
/pwdev-prd:audit stats        # detailed statistics
/pwdev-prd:audit export       # generate PDF report at .planning/audit-report.pdf
/pwdev-prd:audit query "SELECT * FROM events WHERE action='failed'"
```

Add `.planning/pwdev-audit.db` to `.gitignore` (recommended).

---

## Output Formats

### Markdown (PRD.md)

Structured document with standardized sections:

```
PRD: [product] [feature]
├── Summary
├── Context and Problem
├── Objectives and Metrics (table)
├── Scope (in / out)
├── Functional Requirements (per requirement)
├── Non-Functional Requirements (by category)
├── Architecture and Approach
├── Decisions and Trade-offs
├── Dependencies
├── Risks and Mitigation
├── Acceptance Criteria (checklist)
└── Testing and Validation
```

### JSON (prd.json) — Optional

Structured data with English keys, content in original language:

```json
{
  "meta": { "product", "feature", "version", "date" },
  "context": { "summary", "target_audience", "problems" },
  "goals": [{ "goal", "metric", "target" }],
  "scope": { "in_scope", "out_of_scope" },
  "functional_requirements": [{ "id", "name", "main_flow", "priority" }],
  "non_functional_requirements": [{ "category", "specifications" }],
  "architecture": { "approach", "components", "integrations" },
  "decisions_tradeoffs": [{ "decision", "justification", "trade_off" }],
  "dependencies": [{ "type", "title", "description" }],
  "risks": [{ "risk", "probability", "impact", "mitigation", "contingency_plan" }],
  "acceptance_criteria": [],
  "testing_validation": { "test_types", "strategy" }
}
```

---

## Workspace

```
.planning/prds/
├── user-authentication/
│   ├── PRD.md              # Structured PRD document (Status: DRAFT | APPROVED)
│   ├── prd.json            # Optional JSON export
│   └── roadmap/            # /pwdev-prd:roadmap — see references/roadmap-format.md
│       ├── roadmap.json    # pwdev-roadmap/1 machine contract
│       ├── ROADMAP.md  TRACEABILITY.md  RISKS.md
│       ├── DEPENDENCIES.md # generated: Mermaid graph, waves, critical path
│       ├── STORIES.md      # generated: stories per feature, status, CA and RN
│       ├── stories/        # generated: US-NN-<slug>.md (edit through /pwdev-prd:stories)
│       └── F01-<slug>/…    # PHASE.md, EPIC.md, one file per feature
├── inventory-management/
│   ├── PRD.md
│   └── prd.json
└── ...
```

---

## Smart Defaults

When the user doesn't know, the agent offers these as **hypotheses** (explicitly marked):

| Aspect | Default |
|--------|---------|
| API latency | p95 < 150ms |
| Availability (external) | 99.9% |
| Availability (internal) | 99.5% |
| Observability | Structured logs + error metrics + distributed tracing |
| Security | Auth + RBAC + sensitive change audit |
| Critical updates | Transactional |

---

## License

Apache-2.0 — See [LICENSE](./LICENSE)

*PWDEV-PRD v3.0.0 — Clear requirements, consistent documents, better features.*
*Maintained by [Paulo Soares](https://github.com/soarescbm)*
