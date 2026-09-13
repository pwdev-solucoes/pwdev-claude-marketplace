---
type: TRACEABILITY
okf_version: "0.2"
generated:
  by: agent:power-roadmap
  at: "2026-09-12T10:31:30Z"
lifecycle:
  status: APPROVED
sources:
  - resource: ".planning/power/product/prd.md"
  - resource: ".planning/power/features/specflow/spec.md"
  - resource: ".planning/power/features/specflow-m01/plan-amendment-01-runtime-recipe.md"
  - resource: ".planning/power/features/specflow-m01/plan-amendment-02-stale-consumers.md"
verified:
  - event: human_approval
    by: human:user
    at: "2026-09-12T10:35:43Z"
    scope: specflow_v1_power_plan
    source: "user: aprovado"
  - event: human_approval
    by: human:user
    at: "2026-09-13T00:13:19Z"
    scope: .planning/power/features/specflow-m01/plan-amendment-01-runtime-recipe.md
    source: "user: sim"
  - event: human_approval
    by: human:user
    at: "2026-09-13T00:34:42Z"
    scope: .planning/power/features/specflow-m01/plan-amendment-02-stale-consumers.md
    source: "user: Aprovar"
---

# SpecFlow — Traceability

Status: APPROVED
Updated: 2026-09-12
Sources: [PRD](../../product/prd.md), [spec](spec.md), [índice](plan.md)

## Cobertura de requisitos
FR-013, FR-014 e FR-017 são obrigatórios. Resumo opcional FR-015 não torna o encerramento FR-017 opcional. As provas ainda não foram executadas; todas as linhas aguardam gates e evidência.

| Requisito | Critérios do PRD | Módulos | Critérios técnicos |
|---|---|---|---|
| FR-001 | AC-002, AC-015 | M04, M05, M06, M08, M12 | AT-03, AT-04, AT-06, AT-11 |
| FR-002 | AC-002, AC-003, AC-004 | M05, M06, M11, M12 | AT-04 |
| FR-003 | AC-002, AC-011 | M01, M05, M06, M08, M12 | AT-01, AT-07 |
| FR-004 | AC-008 | M01, M11, M12 | AT-10 |
| FR-005 | AC-001 | M01, M04, M12 | AT-03 |
| FR-006 | AC-001, AC-005, AC-006 | M04, M07, M09, M12 | AT-03, AT-05, AT-08 |
| FR-007 | AC-005 | M07, M12 | AT-05 |
| FR-008 | AC-007, AC-012 | M08, M12 | AT-06 |
| FR-009 | AC-007 | M02, M03, M08, M10, M12 | AT-02, AT-09 |
| FR-010 | AC-008, AC-009, AC-013 | M01, M07, M08, M11, M12 | AT-07, AT-10 |
| FR-011 | AC-009, AC-013 | M01, M08, M12 | AT-07 |
| FR-012 | AC-010 | M01, M02, M03, M12 | AT-01, AT-02, AT-12 |
| FR-013 | AC-014 | M01, M12 | AT-01, AT-12 |
| FR-014 | AC-006, AC-016 | M02, M03, M07, M09, M10, M12 | AT-05, AT-08, AT-09 |
| FR-015 | resumo agregado opcional; AC-015 obrigatório pelo FR-017 | M08, M10, M12 | AT-11 |
| FR-016 | limite Won't, testes de ausência | M01, M02, M12 | AT-01, AT-02, AT-12 |
| FR-017 | AC-015 | M08, M10, M12 | AT-11 |

## Não funcionais
| Requisito | Cobertura |
|---|---|
| NFR-001 | M11 QUICK cinco arquivos de implementação; limites de autoria Power são separados |
| NFR-002 | M01/M08 três tentativas totais persistentes, filhos/retomada e stalled |
| NFR-003 | M02/M08/M12 links requisito/critério/teste/prova reais e completos |
| NFR-004 | M01/M04/M07/M08/M09/M10/M11/M12 segredos excluídos e recusas comprovadas |
| NFR-005 | M01/M02/M08/M10/M12 caminhos confinados, arquivos regulares e SHA-256 |
| NFR-006 | M04/M07/M09/M12 consentimento e escopo, nenhuma instalação/ativação implícita |
| NFR-007 | M10/M12 HTML sanitizado, PDF derivado/inspecionado e fetch bloqueado |
| NFR-008 | M12 aceitação real das jornadas do produto; baseline de testes de autoria separado no plano |
| NFR-009 | M02/M03/M12 inventário exato e bindings/distribuição validados |

