# Task 07 — revisão

## SPEC

FAIL

Os contratos distinguem scanner de pentest, delimitam target/method/environment/window, separam
`playwright-cli` interativo de Playwright Test repetível/CI, preservam tentativas flaky e derivam o
gate do verdict normalizado sem usar o exit code do exportador. Porém, o cenário positivo de
segurança omite outras fronteiras que a própria skill torna obrigatórias para um pentest seguro,
embora o marque `READY`.

## QUALITY

FAIL

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_qa_specialists
  tests.test_qa_core tests.test_qa_tooling tests.test_qa_runtime_contracts` — PASS, 47 testes.
- `git diff --check a0407c1..34025b2` — PASS.
- O pacote altera os quatro arquivos de implementação/teste declarados e o relatório; HEAD
  permaneceu em `34025b2`.
- Os testes verdes não validam owner/rate/stop/cleanup no cenário de pentest nem a expiração
  obrigatória da quarentena flaky.

## FINDINGS

### Important — pentest `READY` não carrega todas as fronteiras obrigatórias

`plugins/pwdev-qa/skills/qa-specialist-security/SKILL.md:18-21` exige owner responsável, rate
limits, stop conditions e cleanup, além de target, methods, environment e window; o output em
`SKILL.md:52-54` também exige esses campos. Entretanto, `bounded-pentest` em `SKILL.md:63-65`
contém somente grant genérico, target, methods, environment e window antes de declarar `READY`.
Sem owner, limite de taxa, condição de parada e obrigação de cleanup, o cenário não demonstra uma
autorização operacionalmente delimitada para pentest. O teste em
`tests/test_qa_specialists.py:596-630` cristaliza o subconjunto e não testa omissões. Inclua esses
limites na linha positiva e adicione cenários em que cada ausência mantenha execução `NOT_RUN` e
outcome `BLOCKED`.

### Minor — quarentena flaky proposta sem expiração delimitada

`plugins/pwdev-qa/skills/qa-specialist-automation/SKILL.md:39-41` permite quarentena somente com
owner, rationale, bounded expiry, evidência preservada, root-cause work e cobertura visivelmente
`BLOCKED`. A ação do cenário `reproduced-flaky` em `SKILL.md:72-74` registra owner e investigação,
mas omite a expiração delimitada; o teste em `tests/test_qa_specialists.py:710-738` aceita esse
registro. O resultado continua `BLOCKED`, portanto a falha não é mascarada por rerun, mas o handoff
de quarentena fica incompleto. Registre owner, rationale e expiry separadamente no cenário/teste.

### Critical

Nenhum.

## REVIEW

CHANGES_REQUESTED

Corrigir os dois findings e repetir a suíte focada, as regressões F01/F02 e o `diff --check` com
evidência fresca.
