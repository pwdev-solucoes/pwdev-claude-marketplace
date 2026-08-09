---
description: Estado do plugin — config, REST, MCP e contexto do projeto
---

# /pwdev-obsidian:status

## STEP 0 — Idioma
`${CLAUDE_PLUGIN_ROOT}/references/language.md`

## Verificações
1. `${CLAUDE_PLUGIN_ROOT}/scripts/check-setup.sh` — env vars, API Key
   (mascarada), REST `GET /` (self-assinado, `authenticated`).
2. Prova viva do MCP nesta sessão: chamar `vault_list` com path vazio (ou
   `tag_list`).
   - Sucesso → configurado e o Obsidian está aberto e respondendo.
   - Erro com script verde → sessão iniciada antes das env vars (reiniciar),
     ou Obsidian foi fechado depois do check-setup rodar.
3. `.claude/pwdev-obsidian-context.md` — vault/pastas/convenções preenchidos?

## Saída
```
pwdev-obsidian — {{vault ou "não configurado"}}

Config          OBSIDIAN_MCP_URL {{url}} · API Key {{ok (abc12***…wxyz) | AUSENTE}}
REST            GET / {{ok — autenticado | FALHOU — motivo}}
MCP             sessão {{ok (vault_list responde) | FALHOU — Obsidian aberto? reiniciar sessão?}}
Contexto        vault: {{nome | —}} · pastas: {{n | —}}

Modo: completo | consultivo
```

Modo consultivo = entrega o passo a passo, não executa. Erro de tool com
script verde é quase sempre **Obsidian fechado** ou **reinício de sessão
pendente**, não erro de API Key.
