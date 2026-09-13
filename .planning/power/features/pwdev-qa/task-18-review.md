# Re-revisão independente — Task 18 (round 2)

## SPEC

PASS

Os dois Procedures agora identificam as superfícies reais, consultam apenas especialistas
instalados e aplicáveis antes de refinar/executar, registram especialista indisponível como
limitação e impedem que sua orientação amplie autorização. Os outputs preservam a sequência
exata e única de labels. `qa-explore` declara localmente que nunca retorna `PASS`, usando somente
`FAIL` para falha vigente ou `BLOCKED` para o restante e remetendo a verificação completa a um
workflow determinístico separado.

## QUALITY

PASS

O oracle foi confinado às seções relevantes e agora compara toda a sequência de labels extraída
do bloco `text`. Os três probes que sobreviveram na rodada anterior foram eliminados nesta
execução. A verificação focada e a regressão QA completa passaram sem criar artefatos de produto.

## FINDINGS

### ADDRESSED — Major: consumo dos especialistas aplicáveis

- `plugins/pwdev-qa/skills/qa-test/SKILL.md:31-37` seleciona por superfície, consulta somente
  `qa-specialist-*` instalado/aplicável, registra indisponibilidade e preserva autorização.
- `plugins/pwdev-qa/skills/qa-explore/SKILL.md:33-39` aplica o mesmo contrato antes de refinar
  heurísticas ou executar ações.
- `tests/test_qa_workflows.py:286-304` verifica essas quatro propriedades dentro de Procedure para
  ambos os workflows. A mutação que removeu a consulta foi eliminada.

### ADDRESSED — Major: oracle de output exato e regra anti-`PASS`

- `tests/test_qa_workflows.py:20-24` extrai os labels somente do registro `text`; as comparações
  completas em `:222-237` e `:256-274` exigem ordem, cardinalidade e unicidade exatas.
- `tests/test_qa_workflows.py:275-282` confina a regra anti-`PASS` ao Procedure e também recusa a
  forma contraditória positiva.
- `plugins/pwdev-qa/skills/qa-explore/SKILL.md:53-55` agora define inequivocamente `FAIL` ou
  `BLOCKED`; seu output em `:77` restringe o parecer aos mesmos estados.
- As mutações de reordenação e contradição da regra foram eliminadas.

Nenhum finding Blocker, Major ou Minor permanece aberto nesta rodada.

## REVIEW

APPROVED

Evidência fresca:

- HEAD observado: `bc9b23d`; não foi movido.
- `git diff --check ac9f1e0..bc9b23d`: PASS.
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_qa_workflows`: 14 PASS.
- Python 3.12 empacotado, discovery `test_qa_*.py`: 156 PASS.
- Mutações `drop-specialist-consultation`, `reorder-exact-output` e
  `contradict-explore-pass-rule`: todas eliminadas pelos testes correspondentes.
- Nenhum arquivo de produto ou teste foi alterado; somente esta revisão foi sobrescrita.
