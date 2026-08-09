# PWDEV Obsidian — Notas, Busca e Vault

> [English version](./README.md)

Plugin de Claude Code que gerencia um vault do [Obsidian](https://obsidian.md)
via **servidor MCP embutido no plugin comunitário "Local REST API"** —
leitura, escrita e edição estruturada de notas (heading/block/frontmatter),
busca por JsonLogic e por texto livre, tags, arquivo ativo e comandos da
paleta.

## O que tem aqui

| Peça | Propósito |
|---|---|
| MCP `obsidian` | Embutido no plugin Local REST API, HTTPS self-assinado em `https://127.0.0.1:27124/mcp/` — 16 tools: CRUD do vault, patch estruturado, mover/copiar/apagar, busca (JsonLogic + texto livre), tags, arquivo ativo, abrir arquivo, comandos |
| Skill `obsidian` | Gestão de notas no dia a dia em conversa natural (mapa intenção → tool, confirmar antes de mutar, edições estruturadas) |
| `/pwdev-obsidian:init` | Setup guiado: checagem do pré-requisito Local REST API, API Key gravada no Keychain do macOS, teste de conexão, contexto do vault |
| `/pwdev-obsidian:status` | Diagnóstico: env vars, health check REST, conexão do MCP na sessão |
| `/pwdev-obsidian:vault` | Panorama só-leitura do vault — estrutura de pastas, tags mais usadas, notas modificadas mais recentemente |

## Requisitos

- **App desktop do Obsidian aberto**, com o vault desejado carregado. O
  servidor MCP é o próprio app rodando localmente — não é um serviço remoto
  sempre disponível.
- Plugin comunitário **"Local REST API"** instalado e ativado (Settings →
  Community plugins → Browse), com o endpoint MCP embutido exposto (confira
  nas configs do próprio plugin — versões antigas só têm a REST API
  clássica, sem MCP).
- `curl`; Keychain do macOS recomendado para guardar a API Key (Linux: env
  var).

## Setup

Rode `/pwdev-obsidian:init` e siga os passos. Em resumo, resulta em:

```sh
# ~/.zshrc
export OBSIDIAN_API_KEY="$(security find-generic-password -s pwdev-obsidian -w 2>/dev/null)"
# export OBSIDIAN_MCP_URL="https://127.0.0.1:<porta>/mcp/"   # só se você mudou a porta padrão do plugin
```

O `.mcp.json` do plugin expande essas env vars:

```json
{ "obsidian": { "type": "http",
  "url": "${OBSIDIAN_MCP_URL:-https://127.0.0.1:27124/mcp/}",
  "headers": { "Authorization": "Bearer ${OBSIDIAN_API_KEY:-}" } } }
```

**Reinicie a sessão do Claude Code** depois de setar as env vars — o
ambiente é capturado no launch. Confirme com `/mcp` e
`/pwdev-obsidian:status`. Mantenha o Obsidian aberto sempre que usar este
plugin.

## Segurança da API Key

- A chave fica no Keychain (service `pwdev-obsidian`), nunca num arquivo
  dentro de repositório e nunca na conversa — `check-setup.sh --store` lê
  com input mascarado.
- Diagnósticos sempre imprimem a chave mascarada (`abc12***…wxyz`).
- O health check REST usa `curl -k` porque o plugin Local REST API usa
  certificado self-assinado — isso é esperado, não é misconfiguração.

## Troubleshooting

| Sintoma | Causa / correção |
|---|---|
| `REST … FALHOU — sem conexão` | Obsidian fechado, ou plugin Local REST API desativado — não é problema de API Key |
| `REST … FALHOU — API Key inválida` | Chave inválida/rotacionada → recriar nas configs do plugin e rodar `check-setup.sh --store` de novo |
| Script verde, MCP não conectado | Sessão iniciada antes das env vars → reiniciar a sessão |
| `/mcp` mostra `obsidian` com erro depois do reinício | Obsidian foi fechado ou o plugin foi desativado depois do `check-setup.sh` rodar |
