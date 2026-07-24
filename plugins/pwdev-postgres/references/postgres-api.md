# Postgres — connection string e diagnóstico

O plugin opera pelo servidor MCP; a conexão direta (`psql`/TCP) só é usada
para **diagnóstico** (dentro do `check-setup.sh`). Alvo: PostgreSQL **13–16**
(matriz de CI do servidor).

## Formato da DATABASE_URL

```
postgresql://usuario:senha@host:porta/banco
postgresql://usuario:senha@host:porta/banco?sslmode=require   # remoto
```

- Prefixos aceitos: `postgresql://` ou `postgres://`.
- Tudo vai na URL — não há vars separadas de host/porta/usuário/senha.
- SSL é o que a URL disser (`?sslmode=require|verify-full|disable`); o
  servidor não tem toggle próprio.
- Caracteres especiais na senha precisam de URL-encoding (`@` → `%40`,
  `:` → `%3A`, `/` → `%2F`).

## Env vars do plugin

| Var do shell | Vai para o servidor como | Default |
|---|---|---|
| `PG_MCP_DATABASE_URL` | `DATABASE_URL` (obrigatória) | — |
| `PG_MCP_STATEMENT_TIMEOUT_MS` | `STATEMENT_TIMEOUT_MS` | 10000 |
| `PG_MCP_POOL_MAX` | `POOL_MAX` | 5 |

A var do shell é **dedicada** (`PG_MCP_*`) de propósito: muitos projetos
exportam `DATABASE_URL` no ambiente, e o passthrough direto conectaria o MCP
silenciosamente no banco do projeto atual.

**Sem `DATABASE_URL` o servidor faz `exit(1)` no boot** — não existe modo
placeholder. O `/mcp` mostra o servidor com erro/caído quando a config falta.

## Erros comuns

| Resposta | Causa | Ação |
|---|---|---|
| `DATABASE_URL is required` (servidor não sobe) | Var ausente/vazia na sessão | Export no profile + reiniciar a sessão |
| `password authentication failed` | Senha/usuário errados na URL | Corrigir a URL (re-rodar `check-setup.sh --store`) |
| `ECONNREFUSED` | Host/porta errados ou Postgres parado | Conferir host:porta; `docker compose up -d` se local |
| `no pg_hba.conf entry … no encryption` | Servidor exige SSL | Anexar `?sslmode=require` à URL |
| `database "x" does not exist` | Nome do banco errado no path da URL | Corrigir o path final da URL |
| `canceling statement due to statement timeout` | Query passou do `STATEMENT_TIMEOUT_MS` (10s default) | Otimizar a query ou subir `PG_MCP_STATEMENT_TIMEOUT_MS` |
| `permission denied for table …` | Usuário do banco sem privilégio | Usar usuário adequado ou pedir GRANT ao DBA |
| Aviso "libpg-query fallback" no stderr | Parser AST não carregou; validação de SELECT caiu para regex | Funciona, mas mais restritivo; conferir instalação do pacote |

## Conceitos que evitam erro nas mutações

- **Dry-run em duas fases**: preview (`confirm: false`) é grátis e seguro;
  execução só com `confirm: true`. O preview usa `EXPLAIN` (nunca ANALYZE) e
  `COUNT(*)` — leitura pura por construção.
- **`estimatedRows` é estimativa** (contagem no momento do preview) — o
  número executado pode divergir se o banco mudou entre preview e confirm.
- **Sem transação entre chamadas**: duas tools = dois statements
  independentes; não há rollback conjunto. Sequências críticas (ex.: migrar
  coluna) devem ser planejadas com isso em mente.
- **Identificadores** são sempre quotados pelo servidor; valores sempre
  parametrizados (`$N`) — não tente escapar manualmente.
- **`statement_timeout`** é aplicado por conexão no pool — protege o banco de
  query desgovernada, inclusive nas de preview.
