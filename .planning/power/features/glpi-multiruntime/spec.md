# GLPI Multi-Runtime — Design

Status: APPROVED
Source: solicitação do owner em 2026-09-12; abordagem aprovada em conversa
Updated: 2026-09-12

## Problem

O plugin `pwdev-glpi` possui manifesto e comandos de Claude Code, mas não declara adapters para
Codex nem Hermes. A skill também pressupõe `${CLAUDE_PLUGIN_ROOT}`, `/mcp` e slash commands,
impedindo uma experiência equivalente nos três runtimes.

## Approach

Manter uma única skill e um único MCP (`@soarescbm/mcp-glpi`) como núcleo. Acrescentar o manifesto
Codex e o adapter Hermes nativo; preservar o adapter Claude existente. Claude e Codex recebem o
MCP pelo manifesto portátil. Hermes registra a skill e documenta `hermes mcp add glpi`, sem editar
configuração pessoal automaticamente.

## Decisions

### D-MR-1 — Fonte única da skill

- Decision: uma implementação de domínio para os três runtimes.
- Options: duplicar skills; skill única runtime-neutral; gerar skills por build.
- Choice: skill única runtime-neutral.
- Why: evita divergência em regras ITSM, segurança e mapeamento de tools.
- Trade-off: instruções condicionais por runtime ficam mais longas.
- Reversible: sim.

### D-MR-2 — Adapter Codex

- Decision: forma de descoberta no Codex.
- Options: somente skill; manifesto `.codex-plugin` com skills e MCP; configuração externa manual.
- Choice: `.codex-plugin/plugin.json` com `skills: "./skills/"` e `mcpServers: "./.mcp.json"`, mais `skills/glpi/agents/openai.yaml`.
- Why: segue o padrão dos plugins multi-runtime existentes e preserva instalação integrada.
- Trade-off: aceitação depende da versão do host Codex que suporta plugins portáteis.
- Reversible: sim.

### D-MR-3 — Adapter Hermes

- Decision: provisionamento do MCP no Hermes.
- Options: editar `~/.hermes/config.yaml`; plugin Python que altera configuração; setup explícito via CLI.
- Choice: `.hermes-plugin/plugin.yaml` + `__init__.py` para registrar a skill; comando guiado `hermes mcp add`.
- Why: Hermes reserva configuração MCP para o operador e plugins não devem mutar arquivos pessoais.
- Trade-off: requer uma etapa explícita de setup no Hermes.
- Reversible: sim.

### D-MR-4 — Compatibilidade de linguagem

- Decision: referências a recursos específicos de Claude.
- Options: remover tudo; manter aliases condicionais; separar apêndices runtime-specific.
- Choice: núcleo sem `${CLAUDE_PLUGIN_ROOT}`, `/mcp` ou slash commands; apêndice de comandos por runtime nos READMEs.
- Why: a skill pode ser carregada por Codex/Hermes sem instruções inválidas.
- Trade-off: Claude perde alguns atalhos implícitos no texto central, preservados no apêndice.
- Reversible: sim.

## Interfaces

```text
Claude: .claude-plugin/plugin.json + .mcp.json + commands/* + skills/glpi/SKILL.md
Codex:  .codex-plugin/plugin.json + .mcp.json + skills/glpi/agents/openai.yaml
Hermes: .hermes-plugin/plugin.yaml + .hermes-plugin/__init__.py + skills/glpi/SKILL.md
MCP:    server glpi, command npx -y @soarescbm/mcp-glpi@0.4.0
```

O namespace da skill deve permanecer `glpi` no Claude/Hermes e `$glpi` no Codex. As tools MCP,
prompts e resources não mudam.

## Constraints

- Preservar exatamente 20 tools, 2 prompts e 3 resources MCP.
- Preservar GLPI 10.x/11.x via Legacy V1 e MCP `0.4.0`.
- Preservar `GLPI_BASE_URL`, `GLPI_PAT`, `GLPI_APP_TOKEN`, `GLPI_USE_SESSION`, `GLPI_TIMEOUT_MS`.
- Não editar `~/.hermes/config.yaml`, `~/.claude.json`, `~/.codex` ou qualquer configuração pessoal.
- Não duplicar a lógica da skill nem criar um segundo servidor MCP.
- O corpo de `skills/glpi/SKILL.md` não pode conter os nomes literais dos arquivos de instruções
  proibidos pelo loader Hermes; referências devem ser indiretas/runtime-neutral.
- Manter comandos slash existentes somente para Claude; Codex/Hermes usam a skill compartilhada.
- Versão do plugin: `1.2.0` em todos os manifests.
- Testes de provider real são informativos; mocks e testes estruturais não podem alegar aceitação
  real em Codex/Hermes.
- Nenhum publish, release, tag, push ou merge nesta fase.

## Out of scope

- Implementação nativa de tools GLPI em Python no Hermes.
- OAuth2/API V2 do GLPI.
- Alteração do servidor MCP ou dos schemas públicos.
- Escrita automática em configurações de usuário.
- Publicação no marketplace ou npm.

## Acceptance criteria

1. Os manifests Claude, Codex e Hermes são válidos e declaram a mesma versão `1.2.0`.
2. Claude e Codex referenciam o mesmo `.mcp.json` e MCP `0.4.0`.
3. Hermes registra a skill `glpi` nos layouts clone e flattened e não modifica configuração pessoal.
4. A skill não contém pressupostos exclusivos de Claude que impeçam Codex/Hermes.
5. READMEs e setup explicam os três runtimes, incluindo o comando Hermes para configurar o MCP.
6. Testes estruturais cobrem manifests, bootstrap Hermes, skill catalogue e preservação 20/2/3.
7. Nenhuma credencial aparece em manifests, testes, fixtures ou documentação.

## Risks

- O schema de plugins Codex/Hermes pode evoluir; fixtures estruturais devem detectar divergência.
- Hermes portable MCP pode ter limitações de descoberta; o setup explícito é o fallback deliberado.
- A skill pode ficar excessivamente condicional; manter o núcleo curto e os detalhes nos READMEs.
