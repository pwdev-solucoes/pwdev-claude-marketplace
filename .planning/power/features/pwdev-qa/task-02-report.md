# Task 02 report

Status: DONE

## Delivered

- Added the installed `qa-tooling` skill contract with the exact
  `tool/purpose/availability/evidence/prerequisites/alternative/reason` output.
- Added deterministic recommendations that separate exploratory `playwright-cli` from
  repeatable/CI Playwright Test, retain `missing` without installation, and select a
  platform-compatible Android mobile option.
- Added a broader QA surface catalog and a current-claim ledger. Compatibility claims
  cite official publisher documentation checked on 2026-09-12; unverified version,
  cost, and license claims remain explicitly `unverified`.

## TDD evidence

- RED: `python3 -m unittest tests.test_qa_tooling` — 5 failures because
  `qa-tooling/SKILL.md` and `references/tooling.md` did not exist.
- GREEN: `python3 -m unittest tests.test_qa_tooling` — 5 tests passed.
- Regression: `python3 -m unittest tests.test_qa_tooling tests.test_qa_core` — 14 tests
  passed.
- Contract check: `git diff --check` — passed.

### Fix round 1

- RED: expanded focused suite — 6 failures against the previous catalog/probe schema
  and divergent local fallback.
- GREEN: expanded focused suite — 7 tests passed.
- Regression reversions: each restored defect failed its focused scenario before the
  fix was reapplied: absent probe became false `missing`; Appium source/date was absent
  from the final seven-field row; divergent `npx --no-install playwright-cli --version`
  replaced the documented fallback.
- Final regression: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest
  tests.test_qa_tooling tests.test_qa_core` — 16 tests passed.

## Official sources verified

- playwright-cli requirements and interactive/session behavior:
  https://github.com/microsoft/playwright-cli (checked 2026-09-12).
- Playwright Test CI use: https://playwright.dev/docs/ci (checked 2026-09-12).
- Appium platform-driver mapping:
  https://appium.io/docs/en/latest/intro/drivers/ (checked 2026-09-12).

## Limitations

- The tests evaluate deterministic catalog behavior and do not claim that any external
  executable, browser, device, SDK, credential, service, version, cost, or license was
  verified in the local environment.
- No tool was installed or executed, and no external state or personal configuration
  was changed.
- Availability now requires explicit `state/result/evidence` probes: the tool and all
  purpose-specific prerequisites must be positive for `available`; only an explicit
  negative tool probe yields `missing`; absent or incomplete probes yield `unverified`.
