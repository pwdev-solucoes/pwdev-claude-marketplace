---
name: sdd-verify
description: Independently verify fresh truth claims for an SDD Composy task.
metadata:
  version: 0.1.0
---

# SDD Verify

This portable skill reads `references/verification.md` and renders
`templates/verdict.md` for a task in `verify_required`. independently reproduce
every required claim with a fresh command, build the truth table, and attempt
to refute earlier evidence. Record confined evidence paths, SHA-256 digests,
exit codes, environment, and separate generation and verification actors.

Use only `PASS`, `FAIL`, `STALE`, `ENVIRONMENT_FAILURE`, and `NOT_RUN` verdicts.
Classify an environment failure separately from a failed test. Reject stale,
contradictory, missing, or hash-inconsistent evidence. Only all fresh PASS
claims with non-blocking QA/review and explicit human approval can request
`COMPLETE`; all other outcomes request `REJECTED` with a sanitized blocker and
next action. Do not silently change claims, contracts, or source.

Do not commit. Do not read or expose secrets. Do not stop user-owned services.
