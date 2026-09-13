# Re-revisão focada — Task 14, rodada 2

## SPEC

FAIL

A raiz symlink agora é recusada e a publicação descriptor-relative não sobrescreve uma raiz
trocada. Porém, `render_pdf(report, destination)` ainda retorna sucesso quando o PDF não foi
publicado no `destination` fornecido: após a troca da raiz, o artefato fica no inode renomeado.
Isso viola o contrato de saída e transforma uma exportação incompleta no path nominal em
sucesso silencioso.

## QUALITY

FAIL

Os mecanismos de `O_NOFOLLOW`, descritores relativos, revalidação e cleanup são robustos, e a
imagem/legenda permanece correta. A checagem de identidade compara apenas `fstat` do mesmo
descritor, o que não detecta que o pathname deixou de apontar para esse inode; o novo teste
codifica como sucesso justamente essa divergência.

## FINDINGS

### Important original — NOT ADDRESSED

As partes de symlink e redirecionamento de escrita foram corrigidas: `_open_destination_root`
recusa raiz symlink, a imagem é reaberta e validada sob o descritor retido, e criação,
substituição e cleanup do temporário usam `dir_fd`. O probe positivo confirmou uma imagem
480×240 e a legenda extraível; a evidência bloqueada continuou ausente.

O caso de troca da raiz permanece incorreto. Em
`plugins/pwdev-qa/scripts/qa_pdf.py:643`, `os.replace` publica pelo descritor antigo sem
confirmar que `destination.parent` ainda nomeia o mesmo `(st_dev, st_ino)`. O probe renomeou a
raiz validada, criou uma nova raiz no path nominal e colocou um sentinel em `report.pdf`. A
função retornou normalmente, preservou o sentinel e gravou o PDF em `preserved-root/report.pdf`;
logo, o `destination` contratado não contém o resultado. `_assert_root_identity` só executa
`fstat` no descritor já aberto e não pode detectar essa troca de nome. A troca deve abortar com
diagnóstico explícito, ou a API deve devolver o destino efetivo e o chamador deve validar que
ele ainda corresponde ao run path antes de declarar sucesso; não basta publicar em um inode
que deixou de ser o destino solicitado.

O finding Minor da fixture 100×2000 permanece deferred por instrução e não foi reavaliado.

## REVIEW

CHANGES_REQUESTED

### Evidência fresca

- HEAD permaneceu em `d208b36f1adb5bf398f5d0ae763eb53fafbba54f`; `git diff --check
  f283267..d208b36` passou.
- Python 3.12.14 empacotado com ReportLab 4.4.9, pypdf 6.10.0 e pdfplumber 0.11.9.
- `python3 -m unittest -v tests.test_qa_pdf`: 9 testes, PASS.
- `python3 -m unittest discover -s tests -p 'test_qa_*.py'`: 115 testes, PASS.
- Probes focados de raiz symlink e troca de raiz: ambos os testes existentes passaram; o
  segundo confirmou o desvio acima ao manter o sentinel no path nominal e publicar no inode
  renomeado.
- PDF temporário: 7 páginas A4, exatamente um cabeçalho `%PDF` e um `%%EOF`, uma imagem
  incorporada, legenda presente em pypdf/pdfplumber e path bloqueado ausente. As sete páginas
  renderizadas por Poppler foram inspecionadas sem clipping, sobreposição ou regressão visual.
- Artefatos temporários e caches gerados pela revisão foram removidos.
