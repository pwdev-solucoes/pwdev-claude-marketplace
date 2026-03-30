---
description: Display the current project status and progress report
---

# /pwdev-code:status — Status Report

## Procedure
Read and present the current state:

```bash
cat .planning/STATE.md 2>/dev/null || echo "❌ STATE.md not found. No active project."
cat .planning/ROADMAP.md 2>/dev/null
ls .planning/phases/*-PLAN.md 2>/dev/null
ls .planning/phases/*-SUMMARY.md 2>/dev/null
ls .planning/phases/*-CODE-REVIEW.md 2>/dev/null
ls .planning/phases/*-QA-REPORT.md 2>/dev/null
ls .planning/phases/*-VERIFY.md 2>/dev/null
ls .planning/quick/ 2>/dev/null
```

Present:
```markdown
## 📊 Project Status

**Current phase:** [DISCOVER | DESIGN | PLAN | EXECUTE | REVIEW | VERIFY]
**Current plan:** [NN-PP] | **Current task:** [NN-PP-TT]
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
