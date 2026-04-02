---
description: All-in-one quick mode for small tasks (up to 5 files)
---

# /pwdev-code:quick — Quick Mode All-in-One

## Agent
Assume the persona of `.claude/agents/agent-quick.md`.

### Model Resolution
Read `.planning/config.json` for `model_profile` and `model_overrides`.
Resolution order: (1) `model_overrides[agent-name]` → (2) profile lookup → (3) agent frontmatter `model:` default.
Profiles — **performance**: opus for all except reviewer/scanner (sonnet). **balanced**: opus for orchestrator, sonnet for planner/executor/builder/interviewer/reviewer/researcher, haiku for scanner. **economy**: sonnet for most, haiku for reviewer/scanner.
When spawning the agent, pass the resolved model via the `model` parameter.

## References
If `CLAUDE.md` or `.planning/phases/{active-phase-slug}/spec.md` exist, respect their rules.

## Skills
If active skills in spec.md or CLAUDE.md → load before implementing.

## Input
$ARGUMENTS: task description (required).

## Flow

### STEP 0 — Language Selection
Read `.planning/config.json` for the `lang` field (`pt-BR` or `en`).
If set → use it silently. If not set → detect from $ARGUMENTS or ask:
"Em qual idioma deseja seguir? / Which language would you like to use? 1. Portugues (PT-BR) 2. English (EN)"
Save choice to `.planning/config.json` (merge, do not overwrite other fields).
All subsequent output follows the resolved language. Technical terms stay in English.

### STEP 1 — Mini-Discovery (~15s, silent)
```bash
cat [mentioned file] 2>/dev/null
cat .editorconfig CLAUDE.md .planning/phases/{active-phase-slug}/spec.md 2>/dev/null | head -30
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
If `.planning/` exists → save to `.planning/quick/[slug]/`.

## Prohibitions (command-level)
- ❌ NEVER execute without an approved mini-plan
- ❌ NEVER >5 files
- ❌ NEVER escalate silently
