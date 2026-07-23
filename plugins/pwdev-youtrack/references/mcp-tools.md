# MCP oficial do YouTrack — mapa de tools

Servidor embutido no YouTrack 2025.3+ (`https://<instancia>/mcp`). As tools
respeitam as permissões do usuário dono do token. Nomes conforme a documentação
da JetBrains — **confira a lista real via `/mcp` na primeira conexão** e ajuste
este arquivo se divergir.

## Issues

| Tool | O que faz | Quando usar / pegadinhas |
|---|---|---|
| `search_issues` | Busca com a query language | Sempre com query explícita; ver `query-language.md`. Peça poucos resultados por vez |
| `get_issue` | Detalhe de uma issue | Use o ID legível (`PROJ-123`) |
| `get_issue_fields_schema` | Campos disponíveis do projeto | **Rode ANTES de criar/atualizar** — nunca invente custom field ou valor de enum |
| `create_issue` | Cria issue | Exige projeto; confirme summary/campos com o usuário antes |
| `create_draft_issue` | Cria rascunho | Prefira quando o usuário quiser revisar no YouTrack antes de publicar |
| `update_issue` | Atualiza campos | Confirmar antes; para estado/prioridade use os valores do schema |
| `change_issue_assignee` | Troca responsável | Resolva o login com `find_user` se ambíguo |
| `link_issues` | Vincula issues | Tipos: relates to, depends on, duplicates, subtask of… |

## Comentários e tags

| Tool | O que faz | Nota |
|---|---|---|
| `add_issue_comment` | Comenta | Markdown suportado |
| `get_issue_comments` | Lê comentários | |
| `manage_issue_tags` | Adiciona/remove tags | Tag precisa existir ou ser criável pelo usuário |

## Time tracking

| Tool | O que faz | Nota |
|---|---|---|
| `log_work` | Registra work item | Duração no formato YouTrack: `1h 30m`, `45m`, `1d`. Confirme duração e data antes de gravar |

## Knowledge base (artigos)

| Tool | O que faz |
|---|---|
| `search_articles` | Busca artigos |
| `get_article` | Lê artigo |
| `create_article` | Cria artigo (confirmar projeto/pasta e título antes) |
| `update_article` | Atualiza artigo |

## Projetos, pessoas e buscas salvas

| Tool | O que faz |
|---|---|
| `find_projects` / `get_project` | Lista/detalha projetos |
| `find_user` / `get_current_user` | Resolve usuários / usuário do token |
| `find_user_groups` / `get_user_group_members` | Grupos e membros |
| `get_saved_issue_searches` | Buscas salvas do usuário |

## O que o MCP oficial NÃO cobre → skill `youtrack-rest`

- Agile boards e sprints (listar, criar sprint, mover issue de sprint)
- Attachments (upload/download)
- Operações em lote via `/api/commands`
- Leitura agregada de work items (relatórios de tempo)
