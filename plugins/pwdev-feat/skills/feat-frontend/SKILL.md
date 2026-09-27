---
name: feat-frontend
description: >
  Use when the user wants a UI-only action plan — components, pages, composables/hooks, state,
  forms and their E2E coverage — 'plano de frontend para a tela X', 'plan the settings page'.
  Writes .planning/feat/features/{slug}/plan.md with E2E scenarios and playwright-cli checks.
  Do NOT use for API/database work (feat-backend), full features (feat-feature), writing code
  (feat-exec) or UI review (feat-review).
metadata:
  version: 3.2.1
---

# Frontend plan

Plan type **frontend** (`**UI:** yes`). You run in the MAIN session and interview the human.

## Procedure

1. **Language** — resolve `lang` (`references/language.md`).
2. **Method** — follow `references/pwdevia-method.md` with `plan_type: frontend`; context
   documents: architecture, conventions, testing.
3. **Focus for this type**
   - Persona: frontend engineer on the project's real UI stack and component library.
   - §3: screens, states (loading, empty, error, success), API contracts consumed, validation
     rules, permissions.
   - §4 includes the E2E scenario files (`<tests-dir>/e2e/scenarios/E2E-nnn-*.scenario.json`) and their exported specs
     (`<tests-dir>/e2e/generated/E2E-nnn-*.spec.ts`)
     covering happy path, validation error, forbidden access and empty state — or a
     justification in `not_applicable` (`references/testing.md`).
   - §5: component tests for logic, `playwright-cli` checks for each variant, accessibility
     (labels, keyboard, focus) and responsiveness criteria.
   - Reuse existing components and tokens found in `context/conventions.md`.

## Prohibitions

- Never write code — only the plan.
- Never plan UI without E2E scenarios (or an explicit justification).
- Never introduce a component library or styling approach outside the project's stack.

Language: resolve `lang` per `references/language.md` before any human-facing output. Safety: never read or expose `.env*` (except `.env.example`/`.template`/`.sample`), keys, certificates or credentials — `references/safety.md`. Paths `references/`, `scripts/`, `templates/`, `schemas/` are relative to the plugin root (`references/runtime.md`).
