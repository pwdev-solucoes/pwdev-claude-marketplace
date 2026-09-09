---
type: QA_REPORT
okf_version: "0.2"
title: "F05 Task 04 review contract"
sources:
  - .planning/power/features/sdd-composy-f05-quality/task-04-brief.md
  - plugins/sdd-composy/templates/codereview.md
  - plugins/sdd-composy/skills/sdd-review/SKILL.md
  - plugins/sdd-composy/commands/review.md
  - tests/test_sdd_composy_quality.py
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

# F05 Task 04 — Review contract

Implemented the OKF v0.2 `CODE_REVIEW` template, portable `$sdd-review` skill,
OpenAI metadata, and thin Claude adapter. The contract consumes an explicit
base/target diff scope, approved contracts, task evidence, and project rules;
records severity, rule citations, commands and exit codes, skill conformity,
blockers, and a no-silent-fix check; and gates the task to `verify_required` or
`rejected`.

## Verification commands and output

RED before implementation:

`python3 -m unittest tests/test_sdd_composy_quality.py` — failed with four
missing-artifact errors.

Green after implementation:

`python3 -m unittest tests/test_sdd_composy_quality.py` — `Ran 24 tests` / `OK`.

`git diff --check` — passed.
