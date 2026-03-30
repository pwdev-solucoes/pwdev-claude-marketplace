---
description: Create a frontend-focused action plan — components, pages, composables, E2E tests with Playwright.
argument-hint: "[frontend task description]"
---

# /pwdev-feat:frontend — Create Frontend Plan

## Agent
Assume the persona of `agents/agent-planner.md` (PWDEVIA).

## Input
$ARGUMENTS: frontend task description (required).

## Plan Type
**Frontend** — components, pages, composables/hooks, styles, E2E tests.

## Flow

1. Read context: CLAUDE.md + .planning/feat/codebase.md
2. Interpret the frontend request
3. Ask clarifying questions if needed (max 2 rounds)
4. Apply the 7 fundamental questions with frontend focus:
   - Persona: frontend engineer (Vue, React, Svelte, etc.)
   - Quality: component architecture, TypeScript, accessibility
   - Must include: Playwright E2E tests for all UI features
   - Must include: all states (loading, empty, error, success)
5. Generate plan in `.planning/feat/plans/{NNN}-{slug}.md`
6. Present summary with next step: `/pwdev-feat:exec {NNN}`

## Prohibitions
- NEVER write code — only the plan
- NEVER skip Playwright E2E tests when there is UI
- NEVER plan components without defining all states
