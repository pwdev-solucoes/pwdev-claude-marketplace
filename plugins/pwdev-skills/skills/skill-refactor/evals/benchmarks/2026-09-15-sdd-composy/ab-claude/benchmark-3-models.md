# A/B por modelo — sdd-composy (Claude Code 2.1.272, effort medium, 1 rep; sondas reclassificadas)

| modelo | braço | aceitos | US$ total exec | US$/aceito | contexto médio | exec p50 s | exec total s | sondas P / C | sondas p50 s | US$ sondas |
|---|---|---:|---:|---:|---:|---:|---:|---|---:|---:|
| claude-sonnet-5 | candidate | 3/3 | 1.014 | 0.3379 | 614671 | 49.5 | 183.5 | 1.0 / 1.0 | None | 1.0653 |
| claude-sonnet-5 | baseline | 3/3 | 0.866 | 0.2887 | 447407 | 44.6 | 144.0 | 0.6 / 0.75 | None | 1.0734 |
| claude-opus-5 | candidate | 3/3 | 1.895 | 0.6318 | 295674 | 43.9 | 165.6 | 1.0 / 1.0 | 5.3 | 2.3083 |
| claude-opus-5 | baseline | 2/3 | 1.856 | 0.9279 | 287361 | 41.6 | 167.2 | 1.0 / 1.0 | 5.6 | 2.2977 |
| claude-fable-5-1 | candidate | 3/3 | 3.269 | 1.0895 | 288340 | 61.5 | 185.0 | 1.0 / 1.0 | 5.7 | 4.875 |
| claude-fable-5-1 | baseline | 3/3 | 3.595 | 1.1983 | 308742 | 30.3 | 158.4 | 1.0 / 1.0 | 5.6 | 4.8062 |

Sonnet caso 3 após a correção da candidata (rodada 2, 2 reps): candidata US$ 0.341/0.458, 66/76 s; baseline US$ 0.330/0.334, 60/71 s.

| caso | modelo | candidata US$ / s | baseline US$ / s | candidata pass | baseline pass |
|---|---|---|---|---:|---:|
| 1 status_readonly | claude-sonnet-5 | 0.254 / 36 | 0.232 / 27 | 1.00 | 1.00 |
| 1 status_readonly | claude-opus-5 | 0.431 / 24 | 0.424 / 26 | 1.00 | 1.00 |
| 1 status_readonly | claude-fable-5-1 | 0.873 / 29 | 0.879 / 30 | 1.00 | 1.00 |
| 2 tasks_next_readonly | claude-sonnet-5 | 0.297 / 50 | 0.261 / 45 | 1.00 | 1.00 |
| 2 tasks_next_readonly | claude-opus-5 | 0.553 / 44 | 0.547 / 42 | 1.00 | 1.00 |
| 2 tasks_next_readonly | claude-fable-5-1 | 0.980 / 62 | 0.906 / 28 | 1.00 | 1.00 |
| 3 prd_draft_gate | claude-sonnet-5 | 0.463 / 98 | 0.373 / 72 | 1.00 | 1.00 |
| 3 prd_draft_gate | claude-opus-5 | 0.911 / 98 | 0.884 / 99 | 1.00 | 0.92 |
| 3 prd_draft_gate | claude-fable-5-1 | 1.416 / 95 | 1.810 / 100 | 1.00 | 1.00 |

| sonda | esperado | sonnet c/b | opus c/b | fable c/b |
|---|---|---|---|---|
| Em que pé está o fluxo SDD deste repositório? | sdd-status | sdd-status / sdd-status | sdd-status / sdd-status | sdd-status / sdd-status |
| Crie o PRD para a funcionalidade de exportar o relatóri | sdd-prd | sdd-prd / sdd-prd | sdd-prd / sdd-prd | sdd-prd / sdd-prd |
| Liste as tarefas do bundle demo e diga qual é a próxima | sdd-tasks | sdd-tasks / sdd-tasks | sdd-tasks / sdd-tasks | sdd-tasks / sdd-tasks |
| Revisar a TASK-002 que acabou de passar no QA. | sdd-review | sdd-review / sdd-qa | sdd-review / sdd-review | sdd-review / sdd-review |
| Mostra o status do git e quais arquivos mudaram. | NONE | NONE / sdd-status | NONE / NONE | NONE / NONE |
| Quanto está custando a AWS este mês? | NONE | NONE / NONE | NONE / NONE | NONE / NONE |
| Roda um loop de 5 em 5 minutos checando se o deploy ter | NONE | NONE / NONE | NONE / NONE | NONE / NONE |
| Traduza este README para inglês. | NONE | NONE / NONE | NONE / NONE | NONE / NONE |

Gasto total da sessão de A/B (3 modelos + rodada 2 + fumaça Fable + diagnóstico): US$ 32.26 de 80 autorizados. Tempo de parede por grade (22 runs, 3 em paralelo): opus 143.4 s, fable 157.2 s, sonnet None s.
