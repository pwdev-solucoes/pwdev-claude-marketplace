# Re-revisão independente — Task 15

## SPEC

FAIL

Os dois findings Important originais permanecem vigentes. A correção detecta trocas feitas
imediatamente após o rename e rejeita o PDF sem xref, mas ainda pode retornar `complete/PASS`
depois de uma troca da raiz, do diretório do run ou do arquivo final, e ainda aceita um PDF cujo
objeto `/Root` não é um objeto PDF válido.

## QUALITY

FAIL

Os 128 testes aplicáveis passam e a integração ReportLab real funciona, porém os novos testes de
troca exercitam somente o hook de rename, antes das verificações finais. O PDF sintético positivo
prova coerência de offsets, não validade semântica do documento. Assim, a suíte não protege as
duas fronteiras que originaram os findings.

## FINDINGS

### NOT ADDRESSED — Important — Trocas após o último snapshot ainda produzem falso sucesso

Em `plugins/pwdev-qa/scripts/qa_report.py:561-596`, repetir duas vezes a reabertura e o snapshot
não fecha a janela entre o retorno do último `_snapshot_tree` e o retorno de sucesso em
`:754-760`. Os testes novos injetam a troca dentro de `_atomic_rename_exclusive`, portanto sempre
antes das duas verificações.

Probes frescos fizeram a troca logo após o segundo snapshot nominal, ainda dentro da chamada de
`generate_report`. Nos três casos — substituir a raiz `reports`, substituir o diretório
`probe-run` e substituir somente `report.pdf` — a função retornou `export_status=complete` e
`verdict=PASS`; o `output_dir` nominal continha respectivamente `ROOT-SWAP`, `RUN-SWAP` e
`FILE-SWAP`. Isso mantém exatamente o falso sucesso do finding original. É necessário que a
fronteira de publicação/sucesso vincule atomicamente o pacote verificado ao destino nominal, em
vez de tentar encerrar TOCTOU com um número finito de releituras.

### NOT ADDRESSED — Important — Xref coerente ainda permite PDF semanticamente inválido

Em `plugins/pwdev-qa/scripts/qa_report.py:193-263`, o novo parser confirma header, xref, offsets,
trailer e que `/Root` aponta para um objeto vivo, mas não analisa o objeto apontado. Um fixture com
xref e offsets corretos, porém com `1 0 obj` contendo apenas `garbage`, foi publicado por
`generate_report` como `complete/PASS`. O pypdf 6.10.0 em modo estrito abriu o container
preguiçosamente, mas ao dereferenciar `root_object` rejeitou-o com `PdfReadError: Invalid
Elementary Object`. Portanto, rejeitar apenas o PDF marcador foi uma melhora parcial; CA-021
continua aceitando saída corrompida do renderizador. A validação deve ao menos comprovar uma raiz
`/Catalog` e uma árvore `/Pages` dereferenciáveis, com casos negativos semanticamente malformados.

## REVIEW

CHANGES_REQUESTED

### Evidência fresca

- HEAD permaneceu em `be6ae11`; `git diff --check fb4905b..be6ae11` passou.
- Python 3.9.6: `tests.test_qa_report_cli` — 12 testes, PASS; `py_compile`, PASS.
- Python 3.12.14 empacotado: quatro regressões focadas, PASS; CLI + PDF, 22 testes, PASS;
  discovery `test_qa*.py`, 128 testes, PASS.
- ReportLab 4.4.9 real: pacote `complete/PASS` com 7 páginas A4, `/Catalog` válido em pypdf
  6.10.0 estrito, texto extraído por pdfplumber 0.11.9, anexo idêntico, allowlist correta,
  extensão privada ausente e comando inerte.
- Probes temporários de raiz/run/arquivo após o último snapshot e de PDF semanticamente inválido
  reproduziram os falsos sucessos descritos acima; fixtures foram autocontidas e removidas.
