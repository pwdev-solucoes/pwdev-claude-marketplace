# @soarescbm/postgres-mcp — mapa de tools

Servidor MCP próprio (stdio via npx), **14 tools** — sem prompts e sem
resources. Nomes conforme o código do servidor — **confira a lista real via
`/mcp` na primeira conexão** e ajuste este arquivo se divergir.

## Contrato de dry-run (todas as tools de mutação)

Toda tool DML/DDL tem o parâmetro `confirm` (boolean, default `false`):

- `confirm: false` → **preview, nada é executado**. Resposta:
  `{mode: "preview", sql, estimatedRows, plan?, warnings[]}`.
- `confirm: true` → executa. Resposta:
  `{mode: "executed", sql, affectedRows, durationMs, result?}`.

O dry-run não pode ser desabilitado. `confirm` precisa ser boolean de verdade
(Zod rejeita string).

## Leitura e inspeção (6)

| Tool | O que faz | Pegadinhas |
|---|---|---|
| `run_select` | SELECT/EXPLAIN somente-leitura | Validação por AST (só `SelectStmt`/`ExplainStmt`); multi-statement e qualquer DML/DDL rejeitados. `params` posicionais (`$1…`). **SEM limite de linhas — sempre incluir `LIMIT`**. `explain: true` para plano |
| `describe_table` | Colunas, PK, FKs (com ON DELETE/UPDATE), UNIQUE/CHECK, índices | `schema` default `public`; `TABLE_NOT_FOUND` se não existir |
| `list_tables` | Tabelas do schema com estimativa de linhas (`reltuples`) | `include_views: true` inclui views/matviews; estimativa ≠ COUNT exato |
| `list_schemas` | Schemas do banco | Exclui `pg_*`/`information_schema` por default (`include_system: true` inclui) |
| `list_indexes` | Índices do schema, opcionalmente por tabela | — |
| `list_constraints` | PK/UNIQUE/FK/CHECK de uma tabela | `TABLE_NOT_FOUND` se não existir |

## DML (3 — dry-run obrigatório)

| Tool | O que faz | Pegadinhas |
|---|---|---|
| `insert_row` | Insere UMA linha | `values` record; vazio → `DEFAULT VALUES`; preview avisa NOT NULL faltando; `returning` default `['*']` |
| `update_rows` | Atualiza linhas por `where` | `set` E `where` obrigatórios e não-vazios (anti atualização em massa); `null` no where vira `IS NULL`; preview traz `estimatedRows` + EXPLAIN |
| `delete_rows` | Deleta linhas por `where` | `where` obrigatório não-vazio; preview avisa FKs apontando para a tabela |

## DDL (5 — dry-run obrigatório)

| Tool | O que faz | Pegadinhas |
|---|---|---|
| `create_table` | Cria tabela | `columns[]` com `{name, type, nullable?, default?, primary_key?, unique?, references?}`; `references` = `{table, column, on_delete?, schema?}`; `if_not_exists` |
| `alter_table` | UMA ação por chamada | `action.type`: `add_column` \| `drop_column` \| `rename_column` \| `set_default` (omitir `default` = DROP DEFAULT) \| `set_nullable`. **O README do servidor lista nomes antigos — estes são os reais** |
| `drop_table` | Derruba tabela | Preview lista FKs e views dependentes; sem `cascade` o DROP falha se houver dependentes; `if_exists` |
| `create_index` | Cria índice | `method` só `btree` na v1; `unique` opcional; nome auto `idx_<tabela>_<cols>` (truncado a 63 chars) |
| `drop_index` | Derruba índice por nome | Preview avisa se o índice sustenta PK/UNIQUE; `INDEX_NOT_FOUND` sem `if_exists` |

## O que o servidor NÃO cobre

Um único banco por instância (o da `DATABASE_URL`) · transações
multi-statement (cada chamada é um statement isolado) · migrations ·
GRANT/REVOKE/roles · TRUNCATE/COPY · índices não-btree · row limit automático
no `run_select` · BIGINT acima de 2^53 vira `Number` com warning.
