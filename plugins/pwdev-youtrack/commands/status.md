---
description: Estado do plugin — config, REST, MCP e contexto do projeto
---

# /pwdev-youtrack:status

## STEP 0 — Idioma
`${CLAUDE_PLUGIN_ROOT}/references/language.md`

## Verificações
1. `${CLAUDE_PLUGIN_ROOT}/scripts/check-setup.sh` — env vars, token (mascarado),
   REST `/api/users/me`, endpoint `/mcp`
2. MCP conectado nesta sessão: tente a tool leve `get_current_user` do servidor
   `youtrack`. Falha com script verde = sessão iniciada antes das env vars →
   reiniciar sessão.
3. `.claude/pwdev-youtrack-context.md` — projeto/board padrão preenchidos?

## Saída
```
pwdev-youtrack — {{instância}}

Config          YOUTRACK_BASE_URL {{ok | AUSENTE}} · token {{ok (perm-***…abcd) | AUSENTE}}
REST            /api/users/me {{ok — login | FALHOU — motivo}}
MCP             endpoint {{ok | 404 <2025.3 | FALHOU}} · sessão {{connected | não conectado ⚠ reinicie}}
Contexto        projeto: {{SHORT | —}} · board: {{nome | —}}

Modo: completo | consultivo
```

Modo consultivo = entrega comandos e queries, não executa. MCP não conectado
com config ok é **alerta de reinício de sessão**, não de token.
