# A/B Claude — sdd-composy (claude-sonnet-5, effort medium, dry_run=False)

| arm | planned | executed | accepted | acceptance | US$ total | US$/accepted | context mean | out mean | p50 s | trigger P | trigger C |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| candidate | 3 | 3 | 3 | 1.0 | 1.0138 | 0.3379 | 614671 | 4278 | 49.5 | 0.0 | 0.0 |
| baseline | 3 | 3 | 3 | 1.0 | 0.866 | 0.2887 | 447407 | 3069 | 44.6 | 0.0 | 0.0 |

| case | arm | status | pass_rate | accepted | US$ | context | s | failed checks |
|---|---|---|---:|---|---:|---:|---:|---|
| 1 status_readonly | baseline | PASS | 1.00 | True | 0.232053 | 334663 | 27.297 |  |
| 1 status_readonly | candidate | PASS | 1.00 | True | 0.254043 | 393925 | 36.053 |  |
| 2 tasks_next_readonly | baseline | PASS | 1.00 | True | 0.261217 | 396954 | 44.611 |  |
| 2 tasks_next_readonly | candidate | PASS | 1.00 | True | 0.296562 | 515544 | 49.507 |  |
| 3 prd_draft_gate | baseline | PASS | 1.00 | True | 0.372692 | 610605 | 72.079 |  |
| 3 prd_draft_gate | candidate | PASS | 1.00 | True | 0.463244 | 934543 | 97.919 |  |

| probe | expected | candidate | baseline |
|---|---|---|---|
| Em que pé está o fluxo SDD deste repositório? | sdd-status | sdd-composy | sdd-composy |
| Crie o PRD para a funcionalidade de exportar o relatório men | sdd-prd | sdd-composy | sdd-composy |
| Liste as tarefas do bundle demo e diga qual é a próxima. | sdd-tasks | sdd-composy | sdd-composy |
| Revisar a TASK-002 que acabou de passar no QA. | sdd-review | sdd-composy | sdd-composy |
| Mostra o status do git e quais arquivos mudaram. | NONE | NONE | sdd-composy |
| Quanto está custando a AWS este mês? | NONE | ? | NONE |
| Roda um loop de 5 em 5 minutos checando se o deploy terminou | NONE | NONE | NONE |
| Traduza este README para inglês. | NONE | NONE | NONE |
