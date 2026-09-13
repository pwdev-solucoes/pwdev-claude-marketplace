---
type: COMPATIBILITY_PROPOSAL
okf_version: "0.2"
generated:
  by: agent:pwdev-power
  at: "2026-09-13T10:00:00Z"
lifecycle:
  status: DRAFT
human_approval: PENDING
sources:
  - resource: tasks/prd-specflow/prd.md
    sha256: d76143fad520c44972350d48207348c7256fb18a0e112500f6c34d1f6efd2c96
  - resource: tasks/prd-specflow/stories.md
    sha256: 1f0396da2fc57c2156fa1aae9efb45d1133963fa86a1847d2b876bd606e20338
  - resource: .planning/power/features/specflow-m01/probe-recipe.md
    sha256: c606ebbf29d30881e54dd3e66c58d7e273a5f4bf6d49fd60b980e2171240b7c4
verified: []
---

# M01 — proposta de compatibilidade e resultado separado

A `RuntimeRecipe[] concreta` originada na Task 03 permanece preservada como contrato
histórico. A matriz proposta continuava BLOCKED e sem probes antes do gate Task 06.

| ID | Garantia | Resultado |
|---|---|---|
| CORE-001 | Gates humanos/digests | NOT_RUN |
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

## Observação Task 07

O resultado operacional não altera retroativamente esta proposta. Em beta.25,
`extension validate` terminou exit 1 porque `resources.agents` era string onde o
runtime exige tabela; hash da saída
`b8076127fc72b74ee5d883641443ee6614732288ba33c7d5b1b33da4f51fdda4`.
O verdict corrente está em [runtime-qualification.md](runtime-qualification.md):
`FAIL/BLOCKED`; garantias dependentes seguem `NOT_RUN` e M02 não avança.
