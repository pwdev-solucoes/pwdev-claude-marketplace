---
name: ui-theme-reference
description: >
  Canonical design token registry — colors, typography, spacing, sizing, border radius,
  shadows, z-index, breakpoints, motion, and focus tokens. Used by ui-best-practices
  rules and all agents that implement or review UI components. Includes CSS variable
  template for quick project setup.
---

# UI Theme Reference

> Configurable design token registry used by `ui-best-practices` rules.
> Every hardcoded value in the best practices MUST reference a token defined here.
> To customize: override values below or generate via `/pwdev-uiux:theme create`.

---

## How to Use

Rules in the `ui-best-practices` skill reference tokens as `theme.<section>.<token>`.
When implementing, map these tokens to your stack:

| Stack | Token format | File |
|-------|-------------|------|
| shadcn-vue | `hsl(var(--<token>))` | `src/assets/index.css` |
| shadcn-react | `hsl(var(--<token>))` | `src/app/globals.css` |
| primevue | `var(--p-<token>)` | `src/assets/theme.css` |
| tailwind-only | Tailwind config `theme.extend` | `tailwind.config.ts` |
| custom | Any CSS variable scheme | project-specific |

---

## 1. Colors

### 1.1 Surfaces

| Token | Light | Dark | Usage |
|-------|-------|------|-------|
| `--background` | `#F9FAFB` · `210 20% 98%` | `#0A0F1A` · `222 84% 5%` | Page background |
| `--foreground` | `#1D2939` · `220 26% 16%` | `#F0F4F8` · `210 40% 96%` | Primary text |
| `--card` | `#FFFFFF` · `0 0% 100%` | `#111827` · `222 47% 11%` | Card / surface background |
| `--card-foreground` | `#1D2939` · `220 26% 16%` | `#F0F4F8` · `210 40% 96%` | Text on cards |
| `--popover` | `#FFFFFF` · `0 0% 100%` | `#111827` · `222 47% 11%` | Popover / dropdown bg |
| `--popover-foreground` | `#1D2939` · `220 26% 16%` | `#F0F4F8` · `210 40% 96%` | Text on popovers |

### 1.2 Text Hierarchy

| Token | Light | Dark | Usage |
|-------|-------|------|-------|
| `--foreground` | `#1D2939` | `#F0F4F8` | Primary text, headings |
| `--muted-foreground` | `#667085` | `#94A3B8` | Secondary text, labels, placeholders |

### 1.3 Interactive

| Token | Light | Dark | Usage |
|-------|-------|------|-------|
| `--primary` | *brand color* | *brand color (adjusted)* | Buttons, links, focus rings |
| `--primary-foreground` | `#FFFFFF` | `#FFFFFF` | Text on primary backgrounds |
| `--secondary` | `#F1F5F9` | `#1E293B` | Secondary buttons, subtle actions |
| `--secondary-foreground` | `#1D2939` | `#F0F4F8` | Text on secondary backgrounds |
| `--accent` | `#F1F5F9` | `#1E293B` | Hover highlights, active states |
| `--accent-foreground` | `#1D2939` | `#F0F4F8` | Text on accent backgrounds |

### 1.4 Feedback

| Token | Light | Dark | Usage |
|-------|-------|------|-------|
| `--success` | `#039855` | `#34D399` | Positive states, confirmations |
| `--success-foreground` | `#FFFFFF` | `#022C22` | Text on success backgrounds |
| `--warning` | `#F79009` | `#FBBF24` | Alerts, caution states |
| `--warning-foreground` | `#422006` | `#422006` | Text on warning backgrounds |
| `--destructive` | `#D92D20` | `#FCA5A5` | Errors, delete actions |
| `--destructive-foreground` | `#FFFFFF` | `#450A0A` | Text on destructive backgrounds |
| `--info` | `#2563EB` | `#60A5FA` | Informational, tips |
| `--info-foreground` | `#FFFFFF` | `#172554` | Text on info backgrounds |

### 1.5 Structure

| Token | Light | Dark | Usage |
|-------|-------|------|-------|
| `--border` | `#EAECF0` | `#1E293B` | Dividers, separators |
| `--input` | `#D0D5DD` | `#334155` | Input borders |
| `--ring` | *primary* | *primary* | Focus ring color |
| `--muted` | `#F1F5F9` | `#1E293B` | Muted backgrounds (badges, tags) |

### 1.6 Reserved Semantic Colors

These colors carry universal meaning. **Never repurpose them** for decorative or categorical use:

