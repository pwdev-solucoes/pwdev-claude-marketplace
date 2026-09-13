# Task F04-21 — quality review round 3

## SPEC: PASS

Os contratos permanecem conformes. `qa-report` faz uma única invocação exata do exporter, mantém
tests/manifest/evidence commands inertes, valida critérios e evidências antes de renderizar HTML/PDF
pelo pipeline existente e preserva autorização, limitações e diagnósticos. `qa-status` apenas resume
o estado registrado, preserva todos os campos exigidos e não executa, exporta, gera relatório nem
muta estado. Especialistas, outputs exatos, wrappers finos e portabilidade Hermes não regrediram.

## QUALITY: PASS

Os dois findings anteriores foram corrigidos. O scanner estrutural separa sentenças e adversativas,
reconhece formas ativas, passivas e flexionadas dos verbos destrutivos, vincula o verbo ao objeto
protegido e preserva negações explícitas válidas.

## FINDINGS

### Blocker

Nenhum.

### Major

1. **ADDRESSED** — `tests/test_qa_workflows.py:898`: `skips`, `skipped`, `skipping` e a forma passiva
   “may be skipped” para evidence validation são rejeitadas. Controles “never skips” e “must not be
   skipped” permanecem aceitos.

2. **ADDRESSED** — `tests/test_qa_workflows.py:1008`: `discards` é rejeitado isoladamente para cada
   um dos dez campos protegidos: ID, status, expected, observed, evidence reference, sanitization,
   current, superseded, scope decision e missing item. Os controles “does not discard ID” e a
   formulação válida “rather than dropping them” permanecem aceitos.

### Minor

Nenhum.

## Evidência fresca

- HEAD observado e mantido: `98046b8`.
- `git diff --check 75f7335..98046b8`: passou.
- Python 3.12 empacotado, `python -m unittest -v tests.test_qa_workflows`: 31 testes, OK.
- Python 3.12 empacotado, `python -m unittest discover -s tests -p 'test_qa_*.py'`: 173 testes, OK.
- Mutation probes: quatro formas de bypass de evidence validation e dez mutações `discards` foram
  eliminadas individualmente.
- Controles válidos: quatro formulações negativas/não destrutivas passaram, sem falso positivo.

## REVIEW: APPROVED

Nenhuma falha ou pendência vigente foi encontrada no escopo desta re-revisão.
