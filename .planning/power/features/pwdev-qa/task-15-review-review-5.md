# Re-revisão independente — Task 15, rodada 5

## SPEC

PASS

O finding lexical remanescente foi corrigido no escopo solicitado. Keywords nuas inválidas, hex
inválido e valores inválidos aninhados são recusados; valores PDF elementares válidos continuam
aceitos. A matriz anterior de Page/Pages malformado permanece verde e a saída ReportLab real
continua publicável e verificável.

## QUALITY

PASS

A correção é pequena e concentrada no tokenizer, preserva Python 3.9 e não introduz dependência de
verificação no exportador. Os testes cobrem os dois contraexemplos originais, matriz positiva e
negativa de tokens, aninhamento, casos lexicais/recursivos anteriores e as quatro janelas de
commit. Não encontrei defeito vigente no escopo revisado.

## FINDINGS

### ADDRESSED — Dicionário Page com tokens inválidos

Em `plugins/pwdev-qa/scripts/qa_report.py:105-112`, strings hexadecimais agora aceitam apenas
dígitos hex e whitespace PDF. Em `:137-151`, bare values são classificados explicitamente como
inteiro, real, boolean, null ou marcadores controlados; qualquer outro keyword é recusado. O parser
recursivo já percorre valores de dicionários e arrays, portanto a regra também vale em estruturas
aninhadas.

Probes frescos confirmaram:

- `/Bad garbage`, `/Bad maybe`, `R` isolado, `<GG>` e `<0G>` resultam em exportação `incomplete` e
  nunca ocupam o diretório completo;
- keyword e hex inválidos dentro de arrays/dicionários aninhados também resultam em `incomplete`;
- `true`, `false`, `null`, reais válidos, hex vazio, hex com whitespace e quantidade ímpar de
  dígitos continuam aceitos conforme o contrato PDF.

### ADDRESSED — Casos Page/Pages e semântica de commit sem regressão

Os casos de tipos falsos em strings, comentários e streams, string não terminada, dicionário
desbalanceado, filho lixo, ciclos, duplicatas e contagens recursivas incorretas continuam
recusados. Os probes exatos confirmaram ainda que o snapshot reflete mudanças pré-syscall, a troca
pré-syscall da raiz falha preservando sentinel, e mudanças de PDF/raiz pós-syscall permanecem
externas e detectáveis sem alterar a atestação fixada.

Nenhum finding aberto permaneceu nesta rodada.

## REVIEW

APPROVED

### Evidência fresca

- HEAD permaneceu em `dcd096e`; `git diff --check 6e4914f..dcd096e` e `py_compile` passaram.
- Python 3.9.6: `tests.test_qa_report_cli` — 23 testes, PASS.
- Python 3.12.14 empacotado: nove testes focados de parser/commit, PASS; discovery
  `test_qa*.py` — 139 testes, PASS.
- Probes independentes de valores aninhados: keyword inválido, hex inválido e combinação válida —
  todos produziram o resultado esperado.
- ReportLab 4.4.9 real: pacote `complete/PASS`, 7 páginas, Catalog/Page válidos no pypdf 6.10.0
  estrito, texto extraído pelo pdfplumber 0.11.9 e snapshot/digest reconstruídos idênticos.
- Fixtures e caches temporários da revisão foram removidos.
