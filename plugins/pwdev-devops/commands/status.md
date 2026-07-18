---
description: Estado do plugin — contexto, ambientes mapeados, ferramentas e MCPs
---

# /pwdev-devops:status

## STEP 0 — Idioma
`${CLAUDE_PLUGIN_ROOT}/references/language.md`

## Verificações
1. `.claude/pwdev-devops-context.md` — seções com `{{PLACEHOLDER}}`
2. Ambientes mapeados — **produção está identificada sem ambiguidade?**
3. `${CLAUDE_PLUGIN_ROOT}/scripts/check-tools.sh`
4. MCPs: GitHub, Terraform, Notion, Laravel Boost
5. Credencial ativa: `aws sts get-caller-identity`, `kubectl config current-context`

## Saída
```
pwdev-devops — {{organização}}

Contexto        {{n}}/5 seções
Ambientes       prod: {{identificado | NÃO MAPEADO ⚠}}
                staging: {{}}

Ferramentas     aws ✓  kubectl ✓  docker ✓  gh ✓
                helm ✗  psql ✗  terraform ✗  → modo consultivo

Sessão atual    conta {{}} · contexto {{}}
                ambiente: {{prod | staging | INDETERMINADO ⚠}}

Modo: completo | consultivo
```

Ambiente indeterminado é **alerta**, não detalhe: o plugin passa a tratar tudo
como produção.
