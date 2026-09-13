# Task F04-20 — quality review round 3

## SPEC: PASS

Os contratos de `qa-review` e `qa-release` permanecem conformes. Review preserva requisitos,
cobertura, findings e todas as sete superfícies somente leitura. Release mantém parecer e decisão
humana separados, recebe/preserva/registra/emite actor, authority, scope, rationale e timestamp,
aplica `FAIL` / `BLOCKED` / `PASS` com a precedência exigida e exclui individualmente todas as seis
categorias pendentes sob `PASS`. Especialistas, autorização, ausência de efeitos externos/release,
outputs exatos, wrappers finos e portabilidade Hermes não regrediram.

## QUALITY: PASS

Os dois findings da rodada anterior foram corrigidos. Os testes agora protegem a cláusula completa
e inequívoca de somente leitura, rejeitam permissão contraditória independentemente do sujeito e
verificam os cinco campos da decisão humana nos limites de input, procedimento positivo e output.
As verificações de pendências continuam independentes.

## FINDINGS

### Blocker

Nenhum.

### Major

1. **ADDRESSED** — `tests/test_qa_workflows.py:567`: a mutação exata “never ... product, but may
   mutate tests, contracts, approvals, evidence, findings, or state” agora é rejeitada. A remoção
   individual de qualquer uma das sete superfícies também é rejeitada.

2. **ADDRESSED** — `tests/test_qa_workflows.py:626`: a mutação exata “Never record actor,
   authority, scope, rationale, and timestamp” agora é rejeitada. A remoção individual de cada campo
   falha nos testes, e input, ação positiva de registro e output `HUMAN_DECISION` são verificados.
   A remoção individual de pending work, risk, limitation, evidence, gate ou required decision e a
   redução de `PASS` à ausência de falha também são rejeitadas.

### Minor

Nenhum.

## Evidência fresca

- HEAD observado e mantido: `b070d5f`.
- `git diff --check 16c5c78..b070d5f`: passou.
- Python 3.12 empacotado, `python -m unittest -v tests.test_qa_workflows`: 26 testes, OK.
- Python 3.12 empacotado, `python -m unittest discover -s tests -p 'test_qa_*.py'`: 168 testes, OK.
- Mutation probes: as duas mutações contraditórias exatas, sete remoções de superfícies, cinco
  remoções de campos humanos, seis remoções de pendências e a redução global da guarda de `PASS`
  foram todas eliminadas.
- Controle de falso positivo: a formulação válida que permite correção de produto somente em uma
  operação separada, explicitamente solicitada e autorizada continuou aceita.

## REVIEW: APPROVED

Nenhuma falha ou pendência vigente foi encontrada no escopo desta re-revisão.
