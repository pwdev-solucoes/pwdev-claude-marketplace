# Re-revisão independente — Task 15, rodada 3

## SPEC

FAIL

A janela pré-syscall encontrada na rodada anterior foi tratada nos cenários exatos, e os casos de
filho lixo/ciclo agora são recusados. Permanecem, porém, dois defeitos atuais: adulteração
imediatamente posterior ao syscall é reclassificada ou incorporada à atestação apesar de já ser
pós-commit, e um objeto Page lexicalmente malformado ainda é publicado como PDF completo.

## QUALITY

FAIL

Os 135 testes aplicáveis e a integração ReportLab real passam, mas a suíte posiciona os probes
pós-commit somente depois de `_verify_nominal_commit`; não cobre o intervalo imediatamente após o
syscall que o controller definiu como já externo. O parser recursivo confere tipos por regex, sem
validar a sintaxe dos dicionários Page.

## FINDINGS

### ADDRESSED — Finding pré-commit de raiz/staging

O descritor original de staging permanece aberto no chamador durante o rename e o snapshot
retornado é reconstruído por esse descritor após o syscall. Um probe fresco que substituiu
`report.html` na janela pré-syscall obteve snapshot/digest iguais ao pacote efetivamente
commitado. Um probe que trocou a raiz na mesma janela falhou explicitamente na vinculação nominal
e preservou o sentinel. Assim, o falso sucesso específico da rodada anterior foi encerrado.

### Important — A decisão pós-commit do controller não é respeitada na janela após o syscall

O commit ocorre em `plugins/pwdev-qa/scripts/qa_report.py:605-620`. Depois dele, o código ainda
calcula a atestação pelo descritor em `:810-821` e condiciona o sucesso à verificação nominal em
`:822-833`. Logo, uma mutação externa nesse intervalo influencia o que é declarado como conteúdo
commitado ou transforma um commit bem-sucedido em erro do exportador.

Probes frescos fizeram a troca imediatamente **após** o syscall real, mas antes do retorno de
`_rename_no_replace_syscall`:

- uma troca da raiz nominal causou `PublicationError: reports root identity changed at commit`,
  embora, pela decisão vinculante, o commit já tivesse ocorrido e a mudança fosse externa;
- uma troca de `report.html` retornou `complete/PASS`, mas snapshot/digest passaram a atestar os
  bytes externos posteriores ao commit, em vez dos bytes presentes no ponto de linearização.

Os testes novos só injetam adulteração depois de `_verify_nominal_commit`, ocultando essa janela.
Portanto, o finding pós-commit que a rodada anterior considerou encerrado regrediu na semântica
efetiva.

### NOT ADDRESSED — Finding recursivo de PDF Pages

O walk em `plugins/pwdev-qa/scripts/qa_report.py:292-336` rejeita corretamente filho `garbage`,
ciclos, duplicatas e contagens recursivas incorretas. Porém, `dictionary` apenas testa os
delimitadores `<< >>`, e um nó `/Type /Page` retorna imediatamente em `:303-307`, sem analisar o
restante do objeto.

Um fixture com xref, Catalog e Pages coerentes, mas cujo filho era
`<< /Type /Page /Bad (unterminated >>`, foi publicado por `generate_report` como
`complete/PASS`. O pypdf 6.10.0 estrito recusou a enumeração das páginas com
`PdfStreamError('Stream has ended unexpectedly')`. Outro probe mostrou que `/Type /Pages` dentro
de uma string também satisfaz o regex, mesmo quando o tipo real é `/Garbage`. A recursão corrige
os exemplos anteriores, mas ainda não garante um PDF semanticamente parseável.

## REVIEW

CHANGES_REQUESTED

### Evidência fresca

- HEAD permaneceu em `d0ce671`; `git diff --check 1f1fc62..d0ce671` e `py_compile` passaram.
- Python 3.9.6: `tests.test_qa_report_cli` — 19 testes, PASS.
- Python 3.12.14 empacotado: seis testes corretivos focados, PASS; discovery `test_qa*.py` —
  135 testes, PASS.
- ReportLab 4.4.9 real: pacote `complete/PASS`, 7 páginas, Catalog/Page válidos no pypdf 6.10.0
  estrito, texto extraído pelo pdfplumber 0.11.9 e snapshot/digest reconstruídos idênticos.
- Probes temporários das janelas pré/pós-syscall e de árvores Page/Pages malformadas produziram os
  resultados descritos; fixtures e caches criados pela revisão foram removidos.
