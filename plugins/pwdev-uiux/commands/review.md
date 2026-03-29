---
name: pwdev-review
description: Runs a full UX + accessibility Vue review in parallel. Activates a11y-reviewer (WCAG 2.1 AA + Reka UI) and ux-critic (7 Playbook axes) simultaneously.
---

# /pwdev-uiux:review

## Check components

```bash
grep -c "##" .planning/ui/component-log.md 2>/dev/null || echo "0 components"
```

If no components: `Run /pwdev-uiux:build first.`

## Parallel dispatch

**a11y-reviewer**:
```
Audit components in component-log.md against WCAG 2.1 AA.
Stack: Vue 3 + Reka UI v2. Reka manages WAI-ARIA for primitives.
Focus on: project extensions, icons without label, contrast, aria-live.
Append to .planning/ui/review-findings.md (do not overwrite).
```

**ux-critic**:
```
Review components in component-log.md by the 7 Playbook axes.
Each finding must cite the violated principle and the fix in shadcn-vue Vue 3.
Append to .planning/ui/review-findings.md (do not overwrite).
```

## Consolidate result

```
## /pwdev-uiux:review Result

### Accessibility WCAG 2.1 AA
- Status: PASSED / FAILED
- Critical: N | High: N

### UX (7 Playbook axes)
- Status: PASSED / FAILED
- Critical: N | High: N

### Next step
[PASSED] → /pwdev-uiux:handoff to generate documentation
[FAILED] → Fix critical issues → /pwdev-uiux:review again
```
