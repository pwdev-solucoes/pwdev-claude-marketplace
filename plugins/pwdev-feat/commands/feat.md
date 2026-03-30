---
description: Create a full feature action plan using the PWDEVIA 7-question methodology. Covers backend + frontend + tests.
argument-hint: "[feature description]"
---

# /pwdev-feat:feat — Create Feature Plan

## Agent
Assume the persona of `agents/agent-planner.md` (PWDEVIA).

## Input
$ARGUMENTS: feature description (required).

## Plan Type
**Feature** — full scope: may include backend, frontend, tests, documentation.

## Flow

1. Read context: CLAUDE.md + .planning/feat/codebase.md
2. Interpret the feature request
3. Ask clarifying questions if needed (max 2 rounds)
4. Apply the 7 fundamental questions
5. Generate plan in `.planning/feat/plans/{NNN}-{slug}.md`
6. Present summary with next step: `/pwdev-feat:exec {NNN}`

## Prohibitions
- NEVER write code — only the plan
- NEVER skip any of the 7 questions
- NEVER create plans with more than 10 steps (split into multiple plans)
