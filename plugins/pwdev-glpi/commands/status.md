---
description: Estado do plugin — config, REST, MCP e contexto do projeto
---

# /pwdev-glpi:status

## STEP 0 — Idioma
`${CLAUDE_PLUGIN_ROOT}/references/language.md`

## Verificações
1. `${CLAUDE_PLUGIN_ROOT}/scripts/check-setup.sh` — node/npx, env vars, PAT
   (mascarado), REST initSession, pacote npm.
2. Prova viva do MCP nesta sessão: chamar `search_tickets` com `{"limit": 1}`.
   - Sucesso → configurado e autenticado.
   - Erro com script verde → sessão iniciada antes das env vars (reiniciar) —
     lembre que o servidor sobe em modo placeholder, então `/mcp` "connected"
     não prova nada.
3. `.claude/pwdev-glpi-context.md` — entidade/grupos/categorias preenchidos?

## Saída
```
pwdev-glpi — {{instância}}

Config          GLPI_BASE_URL {{ok | AUSENTE | sem /apirest.php}} · PAT {{ok (abc12***…wxyz) | AUSENTE}} · App-Token {{setado | —}}
REST            initSession {{ok | FALHOU — motivo}}
MCP             npm {{0.1.0 | FALHOU}} · sessão {{ok (search_tickets responde) | placeholder/reiniciar ⚠}}
Contexto        entidade: {{nome | —}} · grupos: {{n | —}}

Modo: completo | consultivo
```

Modo consultivo = entrega o passo a passo, não executa. Erro de tool com
script verde é **alerta de reinício de sessão**, não de PAT.