## Provas específicas exigidas
| Critério | Tarefa dona | Evidência de aceitação |
|---|---|---|
| AC-001 | M04.01 | INIT real sem opcionais, recomendações e inventário inalterado |
| AC-002 | M05.01, M06.01 | Standalone com quatro decisões humanas distintas |
| AC-003 | M11.01 | QUICK aceito e sexto arquivo/arquitetura/verificação desconhecida escalados |
| AC-004 | M05.02 | Promoção idempotente, raiz explícita e sem aprovações herdadas |
| AC-005 | M07.01, M07.02 | Dois ambientes isolados; bundle não commitado; engine alterado bloqueado |
| AC-006 | M09.01 | Local padrão e Live com filho fora de escopo recusado |
| AC-007 | M10.01 | HTML/PDF pós-verificação, hash/inspeção e formato solicitado faltante bloqueante |
| AC-008 | M11.02 | Status com fonte/tempo/confiança e zero Run/escrita/mensagem |
| AC-009 | M08.05 | Tentativas persistentes, três no total, ausência de progresso e cancelamento |
| AC-010 | M02.08, M12.01 | Geração instalada em ambiente qualificado, sem outro plugin operacional |
| AC-011 | M01.04, M01.06, M06.01, M08.05 | Edição dos bytes/digest torna gate stale e bloqueia downstream |
| AC-012 | M08.02 | Browser obrigatório ausente é NOT_RUN, nunca PASS/N/A |
| AC-013 | M01.06, M08.05 | Queda antes/depois de publicação; retomada sem repetir gate válido e testes reais frescos quando stale |
| AC-014 | M01.01–M01.07 | Matriz positiva/negativa das garantias centrais, nenhuma capacidade presumida |
| AC-015 | M08.05, M10.01, M12.02 | FeatureClosure completo, integração fresca e decisão humana final |
| AC-016 | M03.04, M10.01, M12.02 | Recibo separado preserva bytes/hash do snapshot aprovado |

## Inventário preservado
9 agentes: coordinator, product, architect, environment, implementer, qa, reviewer, verifier, observer.
20 skills: intake, init, map, promote, network, prd, stories, roadmap, techspec, tasks, quick, environment, execute, qa, evidence, evidence-export, review, verify, status, contracts.
4 Loops: product, feature, quick, delivery. Todos os recursos usam sdd-flow-*.
11 templates: prd.md, stories.md, techspec.md, tasks.md, task.md, quick-contract.md, quick-report.md, qa.md, codereview.md, evidence-report.md, verdict.md. Complementos: roadmap.md, environment.md, approval-receipt.md, export-receipt.md, evidence-report.html.
A matriz das 17 skills-fonte, cláusulas obrigatórias de cada template, enums e tipos está integralmente na [spec](spec.md); dispensa sync/fleet e substituição do motor loop/trace não eliminam segurança/rastreabilidade. Cada diferença requer provenance e teste.

