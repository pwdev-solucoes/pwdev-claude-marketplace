---
okf_version: "0.2"
type: report
title: "pwdev-power 0.1.0 → 0.2.0: leitura condicional das referências, medida em três braços"
generated:
  by: "agent:claude"
  at: "2026-09-15T07:05:00Z"
lifecycle:
  status: draft
sources:
  - resource: "plugins/pwdev-skills/skills/skill-refactor/references/refactoring.md"
    context: "Protocolo aplicado; executor guided; consumidores guided."
  - resource: "tokens-before.json"
  - resource: "tokens-after.json"
  - resource: "ab/summary.json"
    context: "Rodada isolada: 3 casos × candidata/baseline/sem skill × Sonnet 5 medium + OpenCode big-pickle, 1 rep."
  - resource: "ab-opencode-case2-x3/summary.json"
    context: "Repetição do caso 2 no OpenCode, 3 reps, para separar ruído de efeito."
  - resource: "ab-first-attempt-contaminated/summary.json"
    context: "Primeira rodada, inválida: o pwdev-power instalado no Claude Code do usuário entrou em todos os braços."
  - resource: "../cases/power/cases.json"
    context: "Três casos em modo task, escritos à mão sob o plano aprovado em 2026-09-15."
verified:
  - event: static_validation
    by: "agent:claude"
    at: "2026-09-15T06:10:00Z"
    scope: "plugins/pwdev-power (15 skills, 13 referências, manifestos, READMEs)"
    source: "python3 -m unittest tests.test_pwdev_power tests.test_power_hermes → 147 OK sem editar testes; skill-creator quick_validate.py 15/15; links e caminhos inline resolvidos; literais proibidos ausentes; scratchpad/power-load.py antes e depois"
  - event: behavioral_evaluation
    by: "agent:claude"
    at: "2026-09-15T06:45:00Z"
    scope: "ab (18/18 runs, US$ 3,07) e ab-opencode-case2-x3 (9/9, US$ 0)"
    source: "scripts/bench.py com raiz de plugin como skill medida, --claude-disable-plugin pwdev-power@pwdev-claude-marketplace, --isolate-user-skills; grade.py em modo task pelas verificações de cada caso"
---

# pwdev-power 0.1.0 → 0.2.0

**Alvo:** `plugins/pwdev-power`, 15 skills que compartilham 13 referências. **Baseline:** cópia integral
do plugin antes da edição (scratchpad, 49 arquivos com hash; git `2027d72`). **Perfis:** executor
`guided`; consumidores mistos (Claude Code, Codex, Hermes) em `guided` — nenhuma medição lean/guided
existe para eles. **Escopo autorizado:** corpos das skills, referências, manifestos, READMEs da raiz,
CHANGELOG novo; descrições, scripts, hooks, agentes, comandos e testes intocados.

## Diagnóstico

Não há duplicação literal entre skills (zero parágrafos ou linhas repetidos). O custo está na
**leitura incondicional** (categoria 3): onze skills abriam com "Read A, B, C before acting" e
carregavam referências inteiras em toda ativação, inclusive quando o pedido não chegava ao ponto que a
referência cobre. Duplicação núcleo↔referência (categoria 1) em `power-execute` (§Model selection e
§Waiting reescreviam `runtime.md`), `power-init` (§Staleness reescrevia `context.md`), `power-plan` e
`power-brainstorm` (a regra "o mapa informa, o código vence" de `context.md`).

## Mudança

Cada "before acting" virou uma condição no ponto de uso, e cada regra obrigatória da referência ganhou
uma linha de invariante no núcleo, para não depender de uma leitura que talvez não aconteça (regra do
guia que se sobrepõe a todas):

| Referência | Passa a ser lida quando | Invariante que fica no núcleo |
| --- | --- | --- |
| `safety.md` | antes de git, fleet, teardown ou escrita fora de `.planning/power/` | nunca segredos; nunca config do usuário; nunca push/merge/commit em default sem pedido |
| `collaboration.md` | num gate, ao despachar subagente, quando um status volta | gates são humanos; status ≤ 10 linhas; nunca colar relatório |
| `artifacts.md` | antes de escrever `config.json`, `state.md`, `plan.md`, `prd.md`, `verdict.md` | raiz `.planning/power/` |
| `context.md` | quando `.planning/power/context/` existe | o mapa informa, não decide; o código vence |
| `runtime.md` / `*-tools.md` | antes do primeiro despacho | — |
| `model-profiles.md` | no Claude Code, antes de escolher modelo | — |

Carga por ativação (corpo + referências lidas incondicionalmente; tiktoken `o200k_base`):

| Skill | antes | depois | |
| --- | ---: | ---: | --- |
| power-fleet | 7 737 | 1 794 | fleet/cmux/safety/artifacts por rota |
| power-init | 5 228 | 1 579 | por passo |
| power-execute | 4 332 | 1 622 | §Model selection e §Waiting sem duplicar `runtime.md` |
| power-plan | 4 262 | 853 | |
| power-brainstorm | 3 598 | 919 | |
| power-roadmap-status / verify / product | 2 373–2 405 | 788–798 | |
| power-quick | 1 632 | **1 632** | **mantida em 0.1.0 — ver decisão** |
| power-finish | 1 107 | 505 | |
| power (roteador), debug, tdd, review, worktree | = corpo | = corpo | intocadas |
| **soma das 15** | **38 294** | **14 518 (−62 %)** | corpos 13 025 → 13 349 (+2,5 %) |

