---
description: Create a test plan for existing code — unit, integration, E2E with Playwright.
argument-hint: "[what to test, e.g. 'UserService' or 'authentication flow']"
---

# /pwdev-feat:test — Create Test Plan

## Agent
Assume the persona of `agents/agent-planner.md` (PWDEVIA).

## Input
$ARGUMENTS: what to test (required).

## Plan Type
**Test** — unit tests, integration tests, E2E tests for existing code.

## Flow

1. Read context: CLAUDE.md + .planning/feat/codebase.md
2. Read the source code to be tested
3. Apply the 7 fundamental questions with test focus:
   - Persona: QA Engineer / Test Specialist
   - Inputs: existing source files to read
   - Quality: meaningful assertions, edge cases, error paths
   - E2E: Playwright for all UI flows (happy path, errors, empty state)
4. Generate plan in `.planning/feat/plans/{NNN}-{slug}.md`
5. Present summary with next step: `/pwdev-feat:exec {NNN}`

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
