# Model Profiles (single source of truth)

Only **subagents** resolve models — the orchestrator (5-phase workflow
coordination, `references/workflow.md`) and the theme persona
(`references/theme-method.md`) run INLINE in the main context on the session
model, because they interact with the human at gates and interviews.

## Profile table

| Subagent      | `performance` | `balanced` (default) | `economy` |
|---------------|:-------------:|:--------------------:|:---------:|
| ui-builder    | opus          | sonnet               | sonnet    |
| ux-analyst    | sonnet        | sonnet               | sonnet    |
| design-bridge | sonnet        | sonnet               | sonnet    |
| ux-critic     | sonnet        | sonnet               | haiku     |
| ui-scanner    | sonnet        | sonnet               | haiku     |
| a11y-reviewer | sonnet        | haiku                | haiku     |

## Resolution order (when a command spawns a subagent)

1. `.planning/config.json` → `model_overrides["uiux-<agent>"]`
   (e.g. `"uiux-ui-builder"`)
2. `model_profile` → table above (default `balanced`)
3. Agent frontmatter `model:`

Pass the result via the Task tool `model` parameter.

## Shared config warning

`.planning/config.json` is SHARED with pwdev-code and pwdev-feat
(intentional: same `lang`, `model_profile`, `audit`). pwdev-uiux uses
namespaced override keys **`"uiux-<agent>"`** — never plain agent names
(they could collide with other plugins' agents).

## Profile selection prompt (used by `init`)

**PT-BR:**
```
Qual perfil de modelo deseja usar para os subagentes de UI?

1. Performance  — Opus para o ui-builder, Sonnet para os demais (melhor qualidade, maior custo)
2. Balanced     — Sonnet para quase tudo, Haiku para a11y (recomendado)
3. Economy      — Sonnet para construcao, Haiku para revisao/scan (menor custo)

Escolha (1-3, padrao: 2):
```

**EN:**
```
Which model profile would you like to use for the UI subagents?

1. Performance  — Opus for ui-builder, Sonnet for the rest (best quality, highest cost)
2. Balanced     — Sonnet for almost everything, Haiku for a11y (recommended)
3. Economy      — Sonnet for building, Haiku for review/scan (lowest cost)

Choose (1-3, default: 2):
```
