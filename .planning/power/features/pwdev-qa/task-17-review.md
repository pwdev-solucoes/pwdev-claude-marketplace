# Re-revisão independente — Task 17 (round 2)

## SPEC

PASS

As correções recebem, preservam e emitem objetivo/intenção e autorização explicitamente nos
dois workflows. `qa-init` e `qa-strategy` continuam consultando `qa-tooling`, preservando
limitações e mantendo execução/exportação como ações separadas. Os corpos compartilhados
permanecem portáveis e sem dependências nominais exclusivas de Claude; essas variáveis aparecem
somente nos wrappers Claude finos.

## QUALITY

PASS

A suíte agora verifica a propagação de objetivo e autorização pelas seções Inputs, Procedure e
Output, além de recusar os quatro tokens específicos de Claude nos corpos compartilhados. Três
mutações em memória — remoção de `OBJECTIVE`, remoção de `AUTHORIZATION` e injeção de
`CLAUDE.md` — foram eliminadas pelos testes. A verificação focada e a regressão QA completa
passaram.

## FINDINGS

### ADDRESSED — Major: preservação de intenção e autorização

- `plugins/pwdev-qa/skills/qa-init/SKILL.md:15-21` recebe objetivo e limites de autorização;
  `:32-35` exige preservá-los exatamente; `:55-60` emite `OBJECTIVE` e `AUTHORIZATION`.
- `plugins/pwdev-qa/skills/qa-strategy/SKILL.md:15-21` recebe objetivo/intenção e autorização;
  `:26-28` exige preservação exata; `:56-61` emite ambos.
- `tests/test_qa_workflows.py:39-53` cobre a cadeia completa nas duas skills. As mutações que
  removeram separadamente os dois campos falharam como esperado.

### ADDRESSED — Minor: independência do corpo compartilhado para Hermes

`tests/test_qa_workflows.py:55-61` recusa `CLAUDE.md`, `AGENTS.md`,
`${CLAUDE_PLUGIN_ROOT}` e `$ARGUMENTS` nos dois corpos compartilhados. A inspeção atual encontrou
zero ocorrências, e a mutação que injetou `CLAUDE.md` foi eliminada. Os wrappers em
`plugins/pwdev-qa/commands/init.md:8-9` e `plugins/pwdev-qa/commands/strategy.md:8-9` continuam
limitados a carregar a skill, encaminhar argumentos/contexto e devolver o resultado inalterado.

Nenhum finding Blocker, Major ou Minor permanece aberto nesta rodada.

## REVIEW

APPROVED

Evidência fresca:

- HEAD observado: `7017f18`; não foi movido.
- `git diff --check eee8386..7017f18`: PASS.
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_qa_workflows`: 9 PASS.
- Python 3.12 empacotado, discovery `test_qa*.py`: 151 PASS.
- Probe independente dos templates e dos quatro tokens proibidos: PASS.
- Mutações `drop-objective`, `drop-authorization` e `inject-claude-token`: todas eliminadas.
- Nenhum arquivo de produto ou teste foi alterado; somente esta revisão foi sobrescrita.
