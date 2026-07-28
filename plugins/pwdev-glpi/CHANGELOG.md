# Changelog — pwdev-glpi

Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/).
Versionamento: `major.minor.patch` do plugin (`.claude-plugin/plugin.json`),
independente do versionamento do servidor MCP `@soarescbm/mcp-glpi`.

## [1.0.5] — 2026-07-27

### Corrigido
- Pin `@soarescbm/mcp-glpi@0.3.2` — corrige `upload_document`, que falhava em
  **toda** chamada com `"JSON payload seems not valid"`. O `uploadManifest`
  era anexado ao `FormData` multipart sem nome de arquivo e virava um `File`
  em vez de campo de texto puro; o GLPI rejeitava com um erro genérico que
  não apontava para o manifest. Nenhuma mudança de interface — mesmas tools,
  mesmos parâmetros.

## [1.0.4] — 2026-07-27

### Corrigido
- Seções "Limits"/"Limites" de `README.md` e `README.pt-BR.md` ainda listavam
  upload de anexo como não suportado; corrigido para refletir
  `upload_document`/`link_document`, disponíveis desde a 0.3.0/0.3.1.

## [1.0.3] — 2026-07-27
- Pin `@soarescbm/mcp-glpi@0.3.1` — anexo de documentos
  (`upload_document` + `link_document`) e validação de chamados
  (`request_ticket_validation` + `answer_ticket_validation`).
- `close_ticket` ganhou `force_close` na 0.2.0 e nunca tinha sido documentado
  — corrigido junto.

## [1.0.2] — 2026-07-24
- Pin `@soarescbm/mcp-glpi@0.2.0` — `force_close` em `close_ticket` e fix de
  versão do servidor.

## [1.0.1] — 2026-07-24
- Pin `@soarescbm/mcp-glpi@0.1.2` — fix crítico de autenticação por sessão.

## [1.0.0] — 2026-07-24
- Scaffold inicial do plugin: manifesto, MCP `glpi` via `npx`, entrada no
  marketplace.
- References: i18n, mapa de tools MCP, conceitos de API GLPI/ITIL.
- Skill `glpi`: mapa de intenção→tool, prompts MCP, regras ITSM.
- Comandos `/pwdev-glpi:init`, `/pwdev-glpi:status`, `/pwdev-glpi:triagem`,
  `/pwdev-glpi:relatorio`.
- READMEs bilíngues (setup, segurança do PAT, limites, troubleshooting).
