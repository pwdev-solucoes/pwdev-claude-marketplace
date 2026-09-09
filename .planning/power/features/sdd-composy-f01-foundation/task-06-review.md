# Task 06 review — Structural validation

## Verdict

- SPEC: PASS
- QUALITY: PASS
- Findings: 0 critical, 0 important, 0 minor

## Assessment

The implementation satisfies Task 06 and the F01 global constraints. The focused
structural suite rejects unresolved TODO-style and mustache placeholders while
retaining the contractual angle-bracket examples, detects missing relative
Markdown targets, compares the normalized Claude Code and Codex manifest
versions, verifies both marketplace registrations, and rejects portable skills
without matching Claude command adapters. The placeholder, link, and orphan-skill
negative fixtures demonstrate that those checks fail on the intended defect.

The deferred Task 04 minor is resolved. Each core-schema rejection now starts
from a valid document and mutates one constraint at a time. Separate subtests
exercise the config actor and both exact roots, state stage, PRD slug, task ID and
state, each non-empty task collection, allowed paths, trace sequence, event ID,
actor, type, stage, and task ID. The fixtures therefore no longer pass merely
because a combined invalid document fails at an earlier property. The guarded
`skipped` justification coverage remains independently exercised.

The marketplace parser now includes the `sdd-*` namespace, so the registered
plugin is no longer silently omitted from root README coverage. The five
combined-suite failures are the already ruled baseline documentation omissions
for `sdd-composy`; they are not defects introduced by this task. The latent
`pwdev-power` inventory drift is likewise an approved baseline exception.

## Verification

- `python3 -m unittest tests.test_sdd_composy`: 21 tests passed.
- `python3 -m unittest tests.test_sdd_composy tests.test_marketplace_readmes`:
  29 tests ran with the five known root README baseline failures.
- `git diff --check 07cd072..c014c43`: passed.
- Inspected `review-07cd072..c014c43.diff`, the Task 06 brief and report, the
  F01 global constraints, and the deferred Task 04 ledger entry.
- No implementation files were changed during review.
