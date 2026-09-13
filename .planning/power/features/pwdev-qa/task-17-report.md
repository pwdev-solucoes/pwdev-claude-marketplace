# Task 17 — implementation report

Status: DONE
Task: F04-17 — Workflows init / strategy
Date: 2026-09-13

## Delivered

- Added portable `qa-init`, which confines inspection and context creation to the project root,
  refuses unsafe paths, exclusively creates only a missing `.planning/pwdev-qa/context.md`, and
  preserves existing context without overwrite.
- Added portable `qa-strategy`, which preserves target, contract, criterion IDs/text, approvals,
  and external state while producing risk, coverage, environment, data, entry/exit, limitation,
  authorization, verdict, and next-action records.
- Both workflows consult `qa-tooling` with exact probes, distinguish `available`, `missing`, and
  `unverified`, never install tools, and keep planned/stored commands inert.
- Both document the later inert export vector `qa_report.py report --manifest PATH --project-root
  PATH`; report export does not execute or re-run tests.
- Added thin Claude adapters that only load the shared skill, pass `$ARGUMENTS` and repository
  context, and return the shared result unchanged.

## TDD and verification evidence

- RED: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_qa_workflows` — 7 tests produced
  expected assertion failures because both workflow skills and both command adapters were absent.
- GREEN: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_qa_workflows` — 7 tests
  passed.
- The first full QA regression attempt with system Python 3.9 was an environment failure because
  `pdfplumber` was unavailable; it was not treated as approval.
- QA regression with the bundled dependency runtime: 149 tests passed across all
  `tests.test_qa_*` modules.
- `python3 -m compileall -q tests/test_qa_workflows.py` and `git diff --check` passed.

## Correction round 1

- Root cause: the exact output templates were designed from common workflow fields, while tests
  checked their shape but not lossless propagation from inputs through procedure to output. That
  omission allowed explicit objective to disappear from both workflows and authorization from
  `qa-init`.
- RED: the new end-to-end preservation test failed twice: `qa-init` lacked objective/authorization
  preservation and fields, while `qa-strategy` lacked an explicit objective input.
- GREEN: both skills now preserve `OBJECTIVE` and `AUTHORIZATION` explicitly; the focused suite
  passes 9 tests. Removing the correction made the regression test fail again, and restoring it
  returned the test to green.
- Added a portability guard that rejects `CLAUDE.md`, `AGENTS.md`, `${CLAUDE_PLUGIN_ROOT}`, and
  `$ARGUMENTS` in shared workflow bodies; the Claude-only tokens remain in thin wrappers.

## Limitations and safety

- These workflow contracts plan or observe; they do not execute product tests, evidence commands,
  report export, load, penetration testing, production access, or external effects.
- Runtime discovery/invocation smoke and the remaining eight workflows belong to later tasks.
- No ledger, review package, reference plugin, dependency, personal configuration, product code,
  report output, publication, push, or merge was modified or executed.

## Files

- `plugins/pwdev-qa/skills/qa-init/SKILL.md`
- `plugins/pwdev-qa/commands/init.md`
- `plugins/pwdev-qa/skills/qa-strategy/SKILL.md`
- `plugins/pwdev-qa/commands/strategy.md`
- `tests/test_qa_workflows.py`
- `.planning/power/features/pwdev-qa/task-17-report.md`
