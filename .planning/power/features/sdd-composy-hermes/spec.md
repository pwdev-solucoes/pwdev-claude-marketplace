# SDD Composy Hermes — Design
Status: DRAFT
Source: solicitação de adaptação do sdd-composy para Hermes Agent
Updated: 2026-09-09

## Problem

O `sdd-composy` possui manifests para Claude Code e Codex, mas não é descoberto pelo Hermes
Agent. Seus contratos e skills precisam ser registrados no loader nativo do Hermes, mantendo
o mesmo ciclo de vida, idioma, schemas e evidências sem duplicar a lógica de negócio.

## Approach

Adicionar uma camada Hermes fina, inspirada no `pwdev-power`: plugin YAML, bootstrap de primeiro
turn, registro das skills via `ctx.register_skill`, mapeamento de ferramentas e adaptador de
execução/fleet. Os scripts e schemas compartilhados continuam sendo a fonte única.

## Decisions

### DEC-001 — Bootstrap nativo Hermes

- Options: duplicar skills; somente symlink; registrar skills via `__init__.py`.
- Choice: registrar skills e injetar bootstrap em `pre_llm_call`.
- Why: segue o contrato já validado em `pwdev-power`.
- Trade-off: depende da API de plugin do Hermes.
- Reversible: sim, removendo `.hermes-plugin`.

### DEC-002 — Runtime explícito

- Options: fallback Claude/Codex; Hermes sempre que instalado; seleção explícita.
- Choice: Hermes explícito, sem fallback silencioso.
- Why: preserva isolamento e evita executar pelo provider errado.
- Trade-off: exige instalação/configuração do Hermes.
- Reversible: sim.

### DEC-003 — Fleet via Kanban opcional

- Options: ignorar fleet; duplicar runner; ponte Hermes Kanban.
- Choice: adaptar a ponte Kanban existente e manter runner local como caminho principal.
- Why: reutiliza contratos de aprovação e idempotência já implementados.
- Trade-off: integração Kanban precisa ser testada em Hermes real.
- Reversible: sim.

## Interfaces

- `.hermes-plugin/plugin.yaml`: manifesto `sdd-composy`.
- `.hermes-plugin/__init__.py`: `register(ctx)` e hook `pre_llm_call`.
- `references/hermes-tools.md`: mapeamento de ferramentas.
- `scripts/fleet/engine-hermes.sh`: vetor de execução Hermes.
- `scripts/fleet/launch.sh` e `run.sh`: runtime `hermes` explícito.

## Constraints

- Não duplicar o conteúdo das skills.
- Não alterar schemas OKF nem contratos existentes.
- Não permitir fallback silencioso para Claude ou Codex.
- Não executar mutações sem aprovação e contrato válido.
- Manter `pt-BR` e `en-US` definidos pelo `init`.
- Provider real e cmux real devem ser marcados como não testados até validação externa.

## Out of scope

- Alterar a API ou o código do Hermes Agent.
- Reescrever o Kanban do Hermes.
- Publicar o plugin em um registry externo.

## Acceptance criteria

- Hermes descobre e registra todas as skills do `sdd-composy`.
- Primeiro turn carrega bootstrap com ferramentas e regras corretas.
- Um projeto Hermes executa `init`, `map`, `status` e `verify` usando os mesmos artefatos.
- Runner recusa runtime divergente e não usa fallback.
- Fleet Hermes mantém isolamento, hashes e gates.
- Testes simulados passam e limitações de Hermes real ficam documentadas.
