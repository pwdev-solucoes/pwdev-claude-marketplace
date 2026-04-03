---
description: Check project status or resume a previous session
argument-hint: "[resume]"
---

# /pwdev-code:session — Session Management

## Role
Utility agent for session state: displays current project status and progress, or resumes a previous session by reading persisted state.

## Input
$ARGUMENTS: subcommand (optional).
- (empty) → show status report (default)
- `resume` → resume previous session

## Procedure

### STEP 0 — Language Selection
Read `.planning/config.json` for the `lang` field (`pt-BR` or `en`).
If set → use it silently. If not set → detect from $ARGUMENTS or ask:
"Em qual idioma deseja seguir? / Which language would you like to use? 1. Portugues (PT-BR) 2. English (EN)"
Save choice to `.planning/config.json` (merge, do not overwrite other fields).
All subsequent output follows the resolved language. Technical terms stay in English.

### STEP 1 — Route Subcommand

Parse $ARGUMENTS:

- **`resume`** → go to STEP 3
- **empty** → go to STEP 2 (Status Report)

---

## STEP 2 — Status Report (default)

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

---

## STEP 3 — Resume Session

### STEP 3.1 — Read persisted state
```bash
cat .planning/state.md
cat .planning/product/roadmap/roadmap.md 2>/dev/null
ls -la .planning/phases/ 2>/dev/null
```

### STEP 3.2 — Identify resumption point
- Last completed phase
- Last completed task
- Next pending action
- Registered blockers

### STEP 3.3 — Verify integrity
```bash
git status --short
grep -rl "Status: in progress" .planning/phases/*/execution/*.md 2>/dev/null
ls .planning/phases/*/spec.md 2>/dev/null && echo "✅ spec.md present" || echo "❌ spec.md missing"
```

### STEP 3.4 — Present
```markdown
## 🔄 Resuming session

**Last state:** [date]
**Phase:** [current]
**Last completed task:** [ID]
**Next action:** [ID or command]

### Integrity
- spec.md: [✅|❌]
- Uncommitted code: [yes/no]
- Tasks in progress: [list]

### Recommendation
👉 [recommended action]

Proceed? (y/n)
```

If uncommitted code → warn and ask: commit or discard.
If inconsistency → suggest /pwdev-code:review then /pwdev-code:verify.
