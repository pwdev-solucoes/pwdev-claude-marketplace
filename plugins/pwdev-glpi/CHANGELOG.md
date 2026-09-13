# Changelog — pwdev-glpi

Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/).
Versionamento: `major.minor.patch` do plugin (`.claude-plugin/plugin.json`),
independente do versionamento do servidor MCP `@soarescbm/mcp-glpi`.

## [1.2.0] — 2026-09-12 (preparada, não publicada)

### Adicionado
- Compatibilidade do plugin com Claude Code, Codex e Hermes por meio da skill
  compartilhada e dos adaptadores de runtime correspondentes.
- Catálogo atualizado para identificar explicitamente o suporte multi-runtime.

### Mantido
- GLPI 10.x e 11.x via API REST Legacy V1 e servidor MCP
  `@soarescbm/mcp-glpi@0.4.0`, com 20 tools, 2 prompts e 3 resources.
- Esta entrada registra somente a preparação local; publicação, release e
  distribuição exigem autorização separada.

## [1.1.0] — 2026-09-12 (preparada, não publicada)

### Adicionado
- Compatibilidade documentada com GLPI **10.x e 11.x** usando o mesmo backend
  da API REST Legacy V1 em `/apirest.php`.
- Diagnóstico best-effort da geração por `getGlpiConfig`: falha HTTP,
  permissão negada, payload desconhecido ou versão ausente resultam em
  `unknown`, sem bloquear as tools.
- Major numérico diferente de 10 e 11 é informado como `unsupported`, com
  aviso e continuidade; `unsupported` não é tratado como `unknown`.

### Alterado
- Plugin preparado para fixar `@soarescbm/mcp-glpi@0.4.0`, preservando as 20
  tools, 2 prompts, 3 resources e as variáveis `GLPI_PAT`, `GLPI_APP_TOKEN`,
  `GLPI_USE_SESSION` e `GLPI_TIMEOUT_MS`.

### Limites
- A High-Level API V2 do GLPI 11 (`/api.php`) e OAuth2 não são suportados
  nesta versão; o contrato permanece na Legacy V1.
- `@soarescbm/mcp-glpi@0.4.0` ainda não está publicado no npm. Esta entrada
  registra apenas a preparação local do plugin 1.1.0; publicação do MCP e do
  plugin exige autorização separada.

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
