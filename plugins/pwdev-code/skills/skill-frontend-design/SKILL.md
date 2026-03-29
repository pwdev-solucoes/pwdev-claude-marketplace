---
name: skill-frontend-design
version: 1.0.0
description: >
  Design precise, production-grade enterprise UI — dashboards, admin panels, SaaS interfaces,
  and data-heavy applications. Use this skill for professional software interfaces that need
  Jony Ive-level craft: clean, minimal, functional, with intentional personality.
  Do NOT use for creative landing pages, marketing sites, or experimental/artistic frontends.
compatible_with:
  - "any modern frontend framework"
  - "tailwindcss >=3.0"
author: Pwdev
updated: 2026-03-29
---

# Enterprise UI Design Skill

Build polished, professional interfaces for enterprise software, SaaS dashboards, admin panels,
and data-heavy applications. Every pixel intentional. No generic AI aesthetics.

**When to use this skill:** Dashboards, admin interfaces, SaaS products, data tables, settings
pages, internal tools, analytics views, multi-panel layouts, form-heavy interfaces.

---

## Integration with PWDEV-CODE

This skill integrates into the PWDEV-CODE workflow at multiple phases:

### In SPEC.md (DESIGN phase — agent-architect)

When this skill is active, the architect MUST add to SPEC.md:

**Section 1 — Persona:** Include "skill-frontend-design" in Active Skills.

**Section 5 — Quality Criteria:** Add:
- [ ] Design direction explicitly chosen (not defaulted)
- [ ] 4px grid for all spacing
- [ ] Consistent border-radius system
- [ ] ONE depth strategy throughout
- [ ] Four-level text contrast hierarchy
- [ ] Color used only for meaning (status, action, error)
- [ ] Navigation context present (sidebar/topnav, location, user)
- [ ] Monospace for all data values

**Section 7 — Prohibitions:** Add:
- No native form elements in styled UI
- No multiple accent colors in one interface
- No generic AI aesthetics (purple gradients, oversized corners, excessive shadows)
- No asymmetric padding without clear reason

### In PLAN.md (PLAN phase — agent-planner)

When this skill is active, tasks that involve UI MUST include in "Required Context":
```
- Skill: skills/skill-frontend-design/SKILL.md — read before implementing UI components
- Skill: skills/skill-frontend-design/TEMPLATES.md — reference patterns for common components
```

### In REVIEW (REVIEW phase — agent-code-reviewer + agent-qa)

The code reviewer MUST check:
- Design direction was committed to (not generic defaults)
- Spacing follows 4px grid
- Depth strategy is consistent
- Color is used for meaning only

### In VERIFY.md (VERIFY phase — agent-verifier)

Add to verification checklist:
```markdown
## Skill: frontend-design
| Item | Status | Evidence |
|------|:------:|----------|
| Design direction chosen | ✅/❌ | [which direction] |
| 4px grid spacing | ✅/❌ | [spot check 3 components] |
| Consistent radius | ✅/❌ | [all use same system] |
| ONE depth strategy | ✅/❌ | [borders-only / shadows / surface] |
| Monospace for data | ✅/❌ | [numbers, IDs, timestamps] |
| No anti-patterns | ✅/❌ | [checked AVOID list] |
```

---

## Workflow (follow this order)

### Step 1: Analyze Context

Before writing ANY code, read the project's CLAUDE.md and SPEC.md to understand:

| Question                   | Why it matters                                      |
|----------------------------|-----------------------------------------------------|
| What does this product do? | A finance tool ≠ a creative tool ≠ a dev tool       |
| Who are the users?         | Power users want density. Casual users want guidance |
| What's the emotional job?  | Trust? Efficiency? Delight? Focus?                   |
| What data is primary?      | Tables, charts, KPIs, forms — drives layout choice   |
| What stack is defined?     | Read SPEC.md section 1 for framework and conventions |

### Step 2: Commit to a Design Direction

Pick ONE personality. Don't default — choose with intent:

- **Precision & Density** — Tight spacing, monochrome, information-forward. _Think: Linear, Raycast._
- **Warmth & Approachability** — Generous spacing, soft shadows, friendly. _Think: Notion, Coda._
- **Sophistication & Trust** — Cool tones, layered depth, financial gravitas. _Think: Stripe, Mercury._
- **Boldness & Clarity** — High contrast, dramatic negative space, confident type. _Think: Vercel._
- **Utility & Function** — Muted palette, functional density, clear hierarchy. _Think: GitHub._
- **Data & Analysis** — Chart-optimized, technical but accessible. _Think: Grafana, Metabase._

Then lock in these choices:

| Decision           | Options                                                                |
|--------------------|------------------------------------------------------------------------|
| **Color foundation** | Warm (creams) · Cool (slate/blue-gray) · Pure neutral · Tinted        |
| **Light or dark?**   | Light = open, approachable · Dark = focused, premium, technical       |
| **Accent color**     | ONE color. Blue=trust, Green=growth, Orange=energy, Violet=creativity |
| **Depth strategy**   | Borders-only · Single shadow · Layered shadows · Surface color shifts |
| **Corner radius**    | Sharp (2-6px) · Soft (8-12px) — pick a system, stay consistent       |
| **Typography**       | System fonts · Geometric sans (Geist, Inter) · Humanist (SF Pro, Satoshi) · Mono-influenced |
| **Layout**           | Dense grid · Generous spacing · Sidebar nav · Top nav · Split panels  |

