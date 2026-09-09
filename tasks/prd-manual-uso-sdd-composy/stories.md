---
type: STORIES
okf_version: "0.2"
sources:
  - resource: ".planning/sdd-composy/context/project.md"
  - resource: ".planning/sdd-composy/context/codebase.json"
generated:
  by: "agent:sdd-stories"
  at: "2026-09-09T14:30:00+00:00"
lifecycle:
  status: APPROVED
applicability: REQUIRED
applicability_justification: "Manual de uso para adoção do plugin por equipes de desenvolvimento."
human_approval: APPROVED
verified:
  - event: human_approval
    by: user
    at: "2026-09-09T14:35:00+00:00"
language: pt-BR
---

# Manual de uso do plugin SDD Composy — Histórias de usuário

## Atores

### Actor-001 — Pessoa desenvolvedora

Pessoa que instala o plugin e precisa conduzir um trabalho de desenvolvimento orientado a especificações.

### Actor-002 — Pessoa revisora

Pessoa que acompanha critérios, evidências, status e aprovação dos artefatos produzidos.

## Jornada principal

### Journey-001 — Conduzir um trabalho completo

A pessoa desenvolvedora inicializa o projeto, escolhe `pt-BR`, mapeia o codebase, cria uma história,
detalha requisitos, executa tarefas e valida evidências. A pessoa revisora consulta o status e aprova
os gates antes da conclusão.

## Histórias de usuário

### US-001 — RF-001 — Aprender e executar o fluxo do SDD Composy

Como pessoa desenvolvedora, quero consultar um manual de uso completo do plugin para saber qual skill
executar em cada etapa, quais artefatos são gerados e quais aprovações são necessárias.

#### SC-001 — CA-001 — Manual cobre o fluxo ponta a ponta

Dado um projeto com o plugin instalado, quando a pessoa consulta o manual, então encontra instruções
para init, map, stories, PRD, techspec, tasks, execute/quick, QA, evidence, review, verify, status e sync.

#### SC-002 — CA-002 — Manual documenta idioma e contratos

Dado que o idioma é escolhido no init, quando a pessoa segue o manual, então sabe que os artefatos
humanos usam `pt-BR` ou `en-US`, enquanto IDs, chaves JSON, enums e comandos permanecem estáveis.

#### SC-003 — CA-003 — Manual documenta gates e recuperação

Dado que uma etapa falhe ou aguarde aprovação, quando a pessoa consulta o manual, então encontra o
status esperado, a evidência necessária e a ação segura para continuar ou corrigir.

## Dependências

- DEP-001 — Plugin `sdd-composy` instalado e descoberto pelo runtime usado pela equipe.
- DEP-002 — Projeto inicializado com `sdd-init` e idioma persistido.

## Casos-limite

- EDGE-001 — Se o projeto já possuir `.agents` ou `.claude`, o manual deve explicar a integração sem apagar conteúdo existente.
- EDGE-002 — Se não houver idioma persistido, as skills devem orientar a executar `init` antes de gerar artefatos.

## Gate

Este artefato permanece `DRAFT` e requer aprovação humana antes de alimentar PRD e tarefas.
