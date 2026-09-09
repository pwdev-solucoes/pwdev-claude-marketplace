# SDD Composy Hermes — Plan
Status: DRAFT
Spec: .planning/power/features/sdd-composy-hermes/spec.md
Updated: 2026-09-09

## Goal

Adicionar suporte Hermes ao `sdd-composy` reutilizando skills, schemas e contratos existentes.

## File Structure

- `plugins/sdd-composy/.hermes-plugin/plugin.yaml`
- `plugins/sdd-composy/.hermes-plugin/__init__.py`
- `plugins/sdd-composy/references/hermes-tools.md`
- `plugins/sdd-composy/scripts/fleet/engine-hermes.sh`
- `plugins/sdd-composy/scripts/fleet/launch.sh`
- `plugins/sdd-composy/scripts/fleet/run.sh`
- `tests/test_sdd_composy_hermes.py`
- `plugins/sdd-composy/README.md`
- `plugins/sdd-composy/README.pt-BR.md`

## Task 01 — Manifesto e bootstrap Hermes

Complexity: medium
Files: `.hermes-plugin/plugin.yaml`, `.hermes-plugin/__init__.py`, `references/hermes-tools.md`, `tests/test_sdd_composy_hermes.py`

## Task 02 — Runtime e fleet Hermes

Complexity: high
Files: `scripts/fleet/engine-hermes.sh`, `scripts/fleet/launch.sh`, `scripts/fleet/run.sh`, `tests/test_sdd_composy_hermes.py`

## Task 03 — Integração documental e contratos

Complexity: medium
Files: `README.md`, `README.pt-BR.md`, `references/workflow.md`, `references/fleet.md`, `tests/test_sdd_composy_hermes.py`

## Task 04 — Validação final

Complexity: medium
Files: testes Hermes e artefatos de evidência

- Executar suíte SDD Composy.
- Executar testes simulados de bootstrap, runtime mismatch e fleet.
- Registrar que Hermes real, Kanban real e cmux real dependem de ambiente externo.
