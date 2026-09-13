# Re-revisão independente — Task 15, rodada 2

## SPEC

FAIL

A decisão do controller resolve corretamente a interpretação de mutações posteriores ao rename:
elas são externas ao commit, e o snapshot/digest retornado permite detectá-las. Entretanto, a
atestação ainda pode deixar de representar o pacote no próprio instante do commit, e o validador
PDF ainda publica grafos de páginas semanticamente inválidos.

## QUALITY

FAIL

Os 131 testes aplicáveis e a integração ReportLab real passam. A cobertura nova, porém, injeta
trocas antes da última revalidação ou depois do commit; ela não cobre a janela entre a última
revalidação e o syscall de rename. Os testes semânticos de PDF também param nos nós Catalog/Pages
e apenas exigem que os filhos sejam objetos vivos, não que sejam nós Page/Pages válidos.

## FINDINGS

### ADDRESSED — Finding 1 original sob a semântica definida pelo controller

O rename atômico sem overwrite é agora explicitamente o ponto de commit. Em consequência, uma
troca de namespace posterior não invalida retroativamente o sucesso do exportador. O resultado
completo retorna `publication_snapshot` determinístico e `publication_digest` canônico; os probes
de troca pós-commit de run e arquivo demonstram divergência ao reconstruir o snapshot. Esta parte
do finding anterior está encerrada conforme a decisão vinculante.

### Important — A atestação pode divergir do pacote já no instante do commit

Em `plugins/pwdev-qa/scripts/qa_report.py:573-587`, raiz e staging são revalidados e o descritor do
staging é fechado antes de carregar/invocar o rename em `:588-615`. O snapshot retornado já havia
sido calculado em `:716-724`. Há, portanto, uma janela pré-commit na qual o namespace da raiz ou o
conteúdo do staging podem mudar; o syscall ainda sucede via `parent_fd`, mas o resultado atesta os
bytes anteriores.

Dois probes frescos injetaram a mudança imediatamente antes do syscall real:

- ao trocar a raiz nominal, o pacote foi renomeado na raiz antiga pelo descritor retido, enquanto
  o `output_dir` nominal continha um sentinel; ainda assim retornou `complete/PASS`;
- ao substituir `report.html` no staging, o pacote alterado foi efetivamente commitado, mas
  `publication_snapshot`/`publication_digest` descreviam o arquivo anterior.

Nos dois casos o digest reconstruído divergiu. Isso é útil para o consumidor, mas não satisfaz a
exigência do controller de que um resultado completo ateste o staging **commitado**: a divergência
já existia no ponto de linearização, não nasceu de adulteração posterior.

### NOT ADDRESSED — Finding 2 — Filhos inválidos da árvore Pages ainda são publicados

O parser agora rejeita root lixo e valida Catalog/Pages, mas em
`plugins/pwdev-qa/scripts/qa_report.py:307-310` apenas chama `object_body` para cada item de
`/Kids`. Ele não valida que o filho seja `/Type /Page` ou um `/Type /Pages` recursivamente válido,
nem detecta ciclos.

Probes pelo caminho público de `generate_report` publicaram como `complete/PASS` dois PDFs com
xref coerente: um com `/Kids [3 0 R]` cujo objeto 3 era `garbage`, e outro com o nó Pages apontando
para si próprio. O pypdf 6.10.0 estrito rejeitou-os respectivamente com `Invalid Elementary
Object` e `Detected cyclic page references`. Assim, o finding original de PDF não parseável
permanece vigente apesar de a variante de root lixo ter sido corrigida.

## REVIEW

CHANGES_REQUESTED

### Evidência fresca

- HEAD permaneceu em `1f1fc62`; `git diff --check be6ae11..1f1fc62` e `py_compile` passaram.
- Python 3.9.6: `tests.test_qa_report_cli` — 15 testes, PASS.
- Python 3.12.14 empacotado: cinco testes corretivos focados, PASS; discovery `test_qa*.py` —
  131 testes, PASS.
- ReportLab 4.4.9 real: pacote `complete/PASS`, 7 páginas, `/Catalog` e páginas `/Page` válidos no
  pypdf 6.10.0 estrito, texto extraído com pdfplumber 0.11.9 e snapshot/digest reconstruídos
  idênticos aos retornados.
- Probes pré-commit de raiz/staging e PDFs com filho lixo/ciclo reproduziram os falsos sucessos
  descritos; todas as fixtures temporárias foram removidas.
