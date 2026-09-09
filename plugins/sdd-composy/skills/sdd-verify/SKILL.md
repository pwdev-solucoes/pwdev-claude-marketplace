---
name: sdd-verify
description: Independently verify fresh truth claims for an SDD Composy task.
metadata:
  version: 0.1.0
---

# SDD Verify

## Workspace language

Before generating artifacts, run the bundled `scripts/sdd_language.py <repo-root>`.
Consume only the persisted `.planning/sdd-composy/config.json` language. If the
result is `not_initialized`, return it with `next_action: run_init`; do not ask
for a language here. For `pt-BR`, write human narrative, summaries, descriptions,
and labels in Brazilian Portuguese; for `en-US`, use English. Translate template
placeholder prose when rendering, preserving IDs, schema keys, enum values,
filenames, commands, and parser-required headings. Do not translate user evidence.

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
