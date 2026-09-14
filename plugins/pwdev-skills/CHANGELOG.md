# Changelog — pwdev-skills

Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/).
Versionamento: `major.minor.patch` do plugin (`.claude-plugin/plugin.json`), igual nos
manifestos Codex e Hermes.

## [0.1.0] — 2026-09-13 (preparada, não publicada)

### Adicionado
- Plugin multi-runtime para Claude Code, Codex e Hermes Agent com a skill `skill-refactor`,
  movida de `pwdev-code`, onde nunca chegou a ser publicada.
- Contrato de revisão em três partes: achados, mudanças propostas e como verificar o efeito.
- Dez regras de otimização por modelo e escolha de perfil lean/guided por medição.
- `scripts/discover.py`: runtimes instalados e autenticados, modelo e esforço padrão com a
  origem de cada valor, e modelos disponíveis por runtime.
- `scripts/tokens.py`: tamanho por arquivo, camada e cenário de carga com tokenizador genérico.
- `scripts/bench.py`, `runtimes.py` e `grade.py`: benchmark A/B headless em Claude Code, Codex,
  Hermes e OpenCode, avaliado objetivamente, com orçamento, esforço explícito ou default
  registrado, e `--publish` para versionar só os resumos.
- Adaptador Hermes sem hook com inventário fechado; interface Codex em `agents/openai.yaml`.

### Limites
- Benchmarks de 2026-09-13 em `evals/benchmarks/` têm um caso e uma repetição: comparam modelos
  entre si e não comprovam ganho de eficiência.
- Esta entrada registra só a preparação local; publicação, release e distribuição exigem
  autorização separada.
