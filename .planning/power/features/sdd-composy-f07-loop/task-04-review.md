# F07 Task 04 — Review

## Disposition

APPROVED

## Verification

`python3 -m unittest tests.test_sdd_composy_loop -v` — 21 tests passed.

`git diff --check` — passed.

## Findings

- Codex and Claude Code use separate, fixed command-vector builders; provider-only
  flags are not cross-routed.
- Both adapters pin execution to the registered repository root and pass only the
  minimal deterministic environment (`PATH`, `LC_ALL`, `LANG`); ambient environment
  variables are not forwarded.
- The result contract is strict: exact top-level keys, enumerated status/verdict,
  non-empty stage/message, and object evidence. The JSON Schema independently has
  `additionalProperties: false` and the same required fields/enums.
- Non-zero exit, timeout, malformed JSON, and schema-invalid output fail closed with
  deterministic adapter errors; no result is accepted or persisted on failure.
- Stage payloads are canonical JSON and the adapters do not record stdout, stderr,
  secrets, model metadata, or private-path diagnostics. The repository root is used
  only as the execution boundary (`cwd`/provider directory flag), not as result data.
- No mutation or symlink traversal was introduced by these runtime adapters; the
  loop engine's existing root safety test remains green.

No blocking findings.
