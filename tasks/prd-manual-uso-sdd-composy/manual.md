---
type: GUIDE
okf_version: "0.2"
sources:
  - resource: "tasks/prd-manual-uso-sdd-composy/prd.md"
  - resource: "tasks/prd-manual-uso-sdd-composy/stories.md"
  - resource: "tasks/prd-manual-uso-sdd-composy/techspec.md"
generated:
  by: "agent:sdd-execute"
  at: "2026-09-09T14:51:00+00:00"
lifecycle:
  status: DRAFT
---

# Manual de uso do SDD Composy

## Fluxo rápido

1. Execute `sdd_init.py inspect .` e escolha o idioma no `init`.
2. Execute `sdd_map.py --repo-root . --write` para gerar o contexto.
3. Crie e aprove stories, PRD e TechSpec.
4. Decomponha o trabalho em tarefas e aprove o índice.
5. Execute `sdd-execute` para tarefas normais ou `sdd-quick` para mudanças pequenas.
6. Passe por QA, evidências, revisão e verificação antes de concluir.
7. Use status e sync para acompanhar e consolidar o estado.

## Skills por etapa

| Etapa | Skill | Resultado |
|---|---|---|
| Inicialização | `sdd-init` | AGENTS, CLAUDE, regras e configuração |
| Contexto | `sdd-map` | mapa OKF do codebase |
| Produto | `sdd-stories`, `sdd-prd` | histórias e requisitos aprováveis |
| Solução | `sdd-techspec` | decisões e contratos técnicos |
| Planejamento | `sdd-tasks` | tarefas com dependências |
| Execução | `sdd-execute`, `sdd-quick` | implementação controlada |
| Qualidade | `sdd-qa`, `sdd-evidence`, `sdd-review`, `sdd-verify` | gates e evidências |
| Operação | `sdd-status`, `sdd-trace`, `sdd-loop`, `sdd-fleet`, `sdd-sync` | acompanhamento e coordenação |

## Regras essenciais

- O idioma é escolhido somente no `init` e fica persistido no projeto.
- IDs, chaves JSON, enums, caminhos e comandos não são traduzidos.
- Não pule gates de aprovação, QA, evidência ou verificação.
- Se o estado for `not_initialized`, execute `init` antes de gerar artefatos.

## Contratos e gates

### Produto e especificação

`sdd-stories` produz histórias com critérios SC e exige aprovação humana. `sdd-prd` transforma
as histórias em requisitos RF/CA. `sdd-techspec` registra componentes, interfaces, decisões,
riscos e testes. Cada documento aprovado deve registrar `human_approval: APPROVED`, status
`APPROVED` e um evento correspondente em `verified`.

### Tarefas

`sdd-tasks` mantém a projeção JSON com IDs `TASK-*`, dependências acíclicas, critérios `CA-*`,
comandos de verificação e caminhos permitidos. Uma tarefa só fica `ready` quando suas dependências
estão completas.

### Execução

`sdd-execute` segue o contrato aprovado e mantém o trabalho dentro dos caminhos permitidos.
`sdd-quick` atende mudanças pequenas, mas ainda exige contrato, verificação e evidência.
`sdd-loop` só conclui com os cinco estágios e evidência VERIFY recente e íntegra.

### Qualidade e evidência

`sdd-qa` registra resultado de testes e análise. `sdd-evidence` publica manifesto atômico,
com hashes e caminhos confinados. `sdd-review` registra aprovação ou rejeição. `sdd-verify`
faz a validação adversarial final. Falhas mantêm o estado aberto ou rejeitado.

### Status, trace e fleet

`sdd-status` é somente leitura. `sdd-trace` preserva a cadeia entre requisito, tarefa, teste
e evidência. `sdd-fleet` cria isolamento por membro, runner e porta, com teardown condicionado
à verificação de merge. `sdd-sync` atualiza projeções sem apagar campos desconhecidos.

## Recuperação

- `not_initialized`: voltar ao `sdd-init`.
- `blocked`: registrar motivo, corrigir a dependência e retornar a `ready`.
- `rejected`: corrigir o artefato e executar novamente review/verify.
- evidência ausente, antiga ou adulterada: repetir QA e gerar novo manifesto.
