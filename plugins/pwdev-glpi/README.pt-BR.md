# PWDEV GLPI — Tickets, Triagem e Fila ITSM (Claude Code, Codex, Hermes)

A skill compartilhada `glpi` funciona em Claude Code, Codex e Hermes. O setup
por runtime está em [`references/runtime.md`](./references/runtime.md).

> [English version](./README.md)

Plugin do Claude Code que gerencia o [GLPI](https://glpi-project.org/) 10.x e 11.x
pelo [`@soarescbm/mcp-glpi`](https://github.com/soarescbm/mcp-glpi) — servidor
MCP próprio (stdio, iniciado via `npx`) que expõe 20 tools, 2 prompts e
3 resources pela API REST Legacy V1 do GLPI em `/apirest.php`.

## O que vem dentro

| Peça | Função |
|---|---|
| MCP `glpi` | `npx -y @soarescbm/mcp-glpi@0.4.0` — CRUD de tickets + followups + solução/fechamento, upload e vínculo de documentos, validação de chamados, leitura de usuários, grupos, ativos (Computer/Monitor/Phone/NetworkEquipment), projetos e base de conhecimento |
| Skill `glpi` | ITSM do dia a dia em conversa natural — mapa intenção→tool, regras ITIL (nunca setar priority, fechar só com solução aprovada, confirmar antes de mutação) |
| `/pwdev-glpi:init` | Setup guiado: URL da API, PAT no Keychain do macOS, teste de conexão, contexto do projeto |
| `/pwdev-glpi:status` | Diagnóstico: env vars, handshake REST, pacote npm, prova viva do MCP |
| `/pwdev-glpi:triagem` | Triagem da fila guiada pelo prompt MCP `triage_ticket`; ações executadas só após confirmação |
| `/pwdev-glpi:relatorio` | Panorama da fila via `summarize_tickets` — por status/urgência, P1/P2 parados, focos recomendados; somente leitura |

## Requisitos

- GLPI **10.x ou 11.x** com a API REST Legacy V1 habilitada (Setup → General → API) em uma URL terminada por `/apirest.php`.
- Um **API token** de usuário (PAT, ≥16 chars): Preferências → Chaves de
  acesso remoto.
- Node.js **20+** (o `npx` baixa o servidor publicado na primeira execução).
- `GLPI_APP_TOKEN` opcional, se a instância registrar API clients.
- Overrides existentes de `GLPI_USE_SESSION` e `GLPI_TIMEOUT_MS` continuam compatíveis.

## Setup

No Claude Code, rode `/pwdev-glpi:init`. Codex usa o manifesto portátil e `$glpi`;
Hermes usa a skill compartilhada e registra o MCP manualmente:

```sh
hermes mcp add glpi -- npx -y @soarescbm/mcp-glpi@0.4.0
```

Em qualquer runtime, forneça as variáveis documentadas e reinicie a sessão após
alterações. Não edite configurações pessoais do runtime.

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

A versão do npm é **pinada** (`@0.4.0`) por reprodutibilidade. Este branch do
plugin depende da publicação futura de `@soarescbm/mcp-glpi@0.4.0`; a release
está preparada apenas no branch irmão do MCP, portanto a inicialização via
`npx` no registry não funcionará até uma publicação autorizada separadamente.

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
| Geração GLPI desconhecida | A Legacy V1 responde, mas `getGlpiConfig` não expôs versão reconhecível; as tools continuam disponíveis |
| Primeira sessão lenta para conectar | npx baixando o pacote (só na primeira vez) |
