---
type: TASKS
okf_version: "0.2"
generated:
  by: agent:pwdev-power
  at: "2026-09-13T00:49:13Z"
lifecycle:
  status: APPROVED
human_approval: APPROVED
sources:
  - resource: tasks/prd-specflow/prd.md
    sha256: d76143fad520c44972350d48207348c7256fb18a0e112500f6c34d1f6efd2c96
  - resource: tasks/prd-specflow/stories.md
    sha256: 1f0396da2fc57c2156fa1aae9efb45d1133963fa86a1847d2b876bd606e20338
  - resource: tasks/prd-specflow/techspec.md
    sha256: 09bde614371cb465ea1c135244bd6c4e8cc3f3e62c0c9fdeb3dc065d70ab54f3
  - resource: .planning/power/features/specflow-m01/probe-recipe.md
    sha256: c606ebbf29d30881e54dd3e66c58d7e273a5f4bf6d49fd60b980e2171240b7c4
verified:
  - event: human_approval
    by: human:user
    at: "2026-09-12T19:05:36Z"
    scope: tasks/prd-specflow/tasks.md
    source: "user: sim"
  - event: approval_invalidated
    by: agent:pwdev-power
    at: "2026-09-12T19:11:57Z"
    scope: tasks/prd-specflow/tasks.md
    source: ".planning/power/features/specflow-m01/task-02-review-1.md"
    reason: "upstream TechSpec semantic revision; previous approval is stale"
  - event: human_approval
    by: human:user
    at: "2026-09-13T00:02:44Z"
    scope: tasks/prd-specflow/tasks.md
    source: "user: sim"
  - event: approval_invalidated
    by: agent:pwdev-power
    at: "2026-09-13T00:13:19Z"
    scope: tasks/prd-specflow/tasks.md
    source: .planning/power/features/specflow-m01/plan-amendment-01-runtime-recipe.md
    reason: "approved plan amendment adds a new task and changes execution scope"
  - event: human_approval
    by: human:user
    at: "2026-09-13T08:22:00Z"
    scope: tasks/prd-specflow/tasks.md
    source: "user: sim"
    snapshot_sha256: 863e7391fe4b8704c812f4dddea836663237346da07f78a45b1af7d9d65d1b76
  - event: approval_invalidated
    by: agent:pwdev-power
    at: "2026-09-13T08:28:28Z"
    scope: tasks/prd-specflow/tasks.md
    source: ".planning/power/features/specflow-m01/task-04-review.md"
    reason: "upstream TechSpec changed for stale consumer classification"
  - event: human_approval
    by: human:user
    at: "2026-09-13T08:34:15Z"
    scope: tasks/prd-specflow/tasks.md
    source: "user: sim"
    snapshot_sha256: 8ce06b559e9593fef24c0b3c9c7cbbc438756f01b53701b2ab00d4ad1af699a8
---

# SpecFlow — Tasks M01.04

Contrato de execução reaberto pelas Emendas 01/02. PRD APPROVED e Stories APPROVED
permanecem históricos e frescos. O TechSpec corrigido foi aprovado novamente em
2026-09-13T08:30:59Z; este TASKS permanece DRAFT/PENDING e aguarda seu gate separado.
A `RuntimeRecipe[] concreta` e suas sete receitas permanecem
BLOCKED/NOT_RUN, sem ApprovalRef. Task 05 conduz o gate separado da receita e Task 06,
somente após os pré-requisitos, poderá executar probes.

## Task index

| ID | Title | State | Dependencies |
|---|---|---|---|
| TASK-001 | Preparar PRD, Stories/aplicabilidade e receita inicial | historical_done | M01.01; PRD APPROVED; Stories APPROVED |
| TASK-002 | Preparar TechSpec/escopo e contratos de garantias | historical_done | TASK-001; aprovações e invalidações históricas preservadas |
| TASK-003 | Qualificar comandos e propor RuntimeRecipe | pending | TASK-002 histórica; implementação revisada; gates posteriores pendentes |
| TASK-004 | Reconciliar consumidores stale e renovar contratos | pending | TASK-003 revisada; gate renovado de TechSpec antes do gate renovado de TASKS |
| TASK-005 | Vincular aprovação operacional da RuntimeRecipe | blocked | TechSpec e TASKS aprovados/frescos; identidade humana e artifacts demonstráveis |
| TASK-006 | Probe isolado positivo e adversarial | blocked | TASK-005; ApprovalRef real/fresco; receita, escopo, cleanup e budgets aprovados |
| TASK-007 | Reconciliar prova e gate técnico | blocked | TASK-006 com evidência real; QA/review/verify independentes |

