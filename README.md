# PWDEV Marketplace

Official plugin marketplace for [Claude Code](https://docs.anthropic.com/en/docs/claude-code).

---

## What is PWDEV

[Paulo Soares](https://github.com/soarescbm), CTO of PWDEV, a company focused on developing GovTech solutions, believes that artificial intelligence is fundamentally reshaping software development. More than a passing trend, this shift represents a new way to support professionals, extend capabilities, and bring greater consistency across the entire development lifecycle. Guided by this vision, PWDEV is making these solutions available to help teams work with more structure, quality, and predictability.

Our plugins turn Claude Code from a general-purpose coding assistant into a disciplined engineering partner through specialized agents, structured workflows, and domain-specific knowledge packs.

Core philosophy across all plugins:

> **Never execute without a plan. Never ship without verification.**

---

## Plugins

| Plugin | Description | Version | License |
|--------|-------------|:-------:|:-------:|
| [**pwdev-code**](./plugins/pwdev-code/) | Spec-driven development framework — 11 agents, 6 phases, 21 commands | 1.0.0 | Apache-2.0 |
| [**pwdev-uiex**](./plugins/pwdev-uiex/) | UI/UX engineering framework — 7 agents, 5-phase workflow, Figma integration, WCAG 2.1 AA | 1.0.0 | Apache-2.0 |
| [**pwdev-feat**](./plugins/pwdev-feat/) | Simplified feature development — PWDEVIA 7-question plans + executor, fast and practical | 1.0.0 | Apache-2.0 |
| [**pwdev-prd**](./plugins/pwdev-prd/) | Interview-driven PRD creation — 12-step structured interview, Markdown + JSON, technology-agnostic | 1.0.0 | Apache-2.0 |

### pwdev-code

Framework that orchestrates **11 specialized agents** across **6 phases** to ensure every line of code is planned, traceable, and verified.

```
PRD ─▶ ROADMAP ─▶ DISCOVER ─▶ DESIGN ─▶ PLAN ─▶ EXECUTE ─▶ REVIEW ─▶ VERIFY
```

**Agents:** Product Manager, Delivery Lead, Requirements Engineer, Technical Analyst, Software Architect, Planning Engineer, Implementation Engineer, Code Reviewer, QA Engineer, Spec Verifier, Generalist Engineer

See the [full plugin documentation](./plugins/pwdev-code/README.md).

### pwdev-uiex

UI/UX engineering framework for **Vue 3 + shadcn-vue (Reka UI v2)** that orchestrates **7 specialized agents** across a 5-phase workflow.

```
UNDERSTAND ─▶ STRUCTURE ─▶ IMPLEMENT ─▶ REVIEW ─▶ HANDOFF
```

**Agents:** Orchestrator, UX Analyst, Design Bridge, UI Scanner, UI Builder, A11y Reviewer, UX Critic

**Key features:** Figma MCP integration, WCAG 2.1 AA auditing, 7-axis UX review, project-specific contextual skills

See the [full plugin documentation](./plugins/pwdev-uiex/README.md).

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

### Global (recommended)

```bash
git clone https://github.com/pwdev-solucoes/pwdev-claude-marketplace.git

claude plugins add ./pwdev-claude-marketplace/plugins/pwdev-code
```

### Per project

Add to `.claude/settings.json` in your project:

```json
{
  "plugins": [
    { "path": "/path/to/pwdev-claude-marketplace/plugins/pwdev-code" }
  ]
}
```

Via Git:

```json
{
  "plugins": [
    {
      "git": "https://github.com/pwdev-solucoes/pwdev-claude-marketplace.git",
      "subpath": "plugins/pwdev-code",
      "branch": "main"
    }
  ]
}
```

### First run

```bash
/pwdev-code:init          # Creates .planning/ structure and CLAUDE.md
/pwdev-code:setup-mcp     # (Optional) Configure MCP servers for your stack
/pwdev-code:health        # Verify everything is working
```

---

## License

Apache-2.0

*Maintained by [Paulo Soares](https://github.com/pwdev-solucoes)*
