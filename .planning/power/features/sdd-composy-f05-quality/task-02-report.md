---
type: QA_REPORT
okf_version: "0.2"
title: "F05 Task 02 execution report"
sources:
  - .planning/power/features/sdd-composy-f05-quality/task-02-brief.md
  - .planning/power/features/sdd-composy-f05-quality/task-01-report.md
generated:
  by: codex
  at: 2026-09-09T00:00:00Z
verified:
  - by: codex
    at: 2026-09-09T00:00:00Z
    event: focused-tests
lifecycle:
  status: DRAFT
  human_approval: PENDING
---

# F05 Task 02 — QA contract

Implemented the OKF v0.2 QA template, shared quality reference, portable
`sdd-qa` skill, OpenAI metadata, and behavioral contract tests. The contract
consumes a `qa_required` task plus CA/SC/test mappings and produces `qa.md`,
regression evidence, and a guarded `evidence_required` or `rejected` outcome.
It requires unit, integration, E2E, accessibility, responsiveness,
environment, cleanup, and evidence-inventory reporting, with explicit browser
capability and human-approval gates.

## Verification commands and output

RED before implementation:

`python3 -m unittest tests.test_sdd_composy_quality`

Result: `Ran 14 tests` with 4 expected `FileNotFoundError` failures for the
not-yet-created QA template, reference, skill, and metadata.

GREEN after implementation:

`python3 -m unittest tests.test_sdd_composy_quality`

Result: `Ran 14 tests in 0.002s` / `OK`.

Formatting:

`git diff --check`

Result: no output, exit 0.

No commit was created. Independent review and human approval remain required.

## Round 1 review fix

Added `plugins/sdd-composy/scripts/sdd_qa.py:assess`, a deterministic public
QA gate, plus behavioral tests covering CA→SC→test mapping, unit/integration/
E2E results, browser availability, accessibility, responsiveness, environment
readiness and cleanup ownership, evidence inventory hashing/path checks,
sanitized blockers, and `evidence_required`/`rejected` transitions.

`python3 -m unittest tests.test_sdd_composy_quality`

Result: `Ran 16 tests in 0.003s` / `OK`.

## Round 2 review fix

The QA helper now requires complete result records (command, environment, exit
code, and evidence), runtime/version metadata, regression evidence, run-owned
cleanup, known evidence types/results, existing confined files, sanitized
summaries, and verifiable SHA-256 digests. It also rejects duplicate or empty
coverage test IDs and returns a structural OKF QA report with separate
generation/verification actors, lifecycle status, explicit human approval, and
the guarded transition.

`python3 -m unittest tests.test_sdd_composy_quality -v`

Result: `Ran 17 tests in 0.006s` / `OK`.

## Round 3 review fix

`sdd_qa.assess` now optionally persists a complete deterministic `qa.md` with
OKF frontmatter and a reloadable structured body. The report includes title,
sources, provenance timestamps, generation and verification actors, explicit
approval event, lifecycle, blockers, next action, regression, environment and
cleanup, detailed unit/integration/E2E records, coverage, and evidence.

`python3 -m unittest tests.test_sdd_composy_quality -v`

Result: `Ran 18 tests in 0.004s` / `OK`.

## Round 4 review fix

Persistence now writes populated OKF frontmatter with generation and
verification provenance, lifecycle status and approval, transition, and title.
Writes are atomic within the destination directory and reject symlink report
paths. Rejected QA outcomes are also persisted with sanitized blocker, source,
next action, `REJECTED` lifecycle, and reload support.

`python3 -m unittest tests.test_sdd_composy_quality -v`

Result: `Ran 20 tests in 0.005s` / `OK`.

## Integrated review final fix

Rejected QA results now preserve sanitized, machine-readable origin context in
both the returned rejection payload and persisted OKF report: task identifier,
source/provenance, result identifier, and CA/story/result mappings when
available. Origin values are bounded to known fields and redact `token=`
content; persistence remains confined, atomic, and reload-validated.

Regression and fresh verification:

`python3 -m unittest tests.test_sdd_composy_quality.ExecutionContractTest.test_rejected_qa_persists_sanitized_origin_context -v`

Result: `Ran 1 test` / `OK`.

`python3 -m unittest discover -s tests -p 'test_sdd_composy*.py' -q`

Result: `Ran 161 tests` / `OK`.

`git diff --check`

Result: no output, exit 0.

## Round 5 final fix

The report writer now requires an explicit `allowed_root`, accepts only confined
relative report paths, rejects absolute escapes and symlinked parents, and uses
atomic same-directory replacement. Frontmatter serializes the complete OKF
schema with safely quoted titles and machine-readable values. `load_report`
parses and validates frontmatter against the structured body, including
lifecycle enums and all trace fields. Rejected reports preserve source,
coverage/results context, blocker reason, evidence, and next action.

`python3 -m unittest tests.test_sdd_composy_quality -v`

Result: `Ran 20 tests in 0.005s` / `OK`.
