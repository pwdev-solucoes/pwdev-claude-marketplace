# Re-revisão independente — Task 16

## SPEC

PASS

O finding Important original foi corrigido. O teste agora exige cardinalidade exata de 100
critérios na fonte, 100 critérios no modelo público e 100 resultados, e compara as sequências
de IDs uma a uma antes da verificação de conteúdo. Cada linha HTML é isolada por critério e
contém o texto integral de 2.000 caracteres, ID, expected, observed e result. Cada bloco PDF é
isolado da mesma forma e comparado nas duas extrações independentes; a sequência esperada cobre
todo o texto da fixture, inclusive o fragmento final de 9 caracteres sem `á`.

## QUALITY

PASS

O oracle deixou de aceitar truncamento silencioso por `zip`, valida a correspondência 1:1 dos
IDs e confina os asserts aos blocos do respectivo critério. Um probe adversarial fresco alterou
somente a entrada do renderizador PDF, removendo os 9 caracteres finais de cada texto; o teste
falhou no primeiro critério pela ausência de `c000w0181`. Com o renderizador real, o teste focado
e a regressão completa passaram.

## FINDINGS

### ADDRESSED — Important: paridade exata dos 100 critérios e dos campos entre formatos

- `tests/test_qa_reports_e2e.py:82-90` exige as três cardinalidades e sequências de IDs exatas.
- `tests/test_qa_reports_e2e.py:111-126` verifica, no bloco HTML individual, texto completo,
  ID, expected, observed e result.
- `tests/test_qa_reports_e2e.py:128-144` demonstra que as sentinelas recompõem integralmente o
  texto fonte, inclui explicitamente o sufixo parcial final e compara a sequência completa nos
  blocos extraídos por pypdf e pdfplumber, além dos quatro campos.
- O probe de mutação confirmou que remover exatamente o sufixo final não sobrevive ao oracle.

Nenhum finding aberto nesta re-revisão focada.

## REVIEW

APPROVED

### Evidência fresca

- `git diff --check 83b30a2..b8b5ab6`: PASS.
- Python do sistema: `py_compile tests/test_qa_reports_e2e.py`: PASS.
- Python 3.12 empacotado: teste focado, 3 testes PASS.
- Python 3.12 empacotado: discovery `test_qa*.py`, 142 testes PASS.
- Mutação isolada do PDF removendo os 9 caracteres finais: FAIL esperado, acusando
  `c000w0181` ausente; mutação eliminada pelo teste.
- HEAD não foi movido e nenhum arquivo de produto ou teste foi alterado.
