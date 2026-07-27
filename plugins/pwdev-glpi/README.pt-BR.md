# PWDEV GLPI — Tickets, Triagem e Fila ITSM

> [English version](./README.md)

Plugin do Claude Code que gerencia o [GLPI](https://glpi-project.org/) 10.x
pelo [`@soarescbm/mcp-glpi`](https://github.com/soarescbm/mcp-glpi) — servidor
MCP próprio (stdio, iniciado via `npx`) que expõe 20 tools, 2 prompts e
3 resources sobre a API REST do GLPI.

## O que vem dentro

| Peça | Função |
|---|---|
| MCP `glpi` | `npx -y @soarescbm/mcp-glpi@0.3.1` — CRUD de tickets + followups + solução/fechamento, upload e vínculo de documentos, validação de chamados, leitura de usuários, grupos, ativos (Computer/Monitor/Phone/NetworkEquipment), projetos e base de conhecimento |
| Skill `glpi` | ITSM do dia a dia em conversa natural — mapa intenção→tool, regras ITIL (nunca setar priority, fechar só com solução aprovada, confirmar antes de mutação) |
| `/pwdev-glpi:init` | Setup guiado: URL da API, PAT no Keychain do macOS, teste de conexão, contexto do projeto |
| `/pwdev-glpi:status` | Diagnóstico: env vars, handshake REST, pacote npm, prova viva do MCP |
| `/pwdev-glpi:triagem` | Triagem da fila guiada pelo prompt MCP `triage_ticket`; ações executadas só após confirmação |
| `/pwdev-glpi:relatorio` | Panorama da fila via `summarize_tickets` — por status/urgência, P1/P2 parados, focos recomendados; somente leitura |

## Requisitos

- GLPI **10.x** com API REST habilitada (Setup → General → API).
- Um **API token** de usuário (PAT, ≥16 chars): Preferências → Chaves de
  acesso remoto.
- Node.js **20+** (o `npx` baixa o servidor publicado na primeira execução).
- `GLPI_APP_TOKEN` opcional, se a instância registrar API clients.

## Setup

Rode `/pwdev-glpi:init` e siga os passos. Em resumo:

```sh
# ~/.zshrc
export GLPI_BASE_URL="https://seu-glpi.exemplo.com.br/apirest.php"
export GLPI_PAT="$(security find-generic-password -s pwdev-glpi -w 2>/dev/null)"
# export GLPI_APP_TOKEN="..."   # só se a instância exigir
```

O `.mcp.json` do plugin inicia o servidor com essas env vars. **Reinicie a
sessão do Claude Code** depois de defini-las. Atenção: o servidor sobe mesmo
sem configuração (modo placeholder — tools listam mas falham ao invocar),
então `/mcp` mostrando *connected* não prova o setup; `/pwdev-glpi:status`
prova.

A versão do npm é **pinada** (`@0.3.1`) por reprodutibilidade e cache do npx;
releases do servidor chegam como patch do plugin.

## Segurança do token

- O PAT vive no Keychain (service `pwdev-glpi`), nunca em arquivo de
  repositório e nunca na conversa — `check-setup.sh --store` lê com input
  mascarado.
- Diagnósticos sempre imprimem o PAT mascarado (`abc12***…wxyz`).

## Limites

Sem Problems/Changes, SLA/OLA ou administração da instância; escrita só em
tickets (documentos anexados a chamado/followup/task, além de validações —
usuários, grupos, ativos, projetos e KB são somente leitura).

## Troubleshooting

| Sintoma | Causa / correção |
|---|---|
| Tools falham, `check-setup.sh` verde | Sessão iniciada antes das env vars → reiniciar |
| `ERROR_GLPI_LOGIN` / 401 | PAT inválido → regenerar o API token no GLPI |
| Erro `*APP_TOKEN*` | Instância exige App-Token → `export GLPI_APP_TOKEN` |
| HTML em vez de JSON | URL sem `/apirest.php` ou API REST desabilitada |
| Primeira sessão lenta para conectar | npx baixando o pacote (só na primeira vez) |
