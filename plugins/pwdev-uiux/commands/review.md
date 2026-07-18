---
description: >
  Runs a full UX + accessibility + best practices compliance review in parallel.
  Activates a11y-reviewer (WCAG 2.1 AA + best practices P0 a11y rules) and
  ux-critic (7 Playbook axes + 14-section best practices ruleset) simultaneously.
  Generates a unified compliance report with pass/fail counts by priority.
---

# /pwdev-uiux:review

## STEP 0 — Language
Follow `${CLAUDE_PLUGIN_ROOT}/references/language.md` (resolve `lang` from
`.planning/config.json`; ask only if unset).

## Check components

```bash
grep -c "##" .planning/ui/component-log.md 2>/dev/null || echo "0 components"
```

If no components: `Run /pwdev-uiux:build first.`

## Parallel dispatch (REAL subagents — TWO Task calls in the SAME message)

Models per `${CLAUDE_PLUGIN_ROOT}/references/model-profiles.md`
(`uiux-a11y-reviewer`, `uiux-ux-critic`). Skills are NOT auto-loaded — the
prompts list the SKILL.md paths explicitly. Read the stack from
`.planning/ui/stack.json` and pass it in (never hardcode a framework).

1. `subagent_type: "pwdev-uiux:a11y-reviewer"`:
```
TASK: audit components in .planning/ui/component-log.md against WCAG 2.1 AA
AND the accessibility-related P0 rules from ui-best-practices.
STACK: {from .planning/ui/stack.json — headless libs handle WAI-ARIA for
primitives; focus on project extensions}
SKILLS — read these files BEFORE auditing:
  ${CLAUDE_PLUGIN_ROOT}/skills/accessibility/SKILL.md
  ${CLAUDE_PLUGIN_ROOT}/skills/ui-best-practices/SKILL.md (1.1-1.3, 2.2-2.3, 14.1, 14.3, 14.4)
  ${CLAUDE_PLUGIN_ROOT}/skills/ui-theme-reference/SKILL.md
LANGUAGE: {lang}
OUTPUT CONTRACT: WCAG findings + P0 compliance table appended to
.planning/ui/review-findings.md (do not overwrite); reply ≤10 status lines.
```

2. `subagent_type: "pwdev-uiux:ux-critic"`:
```
TASK: review components in .planning/ui/component-log.md by the 7 Playbook
axes AND the ui-best-practices ruleset (P0-P3).
STACK: {from .planning/ui/stack.json}
SKILLS — read these files BEFORE reviewing:
  ${CLAUDE_PLUGIN_ROOT}/skills/component-audit/SKILL.md
  ${CLAUDE_PLUGIN_ROOT}/skills/ux-tokens/SKILL.md
  ${CLAUDE_PLUGIN_ROOT}/skills/ui-best-practices/SKILL.md (all 14 sections)
  ${CLAUDE_PLUGIN_ROOT}/skills/ui-theme-reference/SKILL.md
LANGUAGE: {lang}
OUTPUT CONTRACT: Part A (7 axes) + Part B (compliance table) + priority
summary appended to .planning/ui/review-findings.md (do not overwrite);
every finding cites principle or rule ID; P0 violations are Critical;
reply ≤10 status lines.
```

## Consolidate result

After BOTH status replies arrive, read `.planning/ui/review-findings.md` and
generate a unified compliance report:

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
