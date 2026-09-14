# Benchmark — skill-refactor (2026-09-13)

Verdict: **PASS** · runs executed 2/2 · cost total US$ 0.056316
Budget: US$ 1.0 · baseline: `None` · dry-run: False

| Runtime | Model | Config | Exec/Plan | Acceptance | Pass rate | Cost total | Cost/success | Tokens in (p50) | Tokens out (p50) | p50 s | Skill static tok |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| claude | claude-haiku-4-5-20251001 | with_skill | 1/1 | 0% | 80% | 0.0528 | — | 58559 | 1572 | 24.7 | 2652 |
| hermes | (default) | with_skill | 1/1 | 0% | 80% | 0.0035 | — | 135252 | 4307 | 84.9 | 2652 |

Configs: `with_skill` = candidate version, `without_skill` = baseline version.
Cost sources: Claude `total_cost_usd` (runtime), Codex pricing table, Hermes `--usage-file` (estimated).
A run is *accepted* only when every objective expectation passed.

## Round scope and labels

Adapter validation only: one case (`review_only`), candidate version, **no baseline A/B**, one
repetition. Acceptance shows 0% because one objective expectation ("the review proposes a
comparison with the previous version and separates static validation from measured efficiency")
failed in both runs — a real finding about the skill's review output, not a harness error.

| Runtime | Model observed | Verdict |
|---|---|---|
| Claude Code 2.1.270 | `claude-haiku-4-5-20251001` | PASS — skill loaded from the generated plugin, cost reported by the runtime |
| Hermes Agent v0.21.1 | `deepseek/deepseek-v4-flash-0731` (openrouter, configured default) | PASS — skill read from the workspace, cost estimated by `--usage-file` |
| Codex CLI 0.153.4 | `gpt-5.6-luna` | NOT_RUN — provider usage limit, resets 2026-09-19 |

Evidence labels: the skill is `refactored` + `statically validated`; `behaviorally evaluated`
applies **only** to the two (runtime, model) pairs above, on this single case. Nothing here
supports an efficiency claim: there is no baseline arm and no repetition.
