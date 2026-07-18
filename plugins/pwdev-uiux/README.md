# PWDEV-UIUX v2.0.0

> **Stack-Agnostic UI/UX Engineering Framework for Claude Code**

*Read this in [Português Brasileiro](./README.pt-BR.md)*

```
Configure your stack → Analyze → Implement → Review → Ship
```

PWDEV-UIUX orchestrates **6 real subagents + 2 inline personas** across a **5-phase workflow** to produce UI components that are spec-driven, accessible (WCAG 2.1 AA), and consistent with your project. Works with any modern frontend stack.

---

## Getting Started

### Step 1 — Install

```bash
claude plugin install pwdev-uiux@pwdev-claude-marketplace
```

### Step 2 — Initialize

```
/pwdev-uiux:init
```

This command handles everything in one go:
- Creates the `.planning/ui/` workspace
- Asks for language (PT-BR / EN), model profile, and audit
- Detects your frontend framework
- Prompts you to choose your UI stack (shadcn-vue, shadcn-react, primevue, untitled-ui, tailwind-plus, or custom)
- Checks Figma MCP connection

### Step 3 — Start building

Choose your path based on the project context:

**Brownfield** (existing project with UI components):
```
/pwdev-uiux:scan                              # analyze existing patterns + compliance check
/pwdev-uiux:start "description of your task"  # start 5-phase flow
```

**Greenfield** (new project, no existing UI):
```
/pwdev-uiux:theme create                      # generate semantic color theme
/pwdev-uiux:start "description of your task"  # start 5-phase flow
```

**With Figma designs available**:
```
/pwdev-uiux:setup-figma                       # connect Figma MCP (one-time)
/pwdev-uiux:theme from-figma                  # extract theme from Figma variables
/pwdev-uiux:start "description of your task"  # Figma specs extracted in Phase 2
```

That's it. The orchestrator guides you through the 5 phases automatically.

### Optional setup commands

| Command | When to use |
|---------|------------|
| `/pwdev-uiux:stack` | Change the UI stack after init |
| `/pwdev-uiux:setup-figma` | Connect Figma integration |
| `/pwdev-uiux:scan` | Re-scan after significant project changes |
| `/pwdev-uiux:theme create` | Generate a new theme before building |

---

## What's New in v2.0.0

Rebuilt on the modern Claude Code plugin system. No slash command renamed or
removed.

- **Hybrid orchestration**: the orchestrator and theme-builder are now
  INLINE personas (`references/workflow.md`, `references/theme-method.md`) —
  they interact with the human at gates and interviews, which subagents
  cannot do. The other 6 agents became **real subagents** spawned via the
  Task tool with official frontmatter (description dispatch, restricted
  tools, `maxTurns`) and real parallelism (a11y-reviewer + ux-critic in one
  message; design-bridge + ux-analyst with Figma).