**Record these decisions in CONTEXT.md** during the DESIGN phase.

### Step 3: Build with Craft

Implement the interface following the design rules below. Every component must feel intentional.

### Step 4: Self-Validate

Before delivering, run through the **Validation Checklist** at the bottom of this file.

---

## Design Rules

### MUST (non-negotiable)

1. **4px grid for all spacing.** Values: 4, 8, 12, 16, 24, 32px. No arbitrary numbers.
2. **Symmetrical padding.** If top is 16px, sides and bottom are 16px. Exception: `padding: 12px 16px` when horizontal needs room.
3. **Consistent border-radius.** Pick sharp (2-6px) or soft (8-12px). Never mix systems. Never 16px+ on small elements.
4. **ONE depth strategy.** Borders-only OR single shadows OR layered shadows. Don't mix across the same interface.
5. **Monospace for data.** Numbers, IDs, codes, timestamps get `font-family: monospace` with `font-variant-numeric: tabular-nums`.
6. **Four-level contrast hierarchy.** Foreground (primary) → Secondary → Muted → Faint. Use all four consistently:
   ```css
   --text-primary: #0f172a;    /* headings, key data */
   --text-secondary: #334155;  /* body text */
   --text-muted: #64748b;      /* labels, secondary info */
   --text-faint: #94a3b8;      /* placeholders, disabled */
   ```
7. **Color = meaning only.** Gray builds structure. Color only for: status, action, error, success. No decorative color.
8. **Navigation context.** Never render a floating component — include sidebar/topnav, breadcrumbs/page title, and user context.
9. **No native form elements in styled UI.** Build custom selects, date pickers, checkboxes. Native elements break visual consistency.
10. **Custom select triggers use `display: inline-flex` + `white-space: nowrap`** to keep text and chevron on same row.

### SHOULD (strong recommendations)

1. **Typography scale:** 11, 12, 13, 14 (base), 16, 18, 24, 32px. Headlines at 600 weight with `-0.02em` letter-spacing.
2. **Icons from Lucide** (`lucide-react` or `lucide-vue-next`). Icons clarify, not decorate — if removing one loses no meaning, remove it.
3. **Animation:** 150ms micro-interactions, 200-250ms transitions. Easing: `cubic-bezier(0.25, 1, 0.5, 1)`. No bounce/spring.
4. **Card layout variety.** A metric card ≠ a plan card ≠ a settings card. Vary internal structure, but keep surface treatment consistent.
5. **Sidebar same background as content.** Use a subtle border for separation, not different background colors.
6. **CSS variables for all design tokens.** Colors, spacing, shadows, radii — all as variables for easy theming.

### AVOID (anti-patterns)

- Dramatic drop shadows (`box-shadow: 0 25px 50px...`)
- Thick borders (2px+) for decoration
- Asymmetric padding without clear reason
- Pure white cards on colored backgrounds
- Excessive spacing (margins > 48px between sections)
- Spring/bouncy animations
- Gradients for decoration
- Multiple accent colors in one interface
- Color-coding everything — score bars, grade badges don't need traffic-light colors
- Generic AI aesthetics: purple gradients, oversized rounded corners, excessive card shadows

---

## Dark Mode Rules

When building dark interfaces:

- **Borders over shadows** — Shadows are nearly invisible on dark backgrounds. Use borders at 10-15% white opacity.
- **Desaturate semantic colors** — Success/warning/error colors need lower saturation to avoid harshness.
- **Same hierarchy, inverted values** — The four-level contrast system still applies with inverted lightness values.

---

## Validation Checklist

Run through before delivering:

- [ ] Design direction was explicitly chosen (not defaulted)
- [ ] All spacing aligns to 4px grid
- [ ] Padding is symmetrical on all containers
- [ ] Border-radius is consistent across all components
- [ ] ONE depth strategy used throughout
- [ ] Monospace applied to all data values
- [ ] Color only used for meaning (status, action, error)
- [ ] Four-level text contrast hierarchy applied
- [ ] Navigation context present (sidebar/topnav, location, user)
- [ ] No native form elements — all custom-styled
- [ ] No anti-patterns from AVOID list
- [ ] Card layouts vary by content type, surface treatment stays consistent
- [ ] Dark mode adjustments applied (if applicable)
- [ ] Animations use correct timing and easing
- [ ] Interface feels designed for its specific product context

---

## Template Reference

See `TEMPLATES.md` for starter component patterns: metric cards, data tables, sidebar navigation,
filter bars, form layouts, and status badges — all following these design rules.

Templates are framework-agnostic references. Adapt to your project's stack (React, Vue, Svelte, etc.)
and component library as defined in SPEC.md section 1.
