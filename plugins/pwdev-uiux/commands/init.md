---
name: init
description: Initialize the pwdev-uiux framework — detects project stack, creates .planning/ui/ workspace, checks Figma MCP.
---

# /pwdev-uiux:init — Framework Initialization

## STEP 1 — Check if already initialized

```bash
if [ -d ".planning/ui" ] && [ -f ".planning/ui/current-flow.md" ]; then
  echo "ALREADY_INITIALIZED"
else
  echo "NEW"
fi
```

If already initialized:
```
pwdev-uiux already initialized.
   Workspace: .planning/ui/
   Use /pwdev-uiux:status to see current state.
```
Stop unless user asks to reinitialize.

---

## STEP 2 — Detect project framework

```bash
node -e "
const p=require('./package.json');
const d={...p.dependencies,...p.devDependencies};
console.log('vue:', d.vue||'N/A');
console.log('nuxt:', d.nuxt||'N/A');
console.log('react:', d.react||'N/A');
console.log('next:', d.next||'N/A');
console.log('svelte:', d.svelte||'N/A');
console.log('tailwind:', d.tailwindcss||'N/A');
console.log('typescript:', d.typescript||'N/A');
// Component libraries
console.log('shadcn-vue:', d['shadcn-vue']||'N/A');
console.log('reka-ui:', d['reka-ui']||'N/A');
console.log('primevue:', d['primevue']||'N/A');
console.log('radix-ui:', d['@radix-ui/react-dialog']||'N/A');
console.log('headlessui:', d['@headlessui/react']||d['@headlessui/vue']||'N/A');
" 2>/dev/null
```

If no frontend framework detected:
```
No frontend framework detected in package.json.
pwdev-uiux works with Vue 3, React, Svelte, or any frontend framework.
Make sure you're in the right project directory.
```

---

## STEP 3 — Create .planning/ui/ workspace

```bash
mkdir -p .planning/ui
touch .planning/ui/current-flow.md
touch .planning/ui/ux-spec.md
touch .planning/ui/figma-spec.md
touch .planning/ui/component-log.md
touch .planning/ui/review-findings.md
```

Write initial state to `.planning/ui/current-flow.md`:
```markdown
# pwdev-uiux — State

## Active flow
- Status: no active flow
- Phase: —
- Pending gate: —
- Initialized: [timestamp]
- Stack: not configured (run /pwdev-uiux:stack)

## History
- [timestamp]: Framework initialized
```

---

## STEP 4 — Configure UI stack

Prompt the user to configure the stack:

```
Which UI stack does this project use?

1. shadcn-vue      — Vue 3 + shadcn-vue + Reka UI v2 + Tailwind (default)
2. shadcn-react    — React + shadcn/ui + Radix UI + Tailwind
3. primevue        — Vue 3 + PrimeVue + Tailwind
4. untitled-ui     — React + Untitled UI + Radix UI + Tailwind
5. tailwind-plus   — Any framework + Tailwind Plus + Headless UI
6. custom          — I'll describe my stack

Pick a number or name (default: auto-detect):
```

If user picks or auto-detect succeeds → run `/pwdev-uiux:stack` logic to create `.planning/ui/stack.json`.

---

## STEP 5 — Check Figma MCP

Try `mcp:figma → whoami` to confirm connection.

If not configured:
```
Figma MCP: Not configured (optional)
To set up: /pwdev-uiux:setup-figma
```

---

## STEP 6 — Initialization report

```
pwdev-uiux initialized

Detected stack:
  Framework:    [Vue 3 / React / Svelte / ...]
  Components:   [shadcn-vue / shadcn/ui / PrimeVue / ...]
  Styling:      [Tailwind / ...]
  TypeScript:   [yes / no]

Workspace created:
  .planning/ui/
  ├── current-flow.md
  ├── ux-spec.md
  ├── figma-spec.md
  ├── component-log.md
  ├── review-findings.md
  └── stack.json

Integrations:
  Figma MCP:  [connected / not configured]

Next steps:
  /pwdev-uiux:stack          → Change UI stack configuration
  /pwdev-uiux:setup-figma    → Connect Figma
  /pwdev-uiux:scan           → Analyze existing UI
  /pwdev-uiux:start "task"   → Start new UI development
```

## Prohibitions
- NEVER overwrite existing `.planning/ui/` without confirmation
- NEVER read .env files
- NEVER install packages without asking
