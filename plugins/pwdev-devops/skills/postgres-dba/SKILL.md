---
name: postgres-dba
description: >
  Diagnóstico e tuning de PostgreSQL — EXPLAIN ANALYZE, índice, VACUUM, bloat,
  lock, replicação, WAL, PITR e particionamento. Use quando o usuário disser
  "postgres", "query lenta", "índice", "EXPLAIN", "vacuum", "lock", "deadlock",
  "replicação", "conexões", "banco lento".
metadata: { version: 1.0.0 }
---

# PostgreSQL DBA

Você diagnostica banco. Toda alteração de schema em produção é potencialmente
destrutiva — trate como tal.

## Portão de segurança
`SELECT`, `EXPLAIN`, `\d`, `pg_stat_*` rodam livres.
`CREATE INDEX`, `ALTER`, `VACUUM FULL`, `REINDEX` exigem confirmação.
`DROP`, `TRUNCATE`, `DELETE` sem `WHERE` são destrutivos.

> `VACUUM FULL` e `REINDEX` **travam a tabela**. `ALTER TABLE` em tabela grande
> pode travar por minutos. Em produção, sempre a variante `CONCURRENTLY` e
> sempre em janela.

## Query lenta

```sql
-- 1. quem consome
SELECT query, calls, mean_exec_time, total_exec_time
FROM pg_stat_statements ORDER BY total_exec_time DESC LIMIT 20;

-- 2. o plano real
EXPLAIN (ANALYZE, BUFFERS) SELECT ...;
```

`EXPLAIN` sozinho mostra o plano **estimado**. `ANALYZE` executa e mostra o
real. A diferença entre `rows` estimado e real é o que denuncia estatística
desatualizada.

| No plano | Significa |
|---|---|
| `Seq Scan` em tabela grande | falta índice, ou o índice não serve |
| estimado ≪ real | estatística velha → `ANALYZE tabela` |
| `Nested Loop` com muitas linhas | falta índice no lado interno |
| `Sort` com `disk` | `work_mem` baixo |
| `Filter` removendo muita linha | índice parcial ajudaria |

## Índice
```sql
-- em produção, SEMPRE concurrently
CREATE INDEX CONCURRENTLY idx_x ON t (col);

-- índices nunca usados
SELECT relname, indexrelname, idx_scan FROM pg_stat_user_indexes
WHERE idx_scan = 0 ORDER BY pg_relation_size(indexrelid) DESC;
```

Índice não usado custa em toda escrita. Antes de remover, confirme que a
estatística cobre um ciclo completo — relatório mensal não aparece em 7 dias.

## Bloat e VACUUM
```sql
SELECT relname, n_dead_tup, last_autovacuum
FROM pg_stat_user_tables ORDER BY n_dead_tup DESC LIMIT 20;
```
Autovacuum não dá conta: ajuste `autovacuum_vacuum_scale_factor` na tabela.
`VACUUM FULL` é último recurso — trava.

## Lock
```sql
SELECT blocked.pid, blocked.query, blocking.pid, blocking.query
FROM pg_stat_activity blocked
JOIN pg_stat_activity blocking ON blocking.pid = ANY(pg_blocking_pids(blocked.pid))
WHERE cardinality(pg_blocking_pids(blocked.pid)) > 0;
```

## Conexões
```sql
SELECT count(*), state FROM pg_stat_activity GROUP BY state;
SHOW max_connections;
```
Muitas `idle in transaction`: bug de aplicação que não faz commit. Aumentar
`max_connections` não resolve — **use pooler** (PgBouncer) e corrija a app.

## Anti-padrões
- `CREATE INDEX` sem `CONCURRENTLY` em produção
- `max_connections` alto em vez de pooler
- Backup nunca testado com restore
- `VACUUM FULL` em horário de pico
- `DELETE` em massa sem lote — inflaciona WAL e trava

## Limites
- Não roda DDL em produção sem confirmação e janela
- Não faz `DROP` nem `TRUNCATE` — entrega o comando
- Não altera parâmetro que exija restart sem avisar do downtime
- `psql` ausente hoje: modo consultivo

## Skills relacionadas
`backup-dr` · `performance-engineer` · `observability` · `laravel-platform`
