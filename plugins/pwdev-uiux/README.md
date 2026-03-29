# PWDEV-UIEX v1.0.0

> **Stack-Agnostic UI/UX Engineering Framework for Claude Code**

```
Configure your stack → Analyze → Implement → Review → Ship
```

PWDEV-UIEX orchestrates **7 specialized agents** across a **5-phase workflow** to produce UI components that are spec-driven, accessible (WCAG 2.1 AA), and consistent with your project. Works with any modern frontend stack.

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
     v generates project-ui-skill.md
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
[PHASE 4] REVIEW          -> review-findings.md
     | gate: zero critical failures
     v
[PHASE 5] HANDOFF         -> docs/handoff/[feature].md
```

| Phase | What happens | Gate |
|-------|-------------|------|
| **UNDERSTAND** | UX analyst creates structured spec | Spec approved by human |
| **STRUCTURE** | Design bridge translates Figma into implementation spec | Figma spec filled |
| **IMPLEMENT** | UI builder creates components following stack config + spec | All components logged |
| **REVIEW** | A11y reviewer + UX critic run in parallel | Zero critical failures |
| **HANDOFF** | Generate delivery documentation | Doc in `docs/handoff/` |

### Project Context

The **ui-scanner** analyzes your existing project before development and generates a project-specific contextual skill that the `ui-builder` uses for consistency.

### 7-Axis UX Review

The UX critic reviews every component against: **Experience**, **Gestalt**, **Trust**, **Decision**, **Cognition**, **Attention**, **Accessibility**.

---

## Agents

| Agent | Model | What it does |
|-------|-------|-------------|
| **orchestrator** | Opus | Coordinates phases, reads stack.json. Never writes code. |
| **ux-analyst** | Sonnet | Requirements into structured UX specs |
| **design-bridge** | Sonnet | Bidirectional Figma bridge (read + write) |
| **ui-scanner** | Sonnet | Analyzes existing UI, generates contextual skill |
| **ui-builder** | Sonnet | Reads stack.json, loads skills, implements components |
| **theme-builder** | Sonnet | Creates semantic color themes (CSS vars + Tailwind), light/dark, WCAG AA contrast |
| **a11y-reviewer** | Haiku | WCAG 2.1 AA compliance audit |
| **ux-critic** | Sonnet | 7-axis UX review with principle-based findings |

---

## Commands

### Setup

| Command | What it does |
|---------|-------------|
| `/pwdev-uiux:init` | Initialize framework, detect stack, create `.planning/ui/` |
| `/pwdev-uiux:stack` | Configure UI stack (shadcn-vue, shadcn-react, primevue, untitled-ui, custom) |
| `/pwdev-uiux:setup-figma` | Connect Figma MCP |
| `/pwdev-uiux:scan` | Scan existing project UI |

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
| `/pwdev-uiux:review` | A11y + UX review in parallel |
| `/pwdev-uiux:handoff` | Generate delivery docs |
| `/pwdev-uiux:status` | View current flow state |

### Figma Push

| Command | What it does |
|---------|-------------|
| `/pwdev-uiux:push-to-figma [path]` | Push component to Figma |
| `/pwdev-uiux:push-to-figma screen` | Push screen layout |
| `/pwdev-uiux:push-to-figma library` | Build component library |
| `/pwdev-uiux:push-to-figma tokens` | Sync design tokens |

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

*PWDEV-UIEX v1.0.0 — Quality as a gate, not an aspiration.*
*Maintained by [Paulo Soares](https://github.com/pwdev-solucoes)*
