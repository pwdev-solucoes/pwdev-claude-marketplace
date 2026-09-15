# Benchmark — pwdev-power (2026-09-15)

Verdict: **PASS** · runs executed 18/18 · cost total US$ 3.073003
Budget: US$ 7.0 · baseline: `/private/tmp/claude-501/-Users-paulosoares-Projetos-skills-ia-pwdev-claude-marketplace/a4331304-eba8-4c0f-83c0-acfafca7e5d5/scratchpad/pwdev-power-baseline-full` · dry-run: False

| Runtime | Model | Effort | Config | Exec/Plan | Acceptance | Pass rate | Cost total | Cost/success | Tokens in (p50) | Tokens out (p50) | p50 s | Skill static tok |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| claude | claude-sonnet-5 | medium | baseline | 3/3 | 100% | 100% | 1.0581 | 0.3527 | 449904 | 2914 | 55.7 | — |
| claude | claude-sonnet-5 | medium | candidate | 3/3 | 100% | 100% | 0.9461 | 0.3154 | 437493 | 2560 | 76.4 | — |
| claude | claude-sonnet-5 | medium | no_skill | 3/3 | 0% | 76% | 1.0688 | — | 434097 | 2509 | 31.2 | 0 |
| opencode | opencode/big-pickle | default | baseline | 3/3 | 100% | 100% | 0.0000 | 0.0000 | 123657 | 4672 | 110.4 | — |
| opencode | opencode/big-pickle | default | candidate | 3/3 | 67% | 96% | 0.0000 | 0.0000 | 145902 | 5817 | 184.8 | — |
| opencode | opencode/big-pickle | default | no_skill | 3/3 | 67% | 83% | 0.0000 | 0.0000 | 35929 | 1033 | 120.0 | 0 |

## Paired by case (same case, runtime and model; one column per arm)

| Case | Runtime | Model | Arm | Runs | Acceptance | Pass rate | Cost/success | Context p50 |
|---|---|---|---|---:|---:|---:|---:|---:|
| plan_from_approved_spec | claude | claude-sonnet-5 | candidate | 1 | 100% | 100% | 0.4013 | 399118 |
| plan_from_approved_spec | claude | claude-sonnet-5 | baseline | 1 | 100% | 100% | 0.5104 | 501189 |
| plan_from_approved_spec | claude | claude-sonnet-5 | no_skill | 1 | 0% | 93% | — | 1135111 |
| plan_from_approved_spec | opencode | opencode/big-pickle | candidate | 1 | 100% | 100% | 0.0000 | 357091 |
| plan_from_approved_spec | opencode | opencode/big-pickle | baseline | 1 | 100% | 100% | 0.0000 | 253911 |
| plan_from_approved_spec | opencode | opencode/big-pickle | no_skill | 1 | 100% | 100% | 0.0000 | 94111 |
| quick_change_resists_scope_creep | claude | claude-sonnet-5 | candidate | 1 | 100% | 100% | 0.2571 | 437493 |
| quick_change_resists_scope_creep | claude | claude-sonnet-5 | baseline | 1 | 100% | 100% | 0.2724 | 446282 |
| quick_change_resists_scope_creep | claude | claude-sonnet-5 | no_skill | 1 | 0% | 62% | — | 434097 |
| quick_change_resists_scope_creep | opencode | opencode/big-pickle | candidate | 1 | 0% | 88% | — | 106178 |
| quick_change_resists_scope_creep | opencode | opencode/big-pickle | baseline | 1 | 100% | 100% | 0.0000 | 75239 |
| quick_change_resists_scope_creep | opencode | opencode/big-pickle | no_skill | 1 | 0% | 50% | — | 35929 |
| init_check_reports_without_writing | claude | claude-sonnet-5 | candidate | 1 | 100% | 100% | 0.2877 | 513868 |
| init_check_reports_without_writing | claude | claude-sonnet-5 | baseline | 1 | 100% | 100% | 0.2753 | 449904 |
| init_check_reports_without_writing | claude | claude-sonnet-5 | no_skill | 1 | 0% | 71% | — | 45516 |
| init_check_reports_without_writing | opencode | opencode/big-pickle | candidate | 1 | 100% | 100% | 0.0000 | 145902 |
| init_check_reports_without_writing | opencode | opencode/big-pickle | baseline | 1 | 100% | 100% | 0.0000 | 123657 |
| init_check_reports_without_writing | opencode | opencode/big-pickle | no_skill | 1 | 100% | 100% | 0.0000 | 18452 |

Arms: `candidate` = skill under test, `baseline` = previous version (`--baseline`), `no_skill` = no skill exposed (`--no-skill-arm`).
Cost sources: Claude `total_cost_usd` (runtime), Codex pricing table, Hermes `--usage-file` (estimated).
A run is *accepted* only when every objective expectation passed.