| Color | Meaning | Allowed usage |
|-------|---------|---------------|
| Green (`--success`) | Good / positive / complete | Success states, positive KPIs, completion |
| Orange (`--warning`) | Caution / attention needed | Warnings, pending actions, approaching limits |
| Red (`--destructive`) | Bad / error / danger | Errors, failures, destructive actions, negative KPIs |

For categorical/chart colors, use the chart palette below.

### 1.7 Chart Palette

Dedicated colors for data visualization — independent from feedback semantics:

| Token | Default | Usage |
|-------|---------|-------|
| `--chart-1` | `#2563EB` | Primary data series |
| `--chart-2` | `#7C3AED` | Secondary data series |
| `--chart-3` | `#0891B2` | Tertiary data series |
| `--chart-4` | `#C026D3` | Fourth data series |
| `--chart-5` | `#EA580C` | Fifth data series |
| `--chart-muted` | `#D1D5DB` | De-emphasized / comparison series |

---

## 2. Typography

### 2.1 Font Stack

| Token | Default | Fallbacks |
|-------|---------|-----------|
| `--font-sans` | `Inter` | `system-ui, -apple-system, sans-serif` |
| `--font-mono` | `JetBrains Mono` | `ui-monospace, monospace` |

### 2.2 Type Scale

Progressive scale — adjacent levels must not skip more than one step:

| Token | Size | Line Height | Weight | Usage |
|-------|------|-------------|--------|-------|
| `--text-xs` | `12px` | `16px` | 400 | Footnotes, badges, captions (minimum allowed) |
| `--text-sm` | `14px` | `20px` | 400 | **Default body text**, form labels |
| `--text-base` | `16px` | `24px` | 400 | Emphasized body, card titles |
| `--text-lg` | `18px` | `28px` | 500 | Section headings |
| `--text-xl` | `20px` | `28px` | 600 | Page sub-titles |
| `--text-2xl` | `24px` | `32px` | 600 | Page titles |
| `--text-3xl` | `30px` | `36px` | 700 | Hero headings |
| `--text-4xl` | `36px` | `40px` | 700 | Display / marketing headings |

**Constraint:** never jump more than 2 steps between adjacent text elements (e.g., `text-3xl` → `text-sm` is forbidden; use `text-3xl` → `text-xl` → `text-base` → `text-sm`).

### 2.3 Font Weight Scale

| Token | Value | Usage |
|-------|-------|-------|
| `--font-normal` | `400` | Body text |
| `--font-medium` | `500` | Labels, nav items |
| `--font-semibold` | `600` | Headings, emphasis |
| `--font-bold` | `700` | Hero, display text |

---

## 3. Spacing

Base unit: **4px**. All spacing must be a multiple of 4.

| Token | Value | Tailwind | Typical Usage |
|-------|-------|----------|---------------|
| `--space-0.5` | `2px` | `gap-0.5` | Micro adjustments only |
| `--space-1` | `4px` | `gap-1` | Icon ↔ label gap |
| `--space-1.5` | `6px` | `gap-1.5` | Compact inline gap |
| `--space-2` | `8px` | `gap-2` | Internal gap, small padding |
| `--space-3` | `12px` | `gap-3` | Badge padding, compact lists |
| `--space-4` | `16px` | `gap-4, p-4` | Default card padding (min) |
| `--space-5` | `20px` | `gap-5` | Medium card padding |
| `--space-6` | `24px` | `gap-6, p-6` | Default card padding (max), section gaps |
| `--space-8` | `32px` | `gap-8, p-8` | Large section padding |
| `--space-10` | `40px` | `gap-10` | Page-level vertical spacing |
| `--space-12` | `48px` | `gap-12` | Major section dividers |
| `--space-16` | `64px` | `gap-16` | Page top/bottom margins |

### Card Padding Rule

| Card context | Recommended padding |
|--------------|-------------------|
| Compact (sidebar, list items) | `--space-3` to `--space-4` (12–16px) |
| Standard (content cards) | `--space-4` to `--space-6` (16–24px) |
| Featured / hero cards | `--space-6` to `--space-8` (24–32px) |
| **Ceiling** | Never exceed `--space-8` (32px) in cards |

---

## 4. Sizing

### 4.1 Interactive Elements

| Token | Value | Usage |
|-------|-------|-------|
| `--height-input` | `40px` | Inputs, selects, single-line controls |
| `--height-button` | `40px` | All buttons (must match input height) |
| `--height-button-sm` | `32px` | Compact buttons (tables, toolbars) |
| `--height-button-lg` | `48px` | Hero CTAs, prominent actions |
| `--min-touch-target` | `44px` | Minimum tap area on touch devices (WCAG 2.5.8) |

