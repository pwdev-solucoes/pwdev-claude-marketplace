---
description: Gera runbook, inventário, ADR ou diagrama a partir da infraestrutura real
argument-hint: "[runbook | inventario | adr | arquitetura]"
---

# /pwdev-devops:documentar

## STEP 0 — Idioma
`${CLAUDE_PLUGIN_ROOT}/references/language.md`

## STEP 1 — Artefato
`runbook` (maior retorno) · `inventario` · `adr` · `arquitetura`

## STEP 2 — Coletar
Spawn do `platform-documenter` — coleta somente leitura.
Todo item leva **origem e data**.

## STEP 3 — Gerar
Runbook com **comando exato e copiável**. "Verifique os logs" não é runbook.

## STEP 4 — Gravar
Notion com MCP; sem MCP, entregue markdown e declare que não gravou.
Documento existente: mostre o diff e confirme antes de sobrescrever.

**Nunca documente valor de segredo** — referencie o local.
