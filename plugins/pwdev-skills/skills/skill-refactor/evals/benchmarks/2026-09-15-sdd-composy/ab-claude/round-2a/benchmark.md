# A/B Claude — sdd-composy (claude-sonnet-5, effort medium, dry_run=False)

| arm | planned | executed | accepted | acceptance | US$ total | US$/accepted | context mean | out mean | p50 s | trigger P | trigger C |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| candidate | 1 | 1 | 1 | 1.0 | 0.3406 | 0.3406 | 593324 | 4682 | 66.3 | None | None |
| baseline | 1 | 1 | 1 | 1.0 | 0.3302 | 0.3302 | 531145 | 4885 | 60.1 | None | None |

| case | arm | status | pass_rate | accepted | US$ | context | s | failed checks |
|---|---|---|---:|---|---:|---:|---:|---|
| 3 prd_draft_gate | baseline | PASS | 1.00 | True | 0.330195 | 531145 | 60.08 |  |
| 3 prd_draft_gate | candidate | PASS | 1.00 | True | 0.340636 | 593324 | 66.331 |  |
