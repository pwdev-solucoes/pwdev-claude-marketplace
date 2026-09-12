# Task 11 — revisão

## SPEC

FAIL

O pacote cobre os fluxos básicos de regularidade, tamanhos, hash, target, MIME declarado,
megapixels, credenciais e sanitização, e mantém metadados rejeitados fora da projeção. Porém,
probes adversariais comprovaram três falhas vigentes: uma troca TOCTOU de diretório por symlink
ainda é aceita como `VERIFIED`, bytes que não formam um PNG completo são copiáveis, e credencial
JSON com escape Unicode passa pela detecção e também fica copiável.

## QUALITY

FAIL

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_qa_evidence` — PASS, 8 testes.
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest $(rg --files tests | sed -n
  's#^tests/\(test_qa_[^/]*\)\.py$#tests.\1#p' | sort | tr '\n' ' ')` — PASS, 84 testes em
  Python 3.9.6.
- `git diff --check 8a5185e..614a70b` — PASS.
- Probes frescos adicionais: `PARENT_SWAP VERIFIED`, `TRUNCATED_PNG VERIFIED` e
  `ESCAPED_JSON_SECRET VERIFIED`.
- O pacote altera somente implementação, referência, testes e relatório; o HEAD permaneceu em
  `614a70bf2d651a1acc9362883a69e2b3f098b290`.

## FINDINGS

### Critical — inspeção por pathname permite TOCTOU através de symlink em diretório pai

`plugins/pwdev-qa/scripts/qa_evidence.py:102-120` faz `lstat` dos componentes e devolve um
pathname. Depois, `qa_evidence.py:123-150` chama `os.open(path, O_NOFOLLOW)`, que protege somente o
componente final; os diretórios pais são novamente resolvidos pelo kernel. Um probe determinístico
renomeou o diretório já inspecionado para fora da raiz e colocou no lugar um symlink para esse
mesmo diretório antes do `open`. Como o arquivo aberto conserva device/inode/tamanho, todas as
rechecagens passam e `inspect_evidence` retorna `VERIFIED`/`copy_allowed=true`. Assim, a garantia
“sem symlinks e confinado” não vale no instante de uso, e a projeção ainda fornece um pathname que
pode ser trocado novamente antes da cópia pelo exportador. Faça a travessia a partir de descritor
da raiz com operações relativas e `O_NOFOLLOW` em cada componente (ou equivalente seguro), e não
trate `copy_allowed` como autorização durável sem revalidação atômica no momento da cópia. Adicione
um teste que efetue a troca entre inspeção e abertura.

### Important — cabeçalhos parciais são aceitos como MIME de imagem real

`qa_evidence.py:156-162` considera PNG válido com apenas 24 bytes: assinatura, rótulo `IHDR` e
largura/altura. Não valida tamanho e conteúdo integral do `IHDR`, CRC, chunks nem término `IEND`;
o parser JPEG em `qa_evidence.py:165-209` também retorna assim que encontra dimensões, sem provar
um arquivo completo. Um fixture de 24 bytes, truncado imediatamente após altura, com sanitização
`reviewed`, retornou `VERIFIED` e `copy_allowed=true`. Os próprios testes usam esse cabeçalho
truncado como imagem (`tests/test_qa_evidence.py:194-205` e `228-236`), portanto não exercitam MIME
real. Valide uma estrutura de imagem completa e rejeite arquivos truncados/malformados antes de
calcular pixels ou permitir cópia.

### Important — credencial conhecida em JSON escapa da varredura por codificação Unicode

`qa_evidence.py:229-236` analisa o JSON apenas para confirmar sintaxe, mas descarta o objeto
decodificado; `qa_evidence.py:253-254` aplica regex somente ao texto cru. Consequentemente,
`{"api\u005fkey":"synthetic-secret-token"}` é semanticamente `api_key`, mas não casa com o padrão
conhecido e retorna `VERIFIED`/`copy_allowed=true`. O teste atual em
`tests/test_qa_evidence.py:207-226` cobre apenas a grafia literal. Para JSON, percorra chaves e
valores string após o parse e aplique a política ao conteúdo semântico, mantendo diagnóstico sem
fragmento, path ou conteúdo rejeitado; inclua variantes escapadas nos fixtures sintéticos.

### Minor

Nenhum.

## REVIEW

CHANGES_REQUESTED

Corrigir os três findings e repetir os probes adversariais, a suíte focada, a regressão QA e o
`diff --check` com evidência fresca.
