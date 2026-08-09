# MCP `obsidian` — mapa de tools e resources

Servidor MCP embutido no plugin comunitário **Local REST API** do Obsidian
(HTTP transport, `https://127.0.0.1:27124/mcp/` por padrão, cert
self-assinado). 16 tools, sem prompts, 1 resource. Nomes conforme o schema
real do servidor — **confira via `/mcp` na primeira conexão** e ajuste este
arquivo se divergir.

## Leitura de nota

| Tool | O que faz | Pegadinhas |
|---|---|---|
| `vault_read` | Lê conteúdo + metadados (`content`, `path`, `tags`, `frontmatter`, `stat` `{ctime,mtime,size}`, `links`, `backlinks`, `unresolvedLinks`) | Com `targetType`+`target`, devolve só a seção pedida (string markdown ou valor JSON de frontmatter) em vez do objeto inteiro — **prefira leitura targeted** para arquivos grandes, custa menos contexto. `scope` (`content`\|`marker`\|`markerAndContent`) espelha o de `vault_patch` — o que um scope lê é exatamente o que um `replace` naquele scope consome |
| `vault_get_document_map` | Estrutura do arquivo: árvore de headings, ids de block, chaves de frontmatter, + `version` (hash de conteúdo) | Rode **antes** de qualquer `vault_patch`/`vault_read` targeted para descobrir os targets válidos. Heading/block duplicado ganha sufixo não-imprimível de desambiguação na 2ª ocorrência em diante — **copie a chave verbatim**, nunca retype. `version` vira `ifMatch` num patch condicional |
| `vault_list` | Lista arquivos/subpastas de uma pasta (`path` vazio = raiz) | Entradas de diretório terminam em `/` |
| `search_query` | Busca por JsonLogic avaliado contra `NoteJson` de cada nota (`path`, `content`, `tags`, `frontmatter`, `stat`, `links`, `backlinks`, `unresolvedLinks`) | Operadores extras: `glob`, `regexp`. Retorna `{filename, result}` — **truque útil**: query `{"var": "stat.mtime"}` devolve `result = mtime` para todo arquivo (mtime > 0 é truthy), então dá pra ordenar por data no lado do agente sem tool de "listar recentes" dedicada |
| `search_simple` | Busca textual nativa do Obsidian, por relevância | `{filename, score, matches}`; `contextLength` controla o tamanho do trecho de contexto por match (default 100) |
| `tag_list` | Todas as tags do vault + contagem de uso | Sem `#`. Só leitura — para adicionar/remover tag, ver seção "Escrita" |
| `active_file_get_path` | Path do arquivo aberto no editor do Obsidian | Lança erro se nenhum arquivo estiver ativo |

## Escrita

| Tool | O que faz | Pegadinhas |
|---|---|---|
| `vault_write` | Cria ou **sobrescreve** um arquivo inteiro | Sobrescreve sem aviso se já existir — **confirmar antes** quando o arquivo já existe |
| `vault_append` | Acrescenta ao fim do arquivo | Cria o arquivo se não existir |
| `vault_patch` | Edição estruturada: `operation` (`replace`\|`prepend`\|`append`\|`delete`) sobre um `scope` (`content`\|`marker`\|`markerAndContent`\|`parent`) de um `target` (heading/block/frontmatter) | Payload vai em exatamente **um** campo: `content` (string), `value` (JSON — valor de frontmatter, ou array 2D de linhas para escrever numa tabela via target de bloco), ou `destination` (mover heading). Níveis de heading em `content` são **relativos ao target** (um `#` no início vira filho direto — nunca conte `#`s absolutos). `within` refina para um bloco específico do corpo de um heading (splice literal — `append` com `"\n- item"` estende uma lista). `createTargetIfMissing` cria o target se não existir. `rejectIfContentPreexists` torna `prepend`/`append` idempotente em retry. `ifMatch` = optimistic concurrency via `version` do document map |
| `vault_move` | Move/renomeia, preservando histórico e atualizando links internos | Cria pastas de destino faltantes; `allowOverwrite` (default false) — sem ele, lança erro se o destino já existir |
| `vault_copy` | Duplica arquivo | `destination` terminando em `/` preserva o nome do arquivo original na pasta destino |
| `vault_delete` | Apaga arquivo | Vai para a lixeira por padrão (pasta `.trash` ou lixeira do sistema, conforme preferência do usuário no Obsidian); `permanent: true` é **irreversível** — sempre confirmar antes |
| `open_file` | Abre um arquivo na UI do Obsidian | Cria o arquivo se não existir; `newLeaf: true` abre em painel novo |

### Tags via `vault_patch`

Não há tool dedicada de "add/remove tag" — usar `vault_patch`:

- **Adicionar**: `targetType: "frontmatter"`, `target: "tags"`,
  `operation: "append"`, `value: ["nome-da-tag"]`,
  `createTargetIfMissing: true` se o arquivo ainda não tiver campo `tags`.
- **Remover**: ler a lista atual com `vault_read`, filtrar no lado do
  agente, e regravar o campo inteiro com `operation: "replace"` e o array
  já filtrado em `value`.

## Comandos do Obsidian

| Tool | O que faz | Pegadinhas |
|---|---|---|
| `command_list` | Lista todos os comandos registrados (`id` + `name`) | Inclui comandos de outros plugins instalados no vault, não só do core |
| `command_execute` | Executa um comando pelo `commandId` | **Sem preview do efeito** — pode disparar qualquer comando registrado (inclusive destrutivo, de qualquer plugin). Lança erro se o `commandId` não existir. **Sempre confirmar antes de executar** |

## Resource MCP

`obsidian://local-rest-api/openapi.yaml` — spec OpenAPI completa da Local
REST API subjacente, com exemplos de request/response para os endpoints que
cada tool encapsula. Consultar quando um caso de uso não estiver claro pela
descrição da tool.

## O que o servidor NÃO cobre

Anexos binários (imagens, PDFs — só arquivos markdown); múltiplos vaults
simultâneos (só o vault aberto no Obsidian no momento da chamada);
sincronização; instalação/gestão de plugins do Obsidian.
