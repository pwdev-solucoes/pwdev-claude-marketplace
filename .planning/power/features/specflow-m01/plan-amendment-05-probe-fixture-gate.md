---
type: PLAN_AMENDMENT
okf_version: "0.2"
generated:
  by: agent:pwdev-power
  at: "2026-09-13T09:36:40Z"
lifecycle:
  status: APPROVED
human_approval: APPROVED
sources:
  - resource: .planning/power/features/specflow-m01/task-06-report.md
  - resource: .planning/power/features/specflow-m01/plan.md
  - resource: .planning/power/features/specflow-m01/probe-recipe-approved-snapshot.md
verified:
  - event: human_approval
    result: passed
    actor: human:user
    at: "2026-09-13T09:38:38Z"
    source: "user: sim"
---

# Emenda 05 — preparar fixtures antes do gate de probe

## Problema confirmado

O preflight autorizado da Task 06 parou sem executar probes:

1. os sete argv aprovados leem três inputs sob
   `.planning/power/features/specflow-m01/probe/fixture/`, mas a allowlist da Task 06
   só permite arquivos sob `tests/fixtures/sdd_flow/`;
2. o input `run-config.yaml` não aparece na allowlist vigente;
3. o runtime observado mudou de `compozy 0.3.0-beta.16` para
   `compozy 0.3.0-beta.25`, tornando stale a qualificação ligada à aprovação;
4. a falha de socket dentro do sandbox não é indisponibilidade real: consulta
   read-only autorizada fora dele confirmou daemon `running`, health `ok` e Network
   Local `ready`, PID 41238, versão `0.3.0-beta.25`.

Forçar os argv atuais exigiria escrever fora da allowlist; trocar argv ou aceitar a
versão nova sem novo gate invalidaria o ApprovalRef da Task 05.

## Ajuste proposto

Dividir a execução restante em duas fases, mantendo sete tarefas no M01 e os limites
Power de cinco arquivos/sete passos:

### Task 06 — preparar fixtures e renovar receita, sem probe

Allowlist exata:

- `tests/test_sdd_flow_m01_compatibility.py`;
- `.planning/power/features/specflow-m01/probe/fixture/extension/extension.toml`;
- `.planning/power/features/specflow-m01/probe/fixture/extension/agents/probe/AGENT.md`;
- `.planning/power/features/specflow-m01/probe/fixture/specflow-m01-loop.yaml`;
- `.planning/power/features/specflow-m01/probe/fixture/run-config.yaml`.

Os casos adversariais ficam table-driven no teste; `tests/fixtures/sdd_flow/cases.json`
é removido do escopo. A Task 06 cria fixtures estáticas e testes RED/GREEN somente
estruturais, requalifica read-only a versão/sintaxe beta.25 e prepara uma nova
RuntimeRecipe/ApprovalRef ligada aos bytes finais. Nenhum `extension dev`, `loop
create`, `loop run`, publicação ou cleanup é executado nesta fase.

Ao final, apresentar novo preview com digests dos cinco arquivos, sete argv, escopo,
cleanup e budgets. O humano precisa aprovar novamente o snapshot antes da fase
mutável. O ApprovalRef anterior permanece histórico/stale e nunca é reusado.

### Task 07 — executar probes e reconciliar qualificação

A Task 07 existente passa a consumir fixtures e ApprovalRef renovados, executar
somente os sete argv exatos no escopo aprovado e reconciliar prova/gate técnico em:

- `tests/test_sdd_flow_m01_compatibility.py`;
- `tests/test_sdd_flow_m01_qualification.py`;
- `.planning/power/features/specflow-m01/runtime-qualification.md`;
- `.planning/power/features/specflow-m01/compatibility.md`;
- `.planning/power/features/specflow-m01/interface-decisions.md`.

Ela registra resultados reais, IDs retornados pelo Loop separados dos IDs Power,
exit codes e hashes. Falha, NOT_RUN ou ENVIRONMENT_FAILURE em garantia central bloqueia
M02. Não executa Docker, browser, Live, instalação, cleanup, merge ou publicação fora
dos argv aprovados.

## Efeito da autorização anterior

A autorização `user: sim` de `2026-09-13T09:34:07Z` permanece evidência de intenção,
mas não autoriza a receita corrigida: o contrato anterior ficou stale por versão e
paths. Aprovar esta emenda autoriza somente a fase estática/read-only da nova Task 06.
A execução mutável da Task 07 exigirá novo gate sobre o snapshot final.

## Gate

STATUS: APPROVED em 2026-09-13T09:38:38Z por `human:user` (`user: sim`). A aprovação
autoriza somente a preparação estática/read-only da Task 06. Nenhum probe mutável
está autorizado até o próximo gate sobre o snapshot final.
