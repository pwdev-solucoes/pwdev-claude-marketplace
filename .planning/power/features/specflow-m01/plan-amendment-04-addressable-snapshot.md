---
type: PLAN_AMENDMENT
okf_version: "0.2"
generated:
  by: agent:pwdev-power
  at: "2026-09-13T09:15:00Z"
lifecycle:
  status: APPROVED
human_approval: APPROVED
sources:
  - resource: .planning/power/features/specflow-m01/plan-amendment-03-pre-run-approval.md
  - resource: .planning/power/features/specflow-m01/task-05-review.md
verified:
  - event: human_approval
    result: passed
    actor: human:user
    at: "2026-09-13T09:21:33Z"
    source: "user: sim"
---

# Emenda 04 — snapshot de aprovação endereçável

## Problema confirmado

O ApprovalRef aponta para `probe-recipe.md` com o digest pré-aprovação `c606...b7c4`,
mas esse path agora contém o documento pós-aprovação `5ee9...2c8a`. A reconstrução
byte a byte comprova preservação, porém não satisfaz ArtifactRef, que exige que o path
referenciado resolva diretamente para um arquivo regular com o SHA-256 declarado.

Os testes também validam somente prefixos/campos superficiais; não recomputam os dois
IDs nem rejeitam timestamp, snapshot, artifacts ou prerequisites alterados.

## Ajuste aprovado proposto

Adicionar à allowlist da Task 05 um quinto arquivo:

`.planning/power/features/specflow-m01/probe-recipe-approved-snapshot.md`

Esse arquivo deve conter exatamente os bytes do snapshot pré-aprovação reconstruído,
com SHA-256 esperado
`c606ebbf29d30881e54dd3e66c58d7e273a5f4bf6d49fd60b980e2171240b7c4`.
Deve ser arquivo regular, confinado, sem symlink/traversal. Os sete ArtifactRef passam
a apontar para esse path e digest; `probe-recipe.md` continua sendo o recibo atual.

Nos testes da Task 05:

- recomputar `run_id` e `decision_id` a partir dos registros UTF-8/LF canônicos;
- validar o snapshot pelo path e SHA-256 reais;
- rejeitar run/decision digest alterado, artifacts vazio, path/digest stale,
  prerequisites vazios/fora de ordem, timestamp divergente, ator inválido e mistura
  de namespace Power/Loop;
- confirmar sete receitas com o mesmo ApprovalRef e `observed/result: NOT_RUN`.

Os registros canônicos e seus valores permanecem os aprovados na Emenda 03. A Emenda
04 não altera TechSpec, TASKS, número de tarefas ou a forma de ApprovalRef; apenas torna
o snapshot resolvível e a verificação adversarial.

## Gate

STATUS: APPROVED em 2026-09-13T09:21:33Z por `human:user` (`user: sim`). Esta
aprovação autoriza criar o quinto arquivo e corrigir os dois findings Important da
Task 05. Não autoriza nenhum probe da Task 06.
