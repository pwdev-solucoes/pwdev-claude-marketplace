# Benchmark — pwdev-power (2026-09-15)

Verdict: **PASS** · runs executed 9/9 · cost total US$ 0.0
Budget: US$ 1.0 · baseline: `/private/tmp/claude-501/-Users-paulosoares-Projetos-skills-ia-pwdev-claude-marketplace/a4331304-eba8-4c0f-83c0-acfafca7e5d5/scratchpad/pwdev-power-baseline-full` · dry-run: False

| Runtime | Model | Effort | Config | Exec/Plan | Acceptance | Pass rate | Cost total | Cost/success | Tokens in (p50) | Tokens out (p50) | p50 s | Skill static tok |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| opencode | opencode/big-pickle | default | baseline | 3/3 | 67% | 96% | 0.0000 | 0.0000 | 88488 | 1973 | 39.3 | — |
| opencode | opencode/big-pickle | default | candidate | 3/3 | 0% | 75% | 0.0000 | — | 98061 | 2711 | 57.7 | — |
| opencode | opencode/big-pickle | default | no_skill | 3/3 | 0% | 50% | 0.0000 | — | 35679 | 835 | 16.3 | 0 |

## Paired by case (same case, runtime and model; one column per arm)

| Case | Runtime | Model | Arm | Runs | Acceptance | Pass rate | Cost/success | Context p50 |
|---|---|---|---|---:|---:|---:|---:|---:|
| quick_change_resists_scope_creep | opencode | opencode/big-pickle | candidate | 3 | 0% | 75% | — | 98061 |
| quick_change_resists_scope_creep | opencode | opencode/big-pickle | baseline | 3 | 67% | 96% | 0.0000 | 88488 |
| quick_change_resists_scope_creep | opencode | opencode/big-pickle | no_skill | 3 | 0% | 50% | — | 35679 |

Arms: `candidate` = skill under test, `baseline` = previous version (`--baseline`), `no_skill` = no skill exposed (`--no-skill-arm`).
Cost sources: Claude `total_cost_usd` (runtime), Codex pricing table, Hermes `--usage-file` (estimated).
A run is *accepted* only when every objective expectation passed.
