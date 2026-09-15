---
type: VERIFICATION_VERDICT
okf_version: "0.2"
title: "{{PRODUCT_NAME}} verification verdict"
sources:
  - resource: "tasks/prd-{{SLUG}}/tasks.md"
  - resource: "tasks/prd-{{SLUG}}/qa-{{TASK_ID}}.md"
  - resource: "tasks/prd-{{SLUG}}/codereview-{{TASK_ID}}.md"
generated:
  by: "{{GENERATION_ACTOR}}"
  at: "{{GENERATED_AT}}"
verified: []
lifecycle:
  status: DRAFT
human_approval: PENDING
transition: verify_required
verdict: PENDING
---

# {{PRODUCT_NAME}} — Verification verdict

Verification consumes a `verify_required` task and independently reproduces
each claimed truth with a fresh command. Artifact existence, prior summaries,
and another worker's evidence are not proof.

## truth table

| Claim ID | Claim | Fresh command | Environment | Exit code | Evidence | SHA-256 | Verdict |
|---|---|---|---|---:|---|---|---|
| TR-001 | {{CLAIM}} | `{{COMMAND}}` | {{ENVIRONMENT}} | {{EXIT_CODE}} | `{{EVIDENCE_PATH}}` | `{{SHA256}}` | NOT_RUN |

Each row must be independently reproducible and use a confined relative
evidence path, with an exit code recorded and sha256 digest. A fresh run must refute a prior claim when its output disagrees.
Use only these verdict values: `PASS`, `FAIL`, `STALE`, `ENVIRONMENT_FAILURE`,
and `NOT_RUN`.

## Gate

Set `lifecycle.status: APPROVED`, `human_approval: APPROVED`, and append a
verification actor event only when every required claim is `PASS`, evidence is
fresh and hash-consistent, QA and review are non-blocking, and traceability is
consistent. The permitted transition is `complete`.
Per-claim verdict values stay within the list above; `complete` (the `COMPLETE` workflow stage) is the resulting task state, not a verdict value.

Any `FAIL`, `STALE`, `ENVIRONMENT_FAILURE`, or `NOT_RUN` value sets
`lifecycle.status: REJECTED`, records a sanitized blocker and next action, and
prevents `complete`. Environment failures are not test failures; classify them
explicitly and rerun in a known environment.
