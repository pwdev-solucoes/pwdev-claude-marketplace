# A/B Claude — sdd-composy (claude-sonnet-5, effort medium, claude 2.1.272 (Claude Code), 1 rep, regraded probes)

| arm | planned | executed | accepted | acceptance | US$ total | US$/accepted | context mean | out mean | p50 s | trigger P | trigger C |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| candidate | 3 | 3 | 3 | 1.00 | 1.0138 | 0.3379 | 614671 | 4278 | 49.5 | 1.0 | 1.0 |
| baseline | 3 | 3 | 3 | 1.00 | 0.866 | 0.2887 | 447407 | 3069 | 44.6 | 0.6 | 0.75 |

| case | arm | status | pass_rate | US$ | context | turns-proxy out | s |
|---|---|---|---:|---:|---:|---:|---:|
| 1 status_readonly | baseline | PASS | 1.00 | 0.232053 | 334663 | 1325 | 27.297 |
| 1 status_readonly | candidate | PASS | 1.00 | 0.254043 | 393925 | 1999 | 36.053 |
| 2 tasks_next_readonly | baseline | PASS | 1.00 | 0.261217 | 396954 | 2329 | 44.611 |
| 2 tasks_next_readonly | candidate | PASS | 1.00 | 0.296562 | 515544 | 3133 | 49.507 |
| 3 prd_draft_gate | baseline | PASS | 1.00 | 0.372692 | 610605 | 5554 | 72.079 |
| 3 prd_draft_gate | candidate | PASS | 1.00 | 0.463244 | 934543 | 7702 | 97.919 |

| probe | expected | candidate | baseline |
|---|---|---|---|
| Em que pé está o fluxo SDD deste repositório? | sdd-status | sdd-status | sdd-status |
| Crie o PRD para a funcionalidade de exportar o relatório men | sdd-prd | sdd-prd | sdd-prd |
| Liste as tarefas do bundle demo e diga qual é a próxima. | sdd-tasks | sdd-tasks | sdd-tasks |
| Revisar a TASK-002 que acabou de passar no QA. | sdd-review | sdd-review | sdd-qa |
| Mostra o status do git e quais arquivos mudaram. | NONE | NONE | sdd-status |
| Quanto está custando a AWS este mês? | NONE | NONE | NONE |
| Roda um loop de 5 em 5 minutos checando se o deploy terminou | NONE | NONE | NONE |
| Traduza este README para inglês. | NONE | NONE | NONE |

Total spent this round: US$ 4.0185 (execution + probes); diagnostic rerun of case 3 with stream-json: candidate US$ 0.430 / 14 turns, baseline US$ 0.494 / 15 turns (not aggregated above).
