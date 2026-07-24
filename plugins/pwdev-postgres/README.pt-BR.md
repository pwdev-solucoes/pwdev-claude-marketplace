# PWDEV Postgres — Consultas, Schema e Mutações Seguras

> [English version](./README.md)

Plugin do Claude Code que opera o PostgreSQL pelo
[`@soarescbm/postgres-mcp`](https://github.com/soarescbm/postgres-mcp) —
servidor MCP próprio (stdio, iniciado via `npx`) que expõe 14 tools: SELECT
somente-leitura validado por AST, inspeção de schema e DML/DDL com dry-run
obrigatório (preview antes de executar).

## O que vem dentro

| Peça | Função |
|---|---|
| MCP `postgres` | `npx -y @soarescbm/postgres-mcp@1.0.0` — `run_select` (somente leitura, validado por AST), inspeção de schema (tabelas, índices, constraints), DML (`insert_row`/`update_rows`/`delete_rows`) e DDL (`create/alter/drop table`, índices), toda mutação com dry-run + `confirm: true` |
| Skill `postgres` | Banco de dados no dia a dia em conversa natural — mapa intenção→tool, regras de segurança (mutação em duas fases, sempre `LIMIT`, nunca contornar as travas anti mutação em massa) |
| `/pwdev-postgres:init` | Setup guiado: connection string no Keychain do macOS, teste de conexão, contexto do projeto |
| `/pwdev-postgres:status` | Diagnóstico: env vars, teste de conexão, pacote npm, prova viva do MCP |
| `/pwdev-postgres:esquema` | Panorama do banco — schemas, tabelas, índices, constraints, achados acionáveis; somente leitura |

## Requisitos

- PostgreSQL **13–16** (matriz de CI do servidor).
- Uma connection string (`postgresql://usuario:senha@host:5432/banco`); para
  banco compartilhado, use um usuário de privilégios mínimos — o servidor é
  **v1, orientado a dev/local**.
- Node.js **20+** (o `npx` baixa o servidor publicado na primeira execução).

## Setup

Rode `/pwdev-postgres:init` e siga os passos. Em resumo:

```sh
# ~/.zshrc
export PG_MCP_DATABASE_URL="$(security find-generic-password -s pwdev-postgres -w 2>/dev/null)"
# export PG_MCP_STATEMENT_TIMEOUT_MS="30000"   # opcional (default 10000)
# export PG_MCP_POOL_MAX="10"                  # opcional (default 5)
```

O `.mcp.json` do plugin mapeia `PG_MCP_DATABASE_URL` para o `DATABASE_URL`
do servidor. A env var é **propositalmente dedicada**: muitos projetos
exportam `DATABASE_URL` no shell, e o passthrough direto conectaria o MCP
silenciosamente no banco do projeto atual.

**Reinicie a sessão do Claude Code** depois de definir as vars. Atenção: sem
connection string o servidor **sai no boot** (não há modo placeholder) — o
`/mcp` mostrará o servidor com erro até a var chegar à sessão;
`/pwdev-postgres:status` é a prova real.

A versão do npm é **pinada** (`@1.0.0`) por reprodutibilidade e cache do
npx; releases do servidor chegam como patch do plugin.

## Segurança do segredo

- A connection string (contém a senha) vive no Keychain (service
  `pwdev-postgres`), nunca em arquivo de repositório e nunca na conversa —
  `check-setup.sh --store` lê com input mascarado.
- Diagnósticos sempre imprimem a URL com a senha mascarada
  (`postgresql://usuario:***@host:5432/banco`).

## Modelo de segurança

Toda mutação é em duas fases: a chamada com `confirm: false` retorna um
preview (`sql`, `estimatedRows`, `warnings`) e não executa nada; só uma
segunda chamada com `confirm: true` — após a sua confirmação explícita —
executa. `update_rows`/`delete_rows` recusam `where` vazio (anti mutação em
massa), e o dry-run não pode ser desabilitado.

## Limites

Um banco por instância · sem transações multi-statement · sem migrations,
roles/GRANT, TRUNCATE/COPY · índices só btree · `run_select` sem limite
automático de linhas (a skill sempre adiciona `LIMIT`) · BIGINT acima de
2^53 chega como `Number` com warning.

## Troubleshooting

| Sintoma | Causa / correção |
|---|---|
| `/mcp` mostra o servidor com erro | `PG_MCP_DATABASE_URL` ausente na sessão → export + reiniciar (não há modo placeholder) |
| Tools falham, `check-setup.sh` verde | Sessão iniciada antes das env vars → reiniciar |
| `password authentication failed` | Usuário/senha errados na URL → re-rodar `check-setup.sh --store` |
| `ECONNREFUSED` | Host/porta errados ou Postgres parado (`docker compose up -d` se local) |
| `no pg_hba.conf entry … no encryption` | Servidor exige SSL → anexar `?sslmode=require` |
| `canceling statement due to statement timeout` | Query acima de 10 s → otimizar ou subir `PG_MCP_STATEMENT_TIMEOUT_MS` |
| Primeira sessão lenta para conectar | npx baixando o pacote (só na primeira vez) |
