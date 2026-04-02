---
description: Display the current project status and progress report
---

# /pwdev-code:status — Status Report

## Procedure

### STEP 0 — Language Selection
Read `.planning/config.json` for the `lang` field (`pt-BR` or `en`).
If set → use it silently. If not set → detect from $ARGUMENTS or ask:
"Em qual idioma deseja seguir? / Which language would you like to use? 1. Portugues (PT-BR) 2. English (EN)"
Save choice to `.planning/config.json` (merge, do not overwrite other fields).
All subsequent output follows the resolved language. Technical terms stay in English.

Read and present the current state:

```bash
cat .planning/state.md 2>/dev/null || echo "❌ state.md not found. No active project."
cat .planning/product/roadmap/roadmap.md 2>/dev/null
ls .planning/phases/*/plans/*.md 2>/dev/null
ls .planning/phases/*/execution/*-summary.md 2>/dev/null
ls .planning/phases/*/review/code-review.md 2>/dev/null
ls .planning/phases/*/review/qa-report.md 2>/dev/null
ls .planning/phases/*/verify/verify.md 2>/dev/null
ls .planning/quick/ 2>/dev/null
```

Present:
```markdown
## 📊 Project Status

**Current phase:** [DISCOVER | DESIGN | PLAN | EXECUTE | REVIEW | VERIFY]
**Current plan:** [phase-slug/PP] | **Current task:** [phase-slug/PP-TT]
**Status:** [in progress | awaiting approval | verifying | blocked]

### Progress
| Plan | Tasks | Completed | Status |
|---|---|---|---|
| 01-01 | 3 | 3/3 | ✅ |
| 01-02 | 3 | 1/3 | 🔄 |

### Wave Map
[Wave 1: ✅ | Wave 2: 🔄 | Wave 3: ⏳]

### Blockers
[None | list]

### Next action
👉 [recommended command]
```
