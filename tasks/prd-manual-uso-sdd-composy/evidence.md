---
type: EVIDENCE
okf_version: "0.2"
sources:
  - resource: "tasks/prd-manual-uso-sdd-composy/manual.md"
  - resource: "tasks/prd-manual-uso-sdd-composy/prd.md"
  - resource: "tasks/prd-manual-uso-sdd-composy/techspec.md"
generated:
  by: "agent:sdd-evidence"
  at: "2026-09-09T14:58:00+00:00"
lifecycle:
  status: VERIFIED
language: pt-BR
---

# Evidências do manual de uso

| Critério | Comando | Resultado |
|---|---|---|
| CA-001 | `python3 -m unittest discover -s tests -p 'test_sdd_composy*.py' -q` | Suíte SDD Composy aprovada após correção do init |
| CA-002 | `python3 plugins/sdd-composy/scripts/sdd_init.py verify .` | `ok: true`, índice OKF e integração Claude válidos |
| CA-003 | `python3 plugins/sdd-composy/scripts/sdd_map.py --repo-root .` | Mapa gerado sem alterar o estado do projeto |

## Resultado

Os exemplos principais do manual foram executados. A suíte automatizada cobre 295 testes;
os comandos de init e map retornaram os contratos esperados. O manual pode seguir para revisão
final e publicação.
