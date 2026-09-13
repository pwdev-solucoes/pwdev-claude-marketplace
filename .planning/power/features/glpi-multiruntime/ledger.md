# Power ledger — plan: .planning/power/features/glpi-multiruntime/plan.md

Created: 2026-09-12

## Pre-flight

| Pair / task | Producer | Consumer | Verdict |
|---|---|---|---|
| Task 01 → Task 02 | Codex manifest + runtime assertions | Hermes adapter tests reuse same test module | clean |
| Task 02 → Task 03 | Hermes registration and setup contract | runtime-neutral skill/docs | clean |
| Task 03 → Task 04 | runtime docs and setup wording | version/catalog description | clean |
| Task 01 internal | 3 files, RED/GREEN, JSON + YAML contracts | self-consistent | clean |
| Task 02 internal | 3 files, clone/flattened bootstrap | self-consistent | clean |
| Task 03 internal | 5 files, skill/reference/docs/status | self-consistent | clean |
| Task 04 internal | 4 files, manifests/catalog/changelog | self-consistent | clean |

## Progress

- Baseline feature-specific adapter tests do not exist yet; global marketplace baseline has 7 known unrelated failures recorded in F09 verification.
- Task 01: complete (commits f8f324d..a4ad0cf, review clean after one fix round; 5 focused tests).
- Task 02: ready.
- Task 02: complete (commits a4ad0cf..b79526d, review SPEC PASS; 8 focused tests).
- Task 02: minor (deferred): test assumes Codex manifest exists and `CONTEXT_SPILL_LIMIT` is declared but unused; neither affects runtime registration in current scope.
- Task 03: complete (commits b79526d..6127b1c, review SPEC/QUALITY PASS; pytest unavailable in reviewer environment).
- Task 04: complete (commits f8f324d..15f9d63, review SPEC/QUALITY PASS; runtime tests 8/8, diff check pass).

## Rulings

- Ruling: execute this extension in the existing F09 marketplace worktree `codex/glpi-10-11-compat` to keep the already verified GLPI compatibility changes together. Cost if wrong: multi-runtime and GLPI changes share one eventual branch and review range.
- Ruling: Hermes MCP setup remains explicit via `hermes mcp add`; no user configuration files are read or written. Cost if wrong: Hermes requires one documented manual setup step.

## Verification

- Adversarial verdict: CAVEATS. All 7 acceptance criteria and 8 focused runtime tests passed; the marketplace suite retains 4 pre-existing README failures.
