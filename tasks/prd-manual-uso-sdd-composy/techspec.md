---
type: TECHSPEC
okf_version: "0.2"
sources:
  - resource: "tasks/prd-manual-uso-sdd-composy/prd.md"
  - resource: "tasks/prd-manual-uso-sdd-composy/stories.md"
  - resource: ".planning/sdd-composy/context/project.md"
  - resource: ".planning/sdd-composy/context/codebase.json"
generated:
  by: "agent:sdd-techspec"
  at: "2026-09-09T14:41:00+00:00"
lifecycle:
  status: APPROVED
human_approval: APPROVED
verified:
  - event: human_approval
    by: user
    at: "2026-09-09T14:45:00+00:00"
language: pt-BR
---

# Manual de uso do SDD Composy — Especificação técnica

## Contexto técnico

O repositório contém 17 skills, comandos Markdown, scripts Python/Shell, templates OKF v0.2
e schemas JSON. O manual será um artefato Markdown versionado dentro do diretório da PRD.

## Inventário de componentes

| Componente | Tipo | Responsabilidade | Entradas | Saídas | Ligações |
|---|---|---|---|---|---|
| `manual.md` | Novo | Guia operacional ponta a ponta | PRD, stories, referências do plugin | Manual em pt-BR | RF-001, RF-002, RF-003 |
| `references/*.md` | Existente | Contratos canônicos | Regras das skills | Conteúdo normativo | RF-002 |
| `sdd_init.py`, `sdd_map.py`, `sdd_status.py` | Existente | Exemplos executáveis | Projeto e configuração | Estado e artefatos | CA-002 |

## Interfaces e contratos

| Interface | Entrada | Saída | Falha |
|---|---|---|---|
| Manual → skill | Nome da skill, pré-condições | Comando e artefato esperado | Orienta `init`, status ou recuperação |
| Manual → artefato | Caminho e schema | Markdown/JSON OKF válido | Não prossegue sem gate |

## Modelo de dados

`NOT_APPLICABLE`: o manual não altera modelos persistentes do plugin.

## APIs

`NOT_APPLICABLE`: o manual não expõe API externa.

## Decisões

### DEC-001 — Manual versionado junto da PRD

- Opções: wiki externa; documento no repositório; README único.
- Escolha: documento no repositório, referenciando contratos existentes.
- Racional: mantém exemplos revisáveis e rastreáveis.
- Trade-offs: requer atualização quando skills mudarem.
- Reversível: sim.

## Riscos

### RISK-001 — Manual ficar desatualizado

- Likelihood: média.
- Impact: médio.
- Mitigação: revisão contra os 17 SKILL.md e execução dos exemplos.
- Owner: mantenedor do plugin.
- Sinal: comando ou caminho documentado não existir.

## Casos de teste

### TI-001 — CA-001 — Cobertura das skills

- Level: Integration
- Setup: manual e diretório `plugins/sdd-composy/skills` disponíveis.
- Action: comparar cada skill pública com uma seção do manual.
- Expected: nenhuma skill sem entrada documentada.

### E2E-001 — CA-002 — Execução do fluxo inicial

- Level: End-to-end
- Setup: projeto de teste limpo.
- Action: executar init, map e status conforme manual.
- Expected: artefatos OKF em pt-BR e status verificável.

## Gate

Este TechSpec permanece `DRAFT` até aprovação humana explícita.
