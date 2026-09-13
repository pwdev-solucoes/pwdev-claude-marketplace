# Re-revisão independente — Task 15, rodada 4

## SPEC

FAIL

As semânticas pré e pós-commit foram corrigidas e os casos solicitados de texto enganoso,
comentário, stream, string não terminada e ciclos são recusados. Ainda assim, o parser aceita
outros valores lexicalmente inválidos dentro de um dicionário Page e publica PDFs que o pypdf
estrito não consegue enumerar.

## QUALITY

FAIL

Os 136 testes aplicáveis e a integração ReportLab real passam. A implementação separa agora
corretamente as janelas do commit, mas o tokenizer converte qualquer token não inteiro em
`keyword` e qualquer conteúdo entre `< >` em string hexadecimal sem validar sua gramática. Essa
lacuna não está coberta pela nova matriz adversarial.

## FINDINGS

### ADDRESSED — Semântica exata de commit e atestação

O snapshot/digest é fixado em `plugins/pwdev-qa/scripts/qa_report.py:776-784`, imediatamente antes
do rename atômico em `:786-828`, e é retornado sem releitura ou decisão nominal posterior. Probes
frescos confirmaram:

- alteração pré-syscall do staging é refletida integralmente no snapshot/digest retornado;
- troca pré-syscall da raiz falha e preserva o sentinel;
- alteração de PDF imediatamente após o syscall não muda a atestação, e a recomputação diverge;
- troca da raiz imediatamente após o syscall permanece externa, retorna `complete` com a
  atestação fixada e também é detectada pela recomputação.

Isso resolve o finding pós-commit da rodada 3 e preserva a correção pré-commit anterior sob a
decisão do controller.

### NOT ADDRESSED — Important — Dicionário Page ainda aceita tokens inválidos

Em `plugins/pwdev-qa/scripts/qa_report.py:130-139`, todo token não inteiro vira um `keyword` sem
restrição; em `:84-90`, qualquer sequência delimitada por `< >` vira string sem validar dígitos
hexadecimais. `_parse_pdf_value` aceita esses valores para chaves não usadas, e o nó `/Type /Page`
é então considerado válido em `:445-460`.

Dois probes frescos pelo caminho público de `generate_report` foram publicados como
`complete/PASS`:

- `<< /Type /Page /Bad garbage >>` — pypdf 6.10.0 estrito recusou a enumeração com
  `PdfReadError: Invalid Elementary Object`;
- `<< /Type /Page /Bad <GG> >>` — pypdf 6.10.0 estrito recusou com erro de conversão hexadecimal.

Os casos adicionados de tipo falso em string/comentário/stream, string não terminada, dicionário
desbalanceado, filho lixo e ciclos passam, mas não bastam para garantir que o dicionário Page seja
um objeto PDF parseável. O finding de PDF malformado permanece vigente.

## REVIEW

CHANGES_REQUESTED

### Evidência fresca

- HEAD permaneceu em `6e4914f`; `git diff --check d0ce671..6e4914f` e `py_compile` passaram.
- Python 3.9.6: `tests.test_qa_report_cli` — 20 testes, PASS.
- Python 3.12.14 empacotado: seis probes focados de commit/PDF, PASS; discovery `test_qa*.py` —
  136 testes, PASS.
- ReportLab 4.4.9 real: pacote `complete/PASS`, 7 páginas, Catalog/Page válidos no pypdf 6.10.0
  estrito, texto extraído pelo pdfplumber 0.11.9 e snapshot/digest reconstruídos idênticos.
- Probes adicionais de keyword e hex inválidos reproduziram os falsos sucessos descritos; fixtures
  e caches temporários foram removidos.
