# PWDEV-CODE v2.2.0

*Read this in [Português Brasileiro](./README.pt-BR.md)*

> **Spec-Driven Development Framework for Claude Code**

```
Never execute without a plan. Never ship without verification.
```

PWDEV-CODE uses **hybrid orchestration**: interactive phases run in the main
conversation (where the human approves gates), and heavy work is delegated to
**8 real subagents** with fresh context — across **6 phases** with correction
loops and **curated project memory**, so every line of code is planned,
traceable, and verified.

---

## What's New in v2.2.0

- **Advisor subagent** (`advisor` + `NEEDS_ADVICE` status): when the executor
  hits a hard decision mid-task (spec ambiguity, architectural fork, repeated
  verification failure with a concrete question), it stops and asks. The
  orchestrator consults the advisor — the strong model (Opus even in
  `balanced`), read-only, `effort: high` — and re-spawns the executor with
  the decision attached. Max 1 consultation per task; high-confidence advice
  is captured as a `decision` memory.
- **Per-task model routing**: plans now declare `Complexity: low|medium|high`
  in the wave header; `/pwdev-code:execute` resolves the executor's model per
  task via the complexity matrix in `references/model-profiles.md`
  (e.g. `balanced`: low/medium → sonnet, high → opus; fix plans are
  implicitly high). Backward compatible — no field means `medium`, exactly
  the old behavior.
- **Memory graph**: memories can relate to each other (`related:` frontmatter,
  `[[name]]` links, `[rel:]` suffix in the index). Spawn-time selection
  expands 1 hop through relations (total cap 7) without opening any file.
  New subcommands: `/pwdev-code:memory link <a> <b>` and
  `/pwdev-code:memory graph`.
- **Opt-in parallel waves** (`"parallel_execution": true`): tasks marked
  `Parallel-safe: yes` with disjoint file sets run as a batch of executors in
  isolated git worktrees (`isolation: worktree`), then merge sequentially.
  Default remains serial; any doubt falls back to serial.
- **Optional external reviewer CLI** (`external_models.reviewer` in
  `.planning/config.json`): `/pwdev-code:review` can run a second opinion via
  an external CLI (codex, gemini, opencode, qwen — allowlisted, human-confirmed).
  External findings are advisory only — they never block the review gate.

## What's New in v2.1.0

- **Curated project memory** (`/pwdev-code:memory` + `.planning/memory/`,
  versioned): durable decisions, lessons, and conventions. Every subagent
  spawn gets a RELEVANT MEMORY block; verify rejections and blocked reviews
  auto-capture lessons (cap: 2/phase); design consults decision memories and
  flags contradictions. Protocol: `references/memory.md`.
- **Simplification pass** (`/pwdev-code:simplify` + `simplifier` subagent):
  optional step between EXECUTE and REVIEW. Two passes — ANALYZE proposes
  only >=80%-confidence simplifications (reuse, dead code, complexity,
  efficiency; never bugs, never behavior changes), the human approves by ID,
  APPLY implements with its own `refactor` commit and per-proposal
  verification (failure → revert + SKIPPED). Applying changes marks
  `review_gate: STALE` → review re-runs scoped to the refactor diff.
- **User stories** (`skill-user-stories` + `/pwdev-code:product stories`):
  INVEST, canonical As-a/I-want/So-that format, Gherkin ACs, definition of
  ready, anti-patterns, 10-item checklist — persisted to
  `.planning/product/stories/US-NN-*.md`. PRD §6 now follows the skill.
- **`verify --strict`**: two independent verifiers in parallel (FUNCTIONAL
  lens vs COMPLIANCE lens); final verdict = the worst of the two. ≈2× cost —
  meant for the phase's final gate, not every fix iteration.
- **Scoped automatic re-review** after `execute --fix` and `simplify` — only
  the fix/refactor commits, never the whole phase again.
- **Modern frontmatter**: `effort: high` (verifier) / `effort: low`
  (researcher); skill `paths` auto-load (frontend-design activates on
  frontend files, user-stories on PRD/stories); positional `$1`/`$2` routing
  in subcommand commands. Progressive enhancement — unsupported fields are
  no-ops on older Claude Code versions.
