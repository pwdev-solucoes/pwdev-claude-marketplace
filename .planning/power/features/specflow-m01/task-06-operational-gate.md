---
type: OPERATIONAL_GATE
okf_version: "0.2"
generated:
  by: agent:pwdev-power
  at: "2026-09-13T09:43:17Z"
lifecycle:
  status: APPROVED
human_approval: APPROVED
sources:
  - resource: .planning/power/features/specflow-m01/task-06-report.md
    sha256: 14da44a9ced2223a48d8aebe0197224ef7477dc32ec3bd8c4d753b075118fbe6
  - resource: .planning/power/features/specflow-m01/task-06-review.md
verified:
  - event: human_approval
    result: passed
    actor: human:user
    at: "2026-09-13T09:52:10Z"
    source: "user: sim"
---

# M01 Task 06 — gate operacional renovado para probes beta.25

## Objeto da decisão

Autorizar a Task 07 a executar somente as sete receitas listadas integralmente em
`.planning/power/features/specflow-m01/task-06-report.md`, usando o executável
`/Users/paulosoares/.local/bin/compozy`, versão observada `compozy 0.3.0-beta.25`,
no checkout `/Users/paulosoares/Projetos/skills-ia/pwdev-claude-marketplace/.worktrees/pwdev-composyos`.

ResourceSet aprovado proposto:

| Path | SHA-256 |
|---|---|
| `tests/test_sdd_flow_m01_compatibility.py` | `6fbe0ce718056c925d807c8033bf84236f1611c239339bb8250f048d188f487a` |
| `.planning/power/features/specflow-m01/probe/fixture/extension/extension.toml` | `2a295e23687684bc683c2e751c60b38f20d4fc88ceef14a4989d6a85000d9c96` |
| `.planning/power/features/specflow-m01/probe/fixture/extension/agents/probe/AGENT.md` | `9651e228e3979d26b581c2c1db11c1672248cb71362065ef941d6575f02f6bf8` |
| `.planning/power/features/specflow-m01/probe/fixture/specflow-m01-loop.yaml` | `fecabbc17bdddf452d4973b24defddd3a555dd907c0ae1de425c62e5c5a23faf` |
| `.planning/power/features/specflow-m01/probe/fixture/run-config.yaml` | `4a662133b00b1b3d3a88c5e7539b82763c389b3b0a6008c89bc57305b7564685` |

O preview integral tem SHA-256
`14da44a9ced2223a48d8aebe0197224ef7477dc32ec3bd8c4d753b075118fbe6`.
A revisão independente foi SPEC PASS / QUALITY PASS, sem findings.

## Limites

- São autorizados somente os sete argv e mutable_scope descritos no preview.
- Budgets: 3 tentativas totais, janela de ausência de progresso 2, fan-out 1.
- Network Local; Live, Gateway público/privado e browser permanecem fora do escopo.
- Docker, instalação, push, merge e alteração de governança não são autorizados.
- Cleanup não é autorizado. O daemon não pode ser parado; ele não pertence a esta Task.
- IDs reais retornados pelo Loop devem ser registrados separadamente dos IDs Power.
- Qualquer digest/path/versão divergente torna esta decisão stale e bloqueia execução.
- Falha, NOT_RUN ou ENVIRONMENT_FAILURE em garantia central bloqueia M02.

## Gate

STATUS: APPROVED em 2026-09-13T09:52:10Z por `human:user` (`user: sim`).

## ApprovalRef canônico derivado

O snapshot pré-aprovação deste gate tem SHA-256
`a406943edfdf223be753df2e098dc27f61177cd2ef245c6c5d4e3d8af9319f5d`.
Usar UTF-8, LF, nenhuma linha com espaço final e exatamente uma LF final.

```text
schema=specflow.power-probe-run.v1
feature=specflow-m01
task=M01.07
checkout_revision=fb146297d681a1a6a77d71b5c30772655802590a
runtime_version=compozy 0.3.0-beta.25
preview_sha256=14da44a9ced2223a48d8aebe0197224ef7477dc32ec3bd8c4d753b075118fbe6
gate_snapshot_sha256=a406943edfdf223be753df2e098dc27f61177cd2ef245c6c5d4e3d8af9319f5d
```

`run_id` derivado:
`power-approval-run:b2098dfc41fbdf167c9b202263882a1dd45c9348dc88202dfd560f8dcf05555a`.

```text
schema=specflow.power-probe-decision.v1
run_id=power-approval-run:b2098dfc41fbdf167c9b202263882a1dd45c9348dc88202dfd560f8dcf05555a
gate_id=gate:specflow-m01:runtime-probe-beta25
actor_ref=human:user
decision=approved
decided_at=2026-09-13T09:52:10Z
preview_sha256=14da44a9ced2223a48d8aebe0197224ef7477dc32ec3bd8c4d753b075118fbe6
gate_snapshot_sha256=a406943edfdf223be753df2e098dc27f61177cd2ef245c6c5d4e3d8af9319f5d
```

`decision_id` derivado:
`decision:5bfdf63eb59c86278e4013fb7d3a9643cadd4b3ec9e5803683d32f005a6cd7a2`.
