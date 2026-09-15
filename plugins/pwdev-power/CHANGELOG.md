# Changelog — pwdev-power

Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/). Versão do plugin nos
três manifestos (`.claude-plugin`, `.codex-plugin`, `.hermes-plugin`).

## [0.2.0] — 2026-09-15

### Alterado
- Refatoração com a `skill-refactor` (pwdev-skills), medida antes e depois: as onze skills que
  mandavam ler referências inteiras "before acting" passam a lê-las **sob condição no ponto de uso**
  (safety antes de git/fleet/escrita fora de `.planning/power/`; collaboration num gate ou quando
  um status volta; artifacts antes de escrever `config.json`/`state.md`/`plan.md`; context quando o
  mapa existe; runtime antes do primeiro despacho; model-profiles no Claude Code antes de escolher
  modelo), e cada regra obrigatória dessas referências ganhou uma linha de invariante no núcleo, para
  não depender de uma leitura que talvez não aconteça.
- `power-execute`: §Model selection e §Waiting deixam de reescrever `runtime.md`; `power-init`:
  §Staleness deixa de reescrever `context.md`; `power-plan` e `power-brainstorm` deixam de repetir
  a regra do mapa que `context.md` já dá. Nada foi removido do plugin: o que saiu do núcleo já
  estava na referência.
- `power-quick` **mantida no texto 0.1.0**: na avaliação comportamental a versão refatorada
  regrediu no OpenCode (`big-pickle`, caso "mudança rápida sem scope creep": 0/4 aceitos contra
  3/4 da anterior; no Claude Sonnet 5, 1/1 nas duas). O critério fixado antes da rodada — regressão
  em qualquer modelo mantém a versão anterior daquela skill — decidiu.
- Sem mudança em descrições, scripts, hooks, agentes, comandos ou testes.

### Medido
- Carga por ativação (corpo + referências lidas incondicionalmente, tiktoken `o200k_base`), soma das
  15 skills: ver `evals/benchmarks/2026-09-15/` (`tokens-before.json`, `tokens-after.json`, `report.md`).

## [0.1.0] — 2026-09-06

- Primeira versão publicada no marketplace.
