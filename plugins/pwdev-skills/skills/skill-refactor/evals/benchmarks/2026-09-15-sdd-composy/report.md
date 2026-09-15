---
okf_version: "0.2"
type: report
title: "sdd-composy: revisão e refatoração de Markdown + descoberta OpenCode"
generated:
  by: "agent:claude"
  at: "2026-09-15T03:51:22Z"
lifecycle:
  status: draft
sources:
  - resource: "plugins/pwdev-skills/skills/skill-refactor/references/refactoring.md"
  - resource: "versions/baseline.sha256"
    sha256: "13e9a99e351ddd428c2b050a41c5096933ade797a3306218d48366fca6ae999c"
    context: "Hashes dos 99 arquivos copiados antes da edição (a cópia em versions/ é gitignored)."
  - resource: "tokens-before.json"
    sha256: "db56c24c11016d4a01ea1d3b8861a7b7a5e26f98a77a381a8f1fa2f2e4d27e18"
  - resource: "ab-claude/cases.json"
    sha256: "8c7060718ef0edc40a331ff621c9f04501e75c69e862063c966a90e2d87e021c"
  - resource: "ab-claude/round-1/summary.json"
    sha256: "5fd9b9b16808ca8b41a97dd8ffad6ca1290c41c2471d278e86f8e3cedc845914"
  - resource: "tokens-after.json"
    sha256: "c38443e22c667c1fbd90a42a296a42462f0760a27cea6b3202bd16598184436b"
  - resource: "~/.claude/plans/analisar-o-plugin-sdd-composy-groovy-parrot.md"
    context: "Plano aprovado pelo usuário em 2026-09-15 (Partes 1-3, fases 0-7, recomendações)."
verified:
  - event: behavioral_evaluation
    by: "agent:claude"
    at: "2026-09-15T04:22:29Z"
    scope: "ab-claude/round-1 (3 cases x 2 arms + 8 trigger probes x 2 arms), diag-case3 (stream-json, 2 runs), ab-claude/round-2a and round-2b (case 3 x 2 arms) — claude-sonnet-5, effort medium, Claude Code 2.1.272"
    source: "ab-claude/run_ab.py over skill-refactor scripts/runtimes.py; objective checks in ab-claude/cases.json; probes regraded from disk; protected paths unchanged in every record; total spent US$ 6.41"
  - event: behavioral_evaluation
    by: "agent:claude"
    at: "2026-09-15T04:37:16Z"
    scope: "ab-claude/opus and ab-claude/fable: 3 cases x 2 arms + 8 probes x 2 arms each, claude-opus-5 and claude-fable-5-1, effort medium, 1 rep; Fable smoke on case 1 first (US$ 0.95) to size the caps"
    source: "ab-claude/run_ab.py --model … --exec-cap/--probe-cap/--total-cap; probes regraded from disk; protected paths unchanged; consolidated table ab-claude/benchmark-3-models.md; session total US$ 32.26 of 80 authorized"
  - event: static_validation
    by: "agent:claude"
    at: "2026-09-15T03:51:22Z"
    scope: "plugins/sdd-composy (skills, commands, references, README*, manifestos, 2 templates) + .opencode-plugin/install.py + tests/test_sdd_composy_opencode.py"
    source: "python3 -m unittest discover -s tests -p 'test_sdd_composy_*.py' → Ran 345 tests, OK (336 preexistentes + 9 novos); skill-creator quick_validate.py → 17/17 'Skill is valid!'; links relativos de skills/commands/references resolvidos; 0 referências órfãs; grep sem 'Workspace language', sem chaves yaml no corpo, sem 'Claude Code and Codex'; frontmatter YAML das 17 skills parseável; install.py --dry-run: 17 links + 17 comandos, nada escrito"
---

# sdd-composy — revisão e refatoração (2026-09-15)

**Alvo:** `plugins/sdd-composy` em `cc19ad1 fix(catalog): append pwdev-excalidraw after the pinned order; inventory test ignores benchmark copies` (árvore de trabalho, nada commitado).
**Baseline:** cópia dos arquivos regulares não-secretos de skills, commands, references, READMEs, manifestos e
templates em `versions/baseline/` (gitignored), hashes em `versions/baseline.sha256`.
**Perfis:** executor `guided`; alvo `guided` para consumidores mistos (Claude Code, Codex, Hermes, OpenCode) —
nenhum benchmark mede lean vs guided para os modelos que consomem este plugin.
**Decisões do usuário:** testes existentes intocados (fixam frases literais); escopo Markdown + OpenCode no nível
descoberta/comandos/docs; defeitos de scripts e schemas ficam como recomendações.

## Mudanças por fase

