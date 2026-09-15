# Manual de uso — pwdev-skills

Guia prático do plugin `pwdev-skills` e da skill `skill-refactor`: instalar, pedir uma revisão
ou refatoração, descobrir o que roda na sua máquina, medir tamanho em tokens, rodar benchmark
entre modelos e ler os resultados. Para um roteiro por cenário — o que dizer ao agente e o que
esperar — comece pelo [Guia de uso](./guia-de-uso.md); o método por trás de cada passo está
detalhado em [Metodologia de refatoração](./metodologia-de-refatoracao.md).

> Versão do plugin: 0.1.0 · Runtimes: Claude Code, Codex, Hermes Agent (o benchmark também roda OpenCode)

## Sumário

1. [O que é e quando usar](#1-o-que-é-e-quando-usar)
2. [Instalação](#2-instalação)
3. [Fluxo recomendado](#3-fluxo-recomendado)
4. [Usando a skill](#4-usando-a-skill)
5. [Descobrir runtimes e modelos — `discover.py`](#5-descobrir-runtimes-e-modelos--discoverpy)
6. [Medir tamanho — `tokens.py`](#6-medir-tamanho--tokenspy)
7. [Benchmark — `bench.py`](#7-benchmark--benchpy)
8. [Lendo os resultados](#8-lendo-os-resultados)
9. [Perfis lean e guided](#9-perfis-lean-e-guided)
10. [Custos](#10-custos)
11. [Segurança e dados](#11-segurança-e-dados)
12. [Solução de problemas](#12-solução-de-problemas)
13. [Limites](#13-limites)
14. [Referência rápida](#14-referência-rápida)

---

## 1. O que é e quando usar

A `skill-refactor` revisa ou refatora uma skill existente (`SKILL.md` e seus recursos). O objetivo
é um núcleo menor, carregado sempre, com referências lidas só quando necessárias, sem perder
comportamento. Os scripts que acompanham a skill medem se isso ficou de fato mais eficiente, e
em quais modelos.

**Use quando:**
- uma skill repete regras em vários lugares;
- carrega referências em toda execução em vez de sob condição;
- dispara em tarefas que não são dela, ou deixa de disparar quando deveria;
- você precisa saber em quais modelos ela funciona e a que custo.

**Não use para:** criar uma skill do zero, refatorar código de aplicação, traduzir uma skill
literalmente, ou executar a tarefa da própria skill-alvo.

**O que vem no pacote:**

| Parte | Serve para | Funciona com qualquer skill? |
| --- | --- | --- |
| `SKILL.md` | Revisão e refatoração conduzidas pelo agente | Sim |
| `scripts/discover.py` | Ver runtimes, modelos e padrões disponíveis | Sim (independe da skill) |
| `scripts/tokens.py` | Medir tamanho por arquivo, camada e cenário | Sim |
| `scripts/bench.py` + `runtimes.py` + `grade.py` | Benchmark A/B entre modelos | **Não**: usa os casos e a fixture da própria `skill-refactor` (veja [§7](#7-benchmark--benchpy)) |
| `references/*.md` | Protocolo de refatoração, avaliação e contrato de runtime | — |

## 2. Instalação

**Requisitos:**
- Python 3.10 ou superior para os scripts.
- Recomendado: `pip install tiktoken`. Sem ele, os tamanhos saem com o rótulo `estimate`.
- Para benchmark: os runtimes no `PATH` e já autenticados.

### Claude Code

```bash
claude plugin install pwdev-skills@pwdev-claude-marketplace
# ou, só para esta sessão, a partir do checkout:
claude --plugin-dir ./plugins/pwdev-skills
```

A skill fica disponível como `pwdev-skills:skill-refactor` e dispara por pedidos em linguagem natural.

### Codex

Abra o checkout do marketplace e carregue `plugins/pwdev-skills` pelo mecanismo de plugin local
(o manifesto declara `"skills": "./skills/"`). Invoque com `$skill-refactor`.

### Hermes Agent

```bash
hermes plugins doctor plugins/pwdev-skills
```

O adaptador registra a skill sem hook. Como ela é maior que o limite de injeção inicial do
Hermes, fica listada e carrega sob demanda com `skill_view("pwdev-skills:skill-refactor")`.

## 3. Fluxo recomendado

```
1. descobrir   → discover.py          o que roda aqui, com qual modelo e esforço
2. revisar     → pedido à skill       achados + mudanças + como medir (sem editar)
3. refatorar   → pedido à skill       edição autorizada, baseline preservado
4. medir       → tokens.py --baseline tamanho antes x depois, por camada
5. comparar    → bench.py             A/B nos modelos listados no passo 1
6. decidir     → summary.json         perfil e modelo pelo custo por tarefa aceita
```

Tamanho menor não é ganho por si só. A decisão é sempre pelo **custo por tarefa aceita**, dentro
de um limite de qualidade definido antes de rodar.

## 4. Usando a skill

### Revisão (não edita nada)

```text
Revise plugins/meu-plugin/skills/resumo/SKILL.md sem editar arquivos.
Aponte o que reduziria contexto e como medir o efeito.
```

A resposta segue um contrato em três partes:
1. **Achados**, cada um nomeado por categoria (duplicação, contradição, leitura incondicional,
   descrição ampla ou restrita demais, procedimento sem finalidade) e com as linhas de origem.
2. **Mudanças propostas**, cada uma ligada ao achado que resolve e ao requisito que preserva.
3. **Como verificar o efeito**: tamanho com `tokens.py`, depois A/B com `bench.py` decidido pelo
   custo por tarefa aceita. Uma revisão nunca é evidência de eficiência.

### Refatoração (edição autorizada)

```text
Refatore plugins/meu-plugin/skills/resumo/SKILL.md e seus recursos.
Consumidores: modelo X no perfil lean; demais modelos em guided.
Preserve os requisitos atuais e prepare os casos de avaliação.
Baseline e relatório em .planning/refactor/resumo/.
```

A skill preserva um baseline dos arquivos originais, aplica a mudança, verifica frontmatter, links
e comportamento obrigatório, e fecha a entrega com **todos os rótulos conquistados** (eles se
acumulam; uma refatoração sem benchmark termina `refactored, statically validated`):

| Rótulo | Significa |
| --- | --- |
| `refactored` | O arquivo foi alterado |
| `statically validated` | Frontmatter, links e requisitos conferidos sem executar modelos |
| `behaviorally evaluated` | Rodou em modelos reais; vale **só** para os pares (runtime, modelo) executados |

### Dicas de pedido
- Diga explicitamente se é **revisão** (só leitura) ou **refatoração** (edição).
- Indique o perfil dos consumidores. Sem essa informação, a skill usa `guided` (veja [§9](#9-perfis-lean-e-guided)).
- Indique onde gravar baseline e relatório.
- Não peça benchmark sem informar orçamento e quais modelos usar.

## 5. Descobrir runtimes e modelos — `discover.py`

Somente leitura. Rode antes de planejar qualquer benchmark.

```bash
cd plugins/pwdev-skills/skills/skill-refactor
python3 scripts/discover.py                  # visão em Markdown
python3 scripts/discover.py --json           # dados completos
python3 scripts/discover.py --runtimes codex,opencode --limit 20
```

| Opção | Efeito |
| --- | --- |
| `--runtimes` | Lista separada por vírgula (padrão: `claude,codex,hermes,opencode`) |
| `--json` | Saída JSON completa |
| `--limit N` | Modelos por runtime na visão Markdown (padrão 12) |
| `--cases` | `evals.json` com a tabela de preços usada para o Codex |

O relatório mostra, para cada runtime:
- se está instalado e autenticado;
- versão;
- modelo e esforço padrão, com a origem de cada valor;
- os modelos disponíveis, com a fonte da lista.

| Runtime | Fonte dos modelos |
| --- | --- |
| Claude Code | Não existe comando de listagem: aliases do `claude --help` mais opções em cache. IDs completos (ex.: `claude-sonnet-5`) também são aceitos |
| Codex | `codex debug models`, com esforço padrão e níveis por modelo |
| Hermes | Cache do provedor configurado (`~/.hermes/provider_models_cache.json`) |
| OpenCode | `opencode models --verbose`, com variantes, contexto e preço |

Nenhum e-mail, id de organização ou fragmento de chave vai para a saída.

## 6. Medir tamanho — `tokens.py`

```bash
python3 scripts/tokens.py <pasta-da-skill>
python3 scripts/tokens.py <pasta-da-skill> --baseline <versao-anterior>
python3 scripts/tokens.py <pasta-da-skill> --json
```

| Opção | Efeito |
| --- | --- |
| `--baseline <dir>` | Mostra o Δ por arquivo, camada e cenário |
| `--json` | Saída JSON |
| `--encoding` | Encoding do tiktoken (padrão `o200k_base`) |
| `--no-tiktoken` | Força a estimativa `chars/4`, com rótulo |

**Como ler.** Cada camada é paga numa frequência diferente, e deve ser otimizada nessa ordem:

| Camada | Quando entra no contexto |
| --- | --- |
| `SKILL.md#description` | Em **toda** conversa (catálogo de skills) |
| `SKILL.md#body` | A cada ativação da skill |
| `references/*.md` | Só quando a condição de leitura é atendida |

Os cenários somam o que realmente é carregado em cada tipo de pedido: só revisão, refatoração,
refatoração com avaliação e pior caso. Scripts não entram na conta, porque são executados e não lidos.

## 7. Benchmark — `bench.py`

> **Faz chamadas pagas.** Leia [§10](#10-custos) e [§11](#11-segurança-e-dados) antes.

**O que ele mede.** Os três casos de `skill-refactor/evals/evals.json`, aplicados à skill de
exemplo `meeting-summary` (propositalmente com problemas):

| id | Caso | Verifica |
| ---: | --- | --- |
| 1 | `mixed_consumers_edit` | Refatoração real preservando nome, `paths`, extensões, rótulos e regras do CSV |
| 2 | `unknown_model_explicit_override` | Perfil padrão `guided` sem modelo conhecido; separação de perfis |
| 3 | `review_only` | Revisão sem nenhuma escrita, com achados por categoria, A/B proposto e métricas do protocolo |

Ou seja, por padrão ele avalia **uma versão da skill-refactor** nesses casos. Para avaliar outra
skill com casos do domínio dela, gere-os com `cases.py` (abaixo) e passe a pasta em `--cases`.

**Braços.** Cada caso roda em até três braços, sempre no mesmo runtime e modelo:

| Braço | O que o runtime recebe | Pasta no `--out` |
| --- | --- | --- |
| `candidate` | a skill em `--skill` | `with_skill/` |
| `baseline` | a versão anterior em `--baseline` | `without_skill/` |
| `no_skill` | só o fixture e o pedido (`--no-skill-arm`) | `no_skill/` |

`baseline` × `candidate` responde "a refatoração melhorou?"; `no_skill` × `candidate` responde
"a skill acrescenta alguma coisa neste caso?". Se `no_skill` empata ou vence a candidata num
caso, a skill não está agregando ali — isso é um achado, não um ruído.

### Opções

| Opção | Padrão | Efeito |
| --- | --- | --- |
| `--skill <dir>` | obrigatório | Versão candidata |
| `--baseline <dir \| git:<sha> \| git:<sha>:<caminho>>` | nenhum | Versão anterior; habilita o braço `baseline`. `git:<sha>` acha a skill pelo nome se ela mudou de pasta; se houver mais de uma cópia naquele commit, informe o caminho |
| `--no-skill-arm` | desligado | Acrescenta o braço `no_skill`: o runtime recebe só o fixture e o pedido |
| `--cases <arquivo \| dir>` | `evals/evals.json` | Outro `evals.json`, ou uma pasta gerada por `cases.py` (lê `cases.json` e recusa conjunto não aprovado) |
| `--out <dir>` | obrigatório | Diretório de trabalho da rodada. **Use um temporário** |
| `--publish <dir>` | nenhum | Copia só `summary.json`, `benchmark.md` e `tokens.json` |
| `--runtimes` | `claude,codex,hermes` | Lista, ou `auto` (tudo que o `discover.py` marca como utilizável) |
| `--claude-models` / `--codex-models` / `--opencode-models` | `default` | Lista separada por vírgula; `default` = sem `--model` |
| `--hermes-model` | — | Obrigatório com Hermes: um ou mais slugs do provedor separados por vírgula, ou `default` |
| `--hermes-provider` | configurado | Ex.: `openrouter`. O catálogo (`evals/evals.json`, `matrix`) traz três modelos OpenRouter para Hermes e OpenCode: `z-ai/glm-5.3-flash`, `tencent/hy4-preview` e `deepseek/deepseek-v4.1-flash` (no OpenCode, com prefixo `openrouter/` e depois de `opencode providers login`) |
| `--<runtime>-effort` | padrão configurado | Esforço explícito (`--effort`, `-c model_reasoning_effort=`, `--reasoning`, `--variant`) |
| `--only-case N` | todos | Repetível. Ex.: `--only-case 3` para só revisão |
| `--reps N` | 1 | Repetições por combinação |
| `--budget-usd` | 5 | Teto da rodada; runs seguintes viram `NOT_RUN` |
| `--timeout` | 300 | Segundos por run |
| `--acknowledge-hermes-automation` | desligado | Obrigatório para rodar Hermes de verdade |
| `--dry-run --fake-bin <dir>` | — | Pipeline completo com executáveis falsos, sem custo |
| `--no-skill-creator` | — | Não chama o agregador e o visualizador do skill-creator |

A rodada executa dos modelos mais baratos para os mais caros e para ao atingir o orçamento.

### Receitas

**Smoke barato (só revisão, um modelo por runtime):**
```bash
python3 scripts/bench.py --skill . --only-case 3 \
  --runtimes claude,codex --claude-models claude-haiku-4-5-20251001 --codex-models gpt-5.6-luna \
  --budget-usd 1 --out "$(mktemp -d)" --no-skill-creator
```

**Comparar modelos do mesmo runtime:**
```bash
python3 scripts/bench.py --skill . --only-case 3 --runtimes codex \
  --codex-models gpt-5.6-luna,gpt-5.6-terra,gpt-5.6-sol,gpt-6-astra \
  --budget-usd 10 --timeout 1800 --out "$(mktemp -d)"
```

**Cada runtime no seu padrão (modelo e esforço registrados):**
```bash
python3 scripts/bench.py --skill . --only-case 3 --runtimes claude,codex,hermes \
  --claude-models default --codex-models default --hermes-model default \
  --acknowledge-hermes-automation --budget-usd 6 --timeout 1800 --out "$(mktemp -d)"
```

**Runtimes com o mesmo esforço (comparação justa entre ferramentas):**
```bash
python3 scripts/bench.py --skill . --only-case 3 --runtimes claude,codex \
  --claude-models claude-sonnet-5 --codex-models gpt-5.6-terra \
  --claude-effort medium --codex-effort medium \
  --budget-usd 3 --out "$(mktemp -d)"
```

**A/B da versão antiga contra a nova, publicando os resumos:**
```bash
python3 scripts/bench.py --skill . --baseline git:dc80270:plugins/pwdev-code/skills/skill-refactor \
  --runtimes auto --hermes-model default \
  --acknowledge-hermes-automation --budget-usd 5 \
  --out "$(mktemp -d)" --publish evals/benchmarks/$(date +%F)
```

**Três braços (antes, sem skill e depois) com esforço igual:**
```bash
python3 scripts/bench.py --skill . --baseline git:<sha-antes> --no-skill-arm \
  --runtimes claude,codex,hermes,opencode \
  --claude-models claude-sonnet-5 --codex-models gpt-5.6-terra \
  --hermes-model default --opencode-models opencode/ling-3.0-flash-fin-free \
  --claude-effort medium --codex-effort medium --reps 2 --timeout 1800 \
  --acknowledge-hermes-automation --budget-usd 10 \
  --out "$(mktemp -d)" --publish evals/benchmarks/$(date +%F)/round-2-after
```

**Validar o pipeline sem gastar nada (na raiz do marketplace):**
```bash
python3 -m unittest tests.test_skill_refactor_bench tests.test_skills_packaging
```

### Por que `--out` temporário

A rodada grava workspaces e cópias da skill, e cada uma contém um `SKILL.md`. Se isso ficar dentro
do plugin, as verificações de inventário contam essas cópias como skills extras. Use `--publish`
para trazer só os resumos.

### Não edite a skill durante uma rodada

O runtime recebe uma cópia, então editar a original não afeta os runs. Mesmo assim, o resultado
passa a descrever um alvo em movimento: o `summary.json` lista os arquivos alterados em
`source_skill_changed_during_round`, e uma rodada que passaria fica com o veredito
`PASS_WITH_SOURCE_DRIFT`.

### Casos por contexto — `cases.py`

O benchmark padrão conhece só o fixture `meeting-summary`. Para medir uma refatoração com casos
da própria skill que está sendo refatorada, `cases.py` produz o conjunto em três etapas, cada uma
deixando um arquivo que a seguinte lê:

```bash
python3 scripts/cases.py --extract <pasta-da-skill>                 # sem custo -> evals/cases/<nome>/cases.draft.json
python3 scripts/cases.py --propose <pasta-dos-casos> --runtime claude --model claude-sonnet-5 --effort medium
python3 scripts/cases.py --approve <pasta-dos-casos> --skill <pasta-da-skill>   # pergunta; grava cases.json
python3 scripts/bench.py --skill <pasta-da-skill> --cases <pasta-dos-casos> ...
```

1. **`--extract`** lê a skill e deriva os **invariantes** (nome, `paths`, `metadata` estável,
   literais `CHAVE=valor`, rótulos de saída recorrentes, proibições `never/do not`, blocos
   opcionais com seus termos e regra de guarda, marcadores do idioma), os defeitos que consegue
   detectar por categoria, três pedidos-modelo (refatoração com consumidores mistos, refatoração
   sem modelo conhecido, revisão) e oito consultas de acionamento. O fixture leva a pasta inteira
   da skill, menos `evals/`, arquivos ocultos e nomes que sugerem segredo.
2. **`--propose`** faz **uma** chamada headless, sem skill carregada, com a skill em `./target` e
   o rascunho em `./draft.json`, e pede JSON com dois ou três pedidos realistas no domínio da
   skill e oito a dez consultas de acionamento próximas (positivas e negativas). A resposta passa
   por validação de esquema. **Nada que o modelo escreve vira verificação objetiva**: os pedidos
   propostos usam os invariantes extraídos, e sugestões de invariantes ficam em
   `llm_suggested_invariants` até alguém movê-las à mão.
3. **`--approve`** imprime o conjunto, pede confirmação (ou `--yes`) e grava `cases.json` com
   `approved: true` e o SHA-256 do `SKILL.md` de origem. `--check` avisa se a skill mudou desde a
   aprovação; o `bench.py` recusa um `cases.json` não aprovado.

O `grade.py` lê o bloco `invariants` de cada caso e constrói as verificações a partir dele
("Preserves name: …", "Preserves the literal …", "<tópico> detail is conditional"), em vez de
conhecer um fixture fixo. Os casos de `evals.json` sem `invariants` continuam usando os do
`meeting-summary`.

### Regradar uma rodada sem pagar de novo — `--regrade`

Toda correção do avaliador ou do classificador vale para rodadas já pagas:

```bash
python3 scripts/bench.py --regrade <out-da-rodada> --cases evals/evals.json --publish evals/benchmarks/<data>
```

Reconstrói a lista de runs **a partir do disco** (serve para rodada interrompida e para rodada
completada em várias invocações no mesmo `--out`, um runtime por vez), reclassifica cada
`record.json` (guardando o status anterior em `reclassified_from`), reavalia, reescreve
`summary.json`/`benchmark.md` e, com `--publish`, republica. A rodada grava `meta.json` com os
caminhos não sanitizados; para rodadas anteriores a ele, passe `--cases`.

### `grade.py`

É chamado automaticamente pelo `bench.py`. Para reavaliar um run isolado:

```bash
python3 scripts/grade.py <run_dir> --case caso.json --fixture fixture.md
```

## 8. Lendo os resultados

Uma rodada gera, em `--out`:

```
summary.json        tabela de eficiência por modelo, versões, custo, cada run
benchmark.md        a mesma tabela em Markdown
tokens.json         tamanhos das versões comparadas
eval-<id>-<caso>/<config>/run-<n>-<runtime>-<modelo>/
    record.json     o que o runtime reportou
    grading.json    cada expectativa com passed e evidence
    result.txt      resposta do modelo
    outputs/        artefatos do run
```

### Status de um run (`record.json`)

| Status | Significa | Conta como evidência? |
| --- | --- | --- |
| `PASS` | O runtime concluiu e o envelope veio válido | Sim; veja o `grading.json` para o mérito |
| `FAIL` | Exit diferente de zero, envelope inválido ou caminho protegido alterado | Sim |
| `BLOCKED` | Timeout ou falta de consentimento (Hermes) | Não |
| `NOT_RUN` | Executável ausente, modelo rejeitado, cota, provedor indisponível, teto de orçamento | **Não**: não diz nada sobre a skill |

### Campos que importam

| Campo | Onde | Como ler |
| --- | --- | --- |
| `model_effective` / `effort_effective` (+ `_source`) | `record.json` | Modelo e esforço usados, e de onde veio cada um |
| `model_observed` | `record.json` | O modelo que o runtime diz ter usado; `null` no Codex, que não informa |
| `usage.context_tokens` | `record.json` | Entrada acumulada real: fresca + cache lido + cache gravado |
| `cost_usd` + `cost_source` | `record.json` | `runtime` (Claude, OpenCode), `pricing_table` (Codex, equivalente à API), `estimated` (Hermes) |
| `pass_rate` | `grading.json` | Fração de expectativas atendidas |
| `acceptance_rate` | `summary.json` | Fração de runs com **todas** as expectativas atendidas |
| `cost_per_success_usd` | `summary.json` | Custo total, inclusive falhas, dividido pelos runs aceitos. **É a métrica de decisão** |

### Comparação pareada (`paired_by_case`)

Além das médias por modelo, o `summary.json` traz `paired_by_case`: para cada (caso, runtime,
modelo), os braços lado a lado — runs, aceitos, taxa de aceite, média de expectativas, custo por
tarefa aceita e p50 de contexto. O `benchmark.md` mostra a mesma coisa na tabela "Paired by
case". É nessa tabela, e não na média geral, que a decisão do §10.5 da metodologia se apoia:
candidata contra baseline **dentro de cada modelo**, e `no_skill` como controle.

### Antes de acreditar numa falha

Leia o `evidence` da expectativa que falhou. Na validação de 13/09, o grader teve quatro falsos
resultados, todos já corrigidos:
- texto em português não casava com a palavra "static";
- a separação entre estático e medido estava escrita com outras palavras;
- a métrica proibida aparecia só citada, como proibição;
- o termo estava em português ("precisão").

Reprovação não é, automaticamente, falha do modelo.

## 9. Perfis lean e guided

| Perfil | Núcleo | Apoio extra | Quando escolher |
| --- | --- | --- | --- |
| `lean` | Resultado, invariantes, referências condicionais, verificação | Exemplos só para ambiguidade real | Menor custo por tarefa aceita que `guided` naquele modelo, com aceite dentro do limite |
| `guided` | Mesmos requisitos e permissões | Sequência curta, exemplo resolvido, erro frequente, checklist | Padrão sem medição, ou quando `lean` não atingiu o limite de aceite |

Regras:
- **Seleção explícita no pedido sempre vence.**
- **Perfil vem de medição, nunca do nome do modelo.** Sem medição, `guided`.
- **Consumidores mistos:** um núcleo só, mais apoio guiado com condição de leitura explícita. Nunca uma cópia da skill por modelo.

As dez regras de otimização completas estão em `references/refactoring.md` (1 a 5) e em
`references/evaluation.md` (6 a 10).

## 10. Custos

Valores observados em 2026-09-13, no caso `review_only`, com uma repetição. **São referência de
ordem de grandeza, não tabela de preço.**

| Runtime | Modelo | Custo por run | Tempo | Resultado |
| --- | --- | ---: | ---: | --- |
| Claude Code | `claude-haiku-4-5-20251001` | US$ 0,04 | 29 s | 4/7 |
| Claude Code | `claude-sonnet-5` | US$ 0,28 | 110 s | 7/7 |
| Claude Code | `claude-opus-5` @ high | US$ 0,67 | 87 s | 7/7 |
| Claude Code | `claude-fable-5-1` | US$ 1,55 | 86 s | 7/7 |
| Codex | `gpt-5.6-luna` | US$ 0,008* | 48 s | 7/7 |
| Codex | `gpt-5.6-terra` | US$ 0,07* | 33 s | 7/7 |
| Codex | `gpt-5.6-sol` @ low | US$ 0,14–0,15* | 40–44 s | 7/7 |
| Codex | `gpt-6-astra` | US$ 0,33* | 33 s | 7/7 |
| Hermes | `deepseek-v4-flash` (OpenRouter) | US$ 0,004–0,013 (estimado) | 85–302 s | 6–7/7 |
| OpenCode | modelos gratuitos do Zen | US$ 0 | 15–74 s | 7/7 |

\* Equivalente ao preço de API. O Codex no plano ChatGPT não é cobrado por token.

**Cuidados:**
- **O teto por run do Claude corta no meio do turno e o valor gasto é cobrado mesmo sem resposta.**
  Com teto de US$ 0,75, o Fable gastou US$ 1,05 e não entregou nada. Dimensione o teto pela taxa do
  modelo mais caro da rodada, não pelo mais barato.
- O `--budget-usd` é da rodada inteira. Um run pode ultrapassar um pouco antes da parada.
- Falhas e retentativas entram no custo por sucesso.

## 11. Segurança e dados

- **Bypass só em workspace descartável.** Cada run usa o modo sem aprovação do runtime
  (`--dangerously-skip-permissions`, `--dangerously-bypass-approvals-and-sandbox`, `--yolo`) dentro de
  um diretório temporário novo. Os caminhos protegidos ganham impressão digital antes e depois, e
  qualquer alteração fora do workspace reprova o run.
- **Hermes** exige `--acknowledge-hermes-automation`. O harness nunca usa `--ignore-rules` nem `--safe-mode`.
- **Modelos gratuitos do OpenCode Zen retêm prompts ou os usam para treino**
  ([opencode.ai/docs/zen](https://opencode.ai/docs/zen/)). Cada run envia a skill inteira. Não use esses
  modelos com skills não publicadas ou confidenciais.
- **Sanitização.** Tokens, chaves de API, cabeçalhos bearer e caminhos do seu diretório pessoal são
  removidos de tudo que é gravado.
- **Configuração pessoal nunca é alterada.** Para validar uma instalação no Codex sem mexer na sua
  configuração, use um `CODEX_HOME` temporário.

## 12. Solução de problemas

| Sintoma | Causa | O que fazer |
| --- | --- | --- |
| Codex `NOT_RUN: runtime quota or usage limit` | Cota do plano esgotada | Esperar o reset informado na mensagem |
| Claude `NOT_RUN: per-run budget … reached` | `--max-budget-usd` cortou o turno | Aumentar `--budget-usd` para esse modelo (com uma rodada só dele, o teto por run é o total) |
| OpenCode `NOT_RUN: provider unavailable … 502 … overloaded` | Provedor gratuito sobrecarregado | Tentar mais tarde ou usar outro modelo |
| Hermes estoura o timeout | Contexto enorme ou lentidão do provedor | Aumentar `--timeout` (1800) e repetir; o tempo varia muito entre execuções |
| Hermes: `Unknown skill(s)` | Uso de `--skills` com um nome não confiado | O harness não usa essa opção; se aparecer, a versão do `runtimes.py` está desatualizada |
| Run `FAIL: a protected path changed` | Algo foi escrito fora do workspace, ou a cópia da skill foi editada | Ver `record.protected_diff` |
| Rodada `PASS_WITH_SOURCE_DRIFT` | A skill original foi editada durante a rodada | Refazer depois de terminar as edições |
| Tamanhos com rótulo `estimate` | `tiktoken` não instalado | `pip install tiktoken` |
| Teste de inventário acusa skills extras | Rodada gravada dentro do plugin | Usar `--out` temporário e `--publish` |
| `--baseline git:<sha>`: "found at N other paths" | A skill existia em mais de uma pasta naquele commit | Usar `git:<sha>:<caminho>` |
| `model_observed` vazio no OpenCode | Versão antiga do adaptador lia o `export` por pipe (trunca em 64 KiB) | Atualizar o `runtimes.py` |
| Codex e Claude com esforços diferentes sem você pedir | Os padrões de cada runtime não coincidem | Passar `--claude-effort` e `--codex-effort` iguais |

## 13. Limites

- **Uma repetição não caracteriza nada.** Na validação, o mesmo modelo Hermes deu 7/7 e 6/7 em execuções diferentes. Use `--reps` ≥ 3 antes de decidir.
- **`bench.py` e `grade.py` avaliam a própria skill-refactor.** Para outras skills, escreva casos próprios.
- **Cada runtime expõe a skill de um jeito:** o Claude Code por plugin gerado, o Codex e o Hermes por `AGENTS.md`, e o OpenCode de forma nativa. Só no OpenCode se mede acionamento real; comparações de tokens entre runtimes são aproximadas.
- **Os runtimes carregam também as skills e plugins globais do usuário**, e isso entra no contexto medido.
- **O Codex não informa o modelo usado.** A única evidência é o runtime ter aceito o slug.
- **O Claude Code não tem comando para listar modelos.**
- **Custos do Codex e do Hermes não são cobrança real:** equivalência de API e estimativa, respectivamente.

## 14. Referência rápida

```bash
cd plugins/pwdev-skills/skills/skill-refactor

# o que roda aqui
python3 scripts/discover.py

# tamanho antes x depois
python3 scripts/tokens.py <skill> --baseline <versao-anterior>

# smoke barato
python3 scripts/bench.py --skill . --only-case 3 --runtimes claude \
  --claude-models claude-haiku-4-5-20251001 --budget-usd 1 --out "$(mktemp -d)"

# A/B completo, publicando os resumos
python3 scripts/bench.py --skill . --baseline git:<sha> --runtimes auto --hermes-model default \
  --acknowledge-hermes-automation --budget-usd 5 --reps 3 \
  --out "$(mktemp -d)" --publish evals/benchmarks/$(date +%F)

# pipeline sem custo (na raiz do marketplace)
python3 -m unittest tests.test_skill_refactor_bench tests.test_skills_packaging
```

| Pedido à skill | Resultado |
| --- | --- |
| "Revise … sem editar" | Achados → mudanças → como medir; nenhuma escrita |
| "Refatore … consumidores X em lean, demais guided" | Edição + baseline + rótulos de entrega |
| "Compare a versão anterior com a candidata em …" | Plano de A/B; só executa com orçamento e modelos definidos |
