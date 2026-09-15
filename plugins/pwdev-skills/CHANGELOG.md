# Changelog — pwdev-skills

Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/).
Versionamento: `major.minor.patch` do plugin (`.claude-plugin/plugin.json`), igual nos
manifestos Codex e Hermes.

## [Não publicado] — 2026-09-14 a 2026-09-15

### Adicionado
- `scripts/cases.py`: casos de benchmark derivados da skill em refatoração — `--extract`
  (invariantes e defeitos por script, três pedidos-modelo, oito consultas de acionamento),
  `--propose` (uma chamada headless sem skill, resposta validada por esquema, sugestões do modelo
  mantidas fora das verificações objetivas), `--approve` (confirmação humana, `cases.json` amarrado
  ao SHA-256 do `SKILL.md`) e `--check` (deriva).
- `bench.py`: braço de controle `no_skill` (`--no-skill-arm`, o runtime recebe só o fixture e o
  pedido; no Claude Code nenhum plugin é carregado), `--cases <dir>` para conjuntos gerados
  (recusa não aprovados), fixture com a pasta inteira da skill (`fixture.files`), comparação
  pareada por caso (`paired_by_case`) no `summary.json` e no `benchmark.md`, e `--hermes-model`
  com lista de modelos.
- `grade.py`: verificações construídas do bloco `invariants` de cada caso
  (`expectations_from_spec`); o fixture `meeting-summary` passa a ser o primeiro spec.
- Catálogo (`evals/evals.json`): três modelos via OpenRouter a pedido do usuário —
  `z-ai/glm-5.3-flash`, `tencent/hy4-preview`, `deepseek/deepseek-v4.1-flash` — para Hermes
  (`--hermes-provider openrouter`) e OpenCode (`openrouter/<id>`, exige `opencode providers
  login`), com preços datados de openrouter.ai.

- OpenCode declarado como quarto runtime suportado para **usar** a skill, não só para o benchmark,
  com adaptador próprio: `.opencode-plugin/install.py` linka ou copia as skills do plugin em
  `~/.config/opencode/skills/` (ou `<projeto>/.opencode/skills/`), idempotente, com `--uninstall`
  que remove só o que instalou, `--dry-run` e `XDG_CONFIG_HOME`; a skill carrega pela ferramenta
  nativa `skill` (READMEs, manual §2, guia, README da skill, tags do catálogo; 7 testes).
- Isolamento dos braços: `--claude-disable-plugin <id>` desliga um plugin instalado só na sessão
  headless (`--settings` com `enabledPlugins`); `--isolate-user-skills` dá ao OpenCode um `HOME`
  novo; cada run começa de um workspace fresco mesmo numa segunda invocação no mesmo `--out`.
- Raiz de plugin como skill medida: `bench.py --skill <plugin>` (e `--baseline`) expõe o plugin
  inteiro por runtime (Claude `--plugin-dir`; Codex/Hermes `workspace/plugin/` + `AGENTS.md` com
  todas as skills; OpenCode só `skills/`, `references/`, `scripts/`, `templates/` sob `.opencode/`),
  para que `../../references` resolva; `summary.static_tokens` traz o tamanho por skill.
- Modo **`task`** no harness: `bench.py` mede **qualquer skill na tarefa dela** (braços = versões
  dessa skill; workspace com os arquivos de entrada; `grade.py` avalia pelas verificações
  declaradas no caso — `file_exists`, `file_absent`, `contains`, `not_contains`, `regex`, `not_regex`,
  `json_valid`, `script`; casos sem verificação utilizável são recusados antes de pagar).
  `cases.py --kind task` gera o esqueleto e `--propose` pede tarefas com arquivos sintéticos e
  verificações validadas por esquema. Antes, `bench.py`/`grade.py` só mediam a skill-refactor.
- `docs/metodologia-de-refatoracao.md` revisada com o que a aplicação de 14/09 ensinou: `evals/`
  fora do modelo de custo, invariantes extraídos por `cases.py`, bloco movido leva guardas, status
  do run vem do runtime, runs guardados para `--regrade`, regra de decisão em três braços, rótulos
  cumulativos, regra 8 sem prometer o que o `summary.json` não grava, sumário e checklist atualizados.