| Fase | O que mudou | Requisito preservado |
| --- | --- | --- |
| 1 | C1 chaves yaml removidas do corpo de `sdd-status`; C2 seção PT "Runtime Hermes" removida de `workflow.md`; C4 `metadata.version` e H1 em quick/loop/fleet; C5 `$sdd-<name>` (nome do frontmatter, confirmado na doc do Codex); C6/C7 `artifacts.md` com `task-<id>.md` e `fleet/<fleet-id>/members/`, `templates/task.md` CA→`prd.md`; C8 caso dos estados em qa/verify e `quality.md`; C9 CLI real de `sdd_loop.py`, `sdd_trace.py` (record é API), `sdd_tasks.py verify`, `commands/sync.md`; C10 classificações, operações e razões terminais completas; C11 frontmatter inválido removido de `status.md`/`trace.md`; C12 `AGENTS.md` do projeto-alvo; C13 `verdict.md` sem `COMPLETE` como verdict | CLI documentada = CLI real; `transition: verify_required` e `COMPLETE` literais (testes) |
| 2 | Bloco de idioma (147 tokens × 16) → uma linha por skill com condição; `language.md` única fonte; `workflow.md`/`runtime.md` reduzidos a link + tokens exigidos por teste | `not_initialized`/`run_init` em toda skill; localização só de prosa humana |
| 3 | Linha única de segurança em 17 skills; prosa de fronteira do adaptador removida; 17 comandos no mesmo formato de 3 frases (`verify.md` mantém "artifact predicates / lifecycle transitions"); 17 `openai.yaml` no formato `interface:` com `default_prompt` só de roteamento; disclosure do loop só na skill, com propósito | "Do not commit"/"Do not read or expose"/"portable" (testes); política do loop em um lugar |
| 4 | Toda referência lida com condição ("Read when"); 11 órfãs ligadas (`loop`, `fleet`, `cmux`, `status`, `trace`, `quick`, `okf`, `artifacts`, `language`, `hermes-tools` via `runtime.md`); `evidence.md` fundido em `artifacts.md`; regra única por tema (parada do loop → `loop.md`, frontmatter OKF → `okf.md`, admissão → `fleet.md`, Markdown/JSON → `synchronization.md`, append-only → `trace.md`); rosters "when applicable"; P3/P5/P7 com propósito ou removidos | termos obrigatórios acompanharam os blocos movidos |
| 5 | 17 descrições: capacidade + estado de lifecycle + frases EN/PT + "Do NOT use for" | — (camada nova, ver limites) |
| 6 | OpenCode: `.opencode-plugin/install.py` (só link; 17 skills + 17 comandos `/sdd-<name>`; `--project`, `--uninstall`, `--dry-run`, `--force`; inventário fechado) + `tests/test_sdd_composy_opencode.py` (9 casos, TDD); `runtime.md` com 4 runtimes, tabela de vetores, "LOOP/FLEET em OpenCode = NOT_RUN"; READMEs EN/PT com tabela dos 17 comandos e bloco OpenCode; 3 manifestos com 4 runtimes | Hermes: `name`/`version` do manifesto intocados (teste) |

## Medição estática (diagnóstico, não eficiência)

`tokens.py` com `estimate:chars/4` (tiktoken indisponível no interpretador do script; antes e depois medidos com a
mesma fonte).

| skill | description antes | depois | corpo antes | depois | Δ corpo |
|---|---:|---:|---:|---:|---:|
| sdd-evidence | 17 | 106 | 416 | 440 | +24 |
| sdd-execute | 27 | 112 | 507 | 469 | -38 |
| sdd-fleet | 22 | 114 | 706 | 629 | -77 |
| sdd-init | 74 | 114 | 882 | 771 | -111 |
| sdd-loop | 29 | 113 | 631 | 669 | +38 |
| sdd-map | 54 | 114 | 1026 | 698 | -328 |
| sdd-prd | 52 | 104 | 1132 | 831 | -301 |
| sdd-qa | 16 | 111 | 441 | 443 | +2 |
| sdd-quick | 26 | 132 | 584 | 578 | -6 |
| sdd-review | 18 | 108 | 640 | 587 | -53 |
| sdd-status | 19 | 91 | 412 | 342 | -70 |
| sdd-stories | 47 | 97 | 1022 | 865 | -157 |
| sdd-sync | 29 | 106 | 684 | 530 | -154 |
| sdd-tasks | 23 | 119 | 860 | 695 | -165 |
| sdd-techspec | 55 | 114 | 1189 | 951 | -238 |
| sdd-trace | 21 | 87 | 496 | 460 | -36 |
| sdd-verify | 16 | 108 | 379 | 391 | +12 |
| **total** | 545 | 1850 | 12007 | 10349 | -1658 |

