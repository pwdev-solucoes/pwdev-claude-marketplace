---
description: Boards e sprints — visão do sprint, mover issues, criar sprint (via REST)
argument-hint: "[board] [sprint]"
---

# /pwdev-youtrack:sprint

## STEP 0 — Idioma
`${CLAUDE_PLUGIN_ROOT}/references/language.md`

## Gate
`check-setup.sh` sem REST ok → aponte `/pwdev-youtrack:init` e pare.
Receitas: `${CLAUDE_PLUGIN_ROOT}/references/rest-api.md`. Toda chamada via
`${CLAUDE_PLUGIN_ROOT}/scripts/yt-api.sh`.

## STEP 1 — Board
Resolver nesta ordem: `$ARGUMENTS` → board padrão do
`.claude/pwdev-youtrack-context.md` → listar
(`GET /api/agiles?fields=id,name,projects(shortName)`) e perguntar.

## STEP 2 — Sprint
Sem sprint em `$ARGUMENTS`: listar sprints do board
(`GET /api/agiles/{id}/sprints?fields=id,name,start,finish,archived,isDefault`)
e identificar o atual (não arquivado, datas englobando hoje). Confirmar se
houver mais de um candidato.

## STEP 3 — Visão do sprint
Buscar issues (`Board <nome>: {<sprint>}`) com estado, assignee e prioridade.
Apresentar: total, agrupado por estado, não atribuídas, e destaque para o que
está `#Unresolved` perto do fim do sprint.

## STEP 4 — Ações (oferecer, nunca executar sem confirmação)
- **Mover issues para o sprint**: `POST /api/commands` com query
  `Board <nome> <sprint>` — mostre o JSON exato e a lista de issues antes.
- **Tirar do sprint**: query `remove Board <nome>`.
- **Criar sprint**: `POST /api/agiles/{id}/sprints` com `{"name":"...","start":ms,"finish":ms}`.
- **Ver sprint anterior**: repetir STEP 3 com o sprint arquivado escolhido.

Mutação sempre com o comando à vista + confirmação explícita.
