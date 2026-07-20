# Model Profiles (single source of truth)

Only the **executor** and **advisor** subagents need model resolution —
every other flow (feat, backend, frontend, test, review planning; quick;
utilities) runs INLINE in the main context on the session model. The PWDEVIA
planner is inline by design: it interviews the human (up to 2 rounds), and
subagents cannot talk to the user.

## Profile table

| Subagent | `performance` | `balanced` (default) | `economy` |
|----------|:-------------:|:--------------------:|:---------:|
| executor | opus          | sonnet               | sonnet    |
| advisor  | opus          | opus                 | sonnet    |

The advisor exists to BE the strong model at the moment of doubt — opus even
in `balanced`; `economy` uses sonnet (the agent's `effort: high` still
applies).

## Resolution order (when /pwdev-feat:exec spawns a subagent)

1. `.planning/config.json` → `model_overrides["feat-executor"]` /
   `model_overrides["feat-advisor"]`
2. `model_profile` → table above (default `balanced`)
3. Agent frontmatter `model:`

Pass the result via the Task tool `model` parameter.

## Shared config warning

`.planning/config.json` is SHARED with pwdev-code (intentional: same `lang`,
`model_profile`, `audit`). pwdev-feat uses the namespaced override keys
**`"feat-executor"`** and **`"feat-advisor"`** — NEVER read or write the
plain `"executor"` / `"advisor"` keys (they belong to pwdev-code).

```json
{
  "model_profile": "balanced",
  "model_overrides": { "feat-executor": "opus", "feat-advisor": "opus" }
}
```

## Profile selection prompt (used by `init`)

**PT-BR:**
```
Qual perfil de modelo deseja usar para os subagentes (executor e advisor)?

1. Performance  — Opus para executor e advisor (melhor qualidade, maior custo)
2. Balanced     — Sonnet no executor, Opus no advisor (recomendado)
3. Economy      — Sonnet no executor e no advisor (menor custo)

Escolha (1-3, padrao: 2):
```

**EN:**
```
Which model profile would you like to use for the subagents (executor and advisor)?

1. Performance  — Opus for executor and advisor (best quality, highest cost)
2. Balanced     — Sonnet for the executor, Opus for the advisor (recommended)
3. Economy      — Sonnet for both executor and advisor (lowest cost)

Choose (1-3, default: 2):
```
