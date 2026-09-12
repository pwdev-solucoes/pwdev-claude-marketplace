# Task 10 — revisão

## SPEC

PASS

O pacote `review-a67f9a2..8a5185e.diff` implementa o schema v1 e as interfaces
`load_manifest`, `validate_manifest` e `ValidationError` conforme a especificação. A validação
rejeita enums e tipos inválidos, diferencia `bool` de `int`, detecta IDs/referências e campos JSON
duplicados, exige timestamps válidos com fuso, verifica referências e cadeias de reteste, aplica
os limites declarados e recusa caminhos absolutos, traversal e formas não normalizadas. Campos
extras são preservados em cópia profunda, sem criação de projeção pública automática.

## QUALITY

PASS

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_qa_contract` — PASS, 13 testes.
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest $(rg --files tests | sed -n
  's#^tests/\(test_qa_[^/]*\)\.py$#tests.\1#p' | sort | tr '\n' ' ')` — PASS, 76 testes.
- Execução fresca em Python 3.9.6; compilação de `qa_contract.py` e parse do schema com
  `python3 -m json.tool` passaram.
- `git diff --check a67f9a2..8a5185e` — PASS.
- O pacote altera apenas schema, validador, teste e relatório; o HEAD permaneceu em
  `8a5185e1dc4f8b4bfb40df6a0eb78a303db18488`.

## FINDINGS

### Critical

Nenhum.

### Important

Nenhum.

### Minor

Nenhum.

Os limites que dependem do arquivo real — regularidade, symlink/confinamento, digest, conteúdo,
sanitização e megapixels — permanecem corretamente atribuídos ao inspetor de evidências posterior,
sem serem declarados como verificados por este validador de manifesto.

## REVIEW

APPROVED
