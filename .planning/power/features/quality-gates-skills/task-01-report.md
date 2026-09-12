# Task 01 report — shared action plan and generic skill

Status: IMPLEMENTED

## Implementação

- Criada a skill genérica `quality-gates` com coleta obrigatória de stack, risco,
  baseline, orçamento de pipeline e política de bloqueio.
- A skill encaminha ferramentas e limiares concretos para `quality-gates-php`,
  `quality-gates-vue`, `quality-gates-node` e `quality-gates-postgres`.
- Criado o plano de ação em português com quatro fases, entradas, saídas,
  responsáveis, critérios de promoção, exceções e métricas de eficácia.
- A política bloqueia regressões novas, usa ratchet para dívida existente e proíbe
  ampliação automática da baseline pelo CI.
- SonarQube permanece opcional e só pode bloquear com servidor, scanner, Quality
  Profile, Quality Gate e parâmetros controlados.
- Instalação de dependências, alteração de pipeline e mutação externa exigem
  autorização explícita.

## TDD e evidência

- RED: as asserções focadas falharam porque
  `plugins/pwdev-devops/skills/quality-gates/SKILL.md` não existia.
- GREEN: asserções de frontmatter, roteamento, link compartilhado e seções do
  plano passaram.
- O link relativo `../../references/quality-gates-action-plan.md` foi resolvido para
  um arquivo regular existente.
- A busca por PHPStan, Larastan, ESLint, Vitest, `vue-tsc` e percentuais confirmou
  que não há matriz ou limiar específico de stack duplicado.
- `git diff --check` passou antes do commit.
- O validador oficial `quick_validate.py` foi executado, mas o ambiente não possui
  PyYAML funcional: a primeira tentativa retornou `ModuleNotFoundError`; a cópia em
  `/tmp/pwdev-flow-validation-deps` importa `yaml`, mas não expõe `safe_load` nem
  `YAMLError`. A falha foi classificada como ambiental e não como sucesso.

## Escopo e commit

- Commit: `9d2da14 feat(pwdev-devops): add generic quality gates guidance`.
- O commit contém somente os dois arquivos aprovados da Tarefa 01.
- O relatório é o artefato administrativo solicitado e foi escrito após o commit.

STATUS: IMPLEMENTED
REPORT: .planning/power/features/quality-gates-skills/task-01-report.md
COMMITS: 9d2da14
NOTE: Focused assertions and link checks passed; official validator blocked by broken PyYAML environment.
