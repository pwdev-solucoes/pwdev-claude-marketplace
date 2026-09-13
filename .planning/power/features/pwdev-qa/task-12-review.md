# Task 12 — revisão

## SPEC

FAIL

O pacote implementa a allowlist pública, a precedência básica de falha, zero critérios/casos,
transcrição incompleta, evidência bloqueada, links recíprocos, ciclos/ramificações e defeitos sem
critério. Entretanto, três combinações válidas pelo schema produzem parecer incorreto: waiver
`NOT_APPLICABLE` legítimo bloqueia o relatório, um PASS antigo supersedido encerra defeito apesar
do reteste terminal falho, e marcadores contraditórios de escopo excluem defeito vigente sem
diagnóstico.

## QUALITY

FAIL

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_qa_verdict` — PASS, 11 testes.
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest $(rg --files tests | sed -n
  's#^tests/\(test_qa_[^/]*\)\.py$#tests.\1#p' | sort | tr '\n' ' ')` — PASS, 97 testes em
  Python 3.9.6.
- `git diff --check 80286c2..f12fadd` — PASS.
- Probes frescos adicionais: waiver válido `BLOCKED`; reteste PASS supersedido resultou
  `BLOCKED` com zero defeitos vigentes em vez de `FAIL`; `in_scope=true/status=out_of_scope`
  resultou `PASS`.
- O pacote altera somente consolidador, testes e relatório; o HEAD permaneceu em
  `f12fadd38c9184427828e616885dc366b21dd900`.

## FINDINGS

### Important — `NOT_APPLICABLE` legítimo é tratado como pendência global

`plugins/pwdev-qa/scripts/qa_verdict.py:243-257` marca todo terminal diferente de `PASS` como
pending antes de considerar a aplicabilidade dos critérios. Assim, um caso opcional
`NOT_APPLICABLE`, ligado reciprocamente apenas a um critério `applicable=false` com motivo, bloqueia
um relatório cujo outro critério aplicável e obrigatório está em `PASS`; o criterion result é
corretamente `NOT_APPLICABLE`, mas o verdict fica `BLOCKED`. O teste em
`tests/test_qa_verdict.py:174-187` cobre somente a dispensa inválida aplicada a critério aplicável.
Distinga a dispensa válida da inválida: preserve `NOT_APPLICABLE` no histórico, bloqueie ausência
de justificativa ou associação incompatível, mas não transforme uma exclusão válida em pendência.

### Important — defeito resolved pode usar reteste PASS já supersedido

`qa_verdict.py:345-360` procura `retest_attempt_id` em todas as tentativas e encerra o defeito se
essa tentativa antiga for `PASS` com evidência; não exige que ela seja o terminal declarado do
mesmo `case_id`. Um probe adicionou `attempt-2` terminal `FAIL` sem evidência, supersedendo o
`attempt-1=PASS` ainda referenciado pelo defeito. O consolidador encerrou o defeito, contou zero
defeitos vigentes e retornou `BLOCKED` apenas pelo FAIL sem prova. Pela política, não se pode voltar
ao PASS antigo: o defeito permanece vigente e sua evidência própria verificada deve fazer a falha
prevalecer, produzindo `FAIL`. Exija reteste terminal, semanticamente ligado ao defeito, e cubra
PASS referenciado seguido de `FAIL`, `BLOCKED` e `NOT_RUN`.

### Important — marcadores contraditórios permitem excluir defeito in-scope

`qa_verdict.py:349-352` considera fora do escopo quando `not in_scope OR status == out_of_scope`.
Como `qa_contract.py` aceita as duas propriedades independentemente, um defeito
`in_scope=true/status=out_of_scope` é normalizado, contado como out-of-scope e permite verdict
`PASS`, sem diagnóstico da contradição. O teste atual (`tests/test_qa_verdict.py:251-263`) cobre
apenas o par consistente `false/out_of_scope`. Exija uma combinação consistente; ambiguidade deve
ser `BLOCKED`, enquanto um defeito comprovadamente in-scope continua sujeito à precedência
`FAIL`.

### Critical

Nenhum.

### Minor

Nenhum.

## REVIEW

CHANGES_REQUESTED

Corrigir os três findings, acrescentar os cenários combinatórios e repetir suíte focada, regressão
QA e `diff --check` com evidência fresca.
