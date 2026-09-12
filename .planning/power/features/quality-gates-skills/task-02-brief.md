# Task 02 — brief

Plan: .planning/power/features/quality-gates-skills/plan.md
Generated: 2026-09-11T09:54:01Z

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

## Task 02 — PHP and Laravel specialization
Complexity: medium
Files: `plugins/pwdev-devops/skills/quality-gates-php/SKILL.md`
Interfaces:
  Consumes: phased adoption workflow from `plugins/pwdev-devops/references/quality-gates-action-plan.md`
  Produces: PHP and Laravel tool matrix, blocking policy and ratchet thresholds
Steps:
- [ ] Extend validation assertions for specialized triggers, required stack coverage and the shared reference link.
- [ ] Run the focused validation and observe failure because the specialized skill does not exist.
- [ ] Write the specialized skill with PHPStan/Larastan, Pest/PHPUnit, SAST, PHPMD, Composer Audit and Laravel-specific checks.
- [ ] Run focused validation and inspect every blocking rule for deterministic inputs and outputs.
- [ ] Confirm external mutations and dependency installation remain behind explicit authorization.
- [ ] Commit the task file.
