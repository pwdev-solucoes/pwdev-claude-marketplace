# Task 06 — implementation report

## Status

DONE_WITH_CONCERNS

## Implemented

- Added F01 Markdown checks that reject unresolved TODO-style and mustache placeholders while permitting contractual angle-bracket examples such as `<slug>` and `<name>`.
- Added relative Markdown-link validation plus isolated negative fixtures proving missing targets are rejected.
- Required the normalized Claude Code and Codex manifest versions to agree.
- Added skill/Claude-adapter registration validation plus an independently isolated orphan-skill fixture.
- Generalized root marketplace README parsing from `pwdev-*` to the marketplace's `pwdev-*` and `sdd-*` identifiers, so `sdd-composy` can no longer evade coverage checks.
- Replaced Task 04's combined invalid schema documents with one valid baseline and one independently invalid mutation per advertised actor, root, stage, identifier, collection-minimum, and path constraint.

## Verification

- `python3 -m unittest tests.test_sdd_composy`: **PASS**, 21 tests.
- `python3 -m unittest tests.test_sdd_composy tests.test_marketplace_readmes`: **EXPECTED BASELINE FAIL**, 29 tests run with 5 failures. Every reported failure is the pre-declared root README gap for `sdd-composy`: missing table row, section, install command, inventory line, and plugin documentation link. Root README files were outside Task 06's allowed paths and were not modified.
- The previously noted stale `pwdev-power` inventory claim remains outside this task's allowed paths; the inventory test stops at the earlier missing `sdd-composy` claim, so that latent baseline does not appear as an additional failure in this run.
- `git diff --check -- tests/test_sdd_composy.py tests/test_marketplace_readmes.py`: **PASS**.
- `PYTHONPYCACHEPREFIX=/tmp/sdd-composy-pycache python3 -m py_compile tests/test_sdd_composy.py tests/test_marketplace_readmes.py`: **PASS**.

## Scope

No F01 contract defect was exposed by the focused structural module, so no plugin implementation file changed. Changes are limited to the two test paths named by the brief and this required report. Pre-existing untracked task briefs and review packages were not modified.

## Concern

The combined command cannot be green until the separate root README documentation work adds `sdd-composy` and reconciles the stale `pwdev-power` inventory count. The broadened parser intentionally makes that existing drift visible rather than silently excluding the new plugin by prefix.
