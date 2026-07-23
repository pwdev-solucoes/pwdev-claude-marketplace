# PWDEV YouTrack — Issues, Sprints e Time Tracking

> [English version](./README.md)

Plugin do Claude Code que gerencia o [YouTrack](https://www.jetbrains.com/youtrack/)
pelo **MCP server oficial embutido** (YouTrack 2025.3+), com fallback REST
autenticado para o que o MCP não cobre: agile boards, sprints, relatórios de
tempo, anexos e comandos em lote.

## O que vem dentro

| Peça | Função |
|---|---|
| MCP `youtrack` | Servidor oficial da JetBrains em `https://<instancia>/mcp` — ~25 tools: CRUD de issues, busca, comentários, tags, links, artigos da knowledge base, `log_work` |
| Skill `youtrack` | Dia a dia de issues em conversa natural (query language, disciplina de schema de campos, confirmação antes de mutação) |
| Skill `youtrack-rest` | Boards, sprints, leitura de work items, anexos, `/api/commands` em lote via `scripts/yt-api.sh` |
| `/pwdev-youtrack:init` | Setup guiado: URL da instância, token no Keychain do macOS, teste de conexão, contexto do projeto |
| `/pwdev-youtrack:status` | Diagnóstico: env vars, REST, endpoint MCP, conexão da sessão |
| `/pwdev-youtrack:sprint` | Visão do sprint, mover issues entre sprints, criar sprint |
| `/pwdev-youtrack:report` | Relatório de tempo (work items por pessoa/dia/issue) ou de sprint |

## Requisitos

- YouTrack **2025.3+** (Cloud ou self-hosted) — o MCP embutido existe a partir
  dessa versão. Instâncias antigas funcionam em modo somente-REST.
- Um **permanent token** (Profile → Account Security → Tokens → New token,
  escopo *YouTrack*).
- `curl`; Keychain do macOS recomendado para o token (Linux: env var).

## Setup

Rode `/pwdev-youtrack:init` e siga os passos. Em resumo, o resultado é:

```sh
# ~/.zshrc
export YOUTRACK_BASE_URL="https://suaorg.youtrack.cloud"
export YOUTRACK_TOKEN="$(security find-generic-password -s pwdev-youtrack -w 2>/dev/null)"
```

O `.mcp.json` do plugin expande essas env vars:

```json
{ "youtrack": { "type": "http",
  "url": "${YOUTRACK_BASE_URL:-https://example.youtrack.cloud}/mcp",
  "headers": { "Authorization": "Bearer ${YOUTRACK_TOKEN:-}" } } }
```

**Reinicie a sessão do Claude Code** depois de definir as env vars — o
ambiente é capturado no launch. Verifique com `/mcp` e
`/pwdev-youtrack:status`.

## Segurança do token

- O token vive no Keychain (service `pwdev-youtrack`), nunca em arquivo dentro
  de repositório e nunca na conversa — `check-setup.sh --store` lê com input
  mascarado.
- Toda chamada REST passa por `scripts/yt-api.sh`, que monta o header de auth
  internamente; o token não aparece em linha de comando nem no transcript.
- Diagnósticos sempre imprimem o token mascarado (`perm-***…abcd`).

## Troubleshooting

| Sintoma | Causa / correção |
|---|---|
| `/mcp` mostra `youtrack` failed | Env vars ausentes na sessão → exports + reiniciar sessão |
| `MCP … 404` no status | Instância anterior a 2025.3 → modo somente-REST |
| `REST 401` | Token inválido/expirado → recriar e rodar `check-setup.sh --store` |
| Script verde, MCP não conectado | Sessão iniciada antes das env vars → reiniciar |
