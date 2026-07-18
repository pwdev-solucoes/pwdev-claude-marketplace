---
description: Orquestra a produção de copy end-to-end — verifica brief, escreve via subagente e revisa
argument-hint: "[formato] [descrição do que escrever]"
---

# /pwdev-copy:copy — Produzir copy

## STEP 0 — Idioma
`${CLAUDE_PLUGIN_ROOT}/references/language.md`

## STEP 1 — Portões
Leia `.claude/pwdev-copy-context.md` e verifique, nesta ordem:

| Seção | Se vazia |
|---|---|
| 1-2 Organização/produto | pare → `/pwdev-copy:treinar` |
| 3 Posicionamento/promessa/big idea | pare → `/pwdev-copy:brief` |
| 5 Voz | avise e siga (degradado) |
| 6 VOC | avise e siga (degradado, copy sai genérica) |

Não prossiga em cima de placeholder. Copy construída sobre brief vazio custa
mais para consertar do que para refazer.

## STEP 2 — Formato
`page` | `email` | `social` | `ads` | `video` | `ux`
Se não informado, pergunte. Cada um carrega a skill `copy-*` correspondente.

## STEP 3 — Escrever
Spawn do subagente `copywriter` com `BRIEF`, `VOC_FILE`, `CONTEXT_FILE`,
`LANGUAGE`, `COPY_LANGUAGE`, `FORMATO`.

## STEP 4 — Revisar
Spawn do subagente `reviewer` sobre o rascunho. Profundidade completa.

## STEP 5 — Entregar
Apresente a versão revisada, o score anti-slop e a lista consolidada de
`[PREENCHER]`. Ofereça `/pwdev-copy:variar` para gerar alternativas e o
subagente `adversarial-copy` quando for publicação de alto risco.
