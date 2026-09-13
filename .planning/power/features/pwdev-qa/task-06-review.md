# Task 06 — revisão

## SPEC

FAIL

Os três especialistas possuem as seis seções exigidas e dois cenários de referência. Dados separa
reconciliação, integridade, transação e atomicidade; acessibilidade não promove scanner limpo sem
teclado/foco; performance exige percentis, amostra, contexto e bloqueia carga sem autorização.
Entretanto, os cenários positivos de dados e performance não carregam autorização suficiente para
as observações/mutações que representam, contrariando CA-015 e o próprio contrato das skills.

## QUALITY

FAIL

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_qa_specialists
  tests.test_qa_core tests.test_qa_tooling tests.test_qa_runtime_contracts` — PASS, 41 testes.
- `git diff --check 8db1e6b..a071e36` — PASS.
- O pacote altera os quatro arquivos de implementação/teste declarados e o relatório; HEAD
  permaneceu em `a071e36`.
- Os testes verdes codificam os dois cenários incompletos como `READY`, portanto não afastam os
  findings abaixo.

## FINDINGS

### Important — cenário de dados observa mutações sem demonstrar autorização

`plugins/pwdev-qa/skills/qa-specialist-data/SKILL.md:20-21` exige autorização explícita para toda
mutação e `SKILL.md:26-27` proíbe inferi-la da presença de cliente ou credencial. Apesar disso, o
cenário `complete-data-check` em `SKILL.md:63-66` registra commit e rollback observados e ausência
de escrita parcial, mas não inclui autorização, alvo, dataset, limite de escrita ou evidência. O
teste em `tests/test_qa_specialists.py:425-448` aceita esse registro como `READY` sem verificar
nenhuma dessas precondições. Isso permite que um exemplo de execução transacional pareça utilizável
mesmo sem provar que a mutação estava autorizada. Inclua a autorização e seu escopo no cenário
positivo e um cenário/teste que mantenha transação `BLOCKED`/`NOT_RUN` quando ela faltar.

### Important — perfil de carga fica `READY` com autorização não rastreável

`plugins/pwdev-qa/skills/qa-specialist-performance/SKILL.md:22-23` exige que a autorização nomeie
alvo, limites, ambiente e janela de tempo; `SKILL.md:33-35` determina bloquear e não executar se
qualquer parte faltar. A linha `authorized-profile` em `SKILL.md:65-68`, porém, reduz a autorização
a `explicit and bounded`: o workload contém intensidade/duração e o contexto contém staging/build,
mas nenhum alvo nem janela de tempo autorizada são identificados. Ainda assim, a linha recebe
`READY` e o teste em `tests/test_qa_specialists.py:500-523` valida apenas a frase genérica, usando
uma regex separada sobre as instruções como substituto da autorização do cenário. Faça o cenário
carregar os quatro componentes exatos da autorização e teste omissões de alvo, limites, ambiente e
janela como `BLOCKED`/`NOT_RUN`, nunca `READY`.

### Critical

Nenhum.

### Minor

Nenhum.

## REVIEW

CHANGES_REQUESTED

Corrigir os dois findings Important e repetir a suíte focada, as regressões F01/F02 e o
`diff --check` com evidência fresca.
