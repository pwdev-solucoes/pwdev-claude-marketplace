---
description: >
  Push implemented UI components to Figma — creates screens, component library,
  or design system from code. Uses the design-bridge agent in reverse mode (Code → Figma).
argument-hint: "[component-path | 'screen' | 'library' | 'tokens']"
---

# /pwdev-uiux:push-to-figma — Push Designs to Figma

**Argument**: $ARGUMENTS

## Modes

| Argument | What it does |
|----------|-------------|
| `[component-path]` | Push a specific component to Figma |
| `screen` | Push the current feature's full screen layout |
| `library` | Build/update component library in Figma from code |
| `tokens` | Sync design tokens from code to Figma variables |
| *(no argument)* | Interactive — ask what to push |

---

## STEP 0 — Language Selection
Read `.planning/config.json` for the `lang` field (`pt-BR` or `en`).
If set → use it silently. If not set → detect from $ARGUMENTS or ask:
"Em qual idioma deseja seguir? / Which language would you like to use? 1. Portugues (PT-BR) 2. English (EN)"
Save choice to `.planning/config.json` (merge, do not overwrite other fields).
All subsequent output follows the resolved language. Technical terms stay in English.

## Pre-verification

### 1. Check Figma MCP connection

```bash
# Verify Figma is connected
```

Attempt `mcp:figma → whoami`. If fails:
```
⚠️ Figma MCP not connected.
Run /pwdev-uiux:setup-figma to configure the integration.
```
Stop here if not connected.

### 2. Check for implemented components

```bash
# Check component-log for implemented components
cat .planning/ui/component-log.md 2>/dev/null | head -20

# Check for UI components (adapt extension to stack: .vue, .tsx, .svelte, etc.)
find components/ src/components/ -name "*.vue" -o -name "*.tsx" -o -name "*.jsx" 2>/dev/null | head -20
```

---

## Mode: Component Push

When $ARGUMENTS is a component path (e.g., `components/user/UserCard.vue` or `src/components/UserCard.tsx`):

### Step 1 — Analyze the component
```bash
cat [component-path]
```

Extract:
- Component name and props
- Library components used (from configured stack)
- Tailwind classes → design tokens
- States (loading, empty, error, success)
- Variants

### Step 2 — Load prerequisite skill

**MANDATORY**: Load `/figma:figma-use` skill before any `use_figma` call.

### Step 3 — Create in Figma

Use `mcp:figma → use_figma` to:
1. Create a new page or frame named after the component
2. Build the component structure using Figma Auto Layout
3. Map Tailwind tokens → Figma variables
4. Create variants for each state/variant
5. Set up responsive breakpoints if present

### Step 4 — Report

```
✅ Component pushed to Figma

Component: [name]
Figma location: [page/frame]
Variants created: [list]
States: default, loading, empty, error
Tokens mapped: [count]
```

---

## Mode: Screen Push

When $ARGUMENTS is `screen`:

### Step 1 — Gather context

Read current feature state:
```bash
cat .planning/ui/ux-spec.md 2>/dev/null
cat .planning/ui/component-log.md 2>/dev/null
cat .planning/ui/figma-spec.md 2>/dev/null
```

### Step 2 — Load skills

**MANDATORY**: Load `/figma:figma-generate-design` + `/figma:figma-use`

### Step 3 — Build screen in Figma

Using the design generation workflow:
1. Discover existing design system in the Figma file (if any)
2. Map implemented components to Figma counterparts
3. Assemble the full screen layout section-by-section
4. Apply design tokens (use Figma variables, not hardcoded values)
5. Include all states: default, loading, empty, error

### Step 4 — Report

```
✅ Screen pushed to Figma

Feature: [name from ux-spec]
Figma page: [location]
Sections: [count]
Components used: [list]
States rendered: default, loading, empty, error
```

---

## Mode: Library

When $ARGUMENTS is `library`:

### Step 1 — Inventory code components

```bash
# List all project components (adapt extension to stack)
find components/ src/components/ -name "*.vue" -o -name "*.tsx" -o -name "*.jsx" 2>/dev/null | sort

# List library components installed
ls components/ui/ 2>/dev/null || ls src/components/ui/ 2>/dev/null

# Read project UI skill if available
cat .planning/ui/project-ui-skill.md 2>/dev/null | head -50
```

### Step 2 — Load skills

**MANDATORY**: Load `/figma:figma-generate-library` + `/figma:figma-use`

### Step 3 — Build library in Figma

Following the library generation workflow:
1. Create or select a Figma file for the component library
2. Set up design token variables (colors, spacing, typography, radii)
3. Build each component as a Figma component with variants
4. Document prop mappings in component descriptions
5. Set up light/dark mode variable modes

### Step 4 — Report

```
✅ Component library pushed to Figma

File: [Figma file name]
Variables created: [count]
Components built: [count]
  - [ComponentName] ([N] variants)
Themes: light, dark
```

---

## Mode: Tokens

When $ARGUMENTS is `tokens`:

### Step 1 — Extract tokens from code

```bash
# CSS custom properties
grep -r "^--" src/assets/ --include="*.css" 2>/dev/null
grep -r "^--" app.vue --include="*.vue" 2>/dev/null

# Tailwind config
cat tailwind.config.ts 2>/dev/null || cat tailwind.config.js 2>/dev/null

# Library theme/index files
cat components/ui/*/index.ts 2>/dev/null | head -30
```

### Step 2 — Load skills

**MANDATORY**: Load `/figma:figma-use`

### Step 3 — Sync to Figma

Use `mcp:figma → use_figma` to:
1. Create or update variable collections in Figma
2. Map CSS variables → Figma variables
3. Set up light/dark modes as variable modes
4. Group tokens by category (colors, spacing, typography, radii, shadows)

### Step 4 — Report

```
✅ Design tokens synced to Figma

Variable collections: [count]
  Colors: [count] variables
  Spacing: [count] variables
  Typography: [count] variables
  Radii: [count] variables
  Shadows: [count] variables
Modes: light, dark
```

---

## Prohibitions

- NEVER call `use_figma` without loading `/figma:figma-use` skill first
- NEVER push to Figma without verifying connection via `whoami`
- NEVER hardcode design values — always use Figma variables
- NEVER overwrite existing Figma components without asking the user
- NEVER push incomplete components (all states must be present)
