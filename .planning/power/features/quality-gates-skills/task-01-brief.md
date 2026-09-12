# Task 01 — brief

Plan: .planning/power/features/quality-gates-skills/plan.md
Generated: 2026-09-11T09:46:34Z

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

## Task 01 — Shared action plan and generic skill
Complexity: medium
Files: `plugins/pwdev-devops/references/quality-gates-action-plan.md`, `plugins/pwdev-devops/skills/quality-gates/SKILL.md`
Interfaces:
  Consumes: approved decisions and constraints from `.planning/power/features/quality-gates-skills/spec.md`
  Produces: phased adoption workflow and routing contract to `quality-gates-php`, `quality-gates-vue`, `quality-gates-node` and `quality-gates-postgres`
Steps:
- [ ] Write validation assertions for required frontmatter, reference links and phased action-plan sections.
- [ ] Run the validation and observe failure because the new files do not exist.
- [ ] Write the stack-agnostic skill and the phased action plan with deterministic gate criteria.
- [ ] Run focused validation and confirm the generic skill links to the shared reference.
- [ ] Inspect the diff for duplicated stack-specific thresholds.
- [ ] Commit the task files.
