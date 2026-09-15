# SDD Composy quality contract

The `$sdd-qa` skill consumes a task in `qa_required` plus approved CA/SC/test
mappings and produces an OKF v0.2 `qa.md` report. It is portable: orchestration
may use any test runner or browser capability, but semantics and gates are
owned here.

## Required coverage

Every approved acceptance criterion (CA) must map to a story/scenario (SC) and
an executable test. Record separate unit, integration, and end-to-end (E2E)
results with command, environment, exit code, result, and evidence. E2E requires
an available browser capability; unavailable capability is a blocker, not a
pass. Record accessibility checks, responsive viewports, runtime environment,
regression results, and an evidence inventory.

Evidence inventory entries use confined relative paths, known evidence types,
SHA-256 (`sha256`) digests, sanitized summaries, and a result value. Never read or expose
secrets. Services started by a run are owned by that run and must be cleaned;
user-owned services must not be stopped.

## Gate semantics

The input state must be `qa_required`. A complete, human-approved report may
request `evidence_required`; no test or mapping may remain pending. Any missing
CA coverage, failed or unavailable unit/integration/E2E result, accessibility or
responsiveness failure, environment/cleanup failure, missing evidence, or
unresolved blocker yields `rejected` with a sanitized blocker, source, and next
action. Rejected QA cannot advance. human approval is explicit and is never
inferred from generated metadata, artifact existence, or agent confidence.

Reports identify generation actors separately from verification actors and use
the canonical document lifecycle values `DRAFT`, `APPROVED`, or `REJECTED` (QA,
code-review, and verdict reports share this vocabulary; the task itself moves between the
lowercase states in `states.md`). Store
regression evidence under the PRD bundle and preserve deterministic ordering.
