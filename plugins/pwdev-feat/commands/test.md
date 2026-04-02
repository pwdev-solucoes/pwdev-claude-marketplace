---
description: Create a test plan for existing code — unit, integration, E2E with Playwright.
argument-hint: "[what to test, e.g. 'UserService' or 'authentication flow']"
---

# /pwdev-feat:test — Create Test Plan

## Agent
Assume the persona of `agents/agent-planner.md` (PWDEVIA).

## Model Resolution
Read `.planning/config.json` for `model_profile` and `model_overrides`.
Resolution order: (1) `model_overrides[agent-name]` → (2) profile lookup → (3) agent frontmatter `model:` default.
Profiles — **performance**: opus for all except reviewer/scanner (sonnet). **balanced**: opus for orchestrator, sonnet for planner/executor/builder/interviewer/reviewer/researcher, haiku for scanner. **economy**: sonnet for most, haiku for reviewer/scanner.
When spawning the agent, pass the resolved model via the `model` parameter.

## Input
$ARGUMENTS: what to test (required).

## Plan Type
**Test** — unit tests, integration tests, E2E tests for existing code.

## Flow

### STEP 0 — Language Selection
Read `.planning/config.json` for the `lang` field (`pt-BR` or `en`).
If set → use it silently. If not set → detect from $ARGUMENTS or ask:
"Em qual idioma deseja seguir? / Which language would you like to use? 1. Portugues (PT-BR) 2. English (EN)"
Save choice to `.planning/config.json` (merge, do not overwrite other fields).
All subsequent output follows the resolved language. Technical terms stay in English.

1. Read context: CLAUDE.md + .planning/feat/codebase.md
2. Read the source code to be tested
3. Apply the 7 fundamental questions with test focus:
   - Persona: QA Engineer / Test Specialist
   - Inputs: existing source files to read
   - Quality: meaningful assertions, edge cases, error paths
   - E2E: Playwright for all UI flows (happy path, errors, empty state)
4. Create feature directory and generate plan: `mkdir -p .planning/feat/features/{slug}` then write `.planning/feat/features/{slug}/plan.md`
5. Present summary with next step: `/pwdev-feat:exec {slug}`

## Test Strategy

Prioritize:
1. Business logic — calculations, validations, state transitions
2. Edge cases — null, empty, boundary, overflow
3. Error paths — invalid input, network failure, timeouts
4. Security — auth, authorization, input sanitization
5. E2E — critical user flows with Playwright

## Prohibitions
- NEVER skip Playwright E2E when there is UI
- NEVER suggest testing framework internals
- NEVER create tests with only `.toBeDefined()` assertions
