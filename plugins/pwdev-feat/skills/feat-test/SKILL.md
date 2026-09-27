---
name: feat-test
description: >
  Use when the user wants tests planned for existing code or a test audit — unit, integration,
  E2E scenarios exportable to Playwright, playwright-cli UI checks, a coverage matrix —
  'criar testes para o UserService', 'plano de testes E2E do login', 'auditar a cobertura'.
  Writes .planning/feat/features/{slug}/plan.md. Do NOT use for code review (feat-review), for
  implementing features (feat-feature) or to run an existing plan (feat-exec).
metadata:
  version: 3.2.1
---

# Test plan

Plan type **test**. You run in the MAIN session and interview the human. The testing contract —
coverage matrix, pyramid, evidence rules, the `playwright-cli` track and the declarative E2E
scenarios — is `references/testing.md`; read it before planning.

## Procedure

1. **Language** — resolve `lang` (`references/language.md`).
2. **Read the code under test first**, plus `context/testing.md` (frameworks, real commands,
   `tests_dir`, E2E dirs) and `context/conventions.md`. No testing context → suggest
   `feat-map`.
3. **Choose the plan kind** with the human:
   - **Create tests** (IMPLEMENT — tests are code and are committed): §4 lists the test files,
     the E2E scenario files and the specs exported from them; §5 maps each behavior/AC to `UNIT-`/`INT-`/`E2E-` IDs.
   - **Audit coverage** (REPORT): §4 lists only
     `.planning/feat/features/{slug}/test-audit.md`, rendered from `templates/test-report.md`
     (not `report.md`: some runtimes refuse subagent writes to report-like names).
4. **Method** — follow `references/pwdevia-method.md` with `plan_type: test`.
5. **Focus**
   - Persona: QA engineer / test specialist on the project's frameworks.
   - Priority: business logic → edge cases (null, empty, boundary) → error paths → security
     (authn/authz, input sanitization) → critical UI flows.
   - Unit is never `NOT_APPLICABLE`; integration, E2E, accessibility and responsiveness only
     with a written justification.
   - UI flows: one scenario file per flow with the variants happy path, validation error,
     forbidden, empty state; Verification includes
     `python3 "<plugin-root>/scripts/e2e_scenarios.py" validate <scenarios-dir> --plan <plan.md>`
     and the `export --to playwright` command into `<tests-dir>/e2e/generated`.
   - Interactive UI checks use `playwright-cli` in the session `feat-{slug}`, run from the
     feature's `evidence/` directory, with one screenshot per UI criterion.

## Prohibitions

- Never skip E2E scenarios when the code under test has UI.
- Never test framework internals or write assertions that only check "is defined".
- Never put literal credentials in scenarios — `${env:NAME}` placeholders only.

Language: resolve `lang` per `references/language.md` before any human-facing output. Safety: never read or expose `.env*` (except `.env.example`/`.template`/`.sample`), keys, certificates or credentials — `references/safety.md`. Paths `references/`, `scripts/`, `templates/`, `schemas/` are relative to the plugin root (`references/runtime.md`).
