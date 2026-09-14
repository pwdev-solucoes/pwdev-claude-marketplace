---
okf_version: "0.2"
type: report
title: "skill-refactor 0.2.1 → 0.3.0: refatoração medida em três braços"
generated:
  by: "agent:claude"
  at: "2026-09-14T21:18:00Z"
lifecycle:
  status: draft
sources:
  - resource: "docs/skill-refactoring-guide.md"
    sha256: "d6744f5425825434fa208b5a1a8419797379344c6cc6ee0af5cdd7f8eb1bd0e1"
  - resource: "round-1-before/summary.json"
    sha256: "3b29bd4ddc17e13175ed948dc4350b1083376f014a08b55cff874fc94949f6e8"
  - resource: "round-2-after/summary.json"
    sha256: "467ece72febf86d59ca9c6ca6c6666da9ef5d12668568bb8a1595cdd3f3e6769"
  - resource: "round-2-context/summary.json"
    sha256: "10d8005a598783ec2006631ad0e360f70943f5eb98fe42e6652e5a0aaa2225cb"
verified:
  - event: static_validation
    by: "agent:claude"
    at: "2026-09-14T21:18:00Z"
    scope: "skills/skill-refactor"
    source: "skill-creator quick_validate.py: valid; links de SKILL.md resolvidos; tokens.py --baseline contra a cópia 0.2.1"
  - event: behavioral_evaluation
    by: "agent:claude"
    at: "2026-09-14T21:18:00Z"
    scope: "round-1-before (47/48 runs), round-2-after (23/27 runs)"
    source: "scripts/bench.py; avaliador objetivo scripts/grade.py; regrade a partir do disco após correções do classificador"
---

# skill-refactor 0.2.1 → 0.3.0

**Alvo:** `plugins/pwdev-skills/skills/skill-refactor`. **Baseline:** cópia da árvore 0.2.1 feita antes da
edição (não commitada; SHA-256 do `SKILL.md` `248dc824d6fb…`). **Candidata:** 0.3.0 na árvore de trabalho.
**Perfis:** executor `guided` (esta sessão); consumidores mistos, `guided` por padrão — nenhum perfil
por modelo foi presumido.

## Critérios fixados antes da rodada 2

1. Aceite da candidata ≥ baseline **em cada modelo** que rodou nos mesmos casos.
2. Custo por tarefa aceita da candidata ≤ baseline no mesmo modelo.
3. `no_skill` serve de controle: se empata ou vence a candidata num caso, a skill não agrega ali.
4. Regressão em qualquer modelo → manter a baseline e registrar o motivo.

Os critérios foram fixados no plano aprovado e no chat antes da rodada 2; não foram gravados no
`summary.json` da rodada (o harness ainda não tem campo para isso — limite registrado).

## Mudança

| Camada | 0.2.1 | 0.3.0 | Δ |
| --- | ---: | ---: | ---: |
| `description` (paga em toda conversa) | 107 | 107 | 0 |
| corpo do `SKILL.md` (paga por ativação) | 1 258 | 998 | −21 % |
| `references/refactoring.md` (condicional) | 1 746 | 2 027 | +281 |
| `references/runtimes.md` (condicional: antes de rodar scripts) | 2 599 | 2 773 | +174 |

