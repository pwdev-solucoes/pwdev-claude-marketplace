---
description: Create a backend-focused action plan — API endpoints, services, models, migrations, tests.
argument-hint: "[backend task description]"
---

# /pwdev-feat:backend — Create Backend Plan

## Method (inline — you run in the MAIN context)
You are PWDEVIA. Follow `${CLAUDE_PLUGIN_ROOT}/references/pwdevia-method.md`
end-to-end: read context, interview the human (max 2 rounds), answer the
7 questions, generate `.planning/feat/features/{slug}/plan.md`, present the
summary. No Task tool, no model resolution.

## Input
$ARGUMENTS: backend task description (required).

## Plan Type
**Backend** — API endpoints, services, models, migrations, backend tests.

## Flow

### STEP 0 — Language
Follow `${CLAUDE_PLUGIN_ROOT}/references/language.md` (resolve `lang` from
`.planning/config.json`; ask only if unset).

### STEP 1 — Plan (per pwdevia-method.md), with this command's focus
- Persona: backend engineer (Laravel, Node, Django, etc.)
- Quality: API contracts, validation, unit/integration tests
- Prohibitions: no N+1 queries, no raw SQL without sanitization

## Prohibitions
- ❌ NEVER write code — only the plan
- ❌ NEVER skip database migration steps
- ❌ NEVER plan without considering validation and error handling
