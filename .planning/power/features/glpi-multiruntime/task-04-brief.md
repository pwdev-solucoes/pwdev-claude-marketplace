# Task 04 — brief

Plan: .planning/power/features/glpi-multiruntime/plan.md
Generated: 2026-09-12T19:25:09Z

These are your requirements. Every value below is exact — copy it, do not round it,
do not substitute an equivalent, do not improve it.

## Global Constraints

- Preservar exatamente 20 tools, 2 prompts e 3 resources MCP.
- Preservar GLPI 10.x/11.x via Legacy V1 e MCP `0.4.0`.
- Preservar `GLPI_BASE_URL`, `GLPI_PAT`, `GLPI_APP_TOKEN`, `GLPI_USE_SESSION`, `GLPI_TIMEOUT_MS`.
- Não editar `~/.hermes/config.yaml`, `~/.claude.json`, `~/.codex` ou qualquer configuração pessoal.
- Não duplicar a lógica da skill nem criar um segundo servidor MCP.
- O corpo de `skills/glpi/SKILL.md` não pode conter os nomes literais dos arquivos de instruções proibidos pelo loader Hermes; referências devem ser indiretas/runtime-neutral.
- Manter comandos slash existentes somente para Claude; Codex/Hermes usam a skill compartilhada.
- Versão do plugin: `1.2.0` em todos os manifests.
- Testes de provider real são informativos; mocks e testes estruturais não podem alegar aceitação real em Codex/Hermes.
- Nenhum publish, release, tag, push ou merge nesta fase.

## Task 04 — Versão do plugin e catálogo

Complexity: low
Files: `plugins/pwdev-glpi/.claude-plugin/plugin.json`, `README.md`, `README.pt-BR.md`, `plugins/pwdev-glpi/CHANGELOG.md`
Interfaces:
  Consumes: adapters e documentação runtime-neutral produzidos pelas Tasks 01–03.
  Produces: plugin `pwdev-glpi@1.2.0` catalogado com descrição multi-runtime.
Steps:
- [ ] Escrever assertion falha para versão 1.2.0 e descrição Claude/Codex/Hermes.
- [ ] Rodar assertion e confirmar RED na versão atual.
- [ ] Atualizar manifesto Claude, catálogo bilíngue e changelog sem alterar outros plugins.
- [ ] Rodar assertions GREEN, validar JSON e executar `python3 -m unittest tests.test_marketplace_readmes`.
- [ ] Registrar falhas preexistentes sem alegar suíte global verde.
- [ ] Commitar com mensagem convencional e trailers.
