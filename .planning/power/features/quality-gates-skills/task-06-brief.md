# Task 06 — brief

Plan: .planning/power/features/quality-gates-skills/plan.md
Generated: 2026-09-11T23:46:08Z

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

## Task 06 — Plugin discovery and consistency
Complexity: low
Files: `plugins/pwdev-devops/README.md`, `plugins/pwdev-devops/README.pt-BR.md`, `plugins/pwdev-devops/.claude-plugin/plugin.json`
Interfaces:
  Consumes: skill names and capabilities produced by Tasks 01 through 05
  Produces: discoverable documentation and plugin metadata reporting 24 skills
Steps:
- [ ] Add validation assertions that both README files mention all five skills and the manifest reports 24 skills.
- [ ] Run the focused validation and observe failure against the current discovery metadata.
- [ ] Update English and Portuguese discovery documentation without changing unrelated sections.
- [ ] Update the plugin description from 19 to 24 skills and mention quality gates.
- [ ] Run JSON parsing, link checks and skill validation for all five new skill directories.
- [ ] Review the complete diff and commit the task files.