Estados `historical_done` registram trabalho histórico. TASK-003 permanece pending no
contrato porque seus gates posteriores não foram satisfeitos. Todos estão não ready e
não complete por existência deste documento.

## TASK-003 — escopo histórico preservado

O contrato anterior dizia `Primeiro gate: TASKS`; a Emenda 02 o tornou stale e exigiu
antes o gate renovado do TechSpec, agora aprovado. A allowlist histórica permanece registrada para que
o teste focado da Task 03 prove que seu escopo não foi adulterado:

allowed_paths:
  - path: `tests/test_sdd_flow_m01_recipe.py`
  - path: `.planning/power/features/specflow-m01/runtime-command-qualification.md`
  - path: `.planning/power/features/specflow-m01/probe-recipe.md`
  - path: `.planning/power/features/specflow-m01/runtime-qualification.md`
  - path: `tasks/prd-specflow/tasks.md`

Esse registro não reabre autoria da Task 03. O gate operacional separado continua
pendente e nenhum comando mutável foi ou será executado pela Task 04.

## TASK-004 — reconciliação e gates documentais

### Allowed paths

Allowlist exata dos cinco arquivos de implementação:

allowed_paths:
    - path: `tests/test_sdd_flow_m01_qualification.py`
    - path: `tests/test_sdd_flow_m01_contracts.py`
    - path: `.planning/power/features/specflow-m01/compatibility.md`
    - path: `tasks/prd-specflow/techspec.md`
    - path: `tasks/prd-specflow/tasks.md`

O relatório `task-04-report.md` é evidência operacional, contado separadamente.

### Dependencies and inputs

1. M01.01, PRD APPROVED e Stories APPROVED permanecem válidos.
2. Task 03 entregou sete RuntimeRecipe concretas, ainda BLOCKED e NOT_RUN.
3. TechSpec corrigido está APPROVED; TASKS preserva aprovações/invalidações históricas,
   mas nenhum evento anterior autoriza estes bytes atuais.
4. Inputs são RuntimeRecipe[], QualificationCheck[], ApprovalRef e ArtifactRef como dados.
5. CA-002 / SC-002 e CA-014 / SC-014 continuam bloqueados sem gates e prova real.

### Steps

1. Reproduzir as seis falhas stale com os mesmos IDs e causas.
2. Atualizar testes por TDD sem enfraquecer negativos.
3. Reconciliar compatibility e TechSpec para RuntimeRecipe[] concreta NOT_RUN/BLOCKED.
4. Registrar as sete tasks, allowlists e dependências sem promover estado.
5. Executar a suíte combinada e validar links/digests.
6. Com o TechSpec novamente aprovado, parar no gate humano separado de TASKS.
7. Revisar fronteiras sem probe, commit, instalação, daemon, Loop, Docker, browser ou Live.

### Verification

- `python3 -m unittest tests.test_sdd_flow_m01_contracts`
- `python3 -m unittest tests.test_sdd_flow_m01_recipe tests.test_sdd_flow_m01_qualification tests.test_sdd_flow_m01_contracts`
- `python3 -m unittest tests.test_sdd_flow_m01_contracts tests.test_sdd_flow_m01_qualification tests.test_sdd_composy_product`

Testes estruturais devem executar mais de zero testes e zero falhas, mas não provam
comportamento do runtime.

### Gates e limites

O gate humano de TASKS é posterior e separado do TechSpec; ambos são separados do
gate separado da receita. TechSpec APPROVED e TASKS DRAFT/PENDING significam que
TASK-004 ainda não é ready nem complete. Budgets continuam 3 tentativas totais incluindo
a primeira, janela sem progresso 2 e fan-out 1. Sem Fleet, paralelismo ou merge automático.

STATUS: NEEDS_CONTEXT. Próxima ação única: decisão humana sobre
`tasks/prd-specflow/tasks.md`. Nenhuma aprovação operacional ou probe é solicitado.
