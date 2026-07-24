---
description: Panorama do banco — schemas, tabelas, índices e constraints; sinaliza achados; leitura pura
argument-hint: "[schema|tabela]"
---

# /pwdev-postgres:esquema

## STEP 0 — Idioma
`${CLAUDE_PLUGIN_ROOT}/references/language.md`

## Gate
`list_schemas {}` falhou → apontar `/pwdev-postgres:init` e parar.

## STEP 1 — Escopo
Default: todos os schemas de usuário (`list_schemas`), detalhando `public` e
os schemas listados em `.claude/pwdev-postgres-context.md`. Refinos de
`$ARGUMENTS`: um schema → detalhar só ele; uma tabela → mergulhar nela
(describe completo + índices + constraints).

## STEP 2 — Coleta (somente leitura)
1. `list_schemas {}` — visão geral.
2. Por schema no escopo: `list_tables {schema, include_views: true}`.
3. Para as tabelas principais (maiores por `reltuples` ou citadas no
   contexto): `describe_table`, `list_indexes`, `list_constraints`.
4. Métricas extras só se necessário, via `run_select` **sempre com `LIMIT`**
   (ex.: `pg_stat_user_tables` para seq scans; tamanhos via
   `pg_total_relation_size`).

## STEP 3 — Saída
Tabela(s) Markdown:
- Schemas e contagem de tabelas/views
- Por schema: tabelas com estimativa de linhas (`reltuples` — estimativa,
  não COUNT), PK, nº de índices e FKs
- Detalhe das tabelas principais (colunas, tipos, constraints)
- **Achados** (acionáveis): tabelas sem PK · FKs sem índice de apoio ·
  colunas `NOT NULL` sem default em tabelas grandes · índices duplicados

## STEP 4 — Persistir (opcional)
Oferecer salvar em `.planning/reports/postgres-esquema-AAAA-MM-DD.md`
(**só com confirmação**).

Panorama é leitura — nenhuma mutação neste comando (nenhuma tool é chamada
com `confirm: true`).
