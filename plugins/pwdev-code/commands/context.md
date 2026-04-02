---
description: Generate minimal context files for executor subagents to combat context rot
---

# /pwdev-code:context — Context Generator for Subagents

## Role
Utility agent that generates or updates the minimal context files that
executor subagents need. Combats context rot by ensuring each
executor receives ONLY what is necessary.

## When to use
- Before running `/pwdev-code:execute` after a long pause
- When state.md indicates the context may be stale
- When a new dev joins in the middle of a feature

## Procedure

### STEP 0 — Language Selection
Read `.planning/config.json` for the `lang` field (`pt-BR` or `en`).
If set → use it silently. If not set → detect from $ARGUMENTS or ask:
"Em qual idioma deseja seguir? / Which language would you like to use? 1. Portugues (PT-BR) 2. English (EN)"
Save choice to `.planning/config.json` (merge, do not overwrite other fields).
All subsequent output follows the resolved language. Technical terms stay in English.

```bash
# Collect current state
cat .planning/state.md
cat .planning/phases/{active-phase-slug}/spec.md | head -80  # persona + objective + prohibitions
ls .planning/phases/{active-phase-slug}/plans/*-*.md 2>/dev/null
ls .planning/phases/{active-phase-slug}/execution/*-summary.md 2>/dev/null

# Check what changed since last execute
git log --oneline -10
git diff --name-only HEAD~5 2>/dev/null
```

Generate `.planning/phases/{active-phase-slug}/execution/executor-context.md`:

```markdown
# Executor Context — Phase [{phase-slug}]

> Generated on: [date]
> For: next pending task

## Current State
- Plan: [PP] of [total]
- Task: [TT] of [total]
- Last completed task: [ID] — [status]

## Persona (from spec.md)
[copy section 1 in full]

## Active Prohibitions (from spec.md)
[copy section 7 in full]

## Active Stop Conditions (from spec.md)
[copy section 6 in full]

## Recently Modified Files
[git diff --name-only from recent tasks]

## Decisions in Effect
[extract from decisions.md — only decisions relevant to the next task]

## Alerts
- [if there was a deviation in the last task]
- [if there is a pending fix plan]
- [if there is a blocked dependency]
```

## Prohibitions
- ❌ NEVER include full context/ or codebase data (only references)
- ❌ NEVER include history from previous tasks (only the last one)
- ❌ NEVER read .env or secrets
