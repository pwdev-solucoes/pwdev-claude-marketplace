# Guia de uso — skill-refactor

Um roteiro por cenário para quem vai usar a skill pela primeira vez: o que dizer ao agente, o que
esperar de volta e como saber se valeu a pena. As opções completas de cada script estão no
[Manual de uso](./manual-de-uso.md); o porquê de cada passo, na
[Metodologia de refatoração](./metodologia-de-refatoracao.md). Os números citados aqui são os da
aplicação da skill a si mesma em 14/09/2026
(`skills/skill-refactor/evals/benchmarks/2026-09-14/report.md`).

## Sumário

1. [Em cinco minutos](#1-em-cinco-minutos)
2. [Cenário A — revisar uma skill sem tocar nela](#2-cenário-a--revisar-uma-skill-sem-tocar-nela)
3. [Cenário B — refatorar com edição autorizada](#3-cenário-b--refatorar-com-edição-autorizada)
4. [Cenário C — medir antes, sem skill e depois](#4-cenário-c--medir-antes-sem-skill-e-depois)
5. [Cenário D — comparar modelos: mesmo runtime e runtimes diferentes](#5-cenário-d--comparar-modelos-mesmo-runtime-e-runtimes-diferentes)
6. [Cenário E — medir qualquer skill na tarefa dela](#6-cenário-e--medir-qualquer-skill-na-tarefa-dela)
7. [Cenário F — casos no domínio da skill-alvo](#7-cenário-f--casos-no-domínio-da-skill-alvo)
8. [Cenário G — a rodada deu errado](#8-cenário-g--a-rodada-deu-errado)
9. [Como pedir bem](#9-como-pedir-bem)
10. [Checklist de saída](#10-checklist-de-saída)

---

## 1. Em cinco minutos

```bash
claude plugin install pwdev-skills@pwdev-claude-marketplace   # ou: claude --plugin-dir ./plugins/pwdev-skills
python3 plugins/pwdev-skills/.opencode-plugin/install.py       # OpenCode: linka a skill em ~/.config/opencode/skills
cd plugins/pwdev-skills/skills/skill-refactor
python3 scripts/discover.py                                    # o que roda nesta máquina, sem custo
```

Depois, numa sessão do Claude Code (Codex: `$skill-refactor`; Hermes: `skill_view("pwdev-skills:skill-refactor")`;
OpenCode: o agente carrega a skill sozinho pela ferramenta `skill`):

```text
Revise plugins/meu-plugin/skills/resumo/SKILL.md sem editar arquivos.
Aponte o que reduziria contexto e como medir o efeito.
```

Se a resposta vier em três partes — achados por categoria, mudanças propostas, como medir — a skill
foi acionada. Se vier uma opinião solta, ela não foi: veja [§9](#9-como-pedir-bem).

## 2. Cenário A — revisar uma skill sem tocar nela

**Quando:** você suspeita que uma skill repete instruções, carrega referências em toda chamada,
dispara em pedidos errados, ou só quer saber por onde começar.

**O que dizer:** nomeie o caminho, diga "sem editar" e, se souber, quem vai consumir a skill.

```text
Revise plugins/pwdev-code/skills/reports/SKILL.md sem editar nada.
Consumidores: modelos pequenos em lean. Diga como medir o efeito.
```

**O que esperar:**

| Parte | Conteúdo | Como conferir |
| --- | --- | --- |
| 1. Achados | Cada um nomeado por categoria — duplicação, contradição, leitura incondicional, descrição ampla/restrita demais, procedimento sem finalidade — com as linhas de origem | Abra as linhas citadas; um achado sem linha é opinião |
| 2. Mudanças propostas | Cada uma ligada ao achado que resolve e ao requisito que preserva | Toda mudança deve dizer o que continua verdadeiro |
| 3. Como verificar | `tokens.py --baseline` para tamanho, depois A/B com `bench.py` decidido por custo por tarefa aceita | Se propuser "linhas por execução" ou "nota de legibilidade", rejeite: não é medida do protocolo |

Uma revisão **nunca** é evidência de eficiência; ela diz o que medir. Nada é gravado em disco.

## 3. Cenário B — refatorar com edição autorizada

**Quando:** a revisão convenceu, ou você já sabe o que quer mudar.

**O que dizer:** autorize a edição explicitamente, diga onde gravar baseline e relatório, e o que
deve ser preservado.

```text
Refatore plugins/pwdev-code/skills/reports/SKILL.md e seus recursos.
Consumidores: Sonnet em lean, demais modelos em guided.
Preserve nome, paths, metadata e os rótulos de saída. Não rode benchmark.
Baseline e relatório em .planning/refactor/reports/.
```

**O que a skill faz:** copia os arquivos originais para um baseline novo (nunca sobrescreve um
existente), aplica a mudança com as ferramentas de edição do runtime, confere frontmatter, links
relativos e comportamento obrigatório, e grava um relatório OKF na pasta indicada.

**O que esperar na entrega:** caminhos alterados, perfis usados, requisitos preservados, checagens
feitas com resultado observado, limites — e uma linha final com **todos os rótulos conquistados**:

| Rótulo | Ganho quando |
| --- | --- |
| `refactored` | houve edição |
| `statically validated` | frontmatter, links e requisitos foram conferidos |
| `behaviorally evaluated` | rodou em modelos reais, em pares (versão anterior × candidata) |

Os rótulos se acumulam: uma refatoração típica sem benchmark termina `refactored, statically
validated`. Se a entrega afirmar ganho de eficiência sem `behaviorally evaluated`, a afirmação não
tem base — peça o cenário C.

**Confira você mesmo o tamanho:**

```bash
python3 scripts/tokens.py plugins/pwdev-code/skills/reports --baseline .planning/refactor/reports/baseline
```

A tabela "Context layers" separa o que é pago em toda conversa (`description`), por ativação
(`SKILL.md#body`) e sob condição (referências). Corte no corpo com referência crescendo é o
resultado esperado de uma refatoração bem feita; corte no total à custa da `description` é suspeito.

## 4. Cenário C — medir antes, sem skill e depois

**Quando:** você vai afirmar que a versão nova é melhor, ou precisa escolher perfil/modelo.

**Faz chamadas pagas.** Antes de rodar: `discover.py` para saber o que está autenticado, e um
orçamento. Referência real (14/09/2026, um caso de edição): Sonnet 5 em `medium` custou US$ 0,49–0,66
por run; Codex no plano ChatGPT não é cobrado por token; modelos gratuitos do OpenCode custam zero,
mas são instáveis acima de alguns runs; Hermes com modelo barato custa centavos e leva 3–30 min.

**Três braços no mesmo `--out`:**

```bash
cp -r plugins/pwdev-code/skills/reports /tmp/reports-antes        # ou --baseline git:<sha>
# ... refatore (cenário B) ...
python3 scripts/bench.py --skill plugins/pwdev-code/skills/reports --baseline /tmp/reports-antes --no-skill-arm \
  --runtimes claude,codex --claude-models claude-sonnet-5 --codex-models gpt-5.6-terra \
  --claude-effort medium --codex-effort medium --reps 2 --timeout 1800 --budget-usd 8 \
  --out "$(mktemp -d)" --publish plugins/pwdev-code/skills/reports/evals/benchmarks/$(date +%F)
```

- `candidate` = a skill em `--skill`; `baseline` = a versão anterior; `no_skill` = o runtime recebe só
  o fixture e o pedido. O terceiro braço responde "a skill acrescenta alguma coisa?" — se ele empata
  com a candidata num caso, a skill não agrega ali, e isso é um achado.
- `--reps 2` no mínimo para afirmar direção e `--reps 3` antes de uma decisão que vai ser publicada;
  uma repetição por célula é indicação, não prova (o manual, §13, mostra o mesmo modelo dando 7/7 e 6/7).
- Iguale o esforço antes de comparar runtimes (`--claude-effort`, `--codex-effort`): esforços
  diferentes comparam configurações, não modelos.
- Não edite a skill enquanto a rodada roda: o resumo passa a `PASS_WITH_SOURCE_DRIFT`.

**Onde ler:** `summary.json` → `paired_by_case`, ou a tabela "Paired by case" do `benchmark.md`.
A decisão é **por modelo**, com critérios fixados antes de rodar:

1. aceite da candidata ≥ baseline em cada modelo;
2. custo por tarefa aceita ≤ baseline no mesmo modelo;
3. regressão em qualquer modelo → manter a baseline e registrar o motivo.

Exemplo do relatório de 14/09: Claude 2/3 → 3/3 aceitos, custo por tarefa aceita 0,66 → 0,45;
`no_skill` 0/8. Decisão: adotar, rotulada `behaviorally evaluated` com uma repetição.

## 5. Cenário D — comparar modelos: mesmo runtime e runtimes diferentes

**Quando:** a skill já está estável e a pergunta muda de "a versão nova é melhor?" para "em qual
modelo esta skill sai mais barata por tarefa aceita?" — para escolher perfil por modelo, ou para
decidir onde rodar. As duas perguntas usam o mesmo `bench.py`; o que muda é o que você mantém fixo.

### D1 — modelos do mesmo runtime

Fixe a versão (só `candidate`, sem `--baseline`), o caso e o esforço; varie só o modelo.

```bash
python3 scripts/bench.py --skill plugins/pwdev-code/skills/reports --only-case 3 \
  --runtimes codex --codex-models gpt-5.6-luna,gpt-5.6-terra,gpt-5.6-sol,gpt-6-astra \
  --codex-effort medium --reps 2 --timeout 1800 --budget-usd 10 --out "$(mktemp -d)" \
  --publish plugins/pwdev-code/skills/reports/evals/benchmarks/$(date +%F)-codex-family
```

- `--only-case 3` (revisão) é o caso barato para uma primeira passada; repita com os casos de
  edição antes de concluir, porque a diferença entre modelos costuma aparecer neles.
- Esforço **explícito e igual** (`--codex-effort medium`). Sem isso cada modelo usa o seu padrão
  (`codex debug models` mostra que Sol vem em `low` e Terra em `medium`) e você compara
  configurações, não modelos. O `summary.json` grava `effort_effective` e `effort_source` por run.
- Leia `efficiency_by_model`: uma linha por (runtime, modelo, braço) com aceite, custo por tarefa
  aceita, contexto p50 e latência. A ordem já sai por custo por sucesso.
- Referência (13/09/2026, caso de revisão, 1 rep): Luna 7/7 a US$ 0,008, Terra 7/7 a 0,07, Sol
  7/7 a 0,14, Astra 7/7 a 0,33 — todos aceitos, então a decisão foi só pelo custo. No Claude,
  Haiku 4/7 a 0,04 contra Sonnet 7/7 a 0,28: o mais barato por run não foi o mais barato por
  tarefa aceita, porque não aceitou.

O mesmo desenho vale para a família Claude (`--runtimes claude --claude-models
claude-haiku-4-5-20251001,claude-sonnet-5,claude-opus-5 --claude-effort medium`) e para o
OpenCode (`--opencode-models` com ids de `opencode models`, `--opencode-effort` só onde o modelo
tem variantes). No Hermes, um modelo por rodada ou lista em `--hermes-model`, sempre com
`--hermes-provider`.

### D2 — runtimes diferentes

Fixe caso, esforço e o **mesmo modelo onde for possível** (um modelo servido por dois runtimes,
como `deepseek/deepseek-v4.1-flash` via Hermes e via OpenCode/OpenRouter, isola o runtime); onde
não for, aceite que você compara pares (runtime, modelo), não runtimes puros.

```bash
python3 scripts/bench.py --skill plugins/pwdev-code/skills/reports --only-case 3 \
  --runtimes claude,codex,hermes,opencode \
  --claude-models claude-sonnet-5 --codex-models gpt-5.6-terra \
  --hermes-model deepseek/deepseek-v4.1-flash --hermes-provider openrouter \
  --opencode-models openrouter/deepseek/deepseek-v4.1-flash \
  --claude-effort medium --codex-effort medium --hermes-effort medium \
  --reps 2 --timeout 1800 --budget-usd 6 --acknowledge-hermes-automation \
  --out "$(mktemp -d)" --publish plugins/pwdev-code/skills/reports/evals/benchmarks/$(date +%F)-runtimes
```

Quatro coisas que só existem nessa comparação:

| Diferença entre runtimes | O que fazer com ela |
| --- | --- |
| **Exposição da skill** difere: Claude Code por plugin gerado, Codex e Hermes por `AGENTS.md`, OpenCode nativo | Tokens de contexto entre runtimes são aproximados; compare aceite e custo, não `context_tokens` |
| **Fonte do custo** difere: Claude reporta `total_cost_usd`; Codex é equivalente de API (plano ChatGPT não cobra por token); Hermes estima no `--usage-file`; OpenCode emite `step_finish.cost` | Leia `cost_source` em cada run antes de somar; nunca some "runtime" com "estimated" como se fosse a mesma coisa |
| **Escala de esforço** difere: `low/medium/high` do Claude não é o `low/medium/high` do Codex nem o `--reasoning` do Hermes | Iguale o rótulo e registre; se a diferença de resultado for pequena, rode um segundo esforço antes de concluir |
| **Contagem de tokens** difere: Codex inclui cache em `input_tokens`, Anthropic separa | O harness normaliza (`normalize_usage`); confira `usage_source` |

Como ler: `efficiency_by_model` responde "qual par (runtime, modelo) aceita mais barato"; a tabela
de defaults (`--claude-models default --codex-models default --hermes-model default`) responde "o
que o usuário recebe sem configurar nada" — e essa segunda pergunta é a que vale para decidir o
perfil padrão da skill, porque é assim que ela vai ser usada. Referência (13/09/2026, defaults,
caso de revisão): Opus em `high` 7/7 a US$ 0,67; Sol em `low` 7/7 a 0,14; Hermes com deepseek em
`medium` 6/7 a 0,01. Mesmo caso, três configurações — não três modelos.

Antes de escrever "o runtime X é mais eficiente", confira: mesmo caso, mesmo esforço, ≥ 3 reps,
`cost_source` igual ou declarado, e a diferença maior que a variação entre as repetições.

## 6. Cenário E — medir qualquer skill na tarefa dela

**Quando:** você refatorou a skill `resumo` (ou qualquer outra) e quer saber se a versão nova faz
**o trabalho dela** tão bem quanto a anterior, e o que ela acrescenta em relação a nenhuma skill.
Os cenários C e D medem a skill-refactor; este mede a sua.

**O que muda:** os três braços passam a ser versões da sua skill; o workspace recebe os arquivos de
entrada da tarefa; e a nota vem de **verificações declaradas no caso** — nada no harness conhece a
skill. Um arquivo `cases.json` com `"kind": "task"`:

```json
{"skill_name": "resumo", "kind": "task", "approved": true,
 "fixture": {"files": {"notes/ata.txt": "Ana: entregar sexta.\nBeto: orçamento aprovado.\n"}},
 "evals": [{"id": 1, "name": "resumir_ata",
   "prompt": "Resuma notes/ata.txt em resumo.md com Pontos-chave, Decisões e Ações.",
   "expected_output": "resumo.md com as três seções e sem nomes inventados",
   "checks": [{"type": "file_exists", "path": "resumo.md"},
              {"type": "regex", "path": "resumo.md", "pattern": "(?im)^## (Pontos-chave|Decisões|Ações)"},
              {"type": "not_regex", "path": "resumo.md", "pattern": "(?i)\\bCarla\\b"}]}]}
```

Tipos de verificação: `file_exists`, `file_absent`, `contains`, `not_contains`, `regex`, `not_regex`,
`json_valid`, `script` (comando que precisa sair com 0). Caminhos são relativos ao workspace; um
caminho absoluto ou com `..` é recusado antes de qualquer chamada paga. Escreva verificações que uma
boa resposta **precisa** satisfazer e uma errada **precisa** falhar — é isso que separa os braços.

```bash
cp -r plugins/meu-plugin/skills/resumo /tmp/resumo-antes      # ou --baseline git:<sha>
python3 scripts/bench.py --skill plugins/meu-plugin/skills/resumo --baseline /tmp/resumo-antes --no-skill-arm \
  --cases plugins/meu-plugin/skills/resumo/evals/cases/resumo \
  --runtimes claude,opencode --claude-models claude-sonnet-5 --opencode-models opencode/big-pickle \
  --claude-effort medium --reps 2 --budget-usd 5 --out "$(mktemp -d)" \
  --publish plugins/meu-plugin/skills/resumo/evals/benchmarks/$(date +%F)
```

Para não escrever os casos à mão: `cases.py --extract <skill> --kind task` gera o esqueleto,
`--propose` pede a um modelo duas ou três tarefas com arquivos sintéticos e verificações (validadas
por esquema), e `--approve` fecha o conjunto — leia cada verificação `script` antes de aprovar,
porque ela roda um comando no workspace. A leitura do resultado é a do cenário C: `paired_by_case`,
decisão por modelo, `no_skill` como controle.

## 7. Cenário F — casos no domínio da skill-alvo

**Quando:** você quer medir a **skill-refactor** trabalhando sobre a sua skill (não a sua skill na
tarefa dela — isso é o cenário E). O fixture padrão é o `meeting-summary`; aqui os casos vêm da sua.

```bash
python3 scripts/cases.py --extract plugins/pwdev-code/skills/reports          # sem custo
python3 scripts/cases.py --propose plugins/pwdev-code/skills/reports/evals/cases/reports \
  --runtime claude --model claude-sonnet-5 --effort medium                    # uma chamada (~US$ 0,25)
python3 scripts/cases.py --approve plugins/pwdev-code/skills/reports/evals/cases/reports \
  --skill plugins/pwdev-code/skills/reports                                    # você lê e confirma
python3 scripts/bench.py --skill ... --cases plugins/pwdev-code/skills/reports/evals/cases/reports ...
```

- `--extract` deriva os **invariantes** (nome, `paths`, metadados estáveis, literais `CHAVE=valor`,
  rótulos de saída, proibições, blocos opcionais com suas guardas, idioma) e os defeitos que consegue
  ver por script. Leia a lista: o extrator é heurístico e pode pegar uma afirmação como se fosse
  proibição — remova o que não for regra antes de aprovar.
- `--propose` pede a um modelo pedidos realistas e consultas de acionamento próximas; a resposta
  passa por esquema, e **nada que o modelo escreve vira verificação objetiva** — as sugestões ficam
  em `llm_suggested_invariants` até você movê-las à mão.
- `--approve` grava `cases.json` amarrado ao hash do `SKILL.md`. Depois de refatorar, `--check`
  acusa deriva: é esperado, porque o fixture é a versão que os casos descrevem.

## 8. Cenário G — a rodada deu errado

| Sintoma | Significa | O que fazer |
| --- | --- | --- |
| `NOT_RUN: runtime quota or usage limit` | O provedor recusou (cota do plano, 429) | Nada a corrigir na skill; repita depois ou troque de modelo |
| `NOT_RUN: provider unavailable` | 5xx, sobrecarga, conexão caiu | Idem; níveis gratuitos fazem isso após poucos runs |
| `NOT_RUN: per-run budget … reached` | O teto por run do Claude cortou a tarefa | Suba `--budget-usd`; o teto por run é orçamento ÷ runs do Claude |
| `BLOCKED: timeout` | Passou de `--timeout` | Aumente o timeout ou rode esse runtime como fatia separada |
| `FAIL` com `protected path changed` | O run alterou algo fora do workspace | Leia o `record.json`; isso reprova o run, não a skill |
| Veredito `PASS_WITH_SOURCE_DRIFT` | A skill foi editada durante a rodada | Rode de novo depois de estabilizar |

Corrigiu o avaliador ou o classificador depois de uma rodada paga? Não pague de novo:

```bash
python3 scripts/bench.py --regrade <out-da-rodada> --cases evals/evals.json --publish evals/benchmarks/<data>
```

O `--regrade` reconstrói a rodada a partir do disco — inclusive uma rodada interrompida, ou
completada em várias invocações no mesmo `--out` (um runtime por vez).

## 9. Como pedir bem

| Diga | Porque |
| --- | --- |
| "sem editar" ou "edição autorizada" | Define revisão × refatoração; sem isso a skill pergunta ou para na auditoria |
| O caminho da skill-alvo | A skill não adivinha alvos nem varre o repositório |
| Quem consome (modelo e perfil), se souber | Sem isso o padrão é `guided`; um perfil explícito sempre vence |
| Onde gravar baseline e relatório | A skill nunca grava fora da área autorizada |
| "não rode benchmark" ou o orçamento | Benchmark é pago; sem orçamento ela não roda |

Evite: pedir "deixe mais curta" (tamanho não é a medida), pedir perfil por nome de modelo sem
medição ("Haiku é lean"), ou pedir para a skill executar a tarefa da skill-alvo (ela não resume
reuniões; ela refatora a skill que resume).

## 10. Checklist de saída

- [ ] A entrega distingue `refactored` / `statically validated` / `behaviorally evaluated`.
- [ ] Nome, `paths`, metadados, rótulos de saída e proibições da skill-alvo continuam lá.
- [ ] O que saiu do núcleo está numa referência **com condição de leitura** escrita no núcleo.
- [ ] `tokens.py --baseline` mostra o corte no `SKILL.md#body`, não na `description`.
- [ ] Se houve benchmark: ≥ 2 reps para direção (≥ 3 para decidir), esforço igual entre runtimes, decisão por modelo em `paired_by_case`.
- [ ] Nenhum caminho pessoal nem segredo nos artefatos publicados (`summary.json` é sanitizado).
- [ ] Nada foi commitado, publicado ou instalado sem pedido.
