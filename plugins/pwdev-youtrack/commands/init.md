---
description: Setup guiado do YouTrack — instância, token no Keychain, teste de conexão e contexto do projeto
argument-hint: "[url-da-instancia]"
---

# /pwdev-youtrack:init

## STEP 0 — Idioma
`${CLAUDE_PLUGIN_ROOT}/references/language.md`. Este comando sempre pergunta.

## STEP 1 — Instância
Pergunte a URL base (`https://<org>.youtrack.cloud`; self-hosted 2025.3+ também
vale). Aceite de `$ARGUMENTS` se fornecida. Valide o formato (https, sem path,
sem `/api` nem barra final). Requisito: **YouTrack 2025.3+** (MCP embutido).

## STEP 2 — Token (nunca no chat)
Instrua a criação: **Profile → Account Security → Tokens → New token**, escopo
**YouTrack**. Depois peça que o usuário rode ele mesmo (input mascarado, o token
não passa pela conversa):

```
! ${CLAUDE_PLUGIN_ROOT}/scripts/check-setup.sh --store
```

Se não for macOS, o script orienta o fallback (`export YOUTRACK_TOKEN` no
profile). **Nunca peça o token colado na conversa.**

## STEP 3 — Shell profile
Mostre o bloco e pergunte se pode aplicar (append em `~/.zshrc` só com
confirmação explícita; senão, o usuário aplica manualmente):

```sh
export YOUTRACK_BASE_URL="https://<org>.youtrack.cloud"
export YOUTRACK_TOKEN="$(security find-generic-password -s pwdev-youtrack -w 2>/dev/null)"
```

## STEP 4 — Teste
Com as vars no ambiente atual (exporte inline se preciso para o teste), rode
`${CLAUDE_PLUGIN_ROOT}/scripts/check-setup.sh`. Interprete:
- `REST /api/users/me FALHOU 401` → token errado; voltar ao STEP 2
- `MCP ... 404` → instância < 2025.3; plugin opera só via REST (`youtrack-rest`)

## STEP 5 — Contexto do projeto
Pergunte projeto padrão do YouTrack (short name), board padrão e convenções do
time (tipos de issue usados, fluxo de estados). Grave em
`.claude/pwdev-youtrack-context.md`:

```markdown
# pwdev-youtrack — contexto

## 1. Config
Idioma: {{pt-BR | en}}
Instância: {{url}}
Token: Keychain (service pwdev-youtrack) — local do segredo, nunca o valor

## 2. Padrões
Projeto padrão: {{SHORT}}
Board padrão: {{nome}}
Convenções: {{estados, tipos, quem triage}}
```

**Nunca grave credencial.** Registre o local do segredo, nunca o valor.

## STEP 6 — Aviso final
O MCP só conecta com as env vars presentes no ambiente que lançou o Claude
Code: **reinicie a sessão**, confira com `/mcp` (servidor `youtrack`
connected) e rode `/pwdev-youtrack:status`.
