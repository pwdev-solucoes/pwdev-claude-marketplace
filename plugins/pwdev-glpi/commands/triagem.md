---
description: Triagem da fila de chamados — prompt MCP triage_ticket, ações só com confirmação
argument-hint: "[filtro ex.: novos | grupo X | urgência 4+]"
---

# /pwdev-glpi:triagem

## STEP 0 — Idioma
`${CLAUDE_PLUGIN_ROOT}/references/language.md`

## Gate
`search_tickets {"limit": 1}` falhou → apontar `/pwdev-glpi:init` (ou
reinício de sessão, se `check-setup.sh` estiver verde) e parar.

## STEP 1 — Fila
Escopo default: `{"status": ["new"], "sort": "date_creation", "order": "ASC",
"limit": 20}` (mais antigo primeiro). Refinos de `$ARGUMENTS` mapeados para o
schema do `search_tickets` (grupo → `assignee_group_id`/`requester_group_id`,
"urgência 4+" → `urgency`, período → `date_creation_from/to`). Filtros exatos:
`${CLAUDE_PLUGIN_ROOT}/references/mcp-tools.md`.

Apresente a fila em tabela: id, título, requester, urgency/impact, idade
(dias desde a criação).

## STEP 2 — Triagem por chamado
Pergunte quais tickets triar (um, alguns ou os N primeiros). Para cada um:
1. Invocar o **prompt MCP `triage_ticket {ticket_id}`** e seguir suas
   instruções (categoria incidente/requisição, prioridade 1–5 justificada,
   3 próximas ações, indícios de duplicata).
2. Traduzir o resultado em **ações executáveis propostas**:
   `update_ticket` (urgency, impact, `itilcategories_id`, assignee) e/ou
   `add_ticket_followup` (pergunta ao requester, nota de triagem).

## STEP 3 — Execução
Mostrar a tabela de propostas (ticket → ação → parâmetros) e **executar
somente as confirmadas**, uma a uma, reportando cada resultado.

Regras: nunca fechar chamado em triagem (fechamento exige solução — fluxo
próprio da skill `glpi`); nunca setar `priority` (propor urgency×impact).
