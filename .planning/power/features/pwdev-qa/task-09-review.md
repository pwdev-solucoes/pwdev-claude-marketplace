# Task 09 — revisão

## SPEC

FAIL

As skills definem corretamente denominador e população, bloqueiam zero aplicável, preservam a
precedência `FAIL`/`BLOCKED`/`PASS`, incluem defeitos sem critério e separam recomendação de
aprovação. Contudo, os cenários positivos não materializam a proveniência auditável da métrica
nem uma decisão humana completa, permitindo `80%` e `PASS` com entradas que os próprios contratos
declaram insuficientes.

## QUALITY

FAIL

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_qa_specialists
  tests.test_qa_core tests.test_qa_tooling tests.test_qa_runtime_contracts` — PASS, 61 testes.
- `git diff --check 323a985..da79217` — PASS.
- O pacote altera somente as duas skills, o teste especializado e o relatório, dentro do limite
  da tarefa; o HEAD permaneceu em `da79217d0f8e081029e46a03eaa70ca7d64d6a1a`.
- Os testes verdes repetem os valores resumidos dos cenários, mas não exercitam as precondições
  ausentes descritas nos findings.

## FINDINGS

### Important — a métrica positiva publica `80%` sem proveniência ou registros auditáveis

`plugins/pwdev-qa/skills/qa-specialist-metrics/SKILL.md:40-41` exige ligar registros incluídos e
excluídos aos seus IDs e à proveniência de evidência; o output em `SKILL.md:49-55` também exige
target, contrato, proveniência da coleta, IDs, referências de evidência, limitações e freshness.
Entretanto, `explicit-rate` em `SKILL.md:59-66` contém apenas contagens, uma população declarada e
um build: não identifica os dez critérios, os dois registros fora do numerador, qualquer item
`NOT_APPLICABLE` e seu motivo, a fonte/coleta ou evidência que sustenta 8/10. O teste em
`tests/test_qa_specialists.py:1140-1170` fixa exatamente essa saída incompleta e aceita `80%`.
Materialize no cenário positivo a proveniência, target/contrato, IDs incluídos/excluídos com
motivos e evidências; ausência de qualquer precondição deve resultar em `BLOCKED`, não percentual.

### Important — prontidão produz `PASS` com decisão humana incompleta

`plugins/pwdev-qa/skills/qa-specialist-readiness/SKILL.md:22-23` e `56-57` exigem actor/decision
maker, authority, scope, rationale e timestamp para a decisão humana; `SKILL.md:84-85` determina
explicitamente `BLOCKED` quando qualquer componente falta. Apesar disso, `release-ready` em
`SKILL.md:63-70` reduz a decisão a `release owner approved` e ainda produz `PASS`. O teste em
`tests/test_qa_specialists.py:1197-1227` cristaliza esse falso positivo sem validar nenhum dos
cinco componentes. Exponha-os separadamente no cenário positivo e teste cada omissão como
`BLOCKED`, mantendo a decisão registrada separada do parecer e sem autoaprovação.

### Critical

Nenhum.

### Minor

Nenhum.

## REVIEW

CHANGES_REQUESTED

Corrigir os dois cenários positivos e seus testes, então repetir a suíte completa aplicável e o
`diff --check` com evidência fresca.
