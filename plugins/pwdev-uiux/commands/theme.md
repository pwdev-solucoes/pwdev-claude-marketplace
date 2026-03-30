---
description: Create or update a semantic color theme with CSS custom properties + Tailwind config. Supports light/dark modes with WCAG AA contrast validation.
argument-hint: "[create | update | from-figma | validate]"
---

# /pwdev-uiux:theme — Semantic Theme Builder

## Agent
Assume the persona of `agents/theme-builder.md`.

## Input
$ARGUMENTS: mode of operation.

| Argument | What it does |
|----------|-------------|
| `create` | Create a new theme from scratch via interview |
| `update` | Modify existing theme tokens |
| `from-figma` | Extract theme from a Figma file |
| `validate` | Run contrast validation on existing theme |
| *(empty)* | Auto-detect: update if theme exists, create if not |

---

## Mode: create

### STEP 1 — Read stack config

```bash
cat .planning/ui/stack.json 2>/dev/null || echo "NO_STACK"
```

If no stack → suggest `/pwdev-uiux:stack` first.

### STEP 2 — Brand interview (max 2 rounds)

**Round 1:**
```
Let's create your theme.

1. What personality fits your product?
   a) Professional & precise (Linear, Stripe)
   b) Warm & approachable (Notion, Coda)
   c) Bold & confident (Vercel, Supabase)
   d) Technical & dense (GitHub, Grafana)
   e) Custom — describe it

2. Primary brand color? (hex like #2563EB, or "you choose")

3. Light mode, dark mode, or both? (recommended: both)
```

**Round 2 (if needed):**
- Secondary/accent color
- Typography preference
- Border radius preference (sharp 4px / medium 8px / rounded 12px)

### STEP 3 — Generate theme

Follow the theme-builder agent flow:
1. Generate primitive palette from brand color
2. Build semantic tokens (light + dark)
3. Generate Tailwind config extension
4. Validate all contrast pairs

### STEP 4 — Write files

Determine file paths based on stack:

| Stack | CSS file | Tailwind config |
|-------|----------|----------------|
| shadcn-vue | `src/assets/index.css` or `app/assets/css/main.css` | `tailwind.config.ts` |
| shadcn-react | `src/app/globals.css` or `src/index.css` | `tailwind.config.ts` |
| primevue | `src/assets/theme.css` | `tailwind.config.ts` |
| custom | ask the user | ask the user |

**Before writing:** check if files exist and ask to merge or replace.

### STEP 5 — Generate theme-spec.md

Write to `.planning/ui/theme-spec.md` with full documentation.

### STEP 6 — Summary

```
Theme created

Personality: [direction]
Primary: [color] | Modes: light + dark
Tokens: [N] semantic pairs | Contrast: all AA compliant

Files:
  [css-path]                    ← CSS variables
  tailwind.config.*             ← Tailwind mapping
  .planning/ui/theme-spec.md   ← Documentation

Next:
  /pwdev-uiux:theme validate      → Re-check contrast
  /pwdev-uiux:push-to-figma tokens → Sync tokens to Figma
  /pwdev-uiux:start "task"         → Build with this theme
```

---

## Mode: update

### STEP 1 — Load existing theme

```bash
cat .planning/ui/theme-spec.md 2>/dev/null || echo "NO_THEME"
```

If no theme → redirect to `create`.

### STEP 2 — Ask what to update

```
Current theme loaded. What do you want to change?

1. Primary color
2. Add/change feedback colors (success, warning, destructive)
3. Add component tokens (sidebar, chart colors)
4. Adjust dark mode values
5. Change border radius / spacing
6. Other (describe)
```

### STEP 3 — Apply changes, re-validate contrast, update files.

---

## Mode: from-figma

### STEP 1 — Read Figma design

```
mcp:figma → get_variable_defs(fileKey)
mcp:figma → get_design_context(nodeId)
```

### STEP 2 — Extract tokens

Map Figma variables → semantic tokens:
- Figma color variables → CSS custom properties
- Figma variable modes (light/dark) → CSS `:root` / `.dark`
- Figma spacing/radius variables → geometry tokens

### STEP 3 — Generate theme files + validate + write.

---

## Mode: validate

### STEP 1 — Read current theme CSS

```bash
# Find theme CSS file
grep -rl "^--background:" src/ app/ 2>/dev/null | head -1
```

### STEP 2 — Extract all foreground/background pairs

### STEP 3 — Calculate contrast ratios

For each pair:
```
[token-pair]: [ratio] — [PASS AA / FAIL AA]
```

### STEP 4 — Report

```
Theme Contrast Validation

Light mode:
  background + foreground:      15.4:1  PASS
  primary + primary-fg:          8.6:1  PASS
  destructive + destructive-fg:  4.8:1  PASS
  muted + muted-fg:              4.6:1  PASS
  warning + warning-fg:          3.2:1  FAIL ← needs fix

Dark mode:
  background + foreground:      14.2:1  PASS
  ...

Result: [ALL PASS / N failures — suggestions below]
```

If failures → suggest adjusted values that pass.

---

## Prohibitions
- NEVER write hex values in component code — only semantic tokens
- NEVER generate light-only themes (dark mode is mandatory)
- NEVER skip contrast validation
- NEVER overwrite existing CSS files without asking
- NEVER use color names as token names (`--blue` is wrong, `--primary` is right)
