# Power ledger — plan: .planning/power/features/sdd-composy-corrections/plan.md

Created: 2026-09-09T17:13:28Z

## Progress

- Baseline: `2941fb1`; suíte `python3 -m unittest discover -s tests -p 'test_sdd_composy*.py'` passou (299 testes, 45.139s).
- Aprovação humana registrada em 2026-09-09T17:14:54Z.
- Alterações locais de `sdd_status.py` e `test_sdd_composy_hermes.py` transportadas sem alterar a main.
- Task 01: fix round 1 — dois achados Important devolvidos ao implementador.
- Task 01: minor (deferred): renomear o teste cuja asserção `active` contradiz “is_not_active” no nome.
- Task 01: complete (commits 2941fb1..eb433a8, review clean after fix round 1).
- Task 02: recovery implementer used after prior agent usage-limit failure; commit 664e314 preserved the partial work.
- Task 02: fix round 1 — quatro findings Important devolvidos ao recovery implementer.
- Task 02: fix round 2 — três Important addressed; tratamento estruturado de falha após publicação de documentos permaneceu aberto.
- Task 02: complete (commits eb433a8..fe5686e, review clean after fix round 2).
- Task 03: fix round 1 — preservar campos desconhecidos e impedir tradução de evidência dinâmica.
- Task 03: complete (commits fe5686e..b1301d0, review clean after fix round 1).
- Task 04: fix round 1 — guard do estágio canônico `VERIFY` e evidência real.
- Task 04: minor (deferred): relatório alegou captura de ambiente sem asserção automatizada correspondente.
- Task 04: complete (commits b1301d0..02a1ad8, review clean after fix round 1).
- Task 05: fix round 1 — validação real do schema, fixture/migração v1 e reconciliação da suíte agregada.
- Task 05: minor (deferred): comentário em `run.sh` ainda dizia `codex|claude`.
- Task 05: fix round 2 — validador Draft 2020-12 completo e migração somente de worktree independente.
- Task 05: complete (commits 02a1ad8..fe571e8, review accepted; Compose/teardown carried to Task 06 by ruling).
- Task 06: fix round 1 — central resource precedence, missing Compose fail-closed e reconciliação da evidência de testes.
- Task 06: complete (commits fe571e8..ef59026, review approved; traceability note 88→81 documented).
- Task 07: review rejected — Compose ownership documentation exposed a cross-task implementation defect; Hermes mapping contradicted Kanban limitation.
- Task 05/06 cross-contract: complete (commits 5999fa1, 49dc00a, 1ef7adb, 70d1228; producer and consumer reviews approved).
- Task 07: complete (commits ef59026..3e491f8, review clean after fix round 1).
- Task 08: offline review rejected — cinco Important devolvidos ao implementador; nenhuma inferência real autorizada/executada nesta rodada.
- Task 08: minor (deferred): budget exhaustion deve publicar resultado BLOCKED recuperável em vez de abortar sem summary.
- Task 08: fix round 2 — handoff deve atravessar adaptadores e cópia deve recusar nomes de credenciais adicionais.

## Pre-flight scan

