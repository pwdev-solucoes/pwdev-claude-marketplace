# Model Profiles (single source of truth)

Only **subagents** need model resolution — interactive phases (discover, design, plan, product PRD, quick) run in the main context and use the session model.

## Profile table

| Subagent      | `performance` | `balanced` (default) | `economy` |
|---------------|:-------------:|:--------------------:|:---------:|
| executor      | opus          | sonnet               | sonnet    |
| advisor       | opus          | opus                 | sonnet    |
| roadmap       | opus          | sonnet               | sonnet    |
| simplifier    | opus          | sonnet               | sonnet    |
| code-reviewer | sonnet        | sonnet               | haiku     |
| qa            | sonnet        | sonnet               | haiku     |
| verifier      | sonnet        | sonnet               | haiku     |
| researcher    | sonnet        | haiku                | haiku     |

Notes:
- `performance` gives Opus to the agents that write the most consequential output (executor, roadmap, simplifier).
- `simplifier` edits production code — never haiku; Opus in `performance` because refactor judgment on working code is consequential.
- `verifier` needs real reasoning for adversarial refutation — haiku only in `economy`.
- `advisor` exists to BE the strong model at the moment of doubt — opus even in `balanced`; `economy` uses sonnet (the agent's `effort: high` still applies).

## Per-task complexity routing (executor only)

Plans declare `Complexity: low | medium | high` in their wave-contract
header (see `commands/plan.md`). When /pwdev-code:execute spawns the
executor, the model comes from this matrix instead of the plain profile row:

| Complexity        | `performance` | `balanced` | `economy` |
|-------------------|:-------------:|:----------:|:---------:|
| high              | opus          | **opus**   | sonnet    |
| medium (default)  | opus          | sonnet     | sonnet    |
| low               | **sonnet**    | sonnet     | sonnet    |

Rules:
- The `medium` row equals the profile table — a plan without the field
  behaves exactly as before (backward compatible).
- Floor: the executor NEVER runs on haiku — it edits production code and
  commits (same rationale as the simplifier note above).
- Ceiling: `economy` never escalates to opus — the profile is a cost
  promise. For a one-off boost use `model_overrides["executor"]`.
- Fix plans (`verify/fix-*.md`) are implicitly `high` — the first attempt
  at the normal tier already failed.
- `model_overrides["executor"]` beats the matrix, always.

## Resolution order

When a command spawns a subagent:

1. `.planning/config.json` → `model_overrides["<agent>"]` (e.g. `"executor": "opus"`) — if present, use it.
2. For the executor, when the plan declares `Complexity:` → the complexity
   matrix above (absent → `medium`).
3. Profile table above, using `.planning/config.json` → `model_profile` (default `balanced`).
4. Agent frontmatter `model:` (fallback when no config exists).

Pass the result via the `model` parameter of the Task tool call.

## Configuration (`.planning/config.json`)

```json
{
  "model_profile": "balanced",
  "model_overrides": { "executor": "opus" }
}
```

## Profile selection prompt (used by `init`)

**PT-BR:**
```
Qual perfil de modelo deseja usar para os subagentes?

1. Performance  — Opus para executor/roadmap/simplifier/advisor, Sonnet para os demais (melhor qualidade, maior custo)
2. Balanced     — Sonnet para quase tudo, Opus so para o advisor, Haiku para pesquisa (recomendado)
3. Economy      — Sonnet para execucao e advisor, Haiku para revisao/verificacao/pesquisa (menor custo)

Escolha (1-3, padrao: 2):
```

**EN:**
```
Which model profile would you like to use for subagents?

1. Performance  — Opus for executor/roadmap/simplifier/advisor, Sonnet for the rest (best quality, highest cost)
2. Balanced     — Sonnet for almost everything, Opus only for the advisor, Haiku for research (recommended)
3. Economy      — Sonnet for execution and advisor, Haiku for review/verification/research (lowest cost)

Choose (1-3, default: 2):
```

After selection, optionally ask about `model_overrides` for individual subagents.
