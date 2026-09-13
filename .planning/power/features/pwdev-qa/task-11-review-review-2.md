# Task 11 — re-revisão, rodada 2

## SPEC

PASS

O pacote `review-634e5b7..b0412ba.diff` corrige os dois findings Important remanescentes. A
validação PNG agora rejeita paleta excessiva ou duplicada e preserva o boundary válido; a inspeção
JSON mantém todos os pares decodificados, inclusive duplicados, e bloqueia a credencial Unicode
antes que uma ocorrência posterior possa sobrescrevê-la. As correções anteriores de TOCTOU e da
semântica provisória de `copy_allowed` permanecem intactas.

## QUALITY

PASS

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_qa_evidence` — PASS, 10 testes.
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest $(rg --files tests | sed -n
  's#^tests/\(test_qa_[^/]*\)\.py$#tests.\1#p' | sort | tr '\n' ' ')` — PASS, 86 testes em
  Python 3.9.6.
- `git diff --check 634e5b7..b0412ba` — PASS.
- Probes frescos adicionais: paleta excessiva `REJECTED`; `PLTE` duplicado `REJECTED`; paleta
  válida no limite `VERIFIED` com revalidação obrigatória; JSON Unicode duplicado `BLOCKED` sem
  path ou permissão de cópia.
- O HEAD permaneceu em `b0412baaa175c1fe131f66bb52319fd0234040c8`.

## FINDINGS

### 1. ADDRESSED — Important imagem completa/paleta PNG

`plugins/pwdev-qa/scripts/qa_evidence.py` permite somente um `PLTE` e, para color type 3, limita as
entradas a `2^bit_depth`. Os probes rejeitaram uma imagem 1-bit com três entradas e outra com duas
paletas, enquanto a imagem 1-bit completa com exatamente duas entradas permaneceu `VERIFIED`.

### 2. ADDRESSED — Important JSON Unicode semântico com duplicatas

O parser usa um `object_pairs_hook` que preserva todas as ocorrências e a inspeção percorre cada
par decodificado. O fixture
`{"api\u005fkey":"synthetic-secret-token","api_key":""}` agora produz `BLOCKED`,
`copy_allowed=false` e projeção sanitizada; a ocorrência posterior não apaga a credencial.

### 3. ADDRESSED — Critical TOCTOU permanece sem regressão

A travessia continua descriptor-relative, com no-follow por componente e leitura ligada ao
descriptor já aberto. O probe de parent swap passou novamente sem ler bytes do pathname
substituído.

### 4. ADDRESSED — `copy_allowed`/revalidação permanece sem regressão

Todo resultado `VERIFIED` continua trazendo `requires_copy_revalidation=true`, e a referência
mantém o contrato de reabrir, revalidar e copiar do mesmo descriptor para destino temporário
exclusivo. `copy_allowed` não é tratado como autorização durável.

Nenhum finding aberto nesta rodada.

## REVIEW

APPROVED
