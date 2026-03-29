---
name: pwdev-status
description: Displays the current state of the pwdev-uiux flow — gates, agents, pending items and recommended next action.
---

# /pwdev-uiux:status

## Read all state files

```bash
echo "=== CURRENT FLOW ===" && cat .planning/ui/current-flow.md 2>/dev/null
echo "=== UX SPEC GATE ===" && grep "\- \[" .planning/ui/ux-spec.md 2>/dev/null | tail -10
echo "=== FIGMA SPEC GATE ===" && grep "\- \[" .planning/ui/figma-spec.md 2>/dev/null | tail -5
echo "=== COMPONENTS ===" && grep "^##" .planning/ui/component-log.md 2>/dev/null
echo "=== REVIEW ===" && grep "Result" .planning/ui/review-findings.md 2>/dev/null
echo "=== PROJECT SKILL ===" && head -5 .planning/ui/project-ui-skill.md 2>/dev/null
```

## Calculate and display status

```
## pwdev-uiux Status

**Task**: [from current-flow]
**Current phase**: [phase]

### Gates
| Gate | Condition | Status |
|---|---|---|
| 1 — UX Spec | All checkboxes checked | ✅/⏳/❌ |
| 2 — Figma Spec | Tokens and components mapped | ✅/⏳/❌ |
| 3 — Implementation | Components in component-log | ✅/⏳/❌ |
| 4 — Review | Zero critical failures | ✅/⏳/❌ |
| 5 — Handoff | Doc in docs/handoff/ | ✅/⏳/❌ |

### Project UI Skill
[available / not available — suggest /pwdev-uiux:scan if missing]

### Next action
[based on the first pending gate]
  ⏳ Gate 1 → /pwdev-uiux:analyze "description"
  ⏳ Gate 2 → /pwdev-uiux:analyze [figma-url]
  ⏳ Gate 3 → /pwdev-uiux:build [component]
  ⏳ Gate 4 → /pwdev-uiux:review
  ⏳ Gate 5 → /pwdev-uiux:handoff
  ✅ All → /pwdev-uiux:start for new feature
```
