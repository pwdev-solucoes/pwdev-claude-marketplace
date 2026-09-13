# Task 05 report

Status: DONE
Source: `.planning/power/features/pwdev-qa/task-05-brief.md`; `.planning/power/features/pwdev-qa/spec.md`
Date: 2026-09-12

## Delivered

- Added `qa-specialist-web` with browser/viewport coverage, observable expectations, probe-based
  tool availability, global and local Playwright CLI detection, a task-owned `qa-report`
  session, fresh observed refs, and screenshot review before attachment. It keeps interactive
  exploration distinct from repeatable Playwright Test or repository suites.
- Added `qa-specialist-api` with separate contract, authentication, authorization, documented
  error, and idempotency coverage. Idempotency requires an observable absence of duplicate side
  effects; response equality alone is not accepted as proof.
- Added `qa-specialist-mobile` with distinct Android and iOS prerequisites, including host,
  SDK/toolchain, driver, build, and device/emulator/simulator probes. A missing device blocks the
  execution path and never becomes fabricated coverage.
- Tightened mobile readiness after review: separate positive probes are required for tool,
  compatible host, SDK/toolchain, platform connectivity (ADB on Android), driver, build, signing,
  device, and required service. Missing negative prerequisites are `BLOCKED`; absent or not-run
  probes are `unverified`; neither may become `READY`.
- Kept all three specialists advisory. They do not execute workflows or stored commands, grant
  authorization, install tools, correct product code, or infer observations from absent probes.

## Files changed

- `plugins/pwdev-qa/skills/qa-specialist-web/SKILL.md`
- `plugins/pwdev-qa/skills/qa-specialist-api/SKILL.md`
- `plugins/pwdev-qa/skills/qa-specialist-mobile/SKILL.md`
- `tests/test_qa_specialists.py`

## TDD evidence

- RED: `python3 -m unittest tests.test_qa_specialists` — 13 tests ran with 9 assertion failures
  because the three required specialist files were absent.
- GREEN: `python3 -m unittest tests.test_qa_specialists` — 13 tests passed.
- Regression: `python3 -m unittest tests.test_qa_specialists tests.test_qa_core
  tests.test_qa_tooling tests.test_qa_runtime_contracts` — 34 tests passed.
- Diff hygiene: `git diff --check` — passed with no output.

## Fix round 1 evidence

- Review RED: after adding host, build, signing, and ADB omission assertions,
  `python3 -m unittest tests.test_qa_specialists` — 14 tests ran with 3 failures because the
  existing mobile table did not expose the expanded probe columns.
- Fix GREEN: `python3 -m unittest tests.test_qa_specialists` — 14 tests passed.
- F01/F02 regression: `python3 -m unittest tests.test_qa_specialists tests.test_qa_core
  tests.test_qa_tooling tests.test_qa_runtime_contracts` — 35 tests passed.
- Regression-test proof: with only the mobile readiness fix temporarily reverted and the new
  tests preserved, `python3 -m unittest tests.test_qa_specialists` ran 14 tests and failed 3
  mobile tests because the reduced table could not satisfy the complete probe contract. The fix
  was restored immediately.
- Restored verification: 14 focused tests and all 35 F01/F02 regression tests passed again.
- Diff hygiene after restoration: `git diff --check` — passed with no output.

## Scenario coverage

The tests parse the specialist reference tables and validate their outputs deterministically.
They verify an available Web CLI path with isolated session, fresh snapshot, observed refs,
reviewed capture, and deterministic-suite owner; a missing CLI path with no invented execution;
complete API coverage plus a blocking missing authorization oracle; separate ready Android and
iOS prerequisite sets; a missing Android device that remains `BLOCKED`; and missing/not-run host,
build, signing, or ADB probes that remain `BLOCKED` or `unverified`, never `READY`. Structural
checks continue to enforce the shared sections, common references, and advisory safety boundary.

## Limitations

These tests validate deterministic contract tables and observable documented outputs. They do
not run Playwright, API requests, emulators, simulators, or devices and do not claim real-agent
runtime evaluation; that remains assigned to F05-24. No absent tool was installed or treated as
executed. No capture was produced or attached.