Movido, não removido: a prosa do contrato de revisão foi para `refactoring.md` ("The review contract")
e a seção *Measure* para `runtimes.md` ("Before measuring"), com condição única no núcleo. Duas
mudanças vieram da medição da rodada 1, não do diagnóstico estático: os rótulos de entrega passaram a
ser **cumulativos** (o texto anterior, "`refactored`, `statically validated` **ou** `behaviorally
evaluated`", era lido como escolha — a expectativa mais reprovada mesmo com a skill) e "um bloco que
sai do núcleo leva suas regras de guarda" (modelos perdiam a regra do CSV ao movê-lo).

## Resultado pareado (rodada 2a, 1 rep, Claude/Codex em `medium`)

Aceito = todas as expectativas do caso atendidas. Codex: cota do plano ChatGPT esgotou no meio (eval-2
`no_skill` e todo o eval-3 `NOT_RUN`). Hermes: pulado na rodada 2 por decisão do operador (lentidão).

| Caso | Modelo | baseline 0.2.1 | candidata 0.3.0 | sem skill | US$/aceito b→c |
| --- | --- | --- | --- | --- | --- |
| 1 edição mista | Sonnet 5 | 1/1 (1,00) | 1/1 (1,00) | 0/1 (0,93) | 0,49 → 0,52 |
| 1 | Terra | 0/1 (0,87) | 0/1 (0,93) | 0/1 (0,87) | — |
| 1 | Ling (free) | 1/1 (1,00) | 1/1 (1,00) | 0/1 (0,93) | 0 → 0 |
| 2 modelo desconhecido | Sonnet 5 | 0/1 (0,88) | **1/1 (1,00)** | 0/1 (0,88) | — → 0,57 |
| 2 | Terra | 0/1 (0,76) | 0/1 (0,94) | não rodou | — |
| 2 | Ling (free) | 0/1 (0,94) | **1/1 (1,00)** | 0/1 (0,82) | — → 0 |
| 3 revisão | Sonnet 5 | 1/1 (1,00) | 1/1 (1,00) | 0/1 (0,71) | 0,29 → 0,25 |
| 3 | Ling (free) | 1/1 (1,00) | 1/1 (1,00) | 0/1 (0,57) | 0 → 0 |

- **Critério 1:** Claude 3/3 × 2/3; OpenCode 3/3 × 2/3; Codex 0/2 × 0/2 nos casos em que os dois
  braços rodaram (expectativas 0,93 × 0,87 e 0,94 × 0,76 a favor da candidata). Sem regressão.
- **Critério 2:** Claude, custo por tarefa aceita 0,45 (1,34/3) × 0,66 (1,33/2); por caso, +6 % no
  eval-1 e −14 % no eval-3. OpenCode gratuito. Atendido no agregado; o eval-1 fica como limite.
- **Critério 3:** `no_skill` 0/8 aceitos. A skill agrega em todos os casos que rodaram.
- **Contexto (p50, 1 rep):** direção mista — Claude eval-1 999 k × 726 k, eval-3 280 k × 352 k;
  OpenCode menor nos três casos. Uma repetição não caracteriza.

**Decisão:** adotar a 0.3.0. Rótulos: `refactored`, `statically validated`, `behaviorally evaluated`
— este último com **uma repetição por célula** e sem Hermes na rodada 2: é direção com controle,
não prova de ganho. O que a rodada 1 (2 reps, 47/48 runs) já mostrava e a rodada 2 confirma: na
revisão a skill decide; nas edições o ganho da 0.3.0 está nas duas expectativas que a medição apontou.

## Rodada 2b — casos por contexto (ids 4–6, propostos por Sonnet 5 e aprovados)

1/18 executado (Ling, baseline, eval-4: 0,93). Codex sem cota; OpenCode Zen gratuito com 429 e quedas
de conexão. **Sem conclusão.** Repetir quando a cota do Codex voltar (19/09) e com um modelo pago no
OpenCode/Hermes via OpenRouter (catálogo já traz `z-ai/glm-5.3-flash`, `tencent/hy4-preview`,
`deepseek/deepseek-v4.1-flash`).

## Correções do harness que a medição forçou (todas com teste)

- Cota/indisponibilidade só contam com saída ≠ 0 ou envelope quebrado, e o motivo vem do stderr ou
  do evento de erro antes de qualquer texto citado (dois runs do Codex e um do OpenCode foram
  perdidos ou mal descritos por citação de documentação).
- Rótulos de entrega lidos também na área de artefatos, onde a skill manda gravar o relatório.
- `bench.py --regrade` reconstrói uma rodada a partir do disco (rodada interrompida ou completada em
  várias invocações), sem nova chamada.

## Limites

- 1 rep na rodada 2; Hermes ausente; Codex parcial. Custos do Codex são equivalentes de API.
- `evals/cases/skill-refactor/cases.json` está amarrado ao `SKILL.md` **0.2.1**: é o alvo do fixture,
  por desenho; `cases.py --check` contra a 0.3.0 acusa deriva e isso é esperado.
- Nada foi commitado; a publicação do plugin continua exigindo autorização separada.
