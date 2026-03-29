---
name: backend
description: Create a backend-focused action plan — API endpoints, services, models, migrations, tests.
argument-hint: "[backend task description]"
---

# /pwdev-feat:backend — Create Backend Plan

## Agent
Assume the persona of `agents/agent-planner.md` (PWDEVIA).

## Input
$ARGUMENTS: backend task description (required).

## Plan Type
**Backend** — API endpoints, services, models, migrations, backend tests.

## Flow

1. Read context: CLAUDE.md + .planning/feat/codebase.md
2. Interpret the backend request
3. Ask clarifying questions if needed (max 2 rounds)
4. Apply the 7 fundamental questions with backend focus:
   - Persona: backend engineer (Laravel, Node, Django, etc.)
   - Quality: API contracts, validation, unit/integration tests
   - Prohibitions: no N+1 queries, no raw SQL without sanitization
5. Generate plan in `.planning/feat/plans/{NNN}-{slug}.md`
6. Present summary with next step: `/pwdev-feat:exec {NNN}`

## Prohibitions
- NEVER write code — only the plan
- NEVER skip database migration steps
- NEVER plan without considering validation and error handling
