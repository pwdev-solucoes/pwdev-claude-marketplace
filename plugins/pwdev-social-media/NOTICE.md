# Atribuições

O pwdev-social-media é licenciado sob Apache-2.0 e deriva de trabalhos de terceiros.

## social-media-skills

Copyright (c) 2026 Social Media Skills Contributors — Licença MIT
https://github.com/blacktwist/social-media-skills

| pwdev-social-media | Origem |
|---|---|
| `social-context` | `social-media-context-sms` |
| `carousel-builder` | `carousel-writer-sms` (que produz texto; esta produz a peça) |

Também adotados: o padrão Path A/B e a seção `Limites` (originalmente
`Boundaries`), documentados em `references/anatomia-skill.md`.

**Diferença de escopo:** o repositório de origem produz **texto** e declara
explicitamente que não faz design visual. Este plugin cobre justamente essa
lacuna — produção do criativo, com o Figma como fonte da verdade.

## pwdev-copy

Convenções compartilhadas: arquivo de contexto como memória de treino,
protocolo de idioma, anatomia de skill, portões e calibragem de confiança.
Os dois plugins se acoplam por `.planning/config.json` e pela ponte
copy aprovada → conceito visual.

## Figma

O pipeline segue as skills oficiais servidas pelo MCP do Figma
(`figma-use`, `figma-generate-design`, `figma-generate-library`).
A exigência de carregar `/figma-use` antes de `use_figma` é do próprio MCP.
