# Model Profiles (single source of truth)

Only the **executor** subagent needs model resolution — every other flow
(feat, backend, frontend, test, review planning; quick; utilities) runs
INLINE in the main context on the session model. The PWDEVIA planner is
inline by design: it interviews the human (up to 2 rounds), and subagents
cannot talk to the user.

## Profile table

| Subagent | `performance` | `balanced` (default) | `economy` |
|----------|:-------------:|:--------------------:|:---------:|
| executor | opus          | sonnet               | sonnet    |

## Resolution order (when /pwdev-feat:exec spawns the executor)

1. `.planning/config.json` → `model_overrides["feat-executor"]`
2. `model_profile` → table above (default `balanced`)
3. Agent frontmatter `model:` (sonnet)

Pass the result via the Task tool `model` parameter.

## Shared config warning

`.planning/config.json` is SHARED with pwdev-code (intentional: same `lang`,
`model_profile`, `audit`). pwdev-feat uses the namespaced override key
**`"feat-executor"`** — NEVER read or write the plain `"executor"` key
(it belongs to pwdev-code).

```json
{
  "model_profile": "balanced",
  "model_overrides": { "feat-executor": "opus" }
}
```

## Profile selection prompt (used by `init`)

**PT-BR:**
```
Qual perfil de modelo deseja usar para o executor?

1. Performance  — Opus (melhor qualidade, maior custo)
2. Balanced     — Sonnet (recomendado)
3. Economy      — Sonnet (igual ao balanced neste plugin; menor custo nos demais plugins PWDEV)

Escolha (1-3, padrao: 2):
```

**EN:**
```
Which model profile would you like to use for the executor?

1. Performance  — Opus (best quality, highest cost)
2. Balanced     — Sonnet (recommended)
3. Economy      — Sonnet (same as balanced in this plugin; cheaper in other PWDEV plugins)

Choose (1-3, default: 2):
```