| Tarefas | Contrato compartilhado | Decisão |
|---|---|---|
| 01→02 | estado operacional/configuração consumidos pelo init | 02 deve publicar estado válido conforme a validação de 01 |
| 01→06 | aprovação, dependências e trace consumidos pelo LOOP | 06 usa a autoridade JSON e gates definidos em 01 |
| 01→08 | status/tasks/trace exercitados pelo harness | 08 não duplica validação; chama APIs corrigidas |
| 02↔03 | `test_sdd_composy_runtime.py` e `test_sdd_composy_language.py` | 02 estabelece fixtures de init; 03 as estende sem enfraquecer expectativas |
| 02→07 | política de idioma e compatibilidade documentada | documentação deve refletir comportamento comprovado |
| 02→08 | init bilíngue usado nos cenários reais | harness inicia repositórios temporários limpos |
| 03→08 | mapa e inventário usados no lifecycle | harness valida exclusões e idioma, sem saída autorreferente |
| 04→05 | comandos e identidade dos runtimes consumidos pela fleet | schema/runner devem concordar com os adaptadores reais |
| 04→06 | contrato uniforme dos engines LOOP | 06 preserva `{stage,status,message,verdict,evidence}` |
| 04→08 | launchers reais chamados pelo harness | 08 usa as entradas do plugin, sem reimplementar comandos |
| 05↔06 | `test_sdd_composy_fleet.py`, member v2 e ownership | 06 estende teardown mantendo o schema e isolamento de 05 |
| 05→07 | contratos fleet e migração documentados | documentação descreve somente suporte implementado |
| 05→08 | fleet real de dois membros | harness valida worktrees/branches/ports distintos |
| 06→07 | gates e encerramento LOOP/fleet documentados | docs não prometem merge/completion automáticos |
| 06→08 | lifecycle e teardown exercitados | falhas preservam recursos e não produzem PASS falso |
| 07→08 | comandos públicos de aceitação | smoke confirma exemplos e caminhos documentados |

| Tarefa | Autoconsistência | Resultado |
|---|---|---|
| 01 | 5 arquivos, APIs e teste focado concordam | OK |
| 02 | 4 arquivos, init/localização e testes concordam | OK |
| 03 | 3 arquivos, mapa depende das fixtures de 02 | OK |
| 04 | 5 arquivos, título inclui Claude mas implementação Claude termina em 06 | Ruling registrado abaixo |
| 05 | 5 arquivos, schema/launch/run e testes concordam | OK |
| 06 | 5 arquivos, Claude/LOOP/teardown e testes concordam | OK |
| 07 | 5 arquivos, documentação cobre contratos já implementados | OK |
| 08 | plano enumera 4 arquivos, mas `evidence.md` também é saída administrativa | Ruling registrado abaixo |

## Rulings

Ruling: o título da Tarefa 04 menciona os três runtimes, mas seu escopo implementa Hermes e Codex; Claude Code permanece deliberadamente na Tarefa 06. Se estiver errado, o review de 04 poderá ficar incompleto até 06, sem autorizar antecipar arquivo fora do escopo.
Ruling: `evidence.md` da Tarefa 08 é artefato administrativo de execução sob a pasta do plano, não arquivo de implementação contado no limite. Se estiver errado, a Tarefa 08 excederia seu inventário declarado e deverá ser corrigida antes do commit final.
Ruling: o consumo de `resources.compose_*` pelo teardown é load-bearing, mas `teardown.sh` pertence explicitamente à Tarefa 06; a Tarefa 05 deve publicar e testar o contrato v2, e o finding Critical será carregado como primeiro requisito da Tarefa 06. Se estiver errado, recursos Compose podem ficar órfãos entre as tarefas; por isso nenhuma aceitação real de fleet ocorrerá antes de 06 passar.
Ruling: a evolução v2 tornou duas asserções agregadas obsoletas em `tests/test_sdd_composy.py`, arquivo omitido pelo plano; adicioná-lo excepcionalmente ao fix da Tarefa 05 é a menor correção para manter a suíte verde. Se estiver errado, o escopo da tarefa terá seis arquivos, mas sem essa exceção o gate de qualidade não pode ser satisfeito.
Ruling: a revisão da Tarefa 07 provou que `launch.sh` e `teardown.sh` discordam sobre o Compose central; reabrir as Tarefas 05 e 06 sequencialmente é obrigatório antes de aprovar docs ou executar aceitação. Se estiver errado, haverá commits tardios em tarefas já revisadas; não reabrir custaria possível recurso Compose órfão.
Ruling: `references/hermes-tools.md` pertence à Tarefa 08, mas contradiz agora a limitação Kanban obrigatória; adicioná-lo excepcionalmente ao fix documental da Tarefa 07 evita publicar uma referência incoerente. Se estiver errado, o escopo documental terá seis arquivos, mas a alternativa manteria promessa operacional falsa.
