# YouTrack REST API — receitas via yt-api.sh

Todas as chamadas passam por `${CLAUDE_PLUGIN_ROOT}/scripts/yt-api.sh`
(monta o header de auth internamente — **nunca** montar `curl` com
`$YOUTRACK_TOKEN` inline).

## Convenções da API

- **`fields=` é obrigatório na prática** — sem ele a API devolve só `id`/`$type`.
  Seleção aninhada com parênteses: `fields=id,summary,assignee(login,name)`.
- **Paginação**: `$top` (padrão ~42) e `$skip`. Sempre paginar listas grandes:
  `?$top=100&$skip=0`, depois `$skip=100`…
- **IDs**: issues aceitam o ID legível (`PROJ-123`) na maioria dos endpoints;
  boards/sprints usam ID interno (`105-2`) — obtenha listando primeiro.
- JSON de resposta pode ser formatado com `| python3 -m json.tool`.

## Agile boards e sprints

```sh
# listar boards
yt-api.sh GET "/api/agiles?fields=id,name,projects(shortName)&\$top=50"

# sprints de um board (identificar o atual pelas datas ou archived=false)
yt-api.sh GET "/api/agiles/{boardId}/sprints?fields=id,name,start,finish,archived,isDefault&\$top=50"

# detalhe de um sprint
yt-api.sh GET "/api/agiles/{boardId}/sprints/{sprintId}?fields=id,name,start,finish,issues(idReadable)"
```

Issues de um sprint — mais simples via busca (MCP `search_issues` ou REST):
query `Board <Nome do Board>: {<Nome do Sprint>}`.

```sh
yt-api.sh GET "/api/issues?query=Board%20Meu%20Board%3A%20%7BSprint%2012%7D&fields=idReadable,summary,customFields(name,value(name))&\$top=100"
```

## Mover issues / operações em lote — POST /api/commands

O endpoint de comandos aplica a sintaxe de comando a várias issues de uma vez:

```sh
# mover para um sprint
yt-api.sh POST "/api/commands" '{
  "query": "Board Meu Board Sprint 12",
  "issues": [{"idReadable": "PROJ-101"}, {"idReadable": "PROJ-102"}]
}'

# mudar estado em lote, com comentário
yt-api.sh POST "/api/commands" '{
  "query": "State Fixed",
  "comment": "Corrigido no release 2.4",
  "issues": [{"idReadable": "PROJ-101"}]
}'
```

Comandos úteis: `for <login>` · `State <valor>` · `priority <valor>` ·
`tag <nome>` · `Board <board> <sprint>` · `remove Board <board>`.

## Work items (time tracking — leitura e escrita)

```sh
# work items de uma issue
yt-api.sh GET "/api/issues/PROJ-101/timeTracking/workItems?fields=id,date,duration(minutes,presentation),author(login,name),type(name),text&\$top=100"

# registrar trabalho (date em epoch ms; duration em minutos)
yt-api.sh POST "/api/issues/PROJ-101/timeTracking/workItems" '{
  "date": 1753228800000,
  "duration": {"minutes": 90},
  "text": "Revisão de código"
}'
```

Para relatório de período: busque as issues candidatas
(`updated: <período>` ou projeto), depois agregue os work items de cada uma
filtrando por `date` no intervalo. Datas de work item são epoch ms UTC.

## Attachments

```sh
# listar
yt-api.sh GET "/api/issues/PROJ-101/attachments?fields=id,name,size,url"
```

Upload é multipart (fora do yt-api.sh) — monte o curl **sem token inline**:

```sh
TOKEN_HEADER="Authorization: Bearer $(security find-generic-password -s pwdev-youtrack -w)"
curl -sS -H "$TOKEN_HEADER" -F "file=@/caminho/arquivo.png" \
  "$YOUTRACK_BASE_URL/api/issues/PROJ-101/attachments?fields=id,name"
```

## Erros comuns

| HTTP | Causa provável | Ação |
|---|---|---|
| 401 | Token inválido/expirado | `check-setup.sh`; recriar token |
| 403 | Token sem permissão no projeto | conferir escopo/permissões do usuário |
| 404 | ID interno vs legível, ou endpoint errado | boards usam ID interno |
| 400 | `fields=` malformado ou body inválido | conferir parênteses e JSON |
