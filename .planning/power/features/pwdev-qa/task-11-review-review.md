# Task 11 — re-revisão

## SPEC

FAIL

O pacote `review-614a70b..634e5b7.diff` corrige o finding Critical de TOCTOU e explicita que
`copy_allowed` vale somente para o snapshot inspecionado, exigindo revalidação atômica na cópia.
Também rejeita os fixtures originais de imagem truncada e chave JSON Unicode simples. Porém,
probes adversariais frescos encontraram variantes ainda aceitas como `VERIFIED` dentro dos dois
findings Important: PNG indexado estruturalmente inválido e credencial Unicode ocultada por chave
JSON duplicada.

## QUALITY

FAIL

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_qa_evidence` — PASS, 9 testes.
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest $(rg --files tests | sed -n
  's#^tests/\(test_qa_[^/]*\)\.py$#tests.\1#p' | sort | tr '\n' ' ')` — PASS, 85 testes em
  Python 3.9.6.
- `git diff --check 614a70b..634e5b7` — PASS.
- Probes frescos: parent swap não redirecionou o descriptor; PNG truncado foi rejeitado; chave
  Unicode simples ficou `BLOCKED`; PNG indexado com paleta inválida ficou `VERIFIED`; JSON com
  chave Unicode duplicada e sobrescrita ficou `VERIFIED`.
- O HEAD permaneceu em `634e5b72bd82970f4e192692532e346491223c5f`.

## FINDINGS

### 1. ADDRESSED — Critical TOCTOU/confinamento de diretórios

`plugins/pwdev-qa/scripts/qa_evidence.py:113-180` agora percorre cada componente a partir de um
descriptor da raiz, usa operações relativas com no-follow, compara device/inode e lê do descriptor
do arquivo. O probe que renomeia o diretório aberto e instala um symlink antes da abertura final
continuou ligado ao diretório original e não leu os bytes do atacante. A correção também falha
fechado quando a plataforma não oferece as primitivas necessárias.

### 2. NOT ADDRESSED — Important validação de imagem completa ainda admite PNG inválido

A correção rejeita o cabeçalho truncado original e valida CRC, `IDAT`, payload e `IEND`. Contudo,
`qa_evidence.py:257-260` aceita qualquer `PLTE` não vazio, múltiplo de três e com até 256 entradas,
sem limitar a quantidade ao bit depth do PNG indexado nem impedir múltiplos `PLTE`. Um probe criou
PNG color type 3/bit depth 1 com três entradas de paleta — o formato permite no máximo duas — com
CRC, payload e `IEND` consistentes. O inspetor retornou `VERIFIED`, `copy_allowed=true`. Portanto,
a afirmação de imagem estruturalmente completa/real permanece falsa. Valide as restrições de
paleta do formato e acrescente fixtures malformados além de truncamento.

### 3. NOT ADDRESSED — Important varredura JSON semântica perde credencial em chave duplicada

`qa_evidence.py:446-453` usa `json.loads` em um `dict`; uma chave repetida substitui silenciosamente
a anterior antes de `_json_contains_credential` percorrer o objeto. O fixture
`{"api\u005fkey":"synthetic-secret-token","api_key":""}` contém a credencial na primeira chave
semanticamente decodificada, mas a segunda ocorrência vazia a sobrescreve. Como a grafia crua da
primeira está escapada, as regex também não a detectam, e o resultado é `VERIFIED`/
`copy_allowed=true`. Rejeite campos JSON duplicados durante o parse ou preserve/inspecione todos
os pares antes da projeção; o diagnóstico deve continuar sem expor fragmento, path ou conteúdo.

### 4. ADDRESSED — semântica de `copy_allowed` e revalidação

Registros verificados incluem `requires_copy_revalidation=true` em
`qa_evidence.py:69-82`. `references/evidence.md:29-47` define `copy_allowed` apenas como elegibilidade
do snapshot, proíbe resolver o pathname como autorização durável e exige que o exportador reabra,
revalide todas as propriedades e copie do mesmo descriptor para destino temporário exclusivo.
Essa obrigação deverá ser exercitada quando o exportador for implementado; não há bypass contratual
nesta correção.

## REVIEW

CHANGES_REQUESTED

Corrigir os dois findings Important remanescentes e repetir os probes adversariais, a suíte focada,
a regressão QA e o `diff --check` com evidência fresca.
