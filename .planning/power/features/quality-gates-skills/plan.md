# Quality Gates Skills — Plan
Status: APPROVED
Spec: .planning/power/features/quality-gates-skills/spec.md
Updated: 2026-09-11

For agentic workers: execute this with pwdev-power:power-execute.

## Goal

Publish five complementary skills in `pwdev-devops` and a reusable action plan for adopting
deterministic quality gates.

## Architecture

`quality-gates` owns stack-agnostic decision criteria and routes PHP/Laravel, Vue.js, Node.js and
PostgreSQL requests to their respective specialized skills. Each specialized skill owns its
concrete tool matrix and default thresholds. All five consume the same phased action plan
reference. SonarQube is an optional aggregation layer with controlled server, scanner, Quality
Profile and Quality Gate configuration.

## Tech Stack

- Markdown skill instructions with YAML frontmatter.
- JSON plugin metadata.
- Existing repository shell-based validation commands.

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

## File Structure

- `plugins/pwdev-devops/skills/quality-gates/SKILL.md`
- `plugins/pwdev-devops/skills/quality-gates-php/SKILL.md`
- `plugins/pwdev-devops/skills/quality-gates-vue/SKILL.md`
- `plugins/pwdev-devops/skills/quality-gates-node/SKILL.md`
- `plugins/pwdev-devops/skills/quality-gates-postgres/SKILL.md`
- `plugins/pwdev-devops/references/quality-gates-action-plan.md`
- `plugins/pwdev-devops/README.md`
- `plugins/pwdev-devops/README.pt-BR.md`
- `plugins/pwdev-devops/.claude-plugin/plugin.json`

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

## Task 03 — Vue.js specialization
Complexity: medium
Files: `plugins/pwdev-devops/skills/quality-gates-vue/SKILL.md`
Interfaces:
  Consumes: phased adoption workflow from `plugins/pwdev-devops/references/quality-gates-action-plan.md`
  Produces: Vue.js and TypeScript tool matrix, blocking policy and ratchet thresholds
Steps:
- [ ] Define validation assertions for Vue.js triggers, required gate categories and the shared reference link.
- [ ] Run the focused validation and observe failure because the Vue.js skill does not exist.
- [ ] Write the Vue.js skill with ESLint, vue-tsc, Vitest, coverage, complexity, bundle and accessibility gates.
- [ ] Run focused validation and inspect every blocking rule for deterministic inputs and outputs.
- [ ] Confirm external mutations and dependency installation remain behind explicit authorization.
- [ ] Commit the task file.

## Task 04 — Node.js specialization
Complexity: medium
Files: `plugins/pwdev-devops/skills/quality-gates-node/SKILL.md`
Interfaces:
  Consumes: phased adoption workflow from `plugins/pwdev-devops/references/quality-gates-action-plan.md`
  Produces: Node.js and TypeScript tool matrix, blocking policy and ratchet thresholds
Steps:
- [ ] Define validation assertions for Node.js triggers, required gate categories and the shared reference link.
- [ ] Run the focused validation and observe failure because the Node.js skill does not exist.
- [ ] Write the Node.js skill with ESLint, TypeScript, tests, coverage, complexity, SAST, SCA, build and optional SonarQube aggregation.
- [ ] Run focused validation and inspect every blocking rule for deterministic inputs and outputs.
- [ ] Confirm external mutations and dependency installation remain behind explicit authorization.
- [ ] Commit the task file.

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
