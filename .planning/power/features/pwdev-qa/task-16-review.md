# Revisão independente — Task 16

## SPEC

FAIL

A fixture e a saída corrente exercitam 100 critérios de 2.000 caracteres, os modelos público e
fonte coincidem, o pacote inseguro é excluído e as inspeções reais HTML/PDF são satisfatórias.
Porém, o teste E2E não comprova a paridade **exata** que constitui o comportamento central da
tarefa: há perdas de conteúdo e de itens que o oracle aceita silenciosamente.

## QUALITY

FAIL

As dependências estão fixadas corretamente, o código compila em Python 3.9 e 142 testes passam em
Python 3.12. O problema é a qualidade do oracle, não a renderização observada nesta execução. Os
asserts parciais podem permanecer verdes diante de truncamento de texto, truncamento da lista de
resultados ou ausência de expected/observed de critério no HTML.

## FINDINGS

### Important — O teste não garante os 100 textos completos nem toda a paridade entre formatos

Em `tests/test_qa_reports_e2e.py:76-92`, a iteração usa `zip(source["criteria"],
public["criterion_results"])` sem antes exigir que `criterion_results` tenha 100 itens; uma lista
truncada reduz silenciosamente o conjunto verificado. Para o PDF, `:80-85` compara somente tokens
completos que casam `c\d{3}w\d{4}á`, e não o texto inteiro de 2.000 caracteres. Como
`qa_demo._criterion_text` corta a string em `plugins/pwdev-qa/scripts/qa_demo.py:47-53`, todos os
100 textos terminam em um token parcial como `c000w0181`, sem o `á`. Um probe fresco removeu os
9 caracteres finais de cada texto e a comparação atual de tokens continuou idêntica em 100/100
critérios.

Além disso, expected/observed do assessment do critério são verificados apenas dentro do loop dos
dois textos extraídos do PDF; não há assert correspondente contra `html_report`. Assim, um HTML
sem esses campos ainda passaria desde que o manifesto público e os casos permanecessem intactos.

A saída atual contém os sufixos e campos quando inspecionada, mas a tarefa exige um teste de
paridade reproduzível, não apenas uma execução manual favorável. Exija cardinalidade exata antes
da iteração e compare cada campo/texto completo contra **cada** formato com uma normalização de
quebras controlada ou sentinelas que cubram inclusive o sufixo final.

## REVIEW

CHANGES_REQUESTED

### Evidência fresca

- HEAD permaneceu em `83b30a2`; `git diff --check dcd096e..83b30a2` passou.
- Python 3.9.6: `py_compile` de `qa_demo.py` e `test_qa_reports_e2e.py`, PASS.
- Python 3.12.14 empacotado com pypdf 6.10.0/pdfplumber 0.11.9: teste focado — 3 testes,
  PASS; discovery `test_qa*.py` — 142 testes, PASS.
- Demo real: `complete`, verdict `FAIL`, pacote allowlisted, PDF A4 de 171 páginas. Páginas 1,
  100 e 171 renderizadas com Poppler e inspecionadas visualmente sem clipping ou sobreposição;
  o sufixo do critério estava presente na saída corrente.
- `playwright-cli` 0.1.14: servidor apenas em loopback, sessão isolada `qa-report`, snapshot e
  screenshot frescos; título e seções corretos, zero scripts, zero recursos remotos. Apenas o 404
  esperado de `favicon.ico`; a sessão foi fechada.
- Colisão do diretório demo e pins exatos passaram; segredo, evidência com credencial e imagem com
  revisão pendente não apareceram no pacote público, e o defeito vigente sem critério produziu
  `FAIL`.
- Servidor, outputs, screenshots, fixtures e caches temporários foram encerrados/removidos.