- **Prohibited agent fields removed**: `permissionMode`, `mcpServers`, and
  the non-official `skills:` are gone. Skills are passed as explicit
  SKILL.md paths in every spawn prompt (the old "loaded automatically via
  frontmatter" premise was false). Figma MCP tools live at the SESSION
  level (`/pwdev-uiux:setup-figma`); `push-to-figma` runs inline where those
  tools exist.
- **Deterministic audit via hooks** on the shared `.planning/pwdev-audit.db`
  (`WHERE plugin='pwdev-uiux'`): real `duration_ms`/`session_id`,
  `config_changes` populated by init, secret-guard PreToolUse hook.
- **Packaged references**: workflow, theme-method, spawn-contracts,
  model-profiles (single source — the 3 divergent copies with phantom roles
  are gone), language, audit-schema.
- **Namespaced model overrides**: `uiux-<agent>` keys in the shared config
  (never plain agent names).
- **Fixes**: hardened audit query guard (single-statement SELECT only);
  `echo -e` → `printf`; dead `$SUB_COMMAND`; stale "v1.0.0" strings in
  start/handoff; hardcoded "shadcn-vue"/"Vue 3 + Reka" in stack-agnostic
  prompts now read stack.json.

## What's New in v1.1.2

- **Language Selection** — All commands support PT-BR and EN. Configured during `/pwdev-uiux:init`.
- **Model Profiles** — Agent models configurable via `performance`, `balanced`, or `economy` profiles. Orchestrator defaults to Opus in balanced mode.
- **Audit Trail (opt-in)** — Optional SQLite logging of commands, decisions, and artifacts. Disabled by default.

---

## Usage Examples

### Build a new feature end-to-end

```
/pwdev-uiux:start "User profile page with avatar, settings form, and activity feed"
```

The orchestrator guides you through all 5 phases automatically.

### Build a single component from an existing spec

```
/pwdev-uiux:build UserCard
```

Implements a specific component when the UX spec is already approved. Useful for adding components one-by-one after Phase 1.

### Review existing components

```
/pwdev-uiux:review
```

Runs accessibility (WCAG 2.1 AA) + UX (7-axis + best practices) review in parallel. Generates a compliance report with pass/fail counts by priority (P0/P1/P2).

### Extract theme from Figma

```
/pwdev-uiux:theme from-figma
```

Reads Figma variables and generates CSS + Tailwind config automatically.

### Push components to Figma

```
/pwdev-uiux:push-to-figma UserCard
/pwdev-uiux:push-to-figma screen
/pwdev-uiux:push-to-figma tokens
```

Creates Figma representations from your implemented code.

---

## Supported Stacks

| Stack | Framework | Component Library | Default |
|-------|-----------|------------------|:-------:|
| `shadcn-vue` | Vue 3 | shadcn-vue (Reka UI v2) | yes |
| `shadcn-react` | React | shadcn/ui (Radix UI) | |
| `primevue` | Vue 3 | PrimeVue (styled mode) | |
| `untitled-ui` | React | Untitled UI (Radix UI) | |
| `tailwind-plus` | Vue / React | Tailwind Plus (Headless UI) | |
| `custom` | Any | Any / None | |

Stacks are configured via `/pwdev-uiux:stack` and stored in `.planning/ui/stack.json`. The `ui-builder` agent reads this config before implementing any component.

---

## Methodology

### 5-Phase Workflow

```
/pwdev-uiux:scan (existing project)
     |
     v generates project-ui-skill.md + compliance report
     |
/pwdev-uiux:start "description"
     |
     v
[PHASE 1] UNDERSTAND     -> ux-spec.md
     | gate: spec approved
     v
[PHASE 2] STRUCTURE       -> figma-spec.md
     | gate: figma-spec filled
     v
[PHASE 3] IMPLEMENT       -> Components + component-log.md
     | gate: components implemented
     v
[PHASE 4] REVIEW          -> review-findings.md + compliance report
     | gate: zero critical failures + all P0 rules passed
     v
[PHASE 5] HANDOFF         -> docs/handoff/[feature].md
```

| Phase | What happens | Gate |
|-------|-------------|------|
| **UNDERSTAND** | UX analyst creates structured spec | Spec approved by human |
| **STRUCTURE** | Design bridge translates Figma into implementation spec | Figma spec filled |
| **IMPLEMENT** | UI builder creates components following stack config + spec + best practices | All components logged |
| **REVIEW** | A11y reviewer + UX critic run in parallel with compliance report | Zero critical failures + all P0 passed |
| **HANDOFF** | Generate delivery documentation | Doc in `docs/handoff/` |

### Best Practices Compliance

The framework enforces **60+ UI/UX rules** organized by priority:

| Priority | Meaning | Enforcement |
|----------|---------|-------------|
| **P0 — Mandatory** | Violations are bugs | Always enforced. Blocks review gate. |
| **P1 — Strong default** | Apply unless justified | Enforced by default. Skip requires documentation. |
| **P2 — Recommended** | Apply when context allows | Tracked in compliance report. |
| **P3 — Contextual** | Case by case | Not enforced, informational. |

Rules cover: visual foundation, typography, layout & spacing, button hierarchy, navigation, tabs, data interactions, destructive actions, access & onboarding, forms, reports, errors & validation, performance, and motion & focus.

### 7-Axis UX Review + Rule Compliance

The UX critic reviews every component against two complementary lenses:

1. **7 Qualitative Axes**: Experience, Gestalt, Trust, Decision, Cognition, Attention, Accessibility
2. **Rule-Based Compliance**: 60+ concrete rules with P0–P3 priority from the best practices ruleset

### Project Context

The **ui-scanner** analyzes your existing project before development and generates a project-specific contextual skill that the `ui-builder` uses for consistency. It also runs a compliance check to identify existing violations.

---

## Agents

**Inline personas** (main context — they talk to the human):

| Persona | Where | What it does |
|---------|-------|-------------|
| **orchestrator** | `references/workflow.md` via /start | Coordinates the 5 phases and gates, spawns subagents. Never writes code. |
| **theme-builder** | `references/theme-method.md` via /theme | Semantic color themes (CSS vars + Tailwind), light/dark, WCAG AA contrast — interviews you about brand |

**Real subagents** (Task tool, fresh context):

| Subagent | Model (balanced) | What it does |
|----------|:----------------:|-------------|
| **ux-analyst** | Sonnet | Requirements into structured UX specs |
| **design-bridge** | Sonnet | Bidirectional Figma bridge (read + write; session-level Figma MCP) |
| **ui-scanner** | Sonnet | Analyzes existing UI, generates contextual skill + compliance report |
| **ui-builder** | Sonnet | Reads stack.json, reads the listed skills, implements components |
| **a11y-reviewer** | Haiku | WCAG 2.1 AA + best practices P0 accessibility audit |
| **ux-critic** | Sonnet | 7-axis UX review + best practices compliance (P0–P3) |

*Models per profile in `references/model-profiles.md`; override with
namespaced keys (`"uiux-ui-builder"`) in the shared config.*

---

## Commands

### Setup

| Command | What it does |
|---------|-------------|
| `/pwdev-uiux:init` | Initialize framework, detect stack, create `.planning/ui/`, configure language and model profile |
| `/pwdev-uiux:stack` | Configure UI stack (shadcn-vue, shadcn-react, primevue, untitled-ui, tailwind-plus, custom) |
| `/pwdev-uiux:setup-figma` | Connect Figma MCP |
| `/pwdev-uiux:scan` | Scan existing project UI + best practices compliance check |

### Theming

| Command | What it does |
|---------|-------------|
| `/pwdev-uiux:theme` | Create semantic theme (CSS vars + Tailwind, light/dark, contrast validated) |
| `/pwdev-uiux:theme update` | Modify existing theme tokens |
| `/pwdev-uiux:theme from-figma` | Extract theme from Figma variables |
| `/pwdev-uiux:theme validate` | Run WCAG AA contrast validation on current theme |

### Development

| Command | What it does |
|---------|-------------|
| `/pwdev-uiux:start "task"` | Start new UI flow from Phase 1 |
| `/pwdev-uiux:analyze "desc"` | Quick UX exploration |
| `/pwdev-uiux:build [component]` | Implement component from spec |

### Review & Delivery

| Command | What it does |
|---------|-------------|
| `/pwdev-uiux:review` | A11y + UX + best practices compliance review in parallel |
| `/pwdev-uiux:handoff` | Generate delivery docs |
| `/pwdev-uiux:status` | View current flow state |

### Figma Push

| Command | What it does |
|---------|-------------|
| `/pwdev-uiux:push-to-figma [path]` | Push component to Figma |
| `/pwdev-uiux:push-to-figma screen` | Push screen layout |
| `/pwdev-uiux:push-to-figma library` | Build component library |
| `/pwdev-uiux:push-to-figma tokens` | Sync design tokens |

### Audit

| Command | What it does |
|---------|-------------|
| `/pwdev-uiux:audit` | Query the audit trail — summary, events, decisions, artifacts, stats, export PDF |

---

## Language & Model Configuration

### Language

All commands support **Portuguese (PT-BR)** and **English (EN)**. Configured during `/pwdev-uiux:init` and stored in `.planning/config.json`.

- `/pwdev-uiux:init` — always asks for language preference
- Other commands — use saved preference silently
- Override — switch language mid-conversation and confirm when prompted

### Model Profile

Only the 6 **subagents** resolve models (the orchestrator and theme personas
run inline on the session model). Single source of truth:
`references/model-profiles.md`.

| Profile | ui-builder | ux-analyst / design-bridge | ux-critic / ui-scanner | a11y-reviewer |
|---------|:----------:|:--------------------------:|:----------------------:|:-------------:|
| **performance** | Opus | Sonnet | Sonnet | Sonnet |
| **balanced** (default) | Sonnet | Sonnet | Sonnet | Haiku |
| **economy** | Sonnet | Sonnet | Haiku | Haiku |

Override with **namespaced keys** in the shared `.planning/config.json`:

```json
{
  "lang": "pt-BR",
  "model_profile": "balanced",
  "model_overrides": {
    "uiux-ui-builder": "opus"
  }
}
```

---

## Audit Trail

All plugins share an optional SQLite audit database at `.planning/pwdev-audit.db`. It is **disabled by default** and configured during `/init`. The database file is never versioned (automatically added to `.gitignore`).

**How data gets here (v2.0 — deterministic, via hooks):**
- `scripts/audit-hook.sh` (SessionStart, SubagentStart/Stop, PostToolUse,
  Stop) → session events, subagent runs with real `session_id` and
  `duration_ms`, `.planning/` artifact writes
- `scripts/audit-log.sh` → command milestones (`event`) and configuration
  changes (`config` → `config_changes`, populated by `/init`)
- `scripts/guard-secrets.sh` (PreToolUse) → blocks reads of `.env`, `*.pem`,
  `*.key`, `id_rsa*` (`.env.example` allowed)

The database is **shared with the other PWDEV plugins** — filter this
plugin's rows with `WHERE plugin='pwdev-uiux'`.

### Querying the Audit Trail

Use `/pwdev-uiux:audit` to query the database interactively:

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
/pwdev-uiux:audit              # summary dashboard
/pwdev-uiux:audit stats        # detailed statistics
/pwdev-uiux:audit export       # generate PDF report at .planning/audit-report.pdf
/pwdev-uiux:audit query "SELECT * FROM events WHERE action='failed'"
```

Add `.planning/pwdev-audit.db` to `.gitignore` (recommended).

---

## Stack Configuration

Stored in `.planning/ui/stack.json`:

```json
{
  "name": "shadcn-vue",
  "framework": "vue3",
  "component_library": "shadcn-vue",
  "styling": "tailwindcss",
  "forms": "vee-validate + zod",
  "icons": "lucide-vue-next",
  "skills": ["shadcn-vue", "reka-ui", "ux-tokens", "accessibility"]
}
```

---

## Skills

| Skill | Domain |
|-------|--------|
| **ui-best-practices** | Canonical UI/UX ruleset (14 sections, 60+ rules, P0–P3 priority) |
| **ui-theme-reference** | Canonical design token registry (colors, typography, spacing, shadows, z-index, motion) |
| shadcn-vue | shadcn-vue CLI, components, vee-validate |
| reka-ui | Headless primitives, asChild, controlled state |
| figma | Bidirectional Figma integration |
| ux-tokens | CSS tokens, Tailwind config |
| accessibility | WCAG 2.1 AA |
| component-audit | Audit existing components |
| design-system | Design system documentation |
| ui-scanner | UI analysis protocol |

---

## License

Apache-2.0 — See [LICENSE](./LICENSE)

*PWDEV-UIUX v2.0.0 — Quality as a gate, not an aspiration.*
*Maintained by [Paulo Soares](https://github.com/soarescbm)*
