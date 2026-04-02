# PWDEV Marketplace

*Read this in [Português Brasileiro](./README.pt-BR.md)*

Plugin marketplace for [Claude Code](https://docs.anthropic.com/en/docs/claude-code).

---

## What is PWDEV

[Paulo Soares](https://github.com/soarescbm), CTO of PWDEV, a company focused on developing GovTech solutions, believes that artificial intelligence is fundamentally reshaping software development. More than a passing trend, this shift represents a new way to support professionals, extend capabilities, and bring greater consistency across the entire development lifecycle. Guided by this vision, PWDEV is making these solutions available to help teams work with more structure, quality, and predictability.

Our plugins turn Claude Code from a general-purpose coding assistant into a disciplined engineering partner through specialized agents, structured workflows, and domain-specific knowledge packs.

Core philosophy across all plugins:

> **Never execute without a plan. Never ship without verification.**

---

## What's New in v1.1.0

- **Language Selection** — All commands now support Portuguese (PT-BR) and English (EN). Configured once during `/init`, used silently across all commands.
- **Model Profiles** — Choose between `performance`, `balanced`, or `economy` profiles to control which Claude model (Opus/Sonnet/Haiku) each agent uses.
- **Audit Trail (opt-in)** — Optional SQLite database at `.planning/pwdev-audit.db` records all commands, decisions, and artifacts. Disabled by default, never versioned.
- **Unified Configuration** — Language, model profile, and audit settings stored in `.planning/config.json`, shared across all plugins.

---

## Plugins

| Plugin | Description | Version | License |
|--------|-------------|:-------:|:-------:|
| [**pwdev-code**](./plugins/pwdev-code/) | Spec-driven development framework — 11 agents, 6 phases, 21 commands | 1.1.0 | Apache-2.0 |
| [**pwdev-uiux**](./plugins/pwdev-uiux/) | UI/UX engineering framework — 7 agents, 5-phase workflow, Figma integration, WCAG 2.1 AA | 1.1.0 | Apache-2.0 |
| [**pwdev-feat**](./plugins/pwdev-feat/) | Simplified feature development — PWDEVIA 7-question plans + executor, fast and practical | 1.1.0 | Apache-2.0 |
| [**pwdev-prd**](./plugins/pwdev-prd/) | Interview-driven PRD creation — 12-step structured interview, Markdown + JSON, technology-agnostic | 1.1.0 | Apache-2.0 |

### pwdev-code

Framework that orchestrates **11 specialized agents** across **6 phases** to ensure every line of code is planned, traceable, and verified.

```
PRD ─▶ ROADMAP ─▶ DISCOVER ─▶ DESIGN ─▶ PLAN ─▶ EXECUTE ─▶ REVIEW ─▶ VERIFY
```

**Agents:** Product Manager, Delivery Lead, Requirements Engineer, Technical Analyst, Software Architect, Planning Engineer, Implementation Engineer, Code Reviewer, QA Engineer, Spec Verifier, Generalist Engineer

See the [full plugin documentation](./plugins/pwdev-code/README.md).

### pwdev-uiux

UI/UX engineering framework for **Vue 3 + shadcn-vue (Reka UI v2)** that orchestrates **7 specialized agents** across a 5-phase workflow.

```
UNDERSTAND ─▶ STRUCTURE ─▶ IMPLEMENT ─▶ REVIEW ─▶ HANDOFF
```

**Agents:** Orchestrator, UX Analyst, Design Bridge, UI Scanner, UI Builder, A11y Reviewer, UX Critic

**Key features:** Figma MCP integration, WCAG 2.1 AA auditing, 7-axis UX review, project-specific contextual skills

See the [full plugin documentation](./plugins/pwdev-uiux/README.md).

### pwdev-feat

Simplified AI-assisted feature development using the **PWDEVIA 7-question methodology**. Describe what you want, get a structured plan, execute it.

```
Describe ─▶ Plan ─▶ Execute
```

**Agents:** PWDEVIA (Prompt Engineer) + Executor

**Plan types:** Feature, Backend, Frontend, Test, Review, Quick

See the [full plugin documentation](./plugins/pwdev-feat/README.md).

### pwdev-prd

Interview-driven **PRD creation** with a 12-step structured process. Technology-agnostic, outputs Markdown + optional JSON.

```
Interview (12 steps) ─▶ PRD.md ─▶ Export (JSON / GitHub Issue)
```

**Agent:** PRD Interview Specialist

**Outputs:** Structured PRD with objectives, metrics, functional/non-functional requirements, architecture, risks, acceptance criteria

See the [full plugin documentation](./plugins/pwdev-prd/README.md).

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
# Spec-driven development (11 agents, 6 phases)
claude plugin install pwdev-code@pwdev-claude-marketplace

# UI/UX engineering (8 agents, Figma, WCAG, theming)
claude plugin install pwdev-uiux@pwdev-claude-marketplace

# Simplified feature development (7-question plans)
claude plugin install pwdev-feat@pwdev-claude-marketplace

# Interview-driven PRD creation (12-step process)
claude plugin install pwdev-prd@pwdev-claude-marketplace
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

Each plugin uses specialized agents that can run on different Claude models. Model profiles let you balance quality vs. cost:

| Profile | Orchestrator | Planner / Executor | Reviewer | Scanner |
|---------|:----------:|:-----------------:|:--------:|:-------:|
| **performance** | Opus | Opus | Sonnet | Sonnet |
| **balanced** | Opus | Sonnet | Sonnet | Haiku |
| **economy** | Sonnet | Sonnet | Haiku | Haiku |

- During `/init`: you choose a profile (default: balanced)
- Override specific agents: `model_overrides` in config.json

```json
{
  "lang": "pt-BR",
  "model_profile": "balanced",
  "model_overrides": {
    "agent-architect": "opus"
  }
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
