---
description: Create a backend-focused action plan — API endpoints, services, models, migrations, tests.
argument-hint: "[backend task description]"
---

# /pwdev-feat:backend — Create Backend Plan

## Agent
Assume the persona of `agents/agent-planner.md` (PWDEVIA).

## Model Resolution
Read `.planning/config.json` for `model_profile` and `model_overrides`.
Resolution order: (1) `model_overrides[agent-name]` → (2) profile lookup → (3) agent frontmatter `model:` default.
Profiles — **performance**: opus for all except reviewer/scanner (sonnet). **balanced**: opus for orchestrator, sonnet for planner/executor/builder/interviewer/reviewer/researcher, haiku for scanner. **economy**: sonnet for most, haiku for reviewer/scanner.
When spawning the agent, pass the resolved model via the `model` parameter.

## Input
$ARGUMENTS: backend task description (required).

## Plan Type
**Backend** — API endpoints, services, models, migrations, backend tests.

## Flow

### STEP 0 — Language Selection
Read `.planning/config.json` for the `lang` field (`pt-BR` or `en`).
If set → use it silently. If not set → detect from $ARGUMENTS or ask:
"Em qual idioma deseja seguir? / Which language would you like to use? 1. Portugues (PT-BR) 2. English (EN)"
Save choice to `.planning/config.json` (merge, do not overwrite other fields).
All subsequent output follows the resolved language. Technical terms stay in English.

1. Read context: CLAUDE.md + .planning/feat/codebase.md
2. Interpret the backend request
3. Ask clarifying questions if needed (max 2 rounds)
4. Apply the 7 fundamental questions with backend focus:
   - Persona: backend engineer (Laravel, Node, Django, etc.)
   - Quality: API contracts, validation, unit/integration tests
   - Prohibitions: no N+1 queries, no raw SQL without sanitization
5. Create feature directory and generate plan: `mkdir -p .planning/feat/features/{slug}` then write `.planning/feat/features/{slug}/plan.md`
6. Present summary with next step: `/pwdev-feat:exec {slug}`

## Prohibitions
- NEVER write code — only the plan
- NEVER skip database migration steps
- NEVER plan without considering validation and error handling
