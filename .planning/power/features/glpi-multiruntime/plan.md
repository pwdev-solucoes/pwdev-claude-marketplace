# GLPI Multi-Runtime — Plan

Status: APPROVED
Spec: .planning/power/features/glpi-multiruntime/spec.md
Updated: 2026-09-12

For agentic workers: execute this with pwdev-power:power-execute.

## Goal

Empacotar o `pwdev-glpi` para Claude Code, Codex e Hermes Agent com uma única skill, o mesmo
MCP e setup explícito por runtime.

## Architecture

`.claude-plugin`, `.codex-plugin` e `.hermes-plugin` são adapters finos. `skills/glpi/SKILL.md`,
references e `.mcp.json` permanecem fontes compartilhadas. Hermes registra skills via hook Python;
o operador adiciona o MCP com `hermes mcp add`.

## Tech Stack

JSON manifests, YAML Hermes manifest, Python stdlib adapter, Markdown skills/docs, shell POSIX,
Python unittest e validações estruturais existentes do marketplace.

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

## File Structure

- `plugins/pwdev-glpi/.codex-plugin/plugin.json`
- `plugins/pwdev-glpi/skills/glpi/agents/openai.yaml`
- `plugins/pwdev-glpi/.hermes-plugin/plugin.yaml`
- `plugins/pwdev-glpi/.hermes-plugin/__init__.py`
- `plugins/pwdev-glpi/tests/test_runtime_adapters.py`
- `plugins/pwdev-glpi/skills/glpi/SKILL.md`
- `plugins/pwdev-glpi/references/runtime.md`
- `plugins/pwdev-glpi/README.md`
- `plugins/pwdev-glpi/README.pt-BR.md`
- `plugins/pwdev-glpi/commands/status.md`
- `README.md`
- `README.pt-BR.md`
- `plugins/pwdev-glpi/.claude-plugin/plugin.json`
- `plugins/pwdev-glpi/CHANGELOG.md`

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

## Task 03 — Skill runtime-neutral e documentação operacional

Complexity: medium
Files: `plugins/pwdev-glpi/skills/glpi/SKILL.md`, `plugins/pwdev-glpi/references/runtime.md`, `plugins/pwdev-glpi/README.md`, `plugins/pwdev-glpi/README.pt-BR.md`, `plugins/pwdev-glpi/commands/status.md`
Interfaces:
  Consumes: adapters Codex/Hermes produzidos pelas Tasks 01–02.
  Produces: instruções equivalentes por runtime, sem pressupostos exclusivos de Claude.
Steps:
- [ ] Escrever assertions falhas para ausência de `${CLAUDE_PLUGIN_ROOT}`, `/mcp` obrigatório e comandos Claude no núcleo da skill.
- [ ] Rodar assertions e confirmar RED contra o texto atual.
- [ ] Refatorar skill, referência runtime, READMEs e status com setup Codex/Hermes e comando `hermes mcp add`.
- [ ] Rodar assertions GREEN, `git diff --check` e validação Markdown estrutural disponível.
- [ ] Confirmar que o núcleo mantém as regras ITSM e nenhuma credencial aparece.
- [ ] Commitar com mensagem convencional e trailers.

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

## Self-review

- Coverage: AC 1–2 → Tasks 01/04; AC 3 → Task 02; AC 4–5 → Task 03; AC 6–7 → Tasks 01–04.
- No placeholders, reticências ou referências a tarefas implícitas.
- Interfaces são compatíveis: Task 01 produz assertions/manifesto consumidos pela Task 02; Tasks 01–02 produzem adapters consumidos pela Task 03; Task 03 produz documentação consumida pela Task 04.
