# Task 07 — brief

Plan: .planning/power/features/quality-gates-skills/plan.md
Generated: 2026-09-12T08:40:45Z

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

## Task 07 — Final verification
Complexity: low
Files: none; read-only verification of all feature outputs
Interfaces:
  Consumes: all outputs from Tasks 01 through 06
  Produces: fresh validation evidence for the approved acceptance criteria
Steps:
- [ ] Run the repository skill validator against all five new skills.
- [ ] Parse the plugin manifest and verify the declared skill count against the filesystem inventory.
- [ ] Check every relative Markdown link introduced by this feature.
- [ ] Search the new artifacts for placeholders, floating tags and unconditional mutation instructions.
- [ ] Review the final diff against every acceptance criterion in the approved spec.
- [ ] Record the verification result without changing the implementation.
