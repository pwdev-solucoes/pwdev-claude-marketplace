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
- When STATE.md indicates the context may be stale
- When a new dev joins in the middle of a feature

## Procedure

```bash
# Collect current state
cat .planning/STATE.md
cat .planning/SPEC.md | head -80  # persona + objective + prohibitions
ls .planning/phases/*-PLAN.md 2>/dev/null
ls .planning/phases/*-SUMMARY.md 2>/dev/null

# Check what changed since last execute
git log --oneline -10
git diff --name-only HEAD~5 2>/dev/null
```

Generate `.planning/phases/{NN}-EXECUTOR-CONTEXT.md`:

```markdown
# Executor Context — Phase [NN]

> Generated on: [date]
> For: next pending task

## Current State
- Plan: [PP] of [total]
- Task: [TT] of [total]
- Last completed task: [ID] — [status]

## Persona (from SPEC.md)
[copy section 1 in full]

## Active Prohibitions (from SPEC.md)
[copy section 7 in full]

## Active Stop Conditions (from SPEC.md)
[copy section 6 in full]

## Recently Modified Files
[git diff --name-only from recent tasks]

## Decisions in Effect
[extract from CONTEXT.md — only decisions relevant to the next task]

## Alerts
- [if there was a deviation in the last task]
- [if there is a pending fix plan]
- [if there is a blocked dependency]
```

## Prohibitions
- ❌ NEVER include full research/ or codebase/ (only references)
- ❌ NEVER include history from previous tasks (only the last one)
- ❌ NEVER read .env or secrets
