# Task 12 — re-revisão

## SPEC

PASS

O pacote `review-f12fadd..f6fb6a4.diff` corrige os três findings da revisão original. Waivers
`NOT_APPLICABLE` legítimos são neutros sem relaxar dispensas inválidas; defeitos resolved só fecham
com a tentativa terminal referenciada em `PASS` e com evidência; combinações contraditórias de
escopo bloqueiam o parecer. A precedência de falha comprovada permanece preservada.

## QUALITY

PASS

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_qa_verdict` — PASS, 15 testes.
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest $(rg --files tests | sed -n
  's#^tests/\(test_qa_[^/]*\)\.py$#tests.\1#p' | sort | tr '\n' ' ')` — PASS, 101 testes em
  Python 3.9.6.
- `git diff --check f12fadd..f6fb6a4` — PASS.
- Probes frescos combinatórios: waiver válido `PASS`; PASS histórico supersedido por terminal FAIL
  resulta `FAIL` e um defeito vigente; `true/out_of_scope`, `false/open` e `false/resolved` resultam
  `BLOCKED`, sem classificação falsa como out-of-scope.
- O HEAD permaneceu em `f6fb6a4194cd3820a1e5c862bae5fd75a20c3792`.

## FINDINGS

### 1. ADDRESSED — `NOT_APPLICABLE` legítimo

O consolidador reconhece como válida somente a tentativa terminal cujos links recíprocos apontam
exclusivamente para critérios explicitamente não aplicáveis e justificados. O cenário combinado
com outro critério aplicável aprovado produz `PASS`; links vazios, mistos, aplicáveis ou não
recíprocos continuam bloqueados.

### 2. ADDRESSED — reteste PASS supersedido

O fechamento de defeito consulta agora as tentativas terminais, não todo o histórico. Nos probes,
um PASS referenciado mas supersedido por `FAIL`, `BLOCKED` ou `NOT_RUN` não encerra o defeito; sua
evidência válida mantém o defeito vigente e o verdict global em `FAIL`, sem apagar as tentativas
históricas.

### 3. ADDRESSED — marcadores contraditórios de escopo

`in_scope` e `status` devem concordar. As três contradições exercitadas produzem diagnóstico e
`BLOCKED`, com contagens zero tanto para current-in-scope quanto out-of-scope. O par coerente
`false/out_of_scope` permanece visível e neutro, enquanto defeito coerente e comprovado in-scope
mantém precedência `FAIL`.

Nenhum finding aberto nesta rodada.

## REVIEW

APPROVED
