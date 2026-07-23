---
description: Relatório de tempo trabalhado ou de sprint — agrega work items e estados via REST
argument-hint: "[tempo|sprint] [período|board]"
---

# /pwdev-youtrack:report

## STEP 0 — Idioma
`${CLAUDE_PLUGIN_ROOT}/references/language.md`

## Gate
`check-setup.sh` sem REST ok → aponte `/pwdev-youtrack:init` e pare.
Toda chamada via `${CLAUDE_PLUGIN_ROOT}/scripts/yt-api.sh`; receitas em
`${CLAUDE_PLUGIN_ROOT}/references/rest-api.md`.

## Modo tempo (`/report tempo [período]`)
1. Coletar: período (padrão: mês atual), escopo (projeto do contexto ou
   pergunta), pessoas (todas ou uma).
2. Candidatas: buscar issues com atividade no período
   (`project: X updated: <inicio> .. <fim>`), paginando.
3. Para cada issue, `GET /api/issues/{id}/timeTracking/workItems` (paginar) e
   filtrar `date` dentro do período (epoch ms UTC → converter).
4. Agregar por pessoa → dia → issue. Saída em tabela Markdown com subtotais por
   pessoa e total geral (minutos → `Xh Ym`).

## Modo sprint (`/report sprint [board]`)
1. Resolver board/sprint como no `/pwdev-youtrack:sprint` (STEPs 1–2).
2. Buscar issues do sprint com estado e assignee.
3. Reportar: resolvidas vs abertas, spillover (não resolvidas com sprint
   acabando/acabado), tempo registrado no sprint (work items no intervalo do
   sprint), por pessoa.

## Saída
Tabela Markdown na conversa. Oferecer salvar em
`.planning/reports/youtrack-{{tipo}}-{{AAAA-MM-DD}}.md` (só com confirmação).

Relatório é leitura — nenhuma mutação neste comando.
