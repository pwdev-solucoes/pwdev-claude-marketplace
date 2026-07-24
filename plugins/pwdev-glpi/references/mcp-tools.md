# @soarescbm/mcp-glpi — mapa de tools, prompts e resources

Servidor MCP próprio (stdio via npx), 16 tools + 2 prompts + 3 resources.
Nomes conforme o código do servidor — **confira a lista real via `/mcp` na
primeira conexão** e ajuste este arquivo se divergir.

## Tickets (única área com escrita)

| Tool | O que faz | Pegadinhas |
|---|---|---|
| `search_tickets` | Busca com filtros | Filtros: `status[]` (`new\|assigned\|planned\|waiting\|solved\|closed`), `urgency`/`impact` (1–5), `requester_user_id`, `assignee_user_id`, `requester_group_id`, `assignee_group_id`, `itilcategories_id`, `entities_id`, `q` (texto em título+conteúdo), `date_creation_from/to`, `date_mod_from/to` (ISO), `sort`, `order`, `limit` (máx 1000, default 50), `offset`. **`priority` NÃO é filtrável** (calculada pelo GLPI) |
| `get_ticket` | Detalhe + followups, tasks, validations, documents | Sub-fetches em paralelo; resposta pode vir `degraded` se um falhar |
| `create_ticket` | Abre chamado | `content` em Markdown (servidor converte p/ HTML); `urgency`/`impact` default 3; confirmar antes |
| `update_ticket` | Atualiza campos | Exige ≥1 campo além do id; **NÃO aceita `status: "closed"`** — fechar é `close_ticket` |
| `add_ticket_followup` | Comentário/acompanhamento | `content` Markdown; `is_private` default false |
| `close_ticket` | Anexa solução (ITILSolution) | **Exige texto de solução**; GLPI transiciona para SOLVED — redigir e aprovar com o usuário antes |

## Pessoas e grupos (leitura)

| Tool | O que faz |
|---|---|
| `search_users` | Filtros `q` (name/realname/firstname/email), `is_active`, `entity_id`, `group_id` |
| `get_user` | Por ID; emails e grupos; allowlist de campos (nunca vaza dados sensíveis) |
| `search_groups` | Filtros `q`, `parent_id`, `is_assign`, `is_requester`, `entity_id` |
| `get_group` | Por ID; `members_count`, `parent_name` |

## Ativos (leitura — 4 itemtypes)

| Tool | O que faz |
|---|---|
| `search_assets` | `itemtype` obrigatório: `Computer`, `Monitor`, `Phone` ou `NetworkEquipment`; filtros variam por tipo (`os`/`serial` só Computer, `size` só Monitor, `number` só Phone); exclui deletados |
| `get_asset` | Por `itemtype`+`id`; resolve usuário, estado, fabricante; `os` e documentos |

## Projetos e knowledge base (leitura)

| Tool | O que faz |
|---|---|
| `search_projects` | `q` (name/code) + state, manager, entity |
| `get_project` | Por ID; tasks, membros e tickets vinculados |
| `search_kb` | `q` sobre título+conteúdo; filtro `is_faq` |
| `get_kb_article` | Artigo por ID (HTML, limitado a 100 KB) |

## Prompts MCP

| Prompt | Args | O que faz |
|---|---|---|
| `triage_ticket` | `{ ticket_id }` | Busca o ticket live (com followups) e instrui: categoria, prioridade 1–5 justificada, 3 próximas ações, indícios de duplicata |
| `summarize_tickets` | `{ filter?, limit? }` | `filter` = JSON no schema do `search_tickets` (≤2000 chars); `limit` 1–100 (default 20); agrupa por status/prioridade e sinaliza P1/P2 antigos |

## Resources MCP

`glpi://ticket/{id}` · `glpi://asset/{itemtype}/{id}` · `glpi://kb/{id}` —
leitura de contexto sem invocar tool.

## O que o servidor NÃO cobre

Problems e Changes · SLA/OLA · upload de anexos (documentos só listados) ·
escrita em usuários/grupos/ativos/projetos/KB · administração da instância ·
inventário além dos 4 itemtypes.
