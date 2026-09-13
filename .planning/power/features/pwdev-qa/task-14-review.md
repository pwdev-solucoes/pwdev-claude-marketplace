# Revisão independente — Task 14

## SPEC

FAIL

O PDF atende A4, frame de conteúdo com margens exatas de 18 mm, paginação `Page X of Y`,
índice paginado, rótulos textuais de status, escaping de markup, acentos, conteúdo extenso
quebrável e falha explícita sem ReportLab. Contudo, não implementa a parte de imagens com
legenda exigida pela fixture visual consolidada e pelo comportamento de “legendas”: uma
evidência `image/png` verificada é reduzida ao índice textual de metadados.

## QUALITY

FAIL

O renderizador é legível, determinístico e usa escrita temporária seguida de substituição
atômica. Os testes frescos passaram, mas a cobertura aceita um relatório sem qualquer imagem
incorporada e a asserção de integralidade dos 2.000 caracteres ignora deliberadamente o último
token parcial de cada critério.

## FINDINGS

### Important — Evidências de imagem verificadas não são exibidas nem recebem legenda

Em `plugins/pwdev-qa/scripts/qa_pdf.py:395`, a seção de evidências percorre somente campos
textuais (`ID`, caminho, MIME, tamanho, hashes e estados); não existe `Image`, leitura segura do
anexo já admitido ou flowable de legenda. Um probe fresco com uma evidência `image/png`
`VERIFIED` e outra `pending` gerou PDF com o ID/caminho da imagem verificada, porém
`pdfimages -list` não encontrou imagens e `pypdf` contou zero imagens nas páginas. Assim, a
fixture exigida com imagens e legendas não pode ser satisfeita, embora a evidência bloqueada
tenha sido corretamente omitida das referências aprovadas e substituída por diagnóstico
sanitizado. É necessário definir/usar a entrada segura do anexo verificado e renderizar as
capturas pertinentes com legenda, sem abrir paths não revalidados.

### Minor — O teste de 100×2000 não prova os 2.000 caracteres integrais

Em `tests/test_qa_pdf.py:105-131`, `long_criterion()` fornece `tokens[:-1]` como expectativa e o
teste compara apenas tokens completos pela regex. O fragmento final que completa exatamente
2.000 caracteres não entra na asserção; uma regressão que cortasse esse fragmento ainda
passaria. Compare o texto completo normalizado de cada critério (incluindo o fragmento final),
e inclua na mesma fixture uma imagem verificada com sua legenda.

## REVIEW

CHANGES_REQUESTED

### Evidência fresca

- HEAD permaneceu em `13f5e1a59c70687d24e098b023b589008cf47121`; `git diff --check
  4f6c179..13f5e1a` passou.
- Python empacotado 3.12.14: ReportLab 4.4.9, pypdf 6.10.0 e pdfplumber 0.11.9.
- `python3 -m unittest -v tests.test_qa_pdf`: 5 testes, PASS.
- `python3 -m unittest discover -s tests -p 'test_qa_*.py'`: 111 testes, PASS.
- Fixture fresca 100×2000: 172 páginas A4; 18.100 tokens completos encontrados por pypdf e
  pdfplumber; todas as páginas renderizadas com Poppler e inspecionadas em nove folhas de
  contato, sem corte ou sobreposição aparente. Conteúdo dentro de x=51,02362..544,25199 pt,
  compatível com 18 mm em ambos os lados.
- Probe malicioso: tags de Paragraph, links e `file:///etc/passwd` permaneceram texto literal;
  nenhuma ação URI externa foi criada. Probe real no Python 3.9 sem ReportLab retornou o erro
  explícito esperado.
- Fixture temporária e caches gerados pela revisão foram removidos após a inspeção.
