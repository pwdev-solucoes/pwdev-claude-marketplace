---
description: Setup guiado do Postgres — connection string no Keychain, teste de conexão e contexto do projeto
argument-hint: "[host-ou-descricao-do-banco]"
---

# /pwdev-postgres:init

## STEP 0 — Idioma
`${CLAUDE_PLUGIN_ROOT}/references/language.md`. Este comando sempre pergunta.

## STEP 1 — Connection string
Explique o formato (aceite pistas de `$ARGUMENTS`):

```
postgresql://usuario:senha@host:5432/banco
postgresql://usuario:senha@host:5432/banco?sslmode=require   # remoto
```

Caracteres especiais na senha precisam de URL-encoding (`@`→`%40`, `:`→`%3A`).
**Aviso obrigatório**: o servidor v1 é para **dev/local** — para qualquer
banco compartilhado, recomende um usuário de banco com privilégios mínimos
(só os schemas/tabelas necessários), nunca superuser de produção.

## STEP 2 — Guardar o segredo (nunca no chat)
A connection string contém a senha — peça que o usuário rode ele mesmo
(input mascarado, a URL não passa pela conversa):

```
! ${CLAUDE_PLUGIN_ROOT}/scripts/check-setup.sh --store
```

Se não for macOS, o script orienta o fallback (`export PG_MCP_DATABASE_URL`
no profile). **Nunca peça a connection string colada na conversa.**

## STEP 3 — Opcionais
Só se o usuário precisar de algo diferente dos defaults:
`export PG_MCP_STATEMENT_TIMEOUT_MS="30000"` (default 10000 — queries longas)
e `export PG_MCP_POOL_MAX="10"` (default 5). Detalhes em
`${CLAUDE_PLUGIN_ROOT}/references/postgres-api.md`.

## STEP 4 — Shell profile
Mostre o bloco e pergunte se pode aplicar (append em `~/.zshrc` só com
confirmação explícita; senão, o usuário aplica manualmente):

```sh
export PG_MCP_DATABASE_URL="$(security find-generic-password -s pwdev-postgres -w 2>/dev/null)"
# export PG_MCP_STATEMENT_TIMEOUT_MS="30000"   # opcional
# export PG_MCP_POOL_MAX="10"                  # opcional
```

A var é dedicada (`PG_MCP_*`) de propósito: não colide com o `DATABASE_URL`
que projetos exportam no shell.

## STEP 5 — Teste
Com as vars no ambiente (exporte inline se preciso para o teste), rode
`${CLAUDE_PLUGIN_ROOT}/scripts/check-setup.sh`. Interprete pela tabela de
erros de `${CLAUDE_PLUGIN_ROOT}/references/postgres-api.md`:
`authentication failed` → URL (voltar ao STEP 2); `ECONNREFUSED` →
host/porta/serviço; `no pg_hba.conf … no encryption` → anexar
`?sslmode=require`.

## STEP 6 — Contexto do projeto
Pergunte apelido da instância, schemas principais, tabelas críticas e as
regras do time (é produção? DDL permitido? mutações permitidas?). Grave em
`.claude/pwdev-postgres-context.md`:

```markdown
# pwdev-postgres — contexto

## 1. Config
Idioma: {{pt-BR | en}}
Instância: {{apelido — host/banco, SEM credencial}}
Connection string: Keychain (service pwdev-postgres) — local do segredo, nunca o valor

## 2. Padrões
Ambiente: {{dev | staging | producao}}
Schemas principais: {{lista}}
Tabelas críticas: {{lista — cuidado redobrado em mutação}}
DDL permitido: {{sim | não | só com aprovação}}
Convenções: {{naming, migrations, quem aprova mutação}}
```

**Nunca grave credencial.** Registre o local do segredo, nunca o valor.

## STEP 7 — Aviso final
Reinicie a sessão do Claude Code (env vars são capturadas no launch).
Atenção: **sem a connection string o servidor `postgres` nem sobe**
(`exit 1` no boot) — o `/mcp` mostrará o servidor com erro até a var existir
na sessão. A prova real é `/pwdev-postgres:status`. A primeira execução do
npx baixa o pacote (alguns segundos).
