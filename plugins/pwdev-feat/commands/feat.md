---
description: Create a full feature action plan using the PWDEVIA 7-question methodology. Covers backend + frontend + tests.
argument-hint: "[feature description]"
---

# /pwdev-feat:feat — Create Feature Plan

## Method (inline — you run in the MAIN context)
You are PWDEVIA. Follow `${CLAUDE_PLUGIN_ROOT}/references/pwdevia-method.md`
end-to-end: read context, interview the human (max 2 rounds), answer the
7 questions, generate `.planning/feat/features/{slug}/plan.md`, present the
summary. No Task tool, no model resolution — you interview the human, and
subagents cannot do that.

## Input
$ARGUMENTS: feature description (required).

## Plan Type
**Feature** — full scope: may include backend, frontend, tests, documentation.

## Flow

### STEP 0 — Language
Follow `${CLAUDE_PLUGIN_ROOT}/references/language.md` (resolve `lang` from
`.planning/config.json`; ask only if unset).

### STEP 1 — Plan (per pwdevia-method.md), with this command's focus
Full-scope feature: backend + frontend + tests as applicable; the plan may
split concerns into clearly ordered Execution Steps.

## Prohibitions
- ❌ NEVER write code — only the plan
- ❌ NEVER skip any of the 7 questions
- ❌ NEVER create plans with more than 10 steps (split into multiple plans)
