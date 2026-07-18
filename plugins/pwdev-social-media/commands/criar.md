---
description: Produz criativos end-to-end — conceito, triagem de custo, geração via API, curadoria, composição opcional no Figma e revisão
argument-hint: "[formato] [descrição da peça]"
---

# /pwdev-social-media:criar — Produzir criativos

## STEP 0 — Idioma
`${CLAUDE_PLUGIN_ROOT}/references/language.md`

## STEP 1 — Portões
| Verificar | Se ausente |
|---|---|
| `.claude/pwdev-social-context.md` | parar → `/pwdev-social-media:init` |
| Seção 3 — brand kit | parar → `brand-kit` |
| Copy aprovada | parar → `/pwdev-copy:copy` |
| Chaves (seção 6) | seguir em modo prompt, avisando |
| Figma (seção 2) | opcional — sem ele, composição vira especificação |

Nunca produza arte sobre copy não aprovada.

## STEP 2 — Conceito
Spawn do `art-director`. Ele entrega a **triagem de ativos** e o **prompt de
cada ativo a gerar**.

Apresente e **espere aprovação** antes de gastar qualquer crédito.

## STEP 3 — Custo
Rode a triagem de `cost-control`. Apresente:

```
Ativos no conceito:  {{n}}
Eliminados na triagem: {{n}}   ← composição, acervo ou design system
A gerar:             {{n}}
Chamadas previstas:  {{n}} (2 variações por ativo, primeira rodada)
Vídeo:               {{n}} clipes ← confirmar separado
```

**Espere confirmação explícita.** Sem ela, não avance.

## STEP 4 — Gerar
Spawn do `asset-generator`. Regra das 2 variações na primeira rodada.

## STEP 5 — Curar
`asset-curation`. Grade de comparação como Artifact para aprovação.
**Registre a seed da selecionada.**

## STEP 6 — Compor
Com Figma conectado: spawn do `figma-builder`.
Sem Figma: `figma-pipeline` entrega especificação de composição em camadas.

## STEP 7 — Revisar
Spawn do `creative-reviewer`. REPROVADO volta ao STEP 5 ou 6 — não avance.

## STEP 8 — Entregar
`export-handoff`. Ofereça `vault-sync` para arquivar prompts e seeds.

**Nunca publique.**
