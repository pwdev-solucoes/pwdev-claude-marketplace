---
type: PRD
okf_version: "0.2"
sources:
  - resource: "tasks/prd-manual-uso-sdd-composy/stories.md"
  - resource: ".planning/sdd-composy/context/project.md"
  - resource: ".planning/sdd-composy/context/domain.md"
generated:
  by: "agent:sdd-prd"
  at: "2026-09-09T14:36:00+00:00"
lifecycle:
  status: APPROVED
human_approval: APPROVED
verified:
  - event: human_approval
    by: user
    at: "2026-09-09T14:40:00+00:00"
language: pt-BR
---

# Manual de uso do SDD Composy — PRD

## Problema

Pessoas desenvolvedoras precisam entender a sequência correta das skills, os artefatos gerados,
os gates de aprovação e os caminhos de recuperação do SDD Composy. Sem um manual, o uso fica
dependente de conhecimento informal e aumenta o risco de pular etapas ou produzir evidências inválidas.

## Objetivos

- O-001 — Permitir que uma pessoa nova execute o fluxo completo a partir de um único manual.
- O-002 — Tornar explícitos artefatos, estados, aprovações e comandos de cada etapa.

## Métricas de sucesso

| Objetivo | Métrica | Baseline | Meta | Janela |
|---|---|---:|---:|---|
| O-001 | Fluxos concluídos sem orientação adicional | 0 | 1 fluxo validado | Primeiro uso |
| O-002 | Etapas documentadas com entrada, saída e gate | 0 | 100% das skills públicas | Revisão do manual |

## Escopo

### Incluído

- Manual em Markdown para Claude Code e Codex.
- Instalação, init, idioma, map, stories, PRD, techspec, tasks, execute, quick, QA, evidence,
  review, verify, status, sync, loop e fleet.
- Exemplos de comandos, artefatos esperados, gates, erros comuns e recuperação.

### Fora do escopo

- Alterar o comportamento das skills do plugin.
- Tutorial específico de um framework ou aplicação externa.
- Execução de provedores reais, cmux ou ambientes de produção.

## Premissas

- A pessoa possui acesso ao repositório do marketplace e ao runtime escolhido.
- O idioma é definido no `init` e persistido no projeto.

## Dependências

- D-001 — Plugin `sdd-composy` instalado e descoberto pelo runtime; responsável: manutenção do plugin.
- D-002 — Projeto inicializado e com contexto gerado pelo `sdd-map`; responsável: pessoa desenvolvedora.

## Questões em aberto

- Q-001 — O manual deve incluir uma versão HTML publicada? Responsável: mantenedor; prazo: antes da publicação.

## Requisitos funcionais

### RF-001 — Manual apresenta o fluxo ponta a ponta

O manual deve descrever cada etapa em ordem, sua entrada, ação, saída e próximo passo.

### RF-002 — Manual preserva contratos técnicos

O manual deve distinguir texto traduzível de IDs, chaves JSON, enums, caminhos e comandos estáveis.

### RF-003 — Manual documenta gates e recuperação

O manual deve indicar quando aprovação humana é necessária, quais evidências são exigidas e como recuperar falhas.

## Critérios de aceitação

### CA-001 — RF-001 possui cobertura completa

Dado o plugin instalado, quando uma pessoa consulta o manual, então encontra todas as 17 skills públicas,
suas entradas, saídas e transições.

### CA-002 — RF-002 mantém exemplos executáveis

Dado um exemplo de comando ou artefato, quando a pessoa o copia para um projeto inicializado, então os nomes
de skills, caminhos e contratos correspondem ao plugin instalado.

### CA-003 — RF-003 orienta decisões seguras

Dado um estado pendente, bloqueado ou rejeitado, quando a pessoa consulta o manual, então encontra a evidência
necessária e uma ação de recuperação sem pular gates.

## Gate

Este PRD permanece `DRAFT` até aprovação humana explícita.
