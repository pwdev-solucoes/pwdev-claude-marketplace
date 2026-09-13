# Task 03 — brief

Plan: .planning/power/features/glpi-multiruntime/plan.md
Generated: 2026-09-12T19:21:30Z

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
