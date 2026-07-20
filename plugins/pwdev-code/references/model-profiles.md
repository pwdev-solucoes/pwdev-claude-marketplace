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

## Resolution order

When a command spawns a subagent:

1. `.planning/config.json` → `model_overrides["<agent>"]` (e.g. `"executor": "opus"`) — if present, use it.
2. Profile table above, using `.planning/config.json` → `model_profile` (default `balanced`).
3. Agent frontmatter `model:` (fallback when no config exists).

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
