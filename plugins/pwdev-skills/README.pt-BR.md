# PWDEV Skills — Engenharia de Skills (Claude Code, Codex, Hermes)

Revisa, refatora e faz benchmark de Agent Skills no Claude Code, no Codex e no Hermes Agent. O
benchmark também roda no OpenCode. O plugin traz uma skill, `skill-refactor`, e os scripts que ela
usa para medir uma skill nos modelos realmente disponíveis nesta máquina.

> [English version](./README.md) · [Manual de uso](./docs/manual-de-uso.md)

## O que vem dentro

| Parte | Finalidade |
| --- | --- |
| [`skills/skill-refactor/SKILL.md`](./skills/skill-refactor/SKILL.md) | Revisar ou refatorar uma skill: núcleo menor, referências condicionais, comportamento preservado, perfis lean/guided |
| `references/refactoring.md` | Protocolo de refatoração, as dez regras de otimização e escolha de perfil por medição |
| `references/evaluation.md` | Avaliação A/B: aceite, custo por tarefa aceita, contexto, precisão e cobertura de acionamento |
| `references/runtimes.md` | Contrato headless por runtime: comandos, fontes de uso e custo, regras de segurança |
| `scripts/discover.py` | Quais runtimes estão instalados e autenticados, modelo e esforço padrão de cada um, e os modelos disponíveis |
| `scripts/tokens.py` | Tamanho por arquivo, camada de contexto e cenário de carga com tokenizador genérico (`tiktoken`) |
| `scripts/bench.py` + `runtimes.py` + `grade.py` | Benchmark A/B headless entre runtimes e modelos, avaliado objetivamente, com orçamento |
| `evals/evals.json` | Fixture, casos, verificações de acionamento e roteamento, matriz padrão e preços datados |

Inclui 1 skill. Sem comandos, subagentes, hooks ou servidor MCP.

## Requisitos

- Python 3.10 ou superior para os scripts. `pip install tiktoken` para contagem medida de tokens; sem ele, os tamanhos saem rotulados como `estimate`.
- Para benchmark: os runtimes que você quer medir no `PATH` e já autenticados (`claude`, `codex`, `hermes`, `opencode`). Rode `scripts/discover.py` para ver o que está utilizável.

## Setup

Clone este marketplace e trabalhe a partir da raiz. Nada se instala sozinho nem altera configuração pessoal.

**Claude Code**: instale pelo marketplace ou carregue o checkout para uma sessão:

```bash
claude plugin install pwdev-skills@pwdev-claude-marketplace
claude --plugin-dir ./plugins/pwdev-skills
```

A skill fica disponível como `pwdev-skills:skill-refactor` e é acionada por pedidos como "revise esta SKILL.md".

**Codex**: abra este checkout e carregue `plugins/pwdev-skills` pelo mecanismo de plugin local do
Codex. O `.codex-plugin/plugin.json` declara `"skills": "./skills/"`; invoque com `$skill-refactor`.

**Hermes Agent**: inspecione o pacote antes de habilitar qualquer coisa:

```bash
hermes plugins doctor plugins/pwdev-skills
```

O adaptador registra `skill-refactor` como `pathlib.Path`, sem hook. A skill é maior que o limite de
bootstrap inline do Hermes, então fica listada e é carregada sob demanda com
`skill_view("pwdev-skills:skill-refactor")`.

## Medindo uma skill

```bash
cd plugins/pwdev-skills/skills/skill-refactor
python3 scripts/discover.py                          # runtimes, padrões e modelos disponíveis aqui
python3 scripts/tokens.py <pasta-da-skill> --baseline <versao-anterior>
python3 scripts/bench.py --skill <pasta-da-skill> --baseline git:<sha> --runtimes auto \
  --out "$(mktemp -d)" --publish evals/benchmarks/$(date +%F) --budget-usd 5
```

Use um `--out` temporário. Uma rodada grava workspaces e cópias de versão que contêm arquivos
`SKILL.md`. O `--publish` copia para dentro da skill só `summary.json`, `benchmark.md` e `tokens.json`.

## Segurança

- **Benchmark faz chamadas pagas.** Cada combinação de caso, versão, runtime, modelo e repetição é uma chamada. A execução começa pelos modelos mais baratos e para ao atingir `--budget-usd`; no Claude, cada run também leva `--max-budget-usd`.
- **Flags de bypass só em workspace descartável.** Cada chamada roda com o bypass de aprovação do runtime dentro de um diretório temporário novo. Todo caminho protegido tem impressão digital antes e depois, e qualquer alteração fora do workspace reprova o run.
- **Hermes:** o modo headless ignora aprovações, então só roda com `--acknowledge-hermes-automation`.
- **Modelos gratuitos do OpenCode Zen podem reter prompts ou usá-los para treino** ([opencode.ai/docs/zen](https://opencode.ai/docs/zen/)). Não faça benchmark de skills não publicadas ou confidenciais com eles.
- **Segurança dos segredos.** Os registros gravados passam por um sanitizador que remove tokens, chaves de API, cabeçalhos bearer e caminhos do diretório pessoal. A descoberta nunca registra e-mail, id de organização ou fragmento de chave.

## Limites

- Uma repetição de benchmark não caracteriza nada. Trate execuções únicas como direção, não como alegação de eficiência.
- O Codex em plano ChatGPT não é cobrado por token; os custos dele são equivalentes ao preço de API.
- O Claude Code não tem comando para listar modelos; a descoberta mostra os aliases documentados e as opções em cache.
- Cada runtime expõe a skill de um jeito: o Claude Code por plugin gerado, o Codex e o Hermes por `AGENTS.md`, e o OpenCode de forma nativa. Por isso, comparações de tokens entre runtimes são aproximadas.
