---
type: QUICK_REPORT
okf_version: "0.2"
sources:
  - resource: "{{CONTRACT_RESOURCE}}"
generated:
  by: "{{ACTOR_ID}}"
  at: "{{GENERATED_AT}}"
lifecycle:
  status: DRAFT
human_approval: PENDING
verified: []
quick:
  id: "Q-{{SEQUENCE}}"
  task_id: "TASK-{{TASK_SEQUENCE}}"
  verdict: PENDING
---

# Quick report — {{TITLE}}

This report belongs to the `sdd-composy` bundle.

## Contract

- Contract: [quick-contract.md](quick-contract.md)
- Q-ID: `Q-{{SEQUENCE}}`
- Normal task: `TASK-{{TASK_SEQUENCE}}`

## Evidence

| Gate | Result | Evidence |
|---|---|---|
| Failing test observed first | {{TDD_RESULT}} | {{TEST_LINK}} |
| Scope and five-file gate | {{SCOPE_RESULT}} | {{DIFF_LINK}} |
| Review | {{REVIEW_RESULT}} | {{REVIEW_LINK}} |
| Verification | {{VERIFY_RESULT}} | {{VERIFY_LINK}} |
| Trace integrity | {{TRACE_RESULT}} | {{TRACE_LINK}} |

## Verdict

`{{VERDICT}}` — {{VERDICT_REASON}}

Only a verified `COMPLETE` verdict may advance the normal task through its
evidence/review/verify gates. Otherwise record `ESCALATED`, `REJECTED`, or
`CAVEATS` and the exact next action.
