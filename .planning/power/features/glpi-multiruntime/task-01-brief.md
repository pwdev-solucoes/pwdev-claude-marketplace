# Task 01 — brief

Plan: .planning/power/features/glpi-multiruntime/plan.md
Generated: 2026-09-12T19:13:38Z

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

## Task 01 — Manifesto Codex e contrato estrutural

Complexity: medium
Files: `plugins/pwdev-glpi/.codex-plugin/plugin.json`, `plugins/pwdev-glpi/skills/glpi/agents/openai.yaml`, `plugins/pwdev-glpi/tests/test_runtime_adapters.py`
Interfaces:
  Consumes: `plugins/pwdev-glpi/.mcp.json` com servidor `glpi` e pacote MCP `0.4.0`.
  Produces: manifesto Codex válido, skill `$glpi` e assertions reutilizáveis de manifests/20-2-3.
Steps:
- [ ] Escrever testes falhos para manifesto, versão 1.2.0, referência ao `.mcp.json` e skill `$glpi`.
- [ ] Rodar `python3 -m unittest discover -s plugins/pwdev-glpi/tests -p 'test_runtime_adapters.py'` e observar RED comportamental.
- [ ] Implementar os dois arquivos Codex seguindo o padrão dos plugins multi-runtime existentes.
- [ ] Rodar `python3 -m unittest discover -s plugins/pwdev-glpi/tests -p 'test_runtime_adapters.py'` e confirmar GREEN.
- [ ] Validar JSON com `python3 -m json.tool`.
- [ ] Commitar com mensagem convencional e trailers.
