---
type: TASK
okf_version: "0.2"
id: TASK-002
title: Documentar skills, contratos e gates
state: complete
dependencies: [TASK-001]
acceptance_criteria: [CA-002]
verification_commands:
  - "rg -n 'Contratos e gates|Recuperação' tasks/prd-manual-uso-sdd-composy/manual.md"
allowed_paths:
  - "tasks/prd-manual-uso-sdd-composy/manual.md"
evidence_required: true
---

# TASK-002 — Documentar skills, contratos e gates

Adicionar ao manual os contratos, estados, gates, idioma e caminhos de recuperação.

## Resultado

Seções de contratos e recuperação publicadas no manual.
