# Task 02 scoped re-review package — correction round 1

Re-review only the Important finding recorded in `task-02-review-1.md`. The current bytes are:

| File | SHA-256 |
|---|---|
| `tests/test_sdd_flow_m01_contracts.py` | `a87783aca3ce97ab58c689be3eb6085297b4b4319377b75ca172d12000ada81b` |
| `tasks/prd-specflow/techspec.md` | `f047d562a41062daf1003d363d49cd130ade8d9430fb9b7a9ad943085afbb633` |
| `tasks/prd-specflow/tasks.md` | `3b948fa2cd1922390c438330521946056e8f673316cfce191c4bb6553805d7ae` |
| `.planning/power/features/specflow-m01/task-02-report.md` | `4c981a32830f2eeab888c9cf15cae2595fff0778cfb8252a94a5e1fbc21293c6` |

Expected correction: native traceability preserves original non-null story/scenario identity
when Stories are REQUIRED; permits both null only under a linked approved Stories waiver or
approved QUICK contract; requirement/criterion/test remain real and mandatory; QUICK has local
RF/CA linked to its approved reduced objective; missing/stale gates or identities block; positive
and negative test cases exist. TechSpec and downstream TASKS must be DRAFT/PENDING with prior
approval history preserved as invalidated/stale. No probes are authorized.

Verification observed independently by the controller: 12 focused tests and 44 focused plus
adjacent tests passed. Return `Important: ADDRESSED|NOT ADDRESSED` with exact evidence and report
any regression introduced by the correction separately.