- Corpos (pagos por ativação): 12007 → 10349 (-14 %). `sdd-loop` (+38) e `sdd-evidence` (+24) cresceram por documentar a CLI real.
- Referências: 14 246 → 14 009 chars/4 (movidas atrás de condições, não removidas; `runtime.md` cresceu com OpenCode).
  Antes, a carga por ativação somada nas 17 skills era 37 160 (corpo + referências incondicionais + templates);
  depois nenhuma referência é incondicional — **se** os modelos respeitarem as condições, o que só o transcrito de uma rodada comportamental mostra.
- Comandos: 1 933 → 1 721. `description` (paga em toda conversa nos catálogos Codex/OpenCode/Hermes): 545 → 1850.

## Comandos executados e resultados

- `python3 -m unittest discover -s tests -p "test_sdd_composy_*.py"` — antes: Ran 336, OK; depois de cada fase e no fim: Ran 345, OK.
- `quick_validate.py` (skill-creator) nas 17 skills — 17 × "Skill is valid!" (após remover `<slug>` de três descrições).
- Verificação de links relativos, órfãs, greps de resíduos, parse YAML — sem achados.
- `python3 plugins/sdd-composy/.opencode-plugin/install.py --dry-run` — 17 links + 17 comandos planejados, nada escrito.
- `git diff --stat`: 76 arquivos, +1 027 / −1 116; novos: `.opencode-plugin/install.py`, `tests/test_sdd_composy_opencode.py`, este diretório.

## Rodada A/B mínima no Claude (2026-09-15)

Harness: `ab-claude/run_ab.py` (reutiliza `runtimes.py`; expõe o **plugin inteiro** como `--plugin-dir`, porque
as skills chamam `scripts/` e `references/`); casos, checagens objetivas, sondas, modelo e limites fixados
antes em `ab-claude/cases.json`. Modelo `claude-sonnet-5`, effort `medium`, Claude Code 2.1.272, 1 repetição
(caso 3: 2 repetições extras na rodada 2). Total gasto: US$ 6.41 (teto fixado: 12).

| rodada | braço | executados | aceitos | US$/aceito | contexto médio | sondas P / C |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 (3 casos) | candidata | 3 | 3 | 0,338 | 614 671 | 1,0 / 1,0 |
| 1 (3 casos) | baseline | 3 | 3 | 0,289 | 447 407 | 0,6 / 0,75 |
| 2a+2b (caso 3) | candidata corrigida | 2 | 2 | 0,399 | 739 540 | — |
| 2a+2b (caso 3) | baseline | 2 | 2 | 0,332 | 532 276 | — |

**O que a rodada 1 achou (e corrigiu):** a candidata escreveu o PRD **sem renderizar `templates/prd.md`** em
1 de 2 execuções observadas (diagnóstico com `stream-json`: nenhuma leitura de `templates/prd.md`,
`references/product.md` nem execução de `sdd_language.py`; cabeçalhos próprios, sem `verified`). A baseline,
que mandava ler tudo antes, renderizou o template em 4 de 4. Foi uma instrução essencial perdida ao tornar a
leitura condicional. Correção (rodada 2, dentro das três iterações do protocolo): nas skills de autoria e de
relatório, `sdd_language.py` virou o passo 1 do procedimento e a leitura do template passou a ser explícita e
obrigatória ("Read `templates/x.md` and render it; keep its keys and headings"). Duas checagens de estrutura
entraram nos casos. Rodada 2: candidata 2/2 aceita com as 12 checagens.

**Decisão contra os limites fixados:** aceite — igual (3/3 e 2/2 nos dois braços, após a correção); disparo —
candidata melhor nas 8 sondas (P 1,0 / C 1,0 vs 0,6 / 0,75: a baseline escolheu `qa` para "revisar" e
`status` para "status do git"); **custo por tarefa aceita — candidata acima da baseline em 6 de 7 pares**
(caso 3, n=4 por braço: média 0,42 vs 0,38; casos 1-2: +10 % e +14 %). Um resultado fora de um limite não é
ganho: a refatoração **não** pode ser declarada mais eficiente no Claude. Com 1-2 repetições e um único modelo, o
sinal de custo é direção, não prova (o diagnóstico do caso 3 inverteu: 0,43 vs 0,49).

**Limites desta rodada:** um modelo, 3 casos, 1-2 repetições; a saída `json` não expõe chamadas de ferramenta
(só o diagnóstico `stream-json` mostrou os arquivos lidos); as checagens são proxies do uso do helper (valores
que só o helper produz), não observação direta; sondas de disparo com 8 consultas.

**Próximo passo se o custo importar:** ablação por componente (descrições longas × núcleo curto × leitura
condicional) com ≥ 3 repetições, e Codex/Hermes/OpenCode. Hipótese a testar: a candidata explora mais o
workspace (mais turnos) porque o núcleo perdeu o contexto inline que a baseline carregava.

