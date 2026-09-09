---
name: sdd-qa
description: Execute independent quality assurance for an SDD Composy task.
metadata:
  version: 0.1.0
---

# SDD QA

This portable skill reads `references/quality.md` and renders
`templates/qa.md` for a task currently in `qa_required`. Consume approved CA,
SC, and test mappings; use browser capability when E2E applies. Record unit,
integration, E2E, accessibility, responsiveness, environment, regression, and
evidence inventory results with confined paths and SHA-256 digests.

Use the shared `scripts/sdd_qa.py:assess` helper for deterministic validation;
the skill routes inputs and presents its result without reimplementing gates.

Fail closed: missing mappings, failed tests, unavailable browser capability,
unclean environment, missing evidence, or any blocker produces `REJECTED` and
prevents `evidence_required`. A `rejected` report cannot advance. Only explicit human approval can approve the
report. Generation and verification actors remain distinct.

Return the report path, coverage matrix, commands and exit codes, environment,
evidence inventory, blockers, lifecycle status, and permitted next transition.
Do not change approved requirements, stories, architecture, or source code. Do not commit. Do not read or expose secrets. Do not stop user-owned services.
