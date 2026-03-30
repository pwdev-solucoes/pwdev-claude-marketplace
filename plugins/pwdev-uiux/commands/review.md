---
description: >
  Runs a full UX + accessibility + best practices compliance review in parallel.
  Activates a11y-reviewer (WCAG 2.1 AA + best practices P0 a11y rules) and
  ux-critic (7 Playbook axes + 14-section best practices ruleset) simultaneously.
  Generates a unified compliance report with pass/fail counts by priority.
---

# /pwdev-uiux:review

## Check components

```bash
grep -c "##" .planning/ui/component-log.md 2>/dev/null || echo "0 components"
```

If no components: `Run /pwdev-uiux:build first.`

## Pre-check — Verify skills available

Both `ui-best-practices` and `ui-theme-reference` skills must be installed in the plugin.
These are loaded automatically by the agents via their `skills:` frontmatter declaration.

```bash
ls skills/ui-best-practices/SKILL.md skills/ui-theme-reference/SKILL.md 2>/dev/null
```

If missing: warn that compliance review will be incomplete without canonical reference skills.

## Parallel dispatch

**a11y-reviewer**:
```
Audit components in component-log.md against WCAG 2.1 AA AND the
accessibility-related P0 rules from the ui-best-practices skill.

Skills loaded automatically via frontmatter:
  - ui-best-practices (sections 1.1, 1.2, 1.3, 2.2, 2.3, 14.1, 14.3, 14.4)
  - ui-theme-reference (token values for contrast, focus, motion, sizing)

Stack: Vue 3 + Reka UI v2. Reka manages WAI-ARIA for primitives.
Focus on: project extensions, icons without label, contrast, aria-live,
PLUS best practices P0 rules: dark mode (1.1), semantic tokens (1.2),
reserved colors (1.3), min font size (2.2), type scale (2.3),
reduced motion (14.1), focus indicators (14.3), touch targets (14.4).

Output must include:
  1. Standard WCAG findings
  2. Best practices P0 compliance table (per rule, pass/fail)

Append to .planning/ui/review-findings.md (do not overwrite).
```

**ux-critic**:
```
Review components in component-log.md by:
  1. The 7 Playbook axes (qualitative UX assessment)
  2. The ui-best-practices skill ruleset (concrete rules, P0–P3)

Skills loaded automatically via frontmatter:
  - ui-best-practices (all 14 sections)
  - ui-theme-reference (all token definitions)

Each finding must cite the violated principle (Part A) or rule ID + priority (Part B).
P0 violations are always Critical severity.

Output must include:
  1. Part A — 7-axis findings
  2. Part B — Best practices compliance table with pass/fail per rule
  3. Compliance summary with counts by priority (P0/P1/P2)

Append to .planning/ui/review-findings.md (do not overwrite).
```

## Consolidate result

After both agents complete, read `.planning/ui/review-findings.md` and generate
a unified compliance report:

```
## /pwdev-uiux:review Result

### Accessibility WCAG 2.1 AA
- Status: PASSED / FAILED
- Critical: N | High: N

### Accessibility Best Practices (P0 rules)
- Status: PASSED / FAILED
- Rules checked: N | Passed: N | Failed: N

### UX (7 Playbook axes)
- Status: PASSED / FAILED
- Critical: N | High: N

### Best Practices Compliance (full ruleset)

| Priority | Rules checked | Passed | Failed | N/A | Status |
|----------|:------------:|:------:|:------:|:---:|:------:|
| **P0**   | N            | N      | N      | N   | ✅/❌  |
| **P1**   | N            | N      | N      | N   | ✅/⚠️  |
| **P2**   | N            | N      | N      | N   | ✅/⚠️  |
| **Total**| N            | N      | N      | N   |        |

### P0 Violations (must fix before handoff)

| Rule | Component | File:line | Description | Required Fix |
|------|-----------|-----------|-------------|-------------|
| [ID] | [name]   | [file:ln] | [violation] | [specific fix] |

### P1 Violations (should fix unless justified)

| Rule | Component | File:line | Description | Suggested Fix |
|------|-----------|-----------|-------------|--------------|
| [ID] | [name]   | [file:ln] | [violation] | [specific fix] |

### Gate Decision

| Criterion | Status |
|-----------|:------:|
| Zero critical WCAG failures | ✅/❌ |
| Zero critical UX failures (7 axes) | ✅/❌ |
| All P0 best practices rules passed | ✅/❌ |
| All P1 violations justified or fixed | ✅/❌ |
| **Overall** | **APPROVED / FAILED** |

### Next step
[APPROVED] → /pwdev-uiux:handoff to generate documentation
[FAILED] → Fix issues listed above → /pwdev-uiux:review again
```

## Notes

- The compliance report aggregates findings from both agents — no manual merging needed
- P0 failures from either agent block the gate
- P1 failures do not block but require documented justification if skipped
- P2/P3 rules are tracked for visibility but never block the gate
- Run `/pwdev-uiux:review` again after fixing violations to verify resolution
