# Re-revisão focada — Task 14

## SPEC

FAIL

A incorporação e a legenda de imagem verificada foram implementadas, mas a raiz usada para
reabrir o anexo ainda pode ser um symlink. Isso viola o confinamento sem symlinks exigido para
evidências e permite que o destino nominal aponte para outra árvore.

## QUALITY

FAIL

Os checks de arquivo final são bons: descritores relativos, `O_NOFOLLOW` nos componentes
internos e no arquivo, `fstat`, tamanho, SHA-256, MIME e decodificação completa antes do
flowable. A âncora desses checks, contudo, é aberta seguindo symlink, e os testes novos cobrem
somente symlink na folha.

## FINDINGS

### Important original — NOT ADDRESSED

A parte funcional foi atendida: o probe fresco encontrou exatamente uma imagem 480×240 no
PDF, a legenda `Evidence image: ev-1 — artifacts/capture.png` foi extraída integralmente por
pypdf e pdfplumber, e a imagem `pending` não foi incorporada nem teve o path exposto.

Entretanto, em `plugins/pwdev-qa/scripts/qa_pdf.py:102`, a raiz
`destination.parent` é aberta com `O_DIRECTORY`, mas sem `O_NOFOLLOW`. O mesmo path é usado
novamente por `NamedTemporaryFile` e `os.replace`. Um probe com `linked-root -> actual`
conseguiu ler `linked-root/artifacts/capture.png` e publicou `actual/report.pdf`, retornando
sucesso. Portanto, a entrada ainda não está confinada a uma raiz sem symlinks e há uma janela
de nova resolução do path entre revalidação e publicação. Abra e valide a raiz sem seguir
symlink e mantenha a identidade dessa raiz até a criação/substituição do artefato, ou faça o
caller fornecer uma raiz já validada cuja identidade seja verificada antes e depois.

O finding Minor sobre o fragmento final da fixture 100×2000 permanece deferred por instrução e
não foi reavaliado nesta rodada.

## REVIEW

CHANGES_REQUESTED

### Evidência fresca

- HEAD permaneceu em `f283267295482a717b6bbb3cb70ee14e6ead6b7e`; `git diff --check
  13f5e1a..f283267` passou.
- Python 3.12.14 empacotado com ReportLab 4.4.9, pypdf 6.10.0 e pdfplumber 0.11.9.
- `python3 -m unittest -v tests.test_qa_pdf`: 7 testes, PASS.
- `python3 -m unittest discover -s tests -p 'test_qa_*.py'`: 113 testes, PASS.
- PDF temporário: 7 páginas A4; uma imagem incorporada; legenda presente nas duas extrações;
  path da imagem bloqueada ausente. As sete páginas foram renderizadas com Poppler e
  inspecionadas sem clipping, sobreposição ou quebra da legenda.
- Probe adversarial de raiz symlink: `ROOT_SYMLINK_ACCEPTED True`.
- Artefatos temporários e caches gerados pela revisão foram removidos.