### 4.2 Content Width

| Token | Value | Usage |
|-------|-------|-------|
| `--max-w-form` | `560px` | Form containers (onboarding, settings) |
| `--max-w-button` | `400px` | Max button width in wide forms |
| `--max-w-content` | `768px` | Article/text-heavy content |
| `--max-w-page` | `1280px` | Page container |

### 4.3 Textarea Height

| Context | Rows | Approx Height |
|---------|------|---------------|
| Short input (tagline, slug) | 2 | `~56px` |
| Medium input (description) | 4–5 | `~112px` |
| Long input (feedback, notes) | 6–8 | `~168px` |

Always enable auto-resize to grow with content.

---

## 5. Border Radius

| Token | Value | Usage |
|-------|-------|-------|
| `--radius` | `8px` *(configurable)* | Base radius — defines product personality |
| `--radius-sm` | `calc(var(--radius) - 4px)` | Badges, small elements |
| `--radius-md` | `calc(var(--radius) - 2px)` | Inputs, buttons |
| `--radius-lg` | `var(--radius)` | Cards, modals |
| `--radius-xl` | `calc(var(--radius) + 4px)` | Feature cards, large containers |
| `--radius-full` | `9999px` | Avatars, pills, tags |

### Personality Guide

| Brand Style | `--radius` value |
|-------------|-----------------|
| Modern / trendy | `12px–16px` |
| Neutral / corporate (safe default) | `8px` |
| Enterprise / dense | `4px` |
| Sharp / editorial | `0px–2px` |

---

## 6. Shadows

All shadows use `#000000` with controlled opacity. No colored shadows.

| Token | Value | Usage |
|-------|-------|-------|
| `--shadow-xs` | `0 1px 2px rgba(0,0,0,0.05)` | Subtle lift (inputs, badges) |
| `--shadow-sm` | `0 2px 4px rgba(0,0,0,0.06)` | Cards at rest |
| `--shadow-md` | `0 4px 16px rgba(0,0,0,0.08)` | Elevated cards, dropdowns |
| `--shadow-lg` | `0 8px 24px rgba(0,0,0,0.10)` | Modals, popovers |
| `--shadow-xl` | `0 16px 48px rgba(0,0,0,0.12)` | Command palette, overlays |

**Constraints:**
- Minimum opacity: `0.05` (below is invisible)
- Maximum opacity: `0.12` (above feels heavy)
- Never use colored shadows
- Never use gradients as shadow replacements

---

## 7. Z-Index Scale

Managed scale to prevent z-index wars:

| Token | Value | Usage |
|-------|-------|-------|
| `--z-base` | `0` | Default stacking |
| `--z-dropdown` | `10` | Dropdowns, tooltips |
| `--z-sticky` | `20` | Sticky headers, fixed navs |
| `--z-drawer` | `30` | Side drawers, panels |
| `--z-modal` | `40` | Modals, dialogs |
| `--z-popover` | `50` | Popovers over modals |
| `--z-toast` | `60` | Toast notifications |
| `--z-command` | `70` | Command palette (Cmd+K) |
| `--z-overlay` | `80` | Full-screen overlays |

---

## 8. Breakpoints

| Token | Value | Tailwind | Usage |
|-------|-------|----------|-------|
| `--bp-sm` | `640px` | `sm:` | Large phones landscape |
| `--bp-md` | `768px` | `md:` | Tablets |
| `--bp-lg` | `1024px` | `lg:` | Small laptops |
| `--bp-xl` | `1280px` | `xl:` | Desktops |
| `--bp-2xl` | `1536px` | `2xl:` | Large screens |

### Navigation Breakpoint Rules

| Viewport | Max nav items | Menu style |
|----------|--------------|------------|
| `< md` | 4 visible | Bottom bar or hamburger |
| `md–lg` | 5–6 visible | Top bar or compact sidebar |
| `≥ lg` | Unlimited | Full sidebar |

---

## 9. Motion & Animation

| Token | Value | Usage |
|-------|-------|-------|
| `--duration-instant` | `100ms` | Hover color changes, opacity |
| `--duration-fast` | `150ms` | Button press, toggle switch |
| `--duration-normal` | `200ms` | Dropdown open, tooltip appear |
| `--duration-slow` | `300ms` | Drawer slide, modal enter |
| `--duration-slower` | `500ms` | Page transitions, skeleton fade |
| `--ease-default` | `cubic-bezier(0.4, 0, 0.2, 1)` | General purpose easing |
| `--ease-in` | `cubic-bezier(0.4, 0, 1, 1)` | Elements leaving the screen |
| `--ease-out` | `cubic-bezier(0, 0, 0.2, 1)` | Elements entering the screen |