- **Deliberately rejected** (recorded so it isn't re-litigated): per-agent
  `memory` field (would fork knowledge away from the curated store and break
  the Fresh Context Model) and a SessionStart memory hook (would tax every
  session and go stale mid-session — command STEPs re-read at use time).

## What's New in v2.0.0

**Breaking release** — the framework was rebuilt on the modern Claude Code
plugin system. No slash command was renamed or removed; what changed is how
they work inside.

- **Real subagents (hybrid orchestration).** `execute`, `review`, `verify`,
  `discover` (research) and `product roadmap` now spawn actual subagents via
  the Task tool — the "Fresh Context Model" is literal, and `review` runs
  code-reviewer + qa **genuinely in parallel**.
- **Deterministic audit via hooks.** The SQLite audit trail is now written by
  plugin hooks (`SessionStart`, `SubagentStart/Stop`, `PostToolUse`, `Stop`) —
  no more inline INSERTs that depend on the LLM remembering, and
  `duration_ms` is real.
- **Secret guard hook.** The "never read .env / *.pem / *.key" rule is now
  enforced deterministically by a `PreToolUse` hook, not just prose.
- **Correction loops with a hard stop.** `verify` → fix plans →
  `execute --fix` → re-verify, with a **maximum of 2 fix iterations** before
  escalating to the human. Review gate: critical findings block `verify`.
- **Adversarial verifier.** The verifier tries to REFUTE completion — it
  re-runs evidence itself and distrusts execution summaries.
- **Packaged protocols.** Language, model profiles, spawn contracts, and the
  audit schema live in `references/` inside the plugin (resolved via
  `${CLAUDE_PLUGIN_ROOT}`) — one source of truth, no duplicated blocks.
- **Removed:** `settings.example.json` (legacy manual install flow) and the
  auto-generated `executor-context.md` (obsolete — every spawn is fresh and
  self-contained).

### Installation

```
/plugin marketplace add pwdev-solucoes/pwdev-claude-marketplace
/plugin install pwdev-code
```

Then, inside your project: `/pwdev-code:init`.

---

## Methodology

### The Problem

Without a structured framework, Claude generates ad-hoc code without a plan,
acceptance criteria are subjective, context rot degrades quality in long
sessions, decisions are untraceable, and verification is absent.

### Hybrid Orchestration

The framework separates **what** to do, **who** does it, and **with what** knowledge:

```
┌─────────────────────────────────────────────────────────────┐
│  COMMANDS (commands/) — "WHAT to do"                        │
│  orchestration, gates, flow, persistence; interactive       │
│  phases (interview, design decisions) stay here             │
├─────────────────────────────────────────────────────────────┤
│  SUBAGENTS (agents/) — "WHO does the heavy work"            │
│  8 real subagents spawned with fresh context and a          │
│  self-contained prompt (spawn contract)                     │
├─────────────────────────────────────────────────────────────┤
│  SKILLS (skills/) — "WITH WHAT knowledge"                   │
│  guidelines, patterns, anti-patterns                        │
└─────────────────────────────────────────────────────────────┘
```

**Rule of thumb:** whatever needs to talk to the human (interviews, approval
gates) runs in the main context; whatever is heavy, repetitive, or benefits
from a clean context runs as a subagent.

### 6 Phases

```
DISCOVER  ─▶  DESIGN  ─▶  PLAN  ─▶  EXECUTE  ─▶  REVIEW  ─▶  VERIFY
   │            │           │          │           │           │
Interview    spec.md     Atomic     Executor    Reviewer+QA  Adversarial
+ Researcher + Decisions tasks in   subagent    subagents    verifier
  subagent               waves      per task    in parallel  + fix plans
```

| Phase | Who does the work | Output |
|-------|-------------------|--------|
| **DISCOVER** | Interview (main context) + **researcher** subagent in parallel | project.md, requirements.md, domain/stack/pitfalls |
| **DESIGN** | Architect persona (main context, decisions need approval) | spec.md (8 sections), decisions.md |
| **PLAN** | Planner persona (main context, wave map needs approval) | plans with `Wave:`/`Depends on:` (max 3 tasks each, max 5 files/task) |
| **EXECUTE** | **executor** subagent, fresh context per task | Code + atomic commits + summaries |
| **REVIEW** | **code-reviewer** + **qa** subagents in parallel | code-review.md + qa-report.md |
| **VERIFY** | **verifier** subagent (adversarial, goal-backward) | verify.md + fix plans if rejected |

**Transition rules:** each gate requires human approval. Critical review
findings set `review_gate: BLOCKED` and `verify` refuses to run. VERIFY either
approves or generates fix plans → `execute --fix` → re-verify, at most 2 fix
iterations before escalating.

### Intensity Levels

| Level | When to use | Flow |
|-------|-------------|------|
| **Quick** | Bugfix, config, 1-3 files | `/pwdev-code:quick` — mini-plan → implement → mini-review → mini-verify |
| **Standard** | Medium feature, 2-5 files | DISCOVER → PLAN → EXECUTE → REVIEW → VERIFY |
| **Full** | Complex feature, new project | PRD → ROADMAP → all 6 phases per feature |

**Automatic escalation:** >5 files → Standard. Architectural decision → Standard. Migration/schema → Full.

### spec.md — The Central Contract

Generated in the DESIGN phase, governs all downstream execution. 8 mandatory sections:

| # | Section | Purpose |
|---|---------|---------|
| 1 | **Persona** | Stack, seniority, active skills |
| 2 | **Objective** | What must exist when done (1-3 measurable sentences) |
| 3 | **Inputs** | Entities, endpoints, business rules |
| 4 | **Format** | File structure, naming conventions |
| 5 | **Quality** | Tests, lint, performance + skill-specific criteria |
| 6 | **Stop Conditions** | When the executor MUST stop and ask (min 5) |
| 7 | **Prohibitions** | What to NEVER do (specific + global) |
| 8 | **Definition of Done** | Verifiable checklist with real commands |

### Context Management (harness engineering)

The framework fights **context rot**: each task runs in a real subagent with
fresh context, receiving ONLY: the task + spec excerpts (§1, 6, 7) + active
skills + explicitly listed files. Zero history.

The **spawn contract** (`references/spawn-contracts.md`) formalizes this:
subagents write full reports to `.planning/` files and reply to the
orchestrator with ≤10 status lines — artifacts are the contract, `state.md`
is the source of truth, and the orchestrator never pastes reports back into
its own context.

### Verification — Adversarial Goal-Backward

The verifier doesn't ask "what did we do?" — it asks **"what must be TRUE,
and can I prove it is NOT?"** It re-runs summary evidence itself and attempts
one refutation per truth.

| Verdict | Criterion |
|---------|----------|
| **APPROVED** | 100% ACs + 100% DoD + 0 prohibitions violated |
| **WITH CAVEATS** | >=90% ACs + low severity failures only |
| **REJECTED** | <90% ACs OR critical prohibition OR critical DoD failing |

---

## Subagents

Real subagents (spawned via the Task tool, fresh context, restricted tools):

| Subagent | Model (balanced) | Tools | What it does |
|----------|:---------------:|-------|-------------|
| **executor** | sonnet | Read, Write, Edit, Grep, Glob, Bash | Implements ONE atomic task: code, verification, atomic commit, summary |
| **advisor** | opus | read-only + Write (no Edit) | Resolves ONE hard decision raised by a blocked executor (NEEDS_ADVICE) — picks a direction, never implements |
| **code-reviewer** | sonnet | read-only + Write (no Edit) | Reviews diff across 6 dimensions (correctness, security, perf, arch, conventions, tests) |
| **qa** | sonnet | read-only + Write (no Edit) | Runs the real test suite, traces requirement→test, proposes skeletons |
| **verifier** | sonnet | read-only + Write (no Edit) | Adversarial verification; generates fix plans when it rejects |
| **researcher** | haiku | read + Write + web | Investigates stack/domain/pitfalls in parallel with the interview |
| **roadmap** | sonnet | Read, Write, Grep, Glob, Bash | Decomposes the PRD into the multi-file roadmap with traceability |
| **simplifier** | sonnet | Read, Grep, Glob, Bash, Edit, Write | Two-pass quality refactor: proposes >=80%-confidence simplifications, applies only human-approved ones |

Interactive personas absorbed into commands (main context): interviewer
(`discover`), architect (`design`), planner (`plan`), product manager
(`product prd`), quick engineer (`quick`).

---

## Commands

### Setup & Configuration

| Command | What it does |
|---------|-------------|
| `/pwdev-code:init` | Initialize framework in repo — creates `.planning/`, CLAUDE.md, settings, configures language, model profile, and audit |
| `/pwdev-code:init mcp` | Configure MCP servers (.mcp.json) |
| `/pwdev-code:init stack` | Detect and configure project stack |
| `/pwdev-code:init claude` | Generate CLAUDE.md operational memory file |

### Product Planning

| Command | What it does | Output |
|---------|-------------|--------|
| `/pwdev-code:product prd` | Product discovery interview → structured PRD | prd.md (10 sections) |
| `/pwdev-code:product roadmap` | Decompose PRD via the roadmap subagent | .planning/product/roadmap/ (multi-file with traceability) |
| `/pwdev-code:product stories` | Generate/refine user stories (skill-user-stories quality bar) | .planning/product/stories/US-NN-*.md + index |

### Development Workflow

| Command | Phase | Entry Gate | Output |
|---------|-------|-----------|--------|
| `/pwdev-code:discover` | DISCOVER | `.planning/` exists | project.md, requirements.md |
| `/pwdev-code:design` | DESIGN | project.md + requirements.md | spec.md, decisions.md |
| `/pwdev-code:plan` | PLAN | Approved spec.md | plans with waves |
| `/pwdev-code:execute` | EXECUTE | Approved plans | Code + commits + summaries |
| `/pwdev-code:execute --fix` | EXECUTE | Fix plans from verify | Corrections (max 2 iterations) |
| `/pwdev-code:simplify` | EXECUTE→REVIEW (optional) | Summaries or explicit scope | Approved simplifications + refactor commit |
| `/pwdev-code:review` | REVIEW | Code changes exist | code-review.md + qa-report.md (parallel) |
| `/pwdev-code:verify` | VERIFY | Summaries exist, review gate OK | verify.md, fix plans |
| `/pwdev-code:verify --strict` | VERIFY | Final gate / pre-release | 2 parallel verifiers (FUNCTIONAL + COMPLIANCE), worst verdict wins (≈2× cost) |
| `/pwdev-code:quick` | All-in-one | Task description | Code + commit (simple tasks) |

`review` also accepts `--code-only`, `--tests-only`, `--diff HEAD~N`.

### Session, Diagnostics & Maintenance

| Command | When to use |
|---------|------------|
| `/pwdev-code:memory` | Curate durable project memory — `capture`, `list`, `show`, `forget`, `link`, `graph` |
| `/pwdev-code:session` / `session resume` | Check progress / resume from state.md |
| `/pwdev-code:init map` | First contact with an existing repo |
| `/pwdev-code:health` / `health --deps` | Project health scorecard / dependency audit |
| `/pwdev-code:audit` | Query the audit trail (summary, events, decisions, stats, export PDF, SQL) |
| `/pwdev-code:manager-skills` | Create, list, or audit skills |
| `/pwdev-code:maintenance cleanup` / `changelog` | Archive artifacts / generate changelog |

---

## Language & Model Configuration

### Language

All commands support **Portuguese (PT-BR)** and **English (EN)**. Configured
during `/pwdev-code:init`, stored in `.planning/config.json`, protocol at
`references/language.md`.

### Model Profile

Only subagents resolve models (interactive phases use the session model).
Single source of truth: `references/model-profiles.md`.

| Subagent | performance | balanced (default) | economy |
|----------|:-----------:|:------------------:|:-------:|
| executor / roadmap | opus | sonnet | sonnet |
| advisor | opus | opus | sonnet |
| code-reviewer / qa / verifier | sonnet | sonnet | haiku |
| researcher | sonnet | haiku | haiku |

The executor additionally routes **per task**: plans declare
`Complexity: low|medium|high`, and e.g. `balanced` sends `high` tasks to opus
while `low`/`medium` stay on sonnet (matrix in `references/model-profiles.md`;
the executor never runs on haiku).

Override specific subagents with `model_overrides` in `.planning/config.json`:

```json
{
  "lang": "pt-BR",
  "model_profile": "balanced",
  "model_overrides": { "executor": "opus" },
  "parallel_execution": false,
  "external_models": { "reviewer": { "cmd": "codex exec", "enabled": false, "timeout_s": 300 } }
}
```

`parallel_execution` (default false) enables opt-in parallel wave batches
with worktree isolation. `external_models.reviewer` (optional, manual) lets
`/pwdev-code:review` collect an advisory second opinion from an external CLI
— the command is shown to you before its first run, and external findings
never block the review gate on their own.

---

## Audit Trail (deterministic, via hooks)

Optional SQLite database at `.planning/pwdev-audit.db` — **disabled by
default**, configured during `/init`, never versioned.

Recording is done by the plugin's hooks, not by agents:

- `scripts/audit-hook.sh` (SessionStart, SubagentStart/Stop, PostToolUse,
  Stop) → events with real `duration_ms`, artifact tracking
- `scripts/audit-log.sh` called by commands at phase gates → decisions,
  gate_passed / gate_rejected
- `scripts/guard-secrets.sh` (PreToolUse) → blocks reads of `.env`, `*.pem`,
  `*.key`, `id_rsa*` (`.env.example` allowed)

Query with `/pwdev-code:audit`: `summary`, `events`, `decisions`,
`artifacts`, `stats`, `export` (PDF), `query <SELECT>`.

---

## Skills

Skills are domain knowledge packs that the executor and reviewers consult.
They transform generic output into domain-quality results.

Without skill: `"Create users table"` → functional table that renders data.
With a UI skill: → table with empty state, loading skeleton, sticky header,
hover highlight, mobile card view, keyboard nav, AA contrast.

### Included Skills

| Skill | Domain | Files |
|-------|--------|-------|
| skill-frontend-design | Enterprise UI design — dashboards, admin panels, SaaS, data-heavy apps | SKILL.md + TEMPLATES.md |
| skill-user-stories | User stories — INVEST, Gherkin ACs, definition of ready, review checklist | SKILL.md |

Create your own with `/pwdev-code:manager-skills create <domain>` — the wizard
detects your stack, interviews you (max 3 rounds), and generates a skill in
`.claude/skills/` following the official SKILL.md schema.

---

## Artifacts & Directory Structure

```
.planning/
├── config.json                       # lang, model_profile, audit, parallel_execution, external_models, version
├── state.md                          # Source of truth: position, gates, fix_iteration
├── pwdev-audit.db                    # Audit trail (opt-in, gitignored)
│
├── context/                          # Project-level knowledge (permanent)
│   ├── project.md, requirements.md   # discover
│   ├── domain.md, stack.md, pitfalls.md        # researcher subagent
│   └── architecture.md, conventions.md, ...    # init map
│
├── memory/                           # curated durable knowledge (VERSIONED)
│   ├── MEMORY.md                     # index — 1 line per active memory
│   └── {decision|lesson|convention}-*.md
│
├── product/
│   ├── prd.md
│   ├── stories/                      # user stories (US-NN-*.md + index.md)
│   └── roadmap/                      # roadmap subagent (multi-file)
│
├── phases/F01-slug/
│   ├── spec.md, decisions.md         # design
│   ├── plans/                        # plan (Wave/Depends headers)
│   ├── execution/                    # executor summaries
│   ├── review/                       # code-review.md, qa-report.md
│   └── verify/                       # verify.md, fix-NN.md
│
├── quick/, reports/, templates/, archive/
```

---

## Golden Rules

```
 1. NEVER execute without an approved plan.
 2. NEVER declare "done" without verification against AC.
 3. ALWAYS respect stop conditions — stop and ask.
 4. SPEC.md is the contract — every executor MUST read it.
 5. One task, one commit, one scope.
 6. Fresh subagent > long session with context rot.
 7. Goal-backward: "what must be TRUE?" > "what did we do?"
 8. Security is not optional — and it is enforced by hooks.
 9. Escalate when needed — Quick → Standard → Full.
10. The human has the final word. Always.
```

---

## License

Apache-2.0 — See [LICENSE](./LICENSE)

*PWDEV-CODE v2.2.0 — Complexity lives in the system, not in your workflow.*
*Maintained by [Paulo Soares](https://github.com/soarescbm)*