- `docs/guia-de-uso.md`: roteiro por cenário (revisar, refatorar, medir em três braços, casos por
  contexto, rodada com problema, como pedir), com os números da aplicação de 14/09.
- `bench.py --regrade <out>`: reclassifica e reavalia uma rodada já executada a partir do
  disco, sem nova chamada, e reescreve o resumo (a rodada grava `meta.json` com os caminhos
  não sanitizados; rodadas anteriores passam `--cases`).

### Alterado
- `skill-refactor` **0.3.0**: núcleo de 1 258 para 998 tokens (−21 %) com a descrição intacta.
  A prosa do contrato de revisão foi para `references/refactoring.md` ("The review contract") e
  a seção *Measure* para `references/runtimes.md` ("Before measuring"), lida só antes de rodar os
  scripts. Duas mudanças vieram da medição da rodada 1: os rótulos de entrega passam a ser
  cumulativos ("cada rótulo conquistado", em vez de "um ou outro") e um bloco que sai do
  núcleo leva consigo suas regras de guarda e termos obrigatórios.
- Braços nomeados pelo papel no `summary.json` (`candidate`, `baseline`, `no_skill`); as pastas
  `with_skill/` e `without_skill/` continuam para o agregador do skill-creator.
- `runtimes.py`: classificação extraída em `classify()`; cota, sobrecarga e modelo rejeitado só
  contam com saída diferente de zero ou envelope quebrado — um run limpo cuja resposta cita
  "rate limit" é `PASS` (dois runs do Codex foram perdidos assim em 2026-09-14). O record grava
  `envelope_ok` e `timed_out`.
- `grade.py`: os rótulos de entrega também são lidos nos arquivos da área de artefatos ao lado
  do alvo, onde a skill manda gravar o relatório.
- `tokens.py`: `evals/cases/` e `evals/benchmarks/` ficam fora da medição (nenhum runtime os carrega).

### Corrigido
- Classificação em camadas: stderr e eventos de erro antes do texto da resposta; queda de conexão
  do provedor (`cannot connect`, `socket … closed`, `ECONNRESET`) é `NOT_RUN`, não `FAIL`.
- `--regrade` reconstrói os runs a partir do disco (rodada interrompida ou completada em várias
  invocações); uma segunda invocação no mesmo `--out` renova a cópia da versão em vez de falhar.

### Medido
- Rodada 2a (`round-2-after/`): 0.3.0 × 0.2.1 × sem skill, 1 rep, Sonnet 5 / Terra / Ling (Hermes
  pulado a pedido; Codex parcial por cota): candidata ≥ baseline em todo modelo, `no_skill` 0/8,
  custo por tarefa aceita no Claude 0,45 × 0,66 — decisão: adotar 0.3.0 (`report.md`).
- Rodada 2b (`round-2-context/`): casos por contexto 4–6, 1/18 executado (cota Codex, Zen instável);
  sem conclusão.
- Rodada 1 (`evals/benchmarks/2026-09-14/round-1-before/`): skill 0.2.1 × sem skill, 3 casos ×
  2 reps × Sonnet 5 / Terra / Hermes default / Ling, esforço `medium` no Claude e no Codex; 47/48
  runs, US$ 7,58. Na revisão a skill decide (7/8 aceitos contra 0/8 sem skill); nos dois casos
  de edição o aceite é raro nos dois braços e o erro mais comum, mesmo com a skill, era o rótulo
  de entrega — origem das duas mudanças acima.
- Guia de origem `docs/skill-refactoring-guide.md` revisado no lugar: enquadramento neutro
  quanto a modelos, custo por camada, esforço efetivo e exposição por runtime, regras do
  avaliador, execução cortada por teto, exemplo antes/depois medido. `source_sha256` da skill
  e das referências atualizado para a nova revisão; skill em `0.2.1`. Sem mudança de
  comportamento nem de manifests.

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
