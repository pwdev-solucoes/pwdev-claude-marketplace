# Task 02 — report

Status: DONE

## Implementação

- Criada `plugins/pwdev-devops/skills/quality-gates-php/SKILL.md` com triggers para PHP,
  Laravel, PHPStan, Larastan, Pest, PHPUnit, PHPMD, Composer Audit, cobertura e baseline.
- Definida matriz separando análise estática, testes, cobertura, SAST, SCA, complexidade,
  estilo e verificações específicas de Laravel.
- Registradas entradas fixadas, saídas observáveis e condições bloqueantes para as oito
  categorias.
- Definida política padrão de zero regressão e ratchet: 80% de cobertura nas linhas
  alteradas, queda global de 0,0 ponto percentual, complexidade ciclomática máxima de 10 e
  redução aprovada de ao menos 10%/1 item na categoria priorizada.
- Composer Audit remoto e SonarQube não controlado permanecem informativos; baseline não pode
  crescer automaticamente no CI.
- Instalação de dependências, alteração de pipeline/configuração/baseline e mutações externas
  exigem autorização explícita.
- Referenciado o plano compartilhado em
  `../../references/quality-gates-action-plan.md` e aplicada sua sequência de fases.

## Evidência

RED:

```text
test -f plugins/pwdev-devops/skills/quality-gates-php/SKILL.md &&
  rg -q '^name: quality-gates-php$' plugins/pwdev-devops/skills/quality-gates-php/SKILL.md
exit 1
```

GREEN:

```text
focused assertions: PASS (14 requirements)
deterministic blocking contracts: PASS (8 gate categories)
authorization boundary: PASS
git diff --check: PASS
placeholder/floating-tag/unconditional-mutation search: no matches
```

## Arquivos

- `plugins/pwdev-devops/skills/quality-gates-php/SKILL.md`
- `.planning/power/features/quality-gates-skills/task-02-report.md`

## Observações

Nenhuma preocupação aberta. Nenhuma dependência foi instalada e nenhuma mutação externa ou
alteração de pipeline foi executada.
