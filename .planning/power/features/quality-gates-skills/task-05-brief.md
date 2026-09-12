# Task 05 — brief

Plan: .planning/power/features/quality-gates-skills/plan.md
Generated: 2026-09-11T21:47:16Z

These are your requirements. Every value below is exact — copy it, do not round it,
do not substitute an equivalent, do not improve it.

## Global Constraints

- Os nomes serão exatamente `quality-gates`, `quality-gates-php`, `quality-gates-vue`,
  `quality-gates-node` e `quality-gates-postgres`.
- As skills serão publicadas em `plugins/pwdev-devops/skills/`.
- O plano de ação será escrito em português e será aplicável por fases.
- A skill genérica não duplicará as matrizes tecnológicas das especializações.
- Nenhum gate recomendará configuração remota flutuante como fonte bloqueante.
- SonarQube será opcional e só poderá bloquear com versão, Quality Profile, Quality Gate e
  parâmetros de scanner controlados.
- Nenhuma baseline adicionará automaticamente novos problemas durante o CI.
- Nenhuma skill executará mutações externas, instalará dependências ou alterará pipelines sem
  autorização explícita.
- A descrição do plugin passará de 19 para 24 skills.

## Task 05 — PostgreSQL specialization
Complexity: medium
Files: `plugins/pwdev-devops/skills/quality-gates-postgres/SKILL.md`
Interfaces:
  Consumes: phased adoption workflow from `plugins/pwdev-devops/references/quality-gates-action-plan.md`
  Produces: PostgreSQL migration, schema, constraint, index and query-plan gate policy
Steps:
- [ ] Define validation assertions for PostgreSQL triggers, required gate categories and the shared reference link.
- [ ] Run the focused validation and observe failure because the PostgreSQL skill does not exist.
- [ ] Write the PostgreSQL skill with ephemeral database, migration, schema drift, constraint, index and query-plan gates.
- [ ] Run focused validation and confirm performance checks use fixed fixtures rather than shared-runner timing.
- [ ] Confirm the skill does not perform DBA operations or production mutations.
- [ ] Commit the task file.
