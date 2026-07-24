---
description: Panorama da fila — agrupa por status/urgência, sinaliza P1/P2 parados; leitura pura
argument-hint: "[período|grupo|status]"
---

# /pwdev-glpi:relatorio

## STEP 0 — Idioma
`${CLAUDE_PLUGIN_ROOT}/references/language.md`

## Gate
`search_tickets {"limit": 1}` falhou → apontar `/pwdev-glpi:init` e parar.

## STEP 1 — Escopo
Default: tudo não-fechado
(`{"status": ["new", "assigned", "planned", "waiting"]}`). Refinos de
`$ARGUMENTS` → JSON `filter` no schema do `search_tickets` (período →
`date_creation_from/to`, grupo → `assignee_group_id`, status nomeados).

## STEP 2 — Coleta
Via preferencial: prompt MCP **`summarize_tickets {filter, limit}`**
(`limit` ≤ 100). Se a fila exceder 100 ou o corte pedido não couber no prompt
(por assignee, por idade), complementar com `search_tickets` paginado
(`limit`/`offset`) e agregar localmente.

## STEP 3 — Saída
Tabela(s) Markdown:
- Totais por status e por urgência
- Mais antigos ainda abertos (id, título, idade)
- Alta prioridade parada (urgency/impact ≥4 sem atualização recente)
- Por grupo/assignee (quando o escopo tiver)
- **Focos recomendados** (3 itens acionáveis)

## STEP 4 — Persistir (opcional)
Oferecer salvar em `.planning/reports/glpi-fila-AAAA-MM-DD.md`
(**só com confirmação**).

Relatório é leitura — nenhuma mutação neste comando.
