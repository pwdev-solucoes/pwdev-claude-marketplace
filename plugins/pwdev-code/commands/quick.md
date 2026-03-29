---
name: quick
description: All-in-one quick mode for small tasks (up to 5 files)
---

# /pwdev-code:quick — Quick Mode All-in-One

## Agent
Assume the persona of `.claude/agents/agent-quick.md`.

## References
If `CLAUDE.md` or `.planning/SPEC.md` exist, respect their rules.

## Skills
If active skills in SPEC.md or CLAUDE.md → load before implementing.

## Input
$ARGUMENTS: task description (required).

## Flow

### STEP 1 — Mini-Discovery (~15s, silent)
```bash
cat [mentioned file] 2>/dev/null
cat .editorconfig CLAUDE.md .planning/SPEC.md 2>/dev/null | head -30
```
Evaluate: ≤5 files? No architectural decision? No migration?
If NOT Quick-eligible → warn and suggest escalation.

### STEP 2 — Load Active Skills

### STEP 3 — Mini-Plan (present to the human)
```markdown
## 📋 Quick Plan
**Objective:** [1 sentence]
**Files:** [list with action]
**Approach:** [2-3 sentences]
**ACs:** [verifiable]
**Prohibitions:** [inherited + specific]
**Verification:** [command]
```
**Wait for approval.**

### STEP 4 — Implementation
Follow conventions. Apply skills. If unexpected → STOP.

### STEP 5 — Mini-Review + Mini-Verify + Commit
Quick code review (security, correctness) + lint + tests + ACs with evidence → Conventional commit.

### STEP 6 — Result
```markdown
## ✅ Result
**Status:** ✅ COMPLETE | ❌ FAILED
**Done:** [list of changes]
**Verification:** [real evidence]
**Commit:** `type(scope): description`
```

### Persistence
If `.planning/` exists → save to `.planning/quick/[NNN]-[slug]/`.

## Prohibitions (command-level)
- ❌ NEVER execute without an approved mini-plan
- ❌ NEVER >5 files
- ❌ NEVER escalate silently
