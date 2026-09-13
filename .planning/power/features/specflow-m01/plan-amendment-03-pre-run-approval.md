---
type: PLAN_AMENDMENT
okf_version: "0.2"
generated:
  by: agent:pwdev-power
  at: "2026-09-13T08:50:00Z"
lifecycle:
  status: APPROVED
human_approval: APPROVED
sources:
  - resource: .planning/power/features/specflow-m01/plan.md
  - resource: .planning/power/features/specflow-m01/task-05-report.md
  - resource: .planning/power/features/specflow-m01/probe-recipe.md
verified:
  - event: human_approval
    by: human:user
    at: "2026-09-13T08:53:00Z"
    scope: .planning/power/features/specflow-m01/plan-amendment-03-pre-run-approval.md
    source: "user: aprovado"
---

# Emenda 03 — aprovação operacional anterior ao Run

## Problema reproduzido

Task 05 exige `run_id`, `gate_id` e `decision_id` reais antes de liberar Task 06.
Task 06 é a primeira etapa autorizada a criar um Loop Run e observar seus IDs. Logo,
interpretar `ApprovalRef.run_id` exclusivamente como Loop Run ID cria um ciclo impossível.
O daemon saudável não resolve o ciclo; `compozy whoami` apenas lê identidade de ambiente
e não produz IDs de gate/Run.

## Decisão proposta

Manter a forma de `ApprovalRef`, mas explicitar dois namespaces distintos:

- na Task 05, `run_id` identifica a execução real do gate Power pré-Run, não um Loop Run;
- `gate_id` é a identidade estável `gate:specflow-m01:runtime-recipe`;
- `actor_ref` é o ator humano real registrado pelo gate Power (`human:user`);
- `decision_id` é derivado deterministicamente de `actor_ref`, decisão, `decided_at`,
  checkout/revisão e SHA-256 do snapshot apresentado; o recibo registra o algoritmo e
  todos os inputs, portanto o ID é reproduzível, não inventado;
- `run_id` é derivado deterministicamente do checkout/revisão, Task 05 e SHA-256 do
  snapshot apresentado, com namespace `power-approval-run:`;
- `artifacts` aponta para o snapshot pré-aprovação de `probe-recipe.md`, usando path
  confinado e seu SHA-256 real; o documento final preserva reconstrução byte a byte;
- `prerequisites` referencia as decisões aprovadas de TechSpec e TASKS por IDs
  determinísticos calculados pelo mesmo algoritmo e documentados no recibo;
- todos os resultados continuam `NOT_RUN`; o gate apenas autoriza o escopo.

Os IDs reais de Loop Run/gate observados durante execução são artefatos distintos da
Task 06 e nunca substituem retroativamente o recibo pré-Run. Task 07 relaciona ambos.

### Serialização canônica exata

Usar UTF-8, LF, nenhuma linha com espaço final e exatamente uma LF final. `run_id` é
`power-approval-run:` seguido do SHA-256 hex minúsculo destes bytes, nesta ordem:

```text
schema=specflow.power-approval-run.v1
feature=specflow-m01
task=M01.05
checkout_revision=fb146297d681a1a6a77d71b5c30772655802590a
snapshot_sha256=c606ebbf29d30881e54dd3e66c58d7e273a5f4bf6d49fd60b980e2171240b7c4
```

`decision_id` é `decision:` seguido do SHA-256 hex minúsculo destes bytes, nesta ordem,
substituindo `<run_id>` pelo valor calculado acima:

```text
schema=specflow.power-approval-decision.v1
run_id=<run_id>
gate_id=gate:specflow-m01:runtime-recipe
actor_ref=human:user
decision=approved
decided_at=2026-09-13T08:53:00Z
snapshot_sha256=c606ebbf29d30881e54dd3e66c58d7e273a5f4bf6d49fd60b980e2171240b7c4
techspec_sha256=09bde614371cb465ea1c135244bd6c4e8cc3f3e62c0c9fdeb3dc065d70ab54f3
tasks_sha256=1efe23df5abe7950567a39bc9451adb5672de14f835ec111fed30bb941bd02d4
```

`prerequisites`, na ordem, são
`power-gate:techspec:09bde614371cb465ea1c135244bd6c4e8cc3f3e62c0c9fdeb3dc065d70ab54f3`
e `power-gate:tasks:1efe23df5abe7950567a39bc9451adb5672de14f835ec111fed30bb941bd02d4`.
Esses valores identificam decisões humanas já registradas nos próprios artefatos.

## Alteração do plano

Não acrescenta tarefas nem arquivos. Ajusta apenas Task 05 e consumidores:

1. Task 05 escreve teste RED para recibo ausente, digest stale, algoritmo divergente,
   ator não humano e confusão entre namespace Power/Loop.
2. Após o gate humano real já ocorrido, Task 05 materializa o ApprovalRef determinístico
   nos quatro arquivos permitidos e prova reconstrução do snapshot.
3. Task 06 aceita somente o namespace `power-approval-run:` fresco para iniciar probes;
   registra separadamente os IDs reais retornados pelo CompozyOS.
4. Task 07 verifica o vínculo entre recibo pré-Run, IDs observados e evidência final.

## Segurança e limites

- Nenhum ID aleatório, placeholder ou Loop Run ID é fabricado.
- Nenhum segredo, credencial ou configuração do usuário é lido ou alterado.
- O daemon já autorizado pode permanecer ativo; esta emenda não autoriza extensão,
  Loop, Run, Docker, browser, Live ou cleanup.
- Alteração de bytes, ator, timestamp, checkout, revisão ou escopo torna a decisão stale.
- A Task 06 continua bloqueada até esta emenda e o recibo resultante passarem por gate
  e revisão independente.

## Gate

STATUS: APPROVED. A aprovação humana autoriza somente corrigir a Task 05 e produzir
o recibo determinístico; não autoriza executar os probes da Task 06.
