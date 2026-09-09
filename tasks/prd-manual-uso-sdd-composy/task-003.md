---
type: TASK
okf_version: "0.2"
id: TASK-003
title: Validar exemplos e publicar evidências
state: complete
dependencies: [TASK-002]
acceptance_criteria: [CA-003]
verification_commands:
  - "python3 plugins/sdd-composy/scripts/sdd_init.py verify ."
  - "python3 -m unittest discover -s tests -p 'test_sdd_composy*.py' -q"
allowed_paths:
  - "tasks/prd-manual-uso-sdd-composy/evidence.md"
evidence_required: true
---

# TASK-003 — Validar exemplos e publicar evidências

Executar os exemplos principais, validar o projeto e registrar os resultados em evidências.

## Resultado

`evidence.md` registra init, map e suíte automatizada aprovados.
