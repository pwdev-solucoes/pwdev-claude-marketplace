---
type: RUNTIME_QUALIFICATION
okf_version: "0.2"
generated: {by: agent:pwdev-power, at: "2026-09-13T10:00:00Z"}
lifecycle: {status: FAILED}
human_approval: APPROVED
sources:
  - resource: .planning/power/features/specflow-m01/task-06-report.md
    sha256: 14da44a9ced2223a48d8aebe0197224ef7477dc32ec3bd8c4d753b075118fbe6
verified:
  - {event: runtime_probe, result: failed, at: "2026-09-13T10:00:00Z"}
---

# M01 — qualificação operacional beta.25

Preflight confirmou checkout `fb146297d681a1a6a77d71b5c30772655802590a`, versão,
preview e fixtures aprovados. O retry autorizado de `daemon start` encontrou daemon
já ativo. `extension validate` rejeitou o manifesto: `resources.agents` deveria ser
tabela, não string. A execução parou; mudar fixture/argv exigiria novo escopo e gate.

```json
{
  "version":"compozy 0.3.0-beta.25",
  "command_recipes":[
    {"id":"RCP-DAEMON-START-001","argv":["daemon","start"],"approved_scope":{"run_id":"power-approval-run:b2098dfc41fbdf167c9b202263882a1dd45c9348dc88202dfd560f8dcf05555a","gate_id":"gate:specflow-m01:runtime-probe-beta25","decision_id":"decision:5bfdf63eb59c86278e4013fb7d3a9643cadd4b3ec9e5803683d32f005a6cd7a2"},"observed":"daemon already running (pid recorded separately)","result":"FAIL","exit_code":1,"output_sha256":"7fd010cf97915ae1a4bee01a63e6422074cd169b804e7380f75e072bd66d1e08"},
    {"id":"RCP-EXTENSION-VALIDATE-001","argv":["extension","validate",".planning/power/features/specflow-m01/probe/fixture/extension"],"approved_scope":{"run_id":"power-approval-run:b2098dfc41fbdf167c9b202263882a1dd45c9348dc88202dfd560f8dcf05555a","gate_id":"gate:specflow-m01:runtime-probe-beta25","decision_id":"decision:5bfdf63eb59c86278e4013fb7d3a9643cadd4b3ec9e5803683d32f005a6cd7a2"},"observed":"resources.agents expected table but found string","result":"FAIL","exit_code":1,"output_sha256":"b8076127fc72b74ee5d883641443ee6614732288ba33c7d5b1b33da4f51fdda4"},
    {"id":"RCP-EXTENSION-DEV-001","argv":["extension","dev",".planning/power/features/specflow-m01/probe/fixture/extension","--workspace","specflow-m01-probe-20260913"],"approved_scope":{"run_id":"power-approval-run:b2098dfc41fbdf167c9b202263882a1dd45c9348dc88202dfd560f8dcf05555a","gate_id":"gate:specflow-m01:runtime-probe-beta25","decision_id":"decision:5bfdf63eb59c86278e4013fb7d3a9643cadd4b3ec9e5803683d32f005a6cd7a2"},"observed":"NOT_RUN","result":"NOT_RUN"},
    {"id":"RCP-LOOP-VALIDATE-001","argv":["loop","validate","--file",".planning/power/features/specflow-m01/probe/fixture/specflow-m01-loop.yaml","--name","specflow-m01-qualification","--workspace","specflow-m01-probe-20260913"],"approved_scope":{"run_id":"power-approval-run:b2098dfc41fbdf167c9b202263882a1dd45c9348dc88202dfd560f8dcf05555a","gate_id":"gate:specflow-m01:runtime-probe-beta25","decision_id":"decision:5bfdf63eb59c86278e4013fb7d3a9643cadd4b3ec9e5803683d32f005a6cd7a2"},"observed":"NOT_RUN","result":"NOT_RUN"},
    {"id":"RCP-LOOP-CREATE-001","argv":["loop","create","--file",".planning/power/features/specflow-m01/probe/fixture/specflow-m01-loop.yaml","--expected-version","0","--workspace","specflow-m01-probe-20260913"],"approved_scope":{"run_id":"power-approval-run:b2098dfc41fbdf167c9b202263882a1dd45c9348dc88202dfd560f8dcf05555a","gate_id":"gate:specflow-m01:runtime-probe-beta25","decision_id":"decision:5bfdf63eb59c86278e4013fb7d3a9643cadd4b3ec9e5803683d32f005a6cd7a2"},"observed":"NOT_RUN","result":"NOT_RUN"},
    {"id":"RCP-LOOP-DRY-RUN-001","argv":["loop","run","--dry-run","--name","specflow-m01-qualification","--network","local","--workspace","specflow-m01-probe-20260913","--config-file",".planning/power/features/specflow-m01/probe/fixture/run-config.yaml"],"approved_scope":{"run_id":"power-approval-run:b2098dfc41fbdf167c9b202263882a1dd45c9348dc88202dfd560f8dcf05555a","gate_id":"gate:specflow-m01:runtime-probe-beta25","decision_id":"decision:5bfdf63eb59c86278e4013fb7d3a9643cadd4b3ec9e5803683d32f005a6cd7a2"},"observed":"NOT_RUN","result":"NOT_RUN"},
    {"id":"RCP-LOOP-RUN-001","argv":["loop","run","--name","specflow-m01-qualification","--network","local","--workspace","specflow-m01-probe-20260913","--config-file",".planning/power/features/specflow-m01/probe/fixture/run-config.yaml"],"approved_scope":{"run_id":"power-approval-run:b2098dfc41fbdf167c9b202263882a1dd45c9348dc88202dfd560f8dcf05555a","gate_id":"gate:specflow-m01:runtime-probe-beta25","decision_id":"decision:5bfdf63eb59c86278e4013fb7d3a9643cadd4b3ec9e5803683d32f005a6cd7a2"},"observed":"NOT_RUN","result":"NOT_RUN"}
  ],
  "core_checks":[
    {"id":"CORE-001","result":"FAIL","revision_ref":"fb146297d681a1a6a77d71b5c30772655802590a"},{"id":"CORE-002","result":"FAIL","revision_ref":"fb146297d681a1a6a77d71b5c30772655802590a"},{"id":"CORE-003","result":"NOT_RUN","revision_ref":"fb146297d681a1a6a77d71b5c30772655802590a"},{"id":"CORE-004","result":"NOT_RUN","revision_ref":"fb146297d681a1a6a77d71b5c30772655802590a"},{"id":"CORE-005","result":"NOT_RUN","revision_ref":"fb146297d681a1a6a77d71b5c30772655802590a"},{"id":"CORE-006","result":"NOT_RUN","revision_ref":"fb146297d681a1a6a77d71b5c30772655802590a"},{"id":"CORE-007","result":"NOT_RUN","revision_ref":"fb146297d681a1a6a77d71b5c30772655802590a"},{"id":"CORE-008","result":"NOT_RUN","revision_ref":"fb146297d681a1a6a77d71b5c30772655802590a"},{"id":"CORE-009","result":"NOT_RUN","revision_ref":"fb146297d681a1a6a77d71b5c30772655802590a"}
  ],
  "optional_checks":[{"id":"OPT-001","result":"NOT_RUN"},{"id":"OPT-002","result":"NOT_RUN"},{"id":"OPT-003","result":"NOT_RUN"},{"id":"OPT-004","result":"NOT_RUN"},{"id":"OPT-005","result":"NOT_RUN"}],
  "verdict":"FAIL",
  "evidence_refs":[{"path":".planning/power/features/specflow-m01/task-06-report.md","sha256":"14da44a9ced2223a48d8aebe0197224ef7477dc32ec3bd8c4d753b075118fbe6","role":"contract"}]
}
```

Falha e `NOT_RUN` em garantias centrais bloqueiam M02. STATUS: BLOCKED.

## Matriz legada pré-probe preservada

| ID | Garantia | Resultado |
|---|---|---|
| CORE-001 | Gates/digests | NOT_RUN |
| CORE-002 | Schemas | NOT_RUN |
| CORE-003 | Loading | NOT_RUN |
| CORE-004 | Atomicity | NOT_RUN |
| CORE-005 | History/resume | NOT_RUN |
| CORE-006 | Confinement | NOT_RUN |
| CORE-007 | Read-only | NOT_RUN |
| CORE-008 | Mutual exclusion | NOT_RUN |
| CORE-009 | Role isolation | NOT_RUN |
| OPT-001 | Worktree | NOT_RUN |
| OPT-002 | Docker | NOT_RUN |
| OPT-003 | Live | NOT_RUN |
| OPT-004 | playwright-cli | NOT_RUN |
| OPT-005 | HTML/PDF | NOT_RUN |

Esta tabela é histórico da proposta anterior, não o verdict atual no JSON acima.
