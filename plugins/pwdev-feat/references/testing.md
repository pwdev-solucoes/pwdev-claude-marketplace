# Testing contract (feat-test, and the test section of feature/backend/frontend plans)

## Coverage matrix

Every `AC-*` in §5 and every business rule in §3 maps to at least one test ID:

| Prefix | Level | Notes |
|---|---|---|
| `UNIT-nnn` | unit — business logic, validation, state transitions, edge cases | never `NOT_APPLICABLE` |
| `INT-nnn` | integration — API, database, service boundaries | `NOT_APPLICABLE` only with a written justification |
| `E2E-nnn` | end-to-end UI flow | required when the change has UI; otherwise `NOT_APPLICABLE` with justification |
| `A11Y-nnn` / `RESP-nnn` | accessibility / responsiveness checks | UI only; `NOT_APPLICABLE` with justification |

Pyramid: many unit, moderate integration, few E2E (critical flows only). Prioritize business
logic → edge cases (null, empty, boundary) → error paths → security (authn/authz, input
sanitization) → critical UI flows. Assertions must be meaningful: never tests whose only
assertion is "is defined".

## Evidence

A result is `PASS`, `FAIL`, `NOT_RUN` or `NOT_APPLICABLE`, and each `PASS`/`FAIL` carries the
exact command, environment, exit code and an evidence path or excerpt. Unavailable tooling is
`NOT_RUN` with the probe that showed it; it never becomes `PASS`, and nothing is installed
automatically.

## UI — two complementary tracks

### 1. Interactive verification with `playwright-cli` (default for UI)

Used by the executor to verify UI criteria against the running app, and by `feat-test` audits.

- Probe first: `command -v playwright-cli`. Missing → `NOT_RUN`, record the alternative (the
  project's Playwright Test suite, or manual check by the human).
- Run every command from the evidence directory `.planning/feat/features/{slug}/evidence/`
  (`(cd <evidence-dir> && playwright-cli -s=feat-{slug} ...)`): `playwright-cli` writes its
  working files (`.playwright-cli/`, snapshots, console logs) to the current directory, and they
  must never end up in the project tree.
- Use a task-owned session: `playwright-cli -s=feat-{slug} open <baseURL>`; every later command
  carries the same `-s=feat-{slug}`. Never reuse a personal profile, never export cookies or
  storage.
- Take a fresh `snapshot` before acting on element refs; refs from an older snapshot are stale.
- Walk the variants the plan lists (happy path, validation error, forbidden access, empty
  state). **Every UI AC gets a screenshot**: `screenshot --filename=<AC-id>-<variant>.png`
  (relative to the evidence directory), cited in the AC's evidence cell with the observed state.
- Close only your own session: `playwright-cli -s=feat-{slug} close`.
- A snapshot is text evidence of structure, not proof of pixels; the screenshot is the visual
  evidence.

### 2. Declarative E2E scenarios (for any QA to run later)

Scenarios are data, validated by `schemas/e2e-scenario.schema.json`, and live in the project's
test directory — `<tests-dir>/e2e/scenarios/<E2E-id>-<kebab-title>.scenario.json` — next to their
exported spec `<tests-dir>/e2e/generated/<same base name>.spec.ts`. `<tests-dir>`
comes from `.planning/feat/context/testing.md` (default `tests`). Both the scenario and its exported spec are listed in the plan's Output Format and committed
with the feature; the plan's Verification carries the `validate` and `export` commands
(`plan_lint.py` enforces all three).

Required content per scenario: `schema_version`, `id` (`E2E-nnn`), `title`, `feature_slug`,
`ac_refs`, `priority` (`P0`–`P3`), `preconditions` (with `base_url_env`; users as
`{ "role": ..., "credentials_env": {...} }` placeholders — never literal secrets), optional
`data`, `steps`, `assertions`, and `variants` (at least `happy_path`; with UI forms also
`validation_error`, `forbidden`, `empty_state` or a justification in `not_applicable`).

Locators, in order of preference: `role` (+ `name`), `label`, `placeholder`, `text`, `testid`,
`css` (last resort).

Tooling (`scripts/e2e_scenarios.py`, stdlib only):

```sh
python3 <plugin-root>/scripts/e2e_scenarios.py validate <scenarios-dir> [--plan <plan.md>]
python3 <plugin-root>/scripts/e2e_scenarios.py export --to playwright <scenarios-dir> --out <tests-dir>/e2e/generated
python3 <plugin-root>/scripts/e2e_scenarios.py coverage <plan.md> <scenarios-dir>
```

`export` writes one Playwright Test `*.spec.ts` per scenario (one `test` per variant, annotated
with the E2E id and ACs, `baseURL` and credentials read from environment variables) under a
"generated — do not edit" header. The generated specs open in any Playwright surface — the test
runner, UI mode, the VS Code extension or a desktop runner. The plugin generates, validates and
exports; formal execution belongs to QA unless the plan's Verification lists the run command.
