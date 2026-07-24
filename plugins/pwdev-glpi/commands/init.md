---
description: Setup guiado do GLPI — URL da API, PAT no Keychain, teste de conexão e contexto do projeto
argument-hint: "[url-do-glpi]"
---

# /pwdev-glpi:init

## STEP 0 — Idioma
`${CLAUDE_PLUGIN_ROOT}/references/language.md`. Este comando sempre pergunta.

## STEP 1 — URL da API
Pergunte a URL do GLPI (aceite de `$ARGUMENTS`). Normalize para terminar em
`/apirest.php` (se vier a raiz, anexe). Requisito: **GLPI 10.x** com API REST
habilitada (Setup → General → API). Valide https quando não for localhost.

## STEP 2 — PAT (nunca no chat)
Instrua a criação: **Preferências do usuário → Chaves de acesso remoto →
API token → regenerar**. Depois peça que o usuário rode ele mesmo (input
mascarado, o token não passa pela conversa):

```
! ${CLAUDE_PLUGIN_ROOT}/scripts/check-setup.sh --store
```

Mínimo 16 caracteres (o servidor rejeita menos). Se não for macOS, o script
orienta o fallback (`export GLPI_PAT` no profile). **Nunca peça o PAT colado
na conversa.**

## STEP 3 — App-Token (opcional)
Só se a instância tiver "API client" com App-Token obrigatório
(Setup → General → API → clients). Não é segredo pessoal — pode ir direto no
profile: `export GLPI_APP_TOKEN="..."`. O teste do STEP 5 acusa se faltar.

## STEP 4 — Shell profile
Mostre o bloco e pergunte se pode aplicar (append em `~/.zshrc` só com
confirmação explícita; senão, o usuário aplica manualmente):

```sh
export GLPI_BASE_URL="https://<seu-glpi>/apirest.php"
export GLPI_PAT="$(security find-generic-password -s pwdev-glpi -w 2>/dev/null)"
# export GLPI_APP_TOKEN="..."   # só se o API client exigir
```

## STEP 5 — Teste
Com as vars no ambiente (exporte inline se preciso para o teste), rode
`${CLAUDE_PLUGIN_ROOT}/scripts/check-setup.sh`. Interprete pela tabela de
erros de `${CLAUDE_PLUGIN_ROOT}/references/glpi-api.md`:
`ERROR_GLPI_LOGIN` → PAT (voltar ao STEP 2); `*APP_TOKEN*` → STEP 3;
HTML → URL/API (STEP 1).

## STEP 6 — Contexto do projeto
Pergunte entidade padrão, grupo(s) de atendimento, categorias mais usadas e a
convenção de urgency/impact do time. Grave em `.claude/pwdev-glpi-context.md`:

```markdown
# pwdev-glpi — contexto

## 1. Config
Idioma: {{pt-BR | en}}
Instância: {{url}}
PAT: Keychain (service pwdev-glpi) — local do segredo, nunca o valor

## 2. Padrões
Entidade padrão: {{nome/id}}
Grupos de atendimento: {{lista}}
Categorias frequentes: {{lista}}
Convenção urgency/impact: {{como o time usa 1–5}}
```

**Nunca grave credencial.** Registre o local do segredo, nunca o valor.

## STEP 7 — Aviso final
Reinicie a sessão do Claude Code (env vars são capturadas no launch).
Atenção: o servidor `glpi` aparece **connected no `/mcp` mesmo sem config**
(modo placeholder) — a prova real é `/pwdev-glpi:status`. A primeira execução
do npx baixa o pacote (alguns segundos).
