---
description: Estado do plugin — config, conexão, MCP e contexto do projeto
---

# /pwdev-postgres:status

## STEP 0 — Idioma
`${CLAUDE_PLUGIN_ROOT}/references/language.md`

## Verificações
1. `${CLAUDE_PLUGIN_ROOT}/scripts/check-setup.sh` — node/npx, connection
   string (senha mascarada), teste de conexão (psql ou TCP), pacote npm.
2. Prova viva do MCP nesta sessão: chamar `list_schemas` com `{}`.
   - Sucesso → configurado e conectado.
   - Erro com script verde → sessão iniciada antes das env vars (reiniciar).
     Diferente do padrão placeholder de outros plugins: **sem
     `DATABASE_URL` este servidor nem sobe** — `/mcp` mostra o servidor com
     erro, o que já é diagnóstico por si só.
3. `.claude/pwdev-postgres-context.md` — ambiente/schemas/regras preenchidos?

## Saída
```
pwdev-postgres — {{instância}}

Config          PG_MCP_DATABASE_URL {{ok (user:***@host:port/db) | AUSENTE | prefixo inválido}} · timeout {{n ms | default}} · pool {{n | default}}
Conexão         {{psql select 1 ok | tcp ok (parcial) | FALHOU — motivo}}
MCP             npm {{1.0.0 | FALHOU}} · sessão {{ok (list_schemas responde) | caído/reiniciar ⚠}}
Contexto        ambiente: {{dev|staging|producao | —}} · schemas: {{n | —}} · DDL: {{sim|não | —}}

Modo: completo | consultivo
```

Modo consultivo = entrega o passo a passo, não executa. Erro de tool com
script verde é **alerta de reinício de sessão**, não de credencial.