Nada saiu do plugin: o que deixou o núcleo já estava na referência. Descrições intocadas (gatilhos de
14–44 tokens, exigidos pelos testes). Versão 0.2.0 nos três manifestos.

## Avaliação comportamental

**Casos** (modo task, verificações objetivas por caso): `plan_from_approved_spec` (plano a partir de um
`spec.md` aprovado: estrutura, `Global Constraints` verbatim, `Interfaces`, comandos reais, sem
placeholders, ≤ 8 tarefas, nada implementado), `quick_change_resists_scope_creep` (uma mudança de um
arquivo com uma isca de "aproveita e arruma"; só o arquivo pedido muda; `contract.md`/`report.md`
gravados), `init_check_reports_without_writing` (`--check` relata `pytest` e a superfície de runtime
sem gravar nada).

**Primeira rodada, inválida.** O `pwdev-power` instalado no Claude Code do usuário e os links em
`~/.agents/skills` entraram em todos os braços: "sem skill" seguia o rito do power-quick e parava no
gate. Registrada em `ab-first-attempt-contaminated/`. A correção virou capacidade do harness:
`--claude-disable-plugin` (`--settings` por sessão), `--isolate-user-skills` (HOME novo no OpenCode)
e workspace fresco por run.

**Rodada isolada** (`ab/`, 1 rep, Sonnet 5 `medium`, OpenCode `big-pickle` gratuito):

| Caso | Modelo | baseline 0.1.0 | candidata | sem skill | custo b→c | contexto p50 b→c |
| --- | --- | --- | --- | --- | --- | --- |
| 1 plano | Sonnet 5 | 1/1 | 1/1 | 0/1 (0,93) | 0,51 → 0,40 | 501 k → 399 k |
| 1 | big-pickle | 1/1 | 1/1 | 1/1 | 0 | 254 k → 357 k |
| 2 quick | Sonnet 5 | 1/1 | 1/1 | 0/1 (0,62) | 0,27 → 0,26 | 446 k → 437 k |
| 2 | big-pickle | 1/1 | **0/1** (0,88) | 0/1 (0,50) | 0 | 75 k → 106 k |
| 3 init --check | Sonnet 5 | 1/1 | 1/1 | 0/1 (0,71) | 0,28 → 0,29 | 450 k → 514 k |
| 3 | big-pickle | 1/1 | 1/1 | 1/1 | 0 | 124 k → 146 k |

**Repetição do caso 2 no OpenCode** (`ab-opencode-case2-x3/`, 3 reps): baseline **2/3** (0,96),
candidata **0/3** (0,75: duas vezes editou `legacy.py`, uma vez não fez a mudança), sem skill 0/3
(0,50). Somando as duas rodadas: candidata 0/4 × baseline 3/4.

## Decisão pelos critérios fixados antes

1. *Aceite da candidata ≥ baseline em cada modelo.* Claude: 3/3 × 3/3 ✓. OpenCode: 2/3 × 3/3 ✗ — a
   regressão está inteira no `power-quick`.
2. *Custo por tarefa aceita ≤ baseline.* Claude: 0,32 × 0,35 (0,95/3 × 1,06/3) ✓. OpenCode: gratuito.
3. *Sem skill como controle.* Claude: 0/3 — a skill agrega nos três casos. OpenCode: agrega no caso 2
   (0/3 contra 2–3/3), empata nos casos 1 e 3, que esse modelo resolve sozinho.
4. *Regressão em qualquer modelo → manter a versão anterior daquela skill.* **`power-quick` volta ao
   texto 0.1.0** (byte-idêntico ao commitado); as outras dez refatoradas ficam.

Hipótese sobre a regressão, não verificada: no modelo pequeno, ler `collaboration.md` inteira antes de
agir (a versão 0.1.0) segura o modelo no mini-plano; a linha de invariante ("nunca toque num arquivo
que o mini-plano não nomeou") sem a leitura não teve o mesmo efeito. É exatamente o caso em que a
regra 8 do guia manda medir e não presumir — e o `guided` valeu mais que a economia de 1 200 tokens.

**Rótulos:** `refactored`, `statically validated`, `behaviorally evaluated` — este último para
(Claude Code, Sonnet 5) com 1 rep e (OpenCode, big-pickle) com 1 rep + 3 no caso 2. Codex e Hermes
não rodaram.

## Limites

- 1 repetição por célula no Claude; o OpenCode gratuito é instável e resolve os casos 1 e 3 sem skill.
- A versão final (com `power-quick` revertida) não foi re-executada: a reversão é byte-idêntica à
  baseline, então os runs da baseline para o caso 2 valem para ela; os demais casos não tocam essa skill.
- No Claude, só o plugin foi desligado; as outras skills globais do usuário (141) seguem em todos os
  braços. Codex e Hermes não têm isolamento no harness (links em `~/.agents/skills`).
- O contexto acumulado subiu no OpenCode com a candidata nos três casos (1 rep): direção a vigiar, não
  conclusão — as referências continuam sendo lidas, só que no ponto de uso.
- Custo real: US$ 3,07 (rodada isolada) + US$ 2,76 (primeira rodada, inválida) + sondas ≈ US$ 0,15.
- Nada commitado; publicação do plugin exige autorização separada.
