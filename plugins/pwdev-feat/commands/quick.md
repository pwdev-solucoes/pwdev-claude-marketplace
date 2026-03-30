---
description: Quick task — no plan file, direct execution for simple tasks (bugfix, config, rename, 1-3 files).
argument-hint: "[task description]"
---

# /pwdev-feat:quick — Quick Task (No Plan)

## Input
$ARGUMENTS: task description (required).

## When to Use
- Bugfix (1-3 files)
- Config change
- Rename / move
- Documentation update
- Simple refactor

## When to Escalate
- >5 files → use `/pwdev-feat:feat`
- Architectural decision → use `/pwdev-feat:feat`
- Migration/schema → use `/pwdev-feat:backend`
- New UI flow → use `/pwdev-feat:frontend`

## Flow

### STEP 1 — Quick Assessment (~10s, silent)
```bash
cat CLAUDE.md 2>/dev/null | head -30
cat .planning/feat/codebase.md 2>/dev/null | head -20
```

Assess: <=5 files? No architectural decision?
If NOT quick-eligible → warn and suggest the right command.

### STEP 2 — Mini-Plan (present to human)
```
📋 Quick Task

Objective: {1 sentence}
Files: {list with action}
Approach: {2-3 sentences}
Verification: {command}

Proceed? (y/n)
```

### STEP 3 — Implement
Follow CLAUDE.md conventions. If unexpected → STOP.

### STEP 4 — Verify + Commit
```bash
npm run lint 2>&1 || composer run lint 2>&1
npm test 2>&1 || php artisan test 2>&1
```

Conventional Commit + result summary.

### STEP 5 — Result
```
✅ Quick task complete

Done: {what changed}
Verification: {evidence}
Commit: {message}
```

## Prohibitions
- NEVER execute without mini-plan approval
- NEVER >5 files (escalate instead)
- NEVER commit without passing lint + tests
