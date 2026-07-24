---
name: glpi
description: >
  Tickets, triagem, followups, solução, usuários, grupos, ativos, projetos e
  base de conhecimento no GLPI via MCP (@soarescbm/mcp-glpi). Use quando o
  usuário disser "GLPI", "chamado", "ticket", "abrir chamado", "fila de
  atendimento", "triagem", "followup", "solucionar chamado", "fechar chamado",
  "ativo", "inventário", "base de conhecimento", ou citar um chamado por número.
metadata:
  version: 1.0.0
---

# GLPI

Você gerencia o GLPI (ITSM) do usuário via servidor MCP `glpi`.

## Pré-requisito e degradação

**Path A — MCP `glpi` conectado e configurado**: use as tools diretamente.

**Path B — tools falhando ou MCP ausente**: não simule. O servidor sobe mesmo
sem configuração (modo placeholder: tools listam, invocação falha) — portanto
"connected" no `/mcp` não garante config. Diagnostique com
`${CLAUDE_PLUGIN_ROOT}/scripts/check-setup.sh` e aponte `/pwdev-glpi:init`.
Env var nova só vale após reiniciar a sessão. Não há fallback REST operacional
— a API direta é usada apenas para diagnóstico.

## Mapa de intenção → tool

| Intenção | Tool |
|---|---|
| Buscar chamados | `search_tickets` (filtros; `q` para texto livre) |
| Detalhar chamado | `get_ticket` (traz followups, tasks, validations, documents) |
| Abrir chamado | `create_ticket` (content em Markdown) |
| Atualizar campos | `update_ticket` — **não aceita `status: "closed"`** |
| Acompanhar/comentar | `add_ticket_followup` |
| Solucionar/fechar | `close_ticket` — **exige texto de solução** |
| Pessoas | `search_users` · `get_user` |
| Grupos | `search_groups` · `get_group` |
| Ativos | `search_assets` · `get_asset` — só `Computer`, `Monitor`, `Phone`, `NetworkEquipment` |
| Projetos | `search_projects` · `get_project` |
| Base de conhecimento | `search_kb` · `get_kb_article` |

Filtros exatos e pegadinhas: `${CLAUDE_PLUGIN_ROOT}/references/mcp-tools.md`.

## Prompts e resources do servidor

- Triagem de um chamado: prompt MCP `triage_ticket {ticket_id}` (categoria,
  prioridade justificada, próximas ações, duplicatas).
- Panorama da fila: prompt `summarize_tickets {filter?, limit?}` — `filter` é
  JSON no schema do `search_tickets`.
- Leitura de contexto: resources `glpi://ticket/{id}`,
  `glpi://asset/{itemtype}/{id}`, `glpi://kb/{id}`.

## Regras ITSM

- **Mutação só com confirmação** — create, update, followup, close: mostre o
  que vai fazer antes de fazer.
- **Nunca defina `priority`** — o GLPI calcula pela matriz urgency×impact.
  Proponha `urgency` e `impact` (1–5); conceitos em
  `${CLAUDE_PLUGIN_ROOT}/references/glpi-api.md`.
- **Fechar chamado é fluxo próprio**: redigir a solução, aprovar com o
  usuário, então `close_ticket`. Nunca tente fechar via `update_ticket`.
- Conteúdo aceita Markdown (o servidor converte para o HTML do GLPI).
- Comunique-se pelo ID numérico do chamado.
- Leia `.claude/pwdev-glpi-context.md` (entidade, grupos, categorias padrão)
  antes de perguntar o que já está registrado.
- Texto criado no GLPI segue o idioma da instância/time do usuário.

## Fluxos recomendados

- **Abrir chamado**: coletar título, descrição, urgency/impact → montar
  proposta → confirmar → `create_ticket`.
- **Triagem de fila**: ver `/pwdev-glpi:triagem` (usa o prompt `triage_ticket`).
- **Panorama/relatório**: ver `/pwdev-glpi:relatorio`.

## Limites

- Sem Problems/Changes, SLA/OLA, upload de anexos, administração da instância
- Escrita apenas em tickets — usuários, grupos, ativos, projetos e KB são
  somente leitura
- Relatórios agregados e persistidos → `/pwdev-glpi:relatorio`
