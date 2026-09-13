# Re-revisão independente — Task 19 (round 2)

## SPEC

PASS

Os contratos permanecem conformes. A cadeia de regressão inclui explicitamente change, impact,
risk, criterion/`none`, prior defect/`none` e stable case; `qa-bug` preserva um único caso lógico,
attempts únicos e crescentes, mesmo alvo e cadeia linear sem ciclo/ramificação. Severidade e
prioridade continuam independentes. O guard local de `PASS` agora exige também ausência de
trabalho pendente ou limitações, além de reteste terminal válido, todos os critérios aplicáveis
aprovados e nenhum outro defeito vigente no escopo.

## QUALITY

PASS

O oracle agora codifica as invariantes completas dentro de Procedure. As quatro mutações
requeridas foram eliminadas individualmente. Os 20 testes focados e os 162 testes QA passaram em
execução fresca.

## FINDINGS

### ADDRESSED — Major: cadeia completa de impacto

`tests/test_qa_workflows.py:360-363` exige a ordem completa
change→impact→risk→criterion→prior-defect→case e o `none` justificado. `:365-374` inclui
também `IMP-SESSION-01` no exemplo materializado. A mutação `drop-impact-id-edge` foi eliminada.

### ADDRESSED — Major: invariantes de triagem, reteste e `PASS`

- `tests/test_qa_workflows.py:426-429` exige severidade por impacto e prioridade independente por
  ordem de entrega; `couple-priority-to-severity` foi eliminada.
- `tests/test_qa_workflows.py:430-433` exige caso lógico estável, attempts únicos/crescentes,
  mesmo alvo, `supersedes` linear e ausência de branch/cycle;
  `allow-cross-target-branched-retest` foi eliminada.
- `plugins/pwdev-qa/skills/qa-bug/SKILL.md:50-55` explicita todas as condições para `PASS`, e
  `tests/test_qa_workflows.py:418-425` protege inclusive a ausência de pendências/limitações;
  `allow-pending-pass` foi eliminada.

Nenhum finding Blocker, Major ou Minor permanece aberto nesta rodada.

## REVIEW

APPROVED

Evidência fresca:

- HEAD observado: `f8ddbcd`; não foi movido.
- `git diff --check 6060a73..f8ddbcd`: PASS.
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_qa_workflows`: 20 PASS.
- Python 3.12 empacotado, discovery `test_qa_*.py`: 162 PASS.
- Mutações `drop-impact-id-edge`, `allow-cross-target-branched-retest`,
  `couple-priority-to-severity` e `allow-pending-pass`: todas eliminadas.
- Nenhum arquivo de produto ou teste foi alterado; somente esta revisão foi sobrescrita.
