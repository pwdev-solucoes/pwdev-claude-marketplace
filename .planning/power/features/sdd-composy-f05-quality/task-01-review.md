---
type: REVIEW_REPORT
okf_version: "0.2"
title: "F05 Task 01 execution contract review"
lifecycle:
  status: DRAFT
  human_approval: PENDING
sources:
  - .planning/power/features/sdd-composy-f05-quality/task-01-brief.md
  - .planning/power/features/sdd-composy-f05-quality/task-01-report.md
  - plugins/sdd-composy/references/execution.md
  - plugins/sdd-composy/skills/sdd-execute/SKILL.md
  - plugins/sdd-composy/skills/sdd-execute/agents/openai.yaml
  - plugins/sdd-composy/commands/execute.md
generated:
  by: codex-reviewer
  at: 2026-09-09T00:00:00Z
verified:
  - by: codex-reviewer
    at: 2026-09-09T00:00:00Z
    event: focused-tests
---

# Review verdict

**Disposition: CHANGES_REQUESTED**

The execution contract prose and routing files cover the requested policy at a
high level, and the focused suite currently passes (`Ran 5 tests` / `OK`). The
task is not ready for approval because the required contract tests are only
static substring checks; they do not exercise the failure and transition
behaviors named by the brief.

## Findings

### HIGH — required behavior is not tested

`tests/test_sdd_composy_quality.py` contains five text-presence tests only. It
does not provide failing-then-green behavioral tests for dependency preflight,
TDD RED evidence, allowed-path violations, real command failures/unavailable
commands, environment ownership and cleanup, sanitization, or guarded
transitions. A future implementation could remove or contradict those rules
while all five tests still pass. The report's RED check proves missing files,
not each required behavior.

Add deterministic tests (using small temporary fixtures and a fake command
runner where process execution is not under test) that assert at minimum:

- incomplete dependency blocks before execution;
- missing RED evidence blocks;
- changed paths outside `allowed_paths` are rejected;
- declared commands are represented with exit code, timestamps, stdout/stderr,
  and digests, with non-zero and unavailable classifications;
- environment ownership `unknown` blocks, owned services are cleaned, and
  user-owned processes are preserved;
- secret-like values are sanitized and evidence paths cannot escape their
  relative root; and
- success, blocker, and rejection outcomes record the expected guarded
  transition, reason, and next action.

The tests may target a small reference-level validator if that is the intended
implementation boundary, but they must assert observable behavior rather than
only checking that policy words occur in Markdown.

### MEDIUM — implementation boundary is underspecified

The skill says to "request" guarded transitions and "run" commands, but no
runtime contract, callable interface, or result schema is defined for the
executor. This can be acceptable for a portable policy skill, but then the
tests and reference should explicitly define the adapter boundary and the
required execution-result fields as a schema/fixture. Otherwise downstream
tasks cannot reliably consume `evidence_manifest`, cleanup status, or
transition outcomes.

## Positive observations

- `references/execution.md` explicitly covers dependency preflight, TDD, path
  confinement, real commands, ownership/cleanup, sanitization, SHA-256
  evidence, and `qa_required`/`blocked`/`rejected` outcomes.
- The OpenAI metadata is present and the Claude command is thin: it routes to
  `$sdd-execute` and does not duplicate execution logic or invoke Python.
- The skill forbids commits and exposure of credentials/private keys, and
  separates generation and verification actors in the audit contract.

## Verification performed

Command:

```text
python3 -m unittest tests.test_sdd_composy_quality
```

Result: `Ran 5 tests` / `OK`.

