# PWDEV Marketplace

*Read in [English](./README.md).*

Marketplace de plugins para Claude Code, Codex e runtimes PWDEV compatíveis.

## Instalação

```bash
claude plugin marketplace add /caminho/para/pwdev-claude-marketplace
claude plugin install <plugin>@pwdev-claude-marketplace
```

Reinicie o runtime após a instalação. Consulte o README de cada plugin para setup e permissões.

## Escolha por objetivo

| Objetivo | Plugins |
|---|---|
| Desenvolvimento orientado a especificações | [pwdev-power](./plugins/pwdev-power/), [pwdev-flow](./plugins/pwdev-flow/), [sdd-composy](./plugins/sdd-composy/) |
| Código e delegação | [pwdev-code](./plugins/pwdev-code/), [pwdev-feat](./plugins/pwdev-feat/) |
| Requisitos e UI/UX | [pwdev-prd](./plugins/pwdev-prd/), [pwdev-uiux](./plugins/pwdev-uiux/) |
| Copy e conteúdo social | [pwdev-copy](./plugins/pwdev-copy/), [pwdev-social-media](./plugins/pwdev-social-media/) |
| Planejamento visual | [pwdev-excalidraw](./plugins/pwdev-excalidraw/) |
| DevOps e operações | [pwdev-devops](./plugins/pwdev-devops/) |
| Conhecimento e integrações | [pwdev-brain](./plugins/pwdev-brain/), [pwdev-glpi](./plugins/pwdev-glpi/), [pwdev-obsidian](./plugins/pwdev-obsidian/), [pwdev-postgres](./plugins/pwdev-postgres/), [pwdev-youtrack](./plugins/pwdev-youtrack/) |
| Suporte ao terminal | [pwdev-statusline](./plugins/pwdev-statusline/) |

## Catálogo de plugins

| Plugin | Versão | Descrição |
|---|:---:|---|
| [pwdev-brain](./plugins/pwdev-brain/) | 1.1.0 | Segundo cérebro e LLM Wiki com citações |
| [pwdev-code](./plugins/pwdev-code/) | 2.4.0 | Código orientado a especificações e delegação |
| [pwdev-copy](./plugins/pwdev-copy/) | 1.1.0 | Copywriting treinável |
| [pwdev-devops](./plugins/pwdev-devops/) | 1.0.0 | Plataforma, operações e incidentes |
| [pwdev-excalidraw](./plugins/pwdev-excalidraw/) | 0.1.0 | Planejamento visual com Excalidraw |
| [pwdev-feat](./plugins/pwdev-feat/) | 2.1.1 | Planejamento rápido de features |
| [pwdev-flow](./plugins/pwdev-flow/) | 0.6.0 | Fluxo portátil de desenvolvimento |
| [pwdev-glpi](./plugins/pwdev-glpi/) | 1.0.5 | GLPI ITSM |
| [pwdev-obsidian](./plugins/pwdev-obsidian/) | 1.0.0 | Operações em vault Obsidian |
| [pwdev-postgres](./plugins/pwdev-postgres/) | 1.0.0 | Operações seguras em PostgreSQL |
| [pwdev-power](./plugins/pwdev-power/) | 0.1.0 | Desenvolvimento com gates e frotas cmux |
| [pwdev-prd](./plugins/pwdev-prd/) | 2.0.1 | Requisitos conduzidos por entrevista |
| [pwdev-social-media](./plugins/pwdev-social-media/) | 2.0.1 | Criativos sociais por IA |
| [pwdev-statusline](./plugins/pwdev-statusline/) | 1.1.0 | Status de terminal configurável |
| [pwdev-uiux](./plugins/pwdev-uiux/) | 2.0.1 | UI/UX e acessibilidade |
| [pwdev-youtrack](./plugins/pwdev-youtrack/) | 1.0.0 | Gestão do YouTrack |
| [sdd-composy](./plugins/sdd-composy/) | 0.1.0 | SDD portátil com OKF e rastreabilidade |

### pwdev-excalidraw

Planejamento visual com o servidor MCP oficial do Excalidraw. Instale com `claude plugin install pwdev-excalidraw@pwdev-claude-marketplace`. Consulte a [documentação do plugin](./plugins/pwdev-excalidraw/).

## Primeiro uso

Plugins de workflow geralmente seguem:

```text
init → discover/map → product/specify → plan/tasks → execute → QA/evidence → review → verify
```

No `sdd-composy`, comece com `/sdd-composy:init` e escolha `pt-BR` ou `en-US`.

## Atualizações e segurança

```bash
claude plugin marketplace update pwdev-claude-marketplace
claude plugin update <plugin>@pwdev-claude-marketplace
```

Revise permissões antes de ativar providers externos, integrações MCP ou frotas autônomas.

## Contribuição

Mantenha manifests, skills, comandos, referências, testes e os dois READMEs sincronizados. Execute
`python3 scripts/validate_readme_plugins.py` antes de enviar alterações.

Licença: Apache-2.0.
