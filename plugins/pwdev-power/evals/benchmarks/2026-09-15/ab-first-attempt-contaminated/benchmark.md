# Benchmark — pwdev-power (2026-09-15)

Verdict: **FAIL** · runs executed 18/18 · cost total US$ 2.759924
Budget: US$ 7.0 · baseline: `/private/tmp/claude-501/-Users-paulosoares-Projetos-skills-ia-pwdev-claude-marketplace/a4331304-eba8-4c0f-83c0-acfafca7e5d5/scratchpad/pwdev-power-baseline-full` · dry-run: False

| Runtime | Model | Effort | Config | Exec/Plan | Acceptance | Pass rate | Cost total | Cost/success | Tokens in (p50) | Tokens out (p50) | p50 s | Skill static tok |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| claude | claude-sonnet-5 | medium | baseline | 3/3 | 67% | 83% | 0.9281 | 0.4640 | 428447 | 3074 | 50.0 | — |
| claude | claude-sonnet-5 | medium | candidate | 3/3 | 67% | 83% | 0.8682 | 0.4341 | 277579 | 1737 | 31.0 | — |
| claude | claude-sonnet-5 | medium | no_skill | 3/3 | 67% | 83% | 0.9637 | 0.4818 | 532154 | 3768 | 67.3 | 0 |
| opencode | opencode/big-pickle | default | baseline | 3/3 | 0% | 40% | — | — | — | — | 2.1 | — |
| opencode | opencode/big-pickle | default | candidate | 3/3 | 0% | 40% | — | — | — | — | 2.1 | — |
| opencode | opencode/big-pickle | default | no_skill | 3/3 | 33% | 81% | 0.0000 | 0.0000 | 320208 | 6193 | 131.0 | 0 |

## Paired by case (same case, runtime and model; one column per arm)

| Case | Runtime | Model | Arm | Runs | Acceptance | Pass rate | Cost/success | Context p50 |
|---|---|---|---|---:|---:|---:|---:|---:|
| plan_from_approved_spec | claude | claude-sonnet-5 | candidate | 1 | 100% | 100% | 0.4410 | 511444 |
| plan_from_approved_spec | claude | claude-sonnet-5 | baseline | 1 | 100% | 100% | 0.4176 | 428447 |
| plan_from_approved_spec | claude | claude-sonnet-5 | no_skill | 1 | 100% | 100% | 0.4755 | 532154 |
| plan_from_approved_spec | opencode | opencode/big-pickle | candidate | 1 | 0% | 27% | — | — |
| plan_from_approved_spec | opencode | opencode/big-pickle | baseline | 1 | 0% | 27% | — | — |
| plan_from_approved_spec | opencode | opencode/big-pickle | no_skill | 1 | 0% | 93% | — | 549262 |
| quick_change_resists_scope_creep | claude | claude-sonnet-5 | candidate | 1 | 0% | 50% | — | 215204 |
| quick_change_resists_scope_creep | claude | claude-sonnet-5 | baseline | 1 | 0% | 50% | — | 273799 |
| quick_change_resists_scope_creep | claude | claude-sonnet-5 | no_skill | 1 | 0% | 50% | — | 157232 |
| quick_change_resists_scope_creep | opencode | opencode/big-pickle | candidate | 1 | 0% | 38% | — | — |
| quick_change_resists_scope_creep | opencode | opencode/big-pickle | baseline | 1 | 0% | 38% | — | — |
| quick_change_resists_scope_creep | opencode | opencode/big-pickle | no_skill | 1 | 0% | 50% | — | 72972 |
| init_check_reports_without_writing | claude | claude-sonnet-5 | candidate | 1 | 100% | 100% | 0.2265 | 277579 |
| init_check_reports_without_writing | claude | claude-sonnet-5 | baseline | 1 | 100% | 100% | 0.2963 | 515604 |
| init_check_reports_without_writing | claude | claude-sonnet-5 | no_skill | 1 | 100% | 100% | 0.3168 | 573941 |
| init_check_reports_without_writing | opencode | opencode/big-pickle | candidate | 1 | 0% | 57% | — | — |
| init_check_reports_without_writing | opencode | opencode/big-pickle | baseline | 1 | 0% | 57% | — | — |
| init_check_reports_without_writing | opencode | opencode/big-pickle | no_skill | 1 | 100% | 100% | 0.0000 | 320208 |

Arms: `candidate` = skill under test, `baseline` = previous version (`--baseline`), `no_skill` = no skill exposed (`--no-skill-arm`).
Cost sources: Claude `total_cost_usd` (runtime), Codex pricing table, Hermes `--usage-file` (estimated).
A run is *accepted* only when every objective expectation passed.
