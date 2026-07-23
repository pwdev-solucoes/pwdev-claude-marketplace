---
name: youtrack-rest
description: >
  Agile boards, sprints, relatórios de tempo, anexos e operações em lote no
  YouTrack via REST API direta — o que o MCP oficial não cobre. Use quando o
  usuário disser "board", "quadro", "sprint", "sprint atual", "mover para o
  sprint", "horas registradas", "relatório de tempo", "anexar arquivo",
  "aplicar comando em várias issues". Requer YOUTRACK_BASE_URL e token.
metadata:
  version: 1.0.0
---

# YouTrack REST (fallback)

Você cobre o que o MCP oficial não expõe, chamando a REST API direto.

## Ferramenta única

**Todo acesso REST passa por `${CLAUDE_PLUGIN_ROOT}/scripts/yt-api.sh`**:

```sh
yt-api.sh GET  "/api/agiles?fields=id,name&\$top=50"
yt-api.sh POST "/api/commands" '{"query":"State Fixed","issues":[{"idReadable":"PROJ-1"}]}'
```

**Proibido** montar `curl` com `$YOUTRACK_TOKEN` inline — um erro de citação ou
`set -x` vazaria o token no transcript. O helper monta o header internamente.

## Degradação

Sem config (`check-setup.sh` acusa ausência): não execute. Entregue o comando
modelo com placeholder e aponte `/pwdev-youtrack:init`. Env var nova exige
reiniciar a sessão.

## Convenções da API

- `fields=` **obrigatório** — sem ele a resposta vem só com `id`. Seleção
  aninhada: `fields=id,name,sprints(id,name)`.
- Paginação `$top`/`$skip` em toda lista (padrão do servidor é ~42 itens).
- Boards e sprints usam **ID interno** (`105-2`) — liste primeiro para obter;
  issues aceitam ID legível (`PROJ-123`).
- Erros: 401 token · 403 permissão · 404 ID interno vs legível · 400 `fields=`
  ou JSON malformado.

## Receitas por intenção

| Intenção | Caminho |
|---|---|
| Listar boards | `GET /api/agiles?fields=id,name,projects(shortName)` |
| Sprints de um board | `GET /api/agiles/{id}/sprints?fields=id,name,start,finish,archived` |
| Issues de um sprint | busca `Board <nome>: {<sprint>}` (REST ou MCP `search_issues`) |
| Mover issue para sprint | `POST /api/commands` query `Board <nome> <sprint>` |
| Comando em lote | `POST /api/commands` com várias issues |
| Work items (leitura) | `GET /api/issues/{id}/timeTracking/workItems?fields=...` |
| Anexos | `GET/POST /api/issues/{id}/attachments` (upload multipart) |

Receitas completas com exemplos prontos:
`${CLAUDE_PLUGIN_ROOT}/references/rest-api.md`.

## Regras

- **Mutação (`POST`/`DELETE`) só com o comando à vista e confirmação** —
  especialmente `/api/commands`, que altera várias issues de uma vez.
- Leitura (`GET`) roda livre.
- Não substitua o MCP no que o MCP cobre (issues CRUD, comentários, artigos,
  log_work) — ver skill `youtrack`.
- Datas de work item são epoch ms UTC — converta antes de exibir.

## Limites

- Não administra a instância (usuários, permissões, workflows)
- Não deleta boards nem sprints
- Não faz upload de arquivo sem o usuário indicar o caminho explicitamente

## Skills relacionadas

`youtrack` — dia a dia de issues via MCP oficial
