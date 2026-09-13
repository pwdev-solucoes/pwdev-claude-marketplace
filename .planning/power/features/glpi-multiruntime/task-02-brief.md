# Task 02 — brief

Plan: .planning/power/features/glpi-multiruntime/plan.md
Generated: 2026-09-12T19:18:45Z

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

## Task 02 — Adapter Hermes e bootstrap de skill

Complexity: high
Files: `plugins/pwdev-glpi/.hermes-plugin/plugin.yaml`, `plugins/pwdev-glpi/.hermes-plugin/__init__.py`, `plugins/pwdev-glpi/tests/test_runtime_adapters.py`
Interfaces:
  Consumes: assertions estruturais produzidas pela Task 01.
  Produces: `register(ctx)` que registra `glpi` em layouts clone/flattened e hook `pre_llm_call` sem mutação de config.
Steps:
- [ ] Escrever testes falhos para os dois layouts, hook somente no primeiro turno e ausência de escrita em configuração pessoal.
- [ ] Rodar `python3 -m unittest discover -s plugins/pwdev-glpi/tests -p 'test_runtime_adapters.py'` e confirmar RED comportamental.
- [ ] Implementar manifest YAML e bootstrap Python somente com stdlib.
- [ ] Rodar `python3 -m unittest discover -s plugins/pwdev-glpi/tests -p 'test_runtime_adapters.py'` e confirmar GREEN.
- [ ] Rodar `python3 -m py_compile plugins/pwdev-glpi/.hermes-plugin/__init__.py`.
- [ ] Commitar com mensagem convencional e trailers.