**Constraint:** always respect `prefers-reduced-motion: reduce` — disable or minimize all animations.

---

## 10. Focus & Accessibility

| Token | Value | Usage |
|-------|-------|-------|
| `--ring-width` | `2px` | Focus ring thickness |
| `--ring-offset` | `2px` | Gap between element and focus ring |
| `--ring-color` | `var(--ring)` | Focus ring color (defaults to primary) |

### Contrast Requirements (WCAG AA)

| Element Type | Minimum Ratio |
|-------------|---------------|
| Normal text (< 18px) | **4.5:1** |
| Large text (≥ 18px or ≥ 14px bold) | **3:1** |
| UI components (borders, icons) | **3:1** |
| Non-text contrast (graphs, charts) | **3:1** |

---

## CSS Variable Template

Minimal starter for any project — copy and customize:

```css
@layer base {
  :root {
    /* Surfaces */
    --background: 210 20% 98%;
    --foreground: 220 26% 16%;
    --card: 0 0% 100%;
    --card-foreground: 220 26% 16%;
    --popover: 0 0% 100%;
    --popover-foreground: 220 26% 16%;
    --muted: 210 40% 96%;
    --muted-foreground: 215 16% 47%;

    /* Interactive */
    --primary: 221 83% 53%;       /* ← your brand color */
    --primary-foreground: 0 0% 100%;
    --secondary: 210 40% 96%;
    --secondary-foreground: 220 26% 16%;
    --accent: 210 40% 96%;
    --accent-foreground: 220 26% 16%;

    /* Feedback */
    --destructive: 0 72% 51%;
    --destructive-foreground: 0 0% 100%;
    --success: 160 84% 39%;
    --success-foreground: 0 0% 100%;
    --warning: 32 95% 44%;
    --warning-foreground: 26 83% 14%;
    --info: 221 83% 53%;
    --info-foreground: 0 0% 100%;

    /* Structure */
    --border: 220 13% 91%;
    --input: 218 14% 86%;
    --ring: var(--primary);

    /* Geometry */
    --radius: 0.5rem;

    /* Shadows */
    --shadow-sm: 0 2px 4px rgba(0,0,0,0.06);
    --shadow-md: 0 4px 16px rgba(0,0,0,0.08);
    --shadow-lg: 0 8px 24px rgba(0,0,0,0.10);

    /* Motion */
    --duration-fast: 150ms;
    --duration-normal: 200ms;
    --duration-slow: 300ms;

    /* Focus */
    --ring-width: 2px;
    --ring-offset: 2px;
  }

  .dark {
    --background: 222 84% 5%;
    --foreground: 210 40% 96%;
    --card: 222 47% 11%;
    --card-foreground: 210 40% 96%;
    --popover: 222 47% 11%;
    --popover-foreground: 210 40% 96%;
    --muted: 217 33% 17%;
    --muted-foreground: 215 20% 65%;

    --primary: 217 91% 60%;
    --primary-foreground: 222 47% 11%;
    --secondary: 217 33% 17%;
    --secondary-foreground: 210 40% 96%;
    --accent: 217 33% 17%;
    --accent-foreground: 210 40% 96%;

    --destructive: 0 63% 31%;
    --destructive-foreground: 210 40% 98%;
    --success: 142 69% 58%;
    --success-foreground: 144 61% 10%;
    --warning: 48 96% 53%;
    --warning-foreground: 22 78% 10%;
    --info: 217 91% 60%;
    --info-foreground: 222 47% 11%;

    --border: 217 33% 17%;
    --input: 217 33% 17%;
    --ring: 224 76% 48%;

    --shadow-sm: 0 2px 4px rgba(0,0,0,0.20);
    --shadow-md: 0 4px 16px rgba(0,0,0,0.25);
    --shadow-lg: 0 8px 24px rgba(0,0,0,0.30);
  }

  @media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
      animation-duration: 0.01ms !important;
      transition-duration: 0.01ms !important;
    }
  }
}
```

---

## Integration with Plugin Commands

| Command | How it uses this reference |
|---------|--------------------------|
| `/pwdev-uiux:theme create` | Generates a customized version of the CSS template above |
| `/pwdev-uiux:theme validate` | Checks all foreground/background pairs against contrast requirements |
| `/pwdev-uiux:theme from-figma` | Maps Figma variables to this token structure |
| `/pwdev-uiux:scan` | Audits existing UI against these tokens |
| `/pwdev-uiux:push-to-figma tokens` | Syncs these tokens to Figma variables |