## Hierarquia e IDs
- F01/F01-E01/F01-E01-FT01: [M01](../specflow-m01/plan.md), M01.01 ↔ Task 01 ↔ F01-E01-FT01-T01; M01.02 ↔ Task 02 ↔ F01-E01-FT01-T02; M01.03 ↔ Task 03 ↔ F01-E01-FT01-T03; M01.04 ↔ Task 04 ↔ F01-E01-FT01-T04; M01.05 ↔ Task 05 ↔ F01-E01-FT01-T05; M01.06 ↔ Task 06 ↔ F01-E01-FT01-T06; M01.07 ↔ Task 07 ↔ F01-E01-FT01-T07.
- F01/F01-E01/F01-E01-FT02: [M02](../specflow-m02/plan.md), M02.01 ↔ Task 01 ↔ F01-E01-FT02-T01; M02.02 ↔ Task 02 ↔ F01-E01-FT02-T02; M02.03 ↔ Task 03 ↔ F01-E01-FT02-T03; M02.04 ↔ Task 04 ↔ F01-E01-FT02-T04; M02.05 ↔ Task 05 ↔ F01-E01-FT02-T05; M02.06 ↔ Task 06 ↔ F01-E01-FT02-T06; M02.07 ↔ Task 07 ↔ F01-E01-FT02-T07; M02.08 ↔ Task 08 ↔ F01-E01-FT02-T08.
- F02/F02-E01/F02-E01-FT01: [M03](../specflow-m03/plan.md), M03.01 ↔ Task 01 ↔ F02-E01-FT01-T01; M03.02 ↔ Task 02 ↔ F02-E01-FT01-T02; M03.03 ↔ Task 03 ↔ F02-E01-FT01-T03; M03.04 ↔ Task 04 ↔ F02-E01-FT01-T04.
- F02/F02-E01/F02-E01-FT02: [M04](../specflow-m04/plan.md), M04.01 ↔ Task 01 ↔ F02-E01-FT02-T01; M04.02 ↔ Task 02 ↔ F02-E01-FT02-T02.
- F03/F03-E01/F03-E01-FT01: [M05](../specflow-m05/plan.md), M05.01 ↔ Task 01 ↔ F03-E01-FT01-T01; M05.02 ↔ Task 02 ↔ F03-E01-FT01-T02.
- F03/F03-E01/F03-E01-FT02: [M06](../specflow-m06/plan.md), M06.01 ↔ Task 01 ↔ F03-E01-FT02-T01; M06.02 ↔ Task 02 ↔ F03-E01-FT02-T02.
- F04/F04-E01/F04-E01-FT01: [M07](../specflow-m07/plan.md), M07.01 ↔ Task 01 ↔ F04-E01-FT01-T01; M07.02 ↔ Task 02 ↔ F04-E01-FT01-T02.
- F04/F04-E01/F04-E01-FT02: [M08](../specflow-m08/plan.md), M08.01 ↔ Task 01 ↔ F04-E01-FT02-T01; M08.02 ↔ Task 02 ↔ F04-E01-FT02-T02; M08.03 ↔ Task 03 ↔ F04-E01-FT02-T03; M08.04 ↔ Task 04 ↔ F04-E01-FT02-T04; M08.05 ↔ Task 05 ↔ F04-E01-FT02-T05.
- F05/F05-E01/F05-E01-FT01: [M09](../specflow-m09/plan.md), M09.01 ↔ Task 01 ↔ F05-E01-FT01-T01.
- F05/F05-E01/F05-E01-FT02: [M10](../specflow-m10/plan.md), M10.01 ↔ Task 01 ↔ F05-E01-FT02-T01.
- F06/F06-E01/F06-E01-FT01: [M11](../specflow-m11/plan.md), M11.01 ↔ Task 01 ↔ F06-E01-FT01-T01; M11.02 ↔ Task 02 ↔ F06-E01-FT01-T02.
- F06/F06-E01/F06-E01-FT02: [M12](../specflow-m12/plan.md), M12.01 ↔ Task 01 ↔ F06-E01-FT02-T01; M12.02 ↔ Task 02 ↔ F06-E01-FT02-T02.
IDs hierárquicos são aliases do roadmap e não contratos TASK-NNN. Nenhum contrato existente foi renumerado. Rastreabilidade de contratos do consumidor usa RF/CA/US/SC/DEC/RISK e TU/TI/E2E/TEST reais, sem preencher IDs fictícios.

## Gate
Cobertura proposta não é prova nem aprovação. Todos os módulos dependem de M01 central PASS; release exige testes/jornadas reais, QA/review/verdict independentes, exports contratados e aprovação de Feature, conforme spec. Fonte histórica absoluta e SHA-256 estão na spec somente como provenance, sem dependência operacional de outro checkout.
