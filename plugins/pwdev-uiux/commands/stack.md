---
name: stack
description: Configure the UI stack for the project. Sets which component library, framework, and patterns the agents will follow.
argument-hint: "[stack-name] — shadcn-vue | shadcn-react | primevue | untitled-ui | custom"
---

# /pwdev-uiux:stack — Configure UI Stack

## Input
$ARGUMENTS: stack preset name (optional — interactive if empty).

## Available Stacks

| Stack | Framework | Component Library | Headless Base |
|-------|-----------|------------------|---------------|
| `shadcn-vue` | Vue 3 | shadcn-vue | Reka UI v2 |
| `shadcn-react` | React | shadcn/ui | Radix UI |
| `primevue` | Vue 3 | PrimeVue | PrimeVue (styled) |
| `untitled-ui` | React | Untitled UI | Radix UI |
| `tailwind-plus` | Any | Tailwind Plus | Headless UI |
| `custom` | Any | Custom / None | — |

## Flow

### STEP 1 — Detect current stack

```bash
cat .planning/ui/stack.json 2>/dev/null && echo "CONFIGURED" || echo "NOT_CONFIGURED"
```

If already configured:
```
Current stack: [name]
Framework: [framework]
Component library: [library]

Change stack? (y/n)
```

### STEP 2 — Auto-detect or ask

If $ARGUMENTS is provided → use that stack directly.

If empty → auto-detect from package.json:

```bash
node -e "
const p=require('./package.json');
const d={...p.dependencies,...p.devDependencies};
const stacks = [];
if (d['shadcn-vue'] || d['reka-ui']) stacks.push('shadcn-vue');
if (d['@radix-ui/react-dialog'] || d['@shadcn/ui']) stacks.push('shadcn-react');
if (d['primevue']) stacks.push('primevue');
if (d['@untitled-ui/react']) stacks.push('untitled-ui');
if (d['@tailwindui/react'] || d['@headlessui/react'] || d['@headlessui/vue']) stacks.push('tailwind-plus');
console.log('vue:', d.vue||'N/A');
console.log('react:', d.react||d['next']||'N/A');
console.log('detected:', stacks.join(',') || 'none');
" 2>/dev/null
```

If auto-detected → confirm: "Detected {stack}. Use this? (Y/n)"

If nothing detected → present options:
```
Which UI stack does this project use?

1. shadcn-vue     — Vue 3 + shadcn-vue + Reka UI v2 + Tailwind
2. shadcn-react   — React + shadcn/ui + Radix UI + Tailwind
3. primevue       — Vue 3 + PrimeVue (styled mode) + Tailwind
4. untitled-ui    — React + Untitled UI + Radix UI + Tailwind
5. tailwind-plus  — Any framework + Tailwind Plus + Headless UI
6. custom         — I'll describe my stack

Pick a number or name:
```

### STEP 3 — Configure stack details

#### For preset stacks (1-5)

Write `.planning/ui/stack.json`:

**shadcn-vue:**
```json
{
  "name": "shadcn-vue",
  "framework": "vue3",
  "component_library": "shadcn-vue",
  "headless_base": "reka-ui",
  "styling": "tailwindcss",
  "forms": "vee-validate + zod",
  "icons": "lucide-vue-next",
  "toasts": "vue-sonner",
  "script_style": "<script setup lang=\"ts\">",
  "skills": ["shadcn-vue", "reka-ui", "ux-tokens", "accessibility"]
}
```

**shadcn-react:**
```json
{
  "name": "shadcn-react",
  "framework": "react",
  "component_library": "shadcn/ui",
  "headless_base": "radix-ui",
  "styling": "tailwindcss",
  "forms": "react-hook-form + zod",
  "icons": "lucide-react",
  "toasts": "sonner",
  "script_style": "tsx",
  "skills": ["ux-tokens", "accessibility"]
}
```

**primevue:**
```json
{
  "name": "primevue",
  "framework": "vue3",
  "component_library": "primevue",
  "headless_base": "primevue",
  "styling": "tailwindcss + primevue-styled",
  "forms": "vee-validate + zod",
  "icons": "primeicons",
  "toasts": "primevue-toast",
  "script_style": "<script setup lang=\"ts\">",
  "skills": ["ux-tokens", "accessibility"]
}
```

**untitled-ui:**
```json
{
  "name": "untitled-ui",
  "framework": "react",
  "component_library": "untitled-ui",
  "headless_base": "radix-ui",
  "styling": "tailwindcss",
  "forms": "react-hook-form + zod",
  "icons": "untitled-ui-icons",
  "toasts": "sonner",
  "script_style": "tsx",
  "skills": ["ux-tokens", "accessibility"]
}
```

**tailwind-plus:**
```json
{
  "name": "tailwind-plus",
  "framework": "auto-detect",
  "component_library": "tailwind-plus",
  "headless_base": "headlessui",
  "styling": "tailwindcss",
  "forms": "auto-detect",
  "icons": "heroicons",
  "toasts": "auto-detect",
  "script_style": "auto-detect",
  "skills": ["ux-tokens", "accessibility"]
}
```

#### For custom stack

Ask:
1. Which framework? (Vue 3 / React / Svelte / other)
2. Component library? (name or "none")
3. CSS approach? (Tailwind / CSS Modules / styled-components / other)
4. Form library? (name or "native")
5. Icon library? (name or "none")

Write `.planning/ui/stack.json` with the answers.

### STEP 4 — Summary

```
✅ UI Stack configured

Stack: {name}
Framework: {framework}
Components: {library}
Styling: {styling}
Forms: {forms}
Icons: {icons}

Skills loaded: {list}

📄 Config: .planning/ui/stack.json

👉 Next:
  /pwdev-uiux:scan    → Analyze existing UI
  /pwdev-uiux:start   → Start developing
```

## Prohibitions
- NEVER install packages without asking
- NEVER override stack.json without confirmation
