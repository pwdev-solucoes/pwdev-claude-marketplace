# Task 03 — Artifact routing and final validation report

## Result

Implemented and documented the bilingual artifact-routing contract. The workflow
and both plugin READMEs now state that init is the only prompt boundary, that the
persisted language is consumed by downstream skills, and that human-facing
Markdown follows `pt-BR` or `en-US` while machine contracts remain stable.

## Contract covered

- `/sdd-composy:init` accepts `pt-BR` or `en-US` and asks only when omitted.
- Init without a choice creates no artifacts; downstream stages never prompt.
- Pre-init consumers return `not_initialized` with `next_action: run_init`.
- Human-facing PRDs, stories, TechSpecs, tasks, QA/evidence and status prose are localized.
- Machine keys, IDs, schemas, filenames, lifecycle values and command names stay English.
- Invalid language values fail without mutating persisted configuration.
- Claude Code and Codex retain the same portable workflow meaning.

## Verification

```text
python3 -m unittest tests.test_sdd_composy_language tests.test_sdd_composy
Ran 68 tests ...
OK

python3 -m unittest discover -s tests -p 'test_sdd_composy*.py'
Ran 279 tests in 13.199s
OK
```

`git diff --check` passed.

No commit was created.