## Três modelos Claude (2026-09-15, orçamento autorizado US$ 80)

Mesmos casos, sondas, tetos por run (Opus 3 / 0,5; Fable 6 / 2) e 1 repetição; sondas reclassificadas do disco
(o Fable responde `sdd-composy:sdd-prd`). Tabela completa, com tempo por run, p50 e tempo de parede:
`ab-claude/benchmark-3-models.md`; resumos em `ab-claude/{sonnet,opus,fable}/summary.json`.

| modelo | braço | aceitos | US$/aceito | contexto médio | exec p50 s | sondas P / C |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| claude-sonnet-5 | candidata | 3/3 | 0,338 | 614 671 | 49,5 | 1,0 / 1,0 |
| claude-sonnet-5 | baseline | 3/3 | 0,289 | 447 407 | 44,6 | 0,6 / 0,75 |
| claude-opus-5 | candidata | 3/3 | 0,632 | 295 674 | 43,9 | 1,0 / 1,0 |
| claude-opus-5 | baseline | **2/3** | 0,928 | 287 361 | 41,6 | 1,0 / 1,0 |
| claude-fable-5-1 | candidata | 3/3 | 1,090 | 288 340 | 61,5 | 1,0 / 1,0 |
| claude-fable-5-1 | baseline | 3/3 | 1,198 | 308 742 | 30,3 | 1,0 / 1,0 |

- **Opus:** a baseline reprovou no caso PRD (escreveu o PRD sem os cabeçalhos do template: ['## Problema', '## Objetivos', '## Métricas de sucesso', '## Escopo']…), a candidata
  corrigida passou 3/3; custo por tarefa aceita da candidata **menor** (0,63 vs 0,93) por efeito do aceite; custo
  bruto por run praticamente igual (+1 %). Disparo igual (8/8 nos dois braços).
- **Fable:** 3/3 nos dois braços; candidata **mais barata** por tarefa aceita (1,09 vs 1,20), sobretudo no caso PRD
  (1,42 vs 1,81); tempo p50 maior na candidata (61 s vs 30 s, puxado pelo caso 2: 62 s vs 28 s). Disparo 8/8 nos dois.
- **Sonnet:** único modelo em que a candidata custou mais por tarefa aceita (+17 %); único em que a baseline errou
  sondas (`qa` por "revisar", `status` por "status do git").
- Tempo de parede por grade de 22 runs com 3 processos em paralelo: Opus 143 s, Fable 157 s.

**Decisão contra os limites fixados, por modelo:** aceite — candidata ≥ baseline nos três (Opus: melhor); disparo —
≥ nos três (Sonnet: melhor); custo por tarefa aceita — candidata ≤ baseline em Opus e Fable, > em Sonnet. A
refatoração passa nos limites em Opus e Fable e falha no custo em Sonnet, com 1 repetição por modelo: um resultado
por direção, não uma prova. Não há base para um perfil por modelo além de `guided` para todos.

## Modelos executados

`claude-sonnet-5`, `claude-opus-5`, `claude-fable-5-1` (Claude Code 2.1.272, effort medium), custo real reportado
pelo runtime. Codex, Hermes e OpenCode: não executados.

## Rótulos

`refactored` · `statically validated` · `behaviorally evaluated` (claude-sonnet-5, claude-opus-5, claude-fable-5-1; 3 casos e 8 sondas, 1 repetição). Eficiência: candidata dentro dos limites em Opus e Fable, fora no custo em Sonnet; sem prova estatística.

## Limites e próximos passos

1. Eficiência no Claude: custo por tarefa aceita acima da baseline (ver rodada A/B). Ablação por componente com
   ≥ 3 repetições antes de qualquer decisão sobre as descrições longas; Codex após 2026-09-19; OpenCode só após
   corrigir o vetor (`--auto` em 1.18.31) em `runtimes.py`. `bench.py` não serve para este alvo (mede a skill-refactor);
   `ab-claude/run_ab.py` é o driver.
2. A camada `description` triplicou; mantê-la depende dos `trigger_evals` (precisão/cobertura ≥ baseline por modelo);
   caso contrário, reverter só essa fase (ablação por componente).
3. Fora do escopo, sem edição (ver plano, "Fora do escopo" 1-15): schemas que não validam o que os scripts escrevem,
   `run.sh` → `flow_audit.py` inexistente, `ui-tmux/headless` nunca carregados, duplicação nos `loop-engine-*`,
   engines OpenCode para loop/fleet, prefixo `sdd-composy:` no banner Hermes vs registro sem prefixo,
   `marketplace.json` do repositório ainda com "Claude Code and Codex".
4. Correção ao diagnóstico da revisão: o link `../prd-{{SLUG}}/prd.md` em `templates/task.md` era válido; só o alvo
   de `CA-001` estava errado.
