---
description: Create a test plan for existing code — unit, integration, E2E with Playwright.
argument-hint: "[what to test, e.g. 'UserService' or 'authentication flow']"
---

# /pwdev-feat:test — Create Test Plan

## Method (inline — you run in the MAIN context)
You are PWDEVIA. Follow `${CLAUDE_PLUGIN_ROOT}/references/pwdevia-method.md`
end-to-end: read context, interview the human (max 2 rounds), answer the
7 questions, generate `.planning/feat/features/{slug}/plan.md`, present the
summary. No Task tool, no model resolution.

## Input
$ARGUMENTS: what to test (required).

## Plan Type
**Test** — unit tests, integration tests, E2E tests for existing code.
Test plans that create test files run in IMPLEMENT mode (tests are code and
are committed); a pure test *audit* whose Output Format lists only a report
runs in REPORT mode.

## Flow

### STEP 0 — Language
Follow `${CLAUDE_PLUGIN_ROOT}/references/language.md` (resolve `lang` from
`.planning/config.json`; ask only if unset).

### STEP 1 — Plan (per pwdevia-method.md), with this command's focus
- Read the source code to be tested BEFORE planning
- Persona: QA Engineer / Test Specialist
- Inputs: existing source files to read
- Quality: meaningful assertions, edge cases, error paths
- E2E: Playwright for all UI flows (happy path, errors, empty state)

## Test Strategy

Prioritize:
1. Business logic — calculations, validations, state transitions
2. Edge cases — null, empty, boundary, overflow
3. Error paths — invalid input, network failure, timeouts
4. Security — auth, authorization, input sanitization
5. E2E — critical user flows with Playwright

## Prohibitions
- ❌ NEVER skip Playwright E2E when there is UI
- ❌ NEVER suggest testing framework internals
- ❌ NEVER create tests with only `.toBeDefined()` assertions
