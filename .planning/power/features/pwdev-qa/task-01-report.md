# Task 01 — implementation report

## Status

DONE

## Scope delivered

- Added the `qa` router with explicit-intent-first selection, then surface and risk.
- Added guarded `qa-*` routing: a candidate is returned only when its `SKILL.md` is an existing
  regular file; unavailable routes are explicit errors.
- Added shared result and verdict rules, including `BLOCKED` for missing or zero applicable
  criteria and read-only boundaries for `qa-review` and `qa-status`.
- Added authorization and evidence-safety contracts, including confinement, hashes,
  sanitization, limits, and publication boundaries.
- Added focused behavioral tests for CA-001, CA-004, CA-014, and CA-015.

## Files changed

- `plugins/pwdev-qa/skills/qa/SKILL.md`
- `plugins/pwdev-qa/references/workflow.md`
- `plugins/pwdev-qa/references/safety.md`
- `plugins/pwdev-qa/references/artifacts.md`
- `tests/test_qa_core.py`

## TDD evidence

- RED: `python3 -m unittest tests.test_qa_core` — 8 tests ran and failed with 8 assertion
  failures because the required router and reference contracts did not exist.
- First GREEN attempt: 8 tests ran with 1 assertion failure because the exact result vocabulary
  was split across lines; the production contract was normalized to the required literal list.
- GREEN: `python3 -m unittest tests.test_qa_core` — 8 tests ran, all passed.
- Fresh verification after review: `python3 -m unittest tests.test_qa_core` — 8 tests ran, all
  passed.
- Scope/format check: `git diff --cached --check` passed before commit; the staged diff contained
  exactly the five task files.

## Limitations

Only the router and common contracts exist at this task boundary. The router documents all
candidate names but refuses candidates whose skill file is not installed, so later workflow
tasks can add routes without this task claiming nonexistent capabilities. Full inventory closure
remains assigned to F05.

The deterministic fixtures in this task interpret the Markdown contracts and exercise their
filesystem semantics. They do not replace the real-runtime model evaluation assigned to F05.

## Fix round 1

- Required an explicit diagnostic whenever sanitization is `pending`, in addition to blocking
  attachment copying and `PASS`.
- Replaced the routing, missing-criteria, and read-only word-presence checks with deterministic
  scenario fixtures. The fixtures parse the routing/workflow tables; prefer explicit review over
  conflicting surface/risk hints; resolve a regular installed skill; reject missing, directory,
  and symlink targets; evaluate missing/zero-applicable criteria as `BLOCKED`; and verify that
  review/status leave temporary state bytes unchanged.
- Sanitization regression RED: the focused assertion failed against the original contract;
  GREEN after the fix; deliberate revert failed again; restored fix passed.
- Behavioral regression RED: review/status fixture failed because the original workflow table
  had no machine-readable operation mode; GREEN after adding the mode; deliberate revert failed
  again; restored fix passed.
- Fresh focused suite: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_qa_core` — 9
  tests ran, all passed.
- Correction scope check: `git diff --cached --check` passed; the correction commit contains
  only three of the five authorized task files.

## Commit

`5294a06..5b24fc6` — `feat(pwdev-qa): add router and core contracts`

`5b24fc6..6f9fe9a` — `test(pwdev-qa): exercise router scenarios`
