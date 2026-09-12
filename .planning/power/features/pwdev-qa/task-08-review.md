# Task 08 — revisão

## SPEC

FAIL

As três skills cobrem corretamente as regras narrativas de seleção por impacto, distinção entre
severidade e prioridade, histórico/reteste, defeito vigente sem critério e produção somente
leitura. Porém, seus cenários positivos não materializam rastreabilidade, precedência global e
autorização/prevenção com informação suficiente para sustentar `READY` ou `PASS`.

## QUALITY

FAIL

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_qa_specialists
  tests.test_qa_core tests.test_qa_tooling tests.test_qa_runtime_contracts` — PASS, 54 testes.
- `git diff --check 67872a7..e5a2c0c` — PASS.
- O pacote altera os quatro arquivos de implementação/teste declarados e o relatório; HEAD
  permaneceu em `e5a2c0c`.
- Os testes verdes validam rótulos resumidos e não exercitam as precondições omitidas nos findings.

## FINDINGS

### Important — regressão `READY` não contém rastreabilidade verificável

`plugins/pwdev-qa/skills/qa-specialist-regression/SKILL.md:51-55` exige critérios, riscos,
defeitos/incidentes e stable case IDs no mapa de impacto e nos checks selecionados/excluídos. O
cenário `impact-selected` em `SKILL.md:64-67` usa apenas o texto genérico “changes to risks
criteria and prior defects”, sem nenhum ID de mudança, critério, risco, defeito ou caso e sem
exclusões. O teste em `tests/test_qa_specialists.py:835-861` aceita esse rótulo como
rastreabilidade suficiente e declara `READY`. Inclua IDs concretos e resolvidos para as relações
change → impact/risk/criterion/defect → selected/excluded stable case IDs; ausência deve bloquear.

### Important — resolução de um defeito produz `PASS` sem provar todos os critérios aplicáveis

`plugins/pwdev-qa/skills/qa-specialist-defects/SKILL.md:41-44` preserva a regra de que `PASS` exige
todos os critérios aplicáveis aprovados e nenhum defeito vigente. Porém, `verified-resolution` em
`SKILL.md:61-64` muda diretamente para verdict `PASS` apenas com status resolved, retest terminal e
evidência do defeito; não há catálogo/resultados dos demais critérios nem prova de ausência de
outros defeitos. `tests/test_qa_specialists.py:881-905` cristaliza esse falso positivo. O cenário
pode produzir “defect current=false” como input ao verdict; só produza `PASS` quando também houver
evidência explícita de todos os critérios aplicáveis e ausência de outros defeitos.

### Important — produção `READY` usa autorização resumida, não a fronteira exata exigida

`plugins/pwdev-qa/skills/qa-specialist-production/SKILL.md:18-20` e `31-34` exigem target, fontes de
telemetria, identity/role, read-only boundary, fields, window, owner, data rules, stop conditions e
retention. A linha `authorized-observation` em `SKILL.md:72-75` reduz tudo a “explicit read-only
production grant” e “named service metrics and time window”. O teste em
`tests/test_qa_specialists.py:928-954` não verifica nenhuma dimensão individual. Assim, o cenário
pode ficar `READY` com autorização incompleta. Exponha cada componente e teste cada omissão como
observation `NOT_RUN` e outcome `BLOCKED`.

### Important — prevenção não identifica causa nem check determinístico

O procedimento de produção em `SKILL.md:42-47` só permite afirmar causa quando ela é nomeada,
sustentada por evidência target-bound e confrontada com evidência contrária; a prevenção deve
ligar essa causa a evidence ID, criterion/risk (ou motivo unlinked), stable case ID, oracle,
environment e prerequisites. No cenário positivo (`SKILL.md:72-75`), `cause` é apenas “supported
by EV-PROD-001” e `preventive_regression` apenas “linked to cause and EV-PROD-001”: não existe causa
nomeada, caso, oráculo ou relação verificável. O teste (`tests/test_qa_specialists.py:949-954`)
confere somente esses rótulos e uma regex no texto geral. Materialize a causa e o check preventivo
com seus IDs/oráculo, e bloqueie causa hipotética ou prevenção genérica.

### Critical

Nenhum.

### Minor

Nenhum.

## REVIEW

CHANGES_REQUESTED

Corrigir os quatro findings e repetir a suíte focada, as regressões F01/F02 e o `diff --check` com
evidência fresca.
