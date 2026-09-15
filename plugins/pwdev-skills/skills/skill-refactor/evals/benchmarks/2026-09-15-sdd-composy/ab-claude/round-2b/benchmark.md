# A/B Claude — sdd-composy (claude-sonnet-5, effort medium, dry_run=False)

| arm | planned | executed | accepted | acceptance | US$ total | US$/accepted | context mean | out mean | p50 s | trigger P | trigger C |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| candidate | 1 | 1 | 1 | 1.0 | 0.458 | 0.458 | 885756 | 6042 | 76.4 | None | None |
| baseline | 1 | 1 | 1 | 1.0 | 0.3336 | 0.3336 | 533407 | 5098 | 70.8 | None | None |

| case | arm | status | pass_rate | accepted | US$ | context | s | failed checks |
|---|---|---|---:|---|---:|---:|---:|---|
| 3 prd_draft_gate | baseline | PASS | 1.00 | True | 0.333576 | 533407 | 70.767 |  |
| 3 prd_draft_gate | candidate | PASS | 1.00 | True | 0.457988 | 885756 | 76.42 |  |
