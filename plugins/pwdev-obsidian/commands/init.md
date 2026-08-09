---
description: Setup guiado do Obsidian — plugin Local REST API, API Key no Keychain, teste de conexão e contexto do projeto
argument-hint: "[porta-customizada]"
---

# /pwdev-obsidian:init

## STEP 0 — Idioma
`${CLAUDE_PLUGIN_ROOT}/references/language.md`. Este comando sempre pergunta.

## STEP 1 — Pré-requisito
O servidor MCP não é um serviço remoto — é o **próprio app Obsidian**
rodando localmente. Confirme com o usuário:

1. Obsidian desktop **aberto** com o vault desejado.
2. Plugin comunitário **"Local REST API"** instalado e ativado
   (Settings → Community plugins → Browse → buscar "Local REST API" →
   Install → Enable).
3. A versão instalada expõe o endpoint MCP — confira nas configs do plugin
   (Settings → Local REST API) se há uma seção/toggle de MCP. Versões
   antigas do plugin só têm a REST API clássica, sem MCP.

**O Obsidian precisa estar aberto toda vez que este plugin for usado** —
diferente de um servidor remoto, não há "sempre disponível".

## STEP 2 — API Key (nunca no chat)
Instrua: **Settings → Local REST API → API Key** (botão de copiar). Depois
peça que o usuário rode ele mesmo (input mascarado, a chave não passa pela
conversa):

```
! ${CLAUDE_PLUGIN_ROOT}/scripts/check-setup.sh --store
```

Se não for macOS, o script orienta o fallback (`export OBSIDIAN_API_KEY` no
profile). **Nunca peça a API Key colada na conversa.**

## STEP 3 — Porta customizada (opcional)
Só se o usuário mudou a porta padrão (27124) nas configs do plugin (aceite
de `$ARGUMENTS`):

```sh
export OBSIDIAN_MCP_URL="https://127.0.0.1:<porta>/mcp/"
```

Na grande maioria dos casos o default do `.mcp.json`
(`https://127.0.0.1:27124/mcp/`) já serve e este passo pode ser pulado.

## STEP 4 — Shell profile
Mostre o bloco e pergunte se pode aplicar (append em `~/.zshrc` só com
confirmação explícita; senão, o usuário aplica manualmente):

```sh
export OBSIDIAN_API_KEY="$(security find-generic-password -s pwdev-obsidian -w 2>/dev/null)"
# export OBSIDIAN_MCP_URL="https://127.0.0.1:<porta>/mcp/"   # só se a porta não for a padrão
```

## STEP 5 — Teste
Com o Obsidian aberto e as vars no ambiente (exporte inline se preciso para
o teste), rode `${CLAUDE_PLUGIN_ROOT}/scripts/check-setup.sh`. Interprete:

- `REST .../  FALHOU — sem conexão` → Obsidian fechado, plugin desativado,
  ou porta errada (voltar ao STEP 1 ou 3). **Não é erro de API Key.**
- `REST .../  FALHOU — API Key inválida` → voltar ao STEP 2.

## STEP 6 — Contexto do projeto
Pergunte nome do vault, convenção de organização (pastas principais, daily
notes, PARA/Zettelkasten ou outra), convenção de tags, e se notas podem ser
movidas/deletadas sem confirmação extra. Grave em
`.claude/pwdev-obsidian-context.md`:

```markdown
# pwdev-obsidian — contexto

## 1. Config
Idioma: {{pt-BR | en}}
Vault: {{nome}}
API Key: Keychain (service pwdev-obsidian) — local do segredo, nunca o valor

## 2. Padrões
Pastas principais: {{lista}}
Convenção de organização: {{PARA | Zettelkasten | daily notes | outra}}
Convenção de tags: {{como o time/usuário usa}}
Mover/deletar sem confirmação extra: {{sim | não}}
```

**Nunca grave a API Key.** Registre o local do segredo, nunca o valor.

## STEP 7 — Aviso final
Reinicie a sessão do Claude Code (env vars são capturadas no launch).
Mantenha o Obsidian aberto sempre que for usar este plugin. A prova real é
`/pwdev-obsidian:status`.
