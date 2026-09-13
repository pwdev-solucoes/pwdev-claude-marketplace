# Task 13 — revisão

## SPEC

PASS

O pacote `review-f6fb6a4..4f6c179.diff` implementa `render_html(report: dict) -> str` como projeção
estática UTF-8 do modelo allowlisted produzido por `qa_verdict`. O HTML inclui identificação,
contagens, critérios, histórico de casos, expected/observed, defeitos, evidências verificadas,
diagnósticos e parecer. Valores e atributos são escapados, IDs DOM são internos e os resultados
fornecidos são exibidos sem recálculo.

## QUALITY

PASS

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_qa_html` — PASS, 5 testes.
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest $(rg --files tests | sed -n
  's#^tests/\(test_qa_[^/]*\)\.py$#tests.\1#p' | sort | tr '\n' ' ')` — PASS, 106 testes em
  Python 3.9.6.
- `git diff --check f6fb6a4..4f6c179` — PASS.
- Probe fresco com payload em texto/atributo e path semelhante a URL: zero tags ativas, zero URLs
  remotas/data/javascript, zero IDs derivados da entrada e zero extras renderizados. Verdict
  global `FAIL` e criterion result `BLOCKED` fornecidos artificialmente apareceram literalmente,
  confirmando ausência de recálculo.
- O pacote altera somente renderer, testes e relatório; o HEAD permaneceu em
  `4f6c179b1325c4a5bc0e19d2a594770068932e89`.

## FINDINGS

### Critical

Nenhum.

### Important

Nenhum.

### Minor

Nenhum.

Os links de anexos são criados apenas a partir de `verified_evidence`, recebem prefixo relativo e
percent-encoding. Referências de casos/defeitos só viram links quando o ID possui âncora nesse
conjunto; evidência bloqueada permanece restrita ao diagnóstico sanitizado. Estados vazios e
Unicode foram exercitados sem perda de seções.

## REVIEW

APPROVED
