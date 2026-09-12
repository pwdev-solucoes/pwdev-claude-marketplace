# Task 08 — re-revisão

## SPEC

PASS

O pacote `review-e5a2c0c..323a985.diff` corrige os quatro findings da revisão original. Os
cenários positivos agora tornam verificáveis a rastreabilidade de regressão, a precedência do
verdict global de defeitos, a fronteira completa da autorização de produção e a ligação entre
causa comprovada e prevenção determinística. Os cenários negativos bloqueiam cada ausência
relevante sem inventar execução.

## QUALITY

PASS

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_qa_specialists
  tests.test_qa_core tests.test_qa_tooling tests.test_qa_runtime_contracts` — PASS, 56 testes.
- `git diff --check e5a2c0c..323a985` — PASS.
- O pacote contém o relatório, as três skills corrigidas e o teste especializado; o HEAD
  permaneceu em `323a98505da3d899cac710a7ee0ad8bfb8e77182`.

## FINDINGS

### 1. ADDRESSED — regressão `READY` agora contém rastreabilidade verificável

O cenário positivo identifica mudança, impacto, risco, critério, defeito, casos estáveis
selecionados e excluídos, além das relações entre esses nós. Os testes cobrem separadamente a
ausência de cada nó e das relações, sempre com resultado `BLOCKED`.

### 2. ADDRESSED — resolução isolada não produz mais `PASS` global

O cenário de resolução termina em `defect_current=false` e `BLOCKED` enquanto o catálogo de
critérios e o inventário de outros defeitos não forem avaliados. `PASS` exige catálogo completo
com todos os aplicáveis em `PASS` e ausência explícita de outros defeitos vigentes; outro defeito
vigente, inclusive sem critério associado, produz `FAIL`.

### 3. ADDRESSED — produção `READY` expõe a fronteira exata de autorização

O contrato positivo explicita target, fontes de telemetria, identidade/papel, limite somente
leitura, campos, janela, owner, regras de dados, condições de parada e retenção. A omissão de cada
componente é exercitada individualmente e mantém a observação em `NOT_RUN` e o resultado em
`BLOCKED`.

### 4. ADDRESSED — prevenção identifica causa comprovada e check determinístico

O cenário positivo nomeia a causa, vincula evidência revisada e target-bound, critério/risco,
stable case ID, oráculo, ambiente e pré-requisitos. Causa hipotética e prevenção genérica têm
cenários próprios que resultam em `BLOCKED`.

Nenhum finding aberto nesta rodada.

## REVIEW

APPROVED
