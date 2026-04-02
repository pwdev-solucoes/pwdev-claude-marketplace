---
description: Create a full feature action plan using the PWDEVIA 7-question methodology. Covers backend + frontend + tests.
argument-hint: "[feature description]"
---

# /pwdev-feat:feat — Create Feature Plan

## Agent
Assume the persona of `agents/agent-planner.md` (PWDEVIA).

## Model Resolution
Read `.planning/config.json` for `model_profile` and `model_overrides`.
Resolution order: (1) `model_overrides[agent-name]` → (2) profile lookup → (3) agent frontmatter `model:` default.
Profiles — **performance**: opus for all except reviewer/scanner (sonnet). **balanced**: opus for orchestrator, sonnet for planner/executor/builder/interviewer/reviewer/researcher, haiku for scanner. **economy**: sonnet for most, haiku for reviewer/scanner.
When spawning the agent, pass the resolved model via the `model` parameter.

## Input
$ARGUMENTS: feature description (required).

## Plan Type
**Feature** — full scope: may include backend, frontend, tests, documentation.

## Flow

### STEP 0 — Language Selection
Read `.planning/config.json` for the `lang` field (`pt-BR` or `en`).
If set → use it silently. If not set → detect from $ARGUMENTS or ask:
"Em qual idioma deseja seguir? / Which language would you like to use? 1. Portugues (PT-BR) 2. English (EN)"
Save choice to `.planning/config.json` (merge, do not overwrite other fields).
All subsequent output follows the resolved language. Technical terms stay in English.

1. Read context: CLAUDE.md + .planning/feat/codebase.md
2. Interpret the feature request
3. Ask clarifying questions if needed (max 2 rounds)
4. Apply the 7 fundamental questions
5. Create feature directory and generate plan: `mkdir -p .planning/feat/features/{slug}` then write `.planning/feat/features/{slug}/plan.md`
6. Present summary with next step: `/pwdev-feat:exec {slug}`

## Prohibitions
- NEVER write code — only the plan
- NEVER skip any of the 7 questions
- NEVER create plans with more than 10 steps (split into multiple plans)
