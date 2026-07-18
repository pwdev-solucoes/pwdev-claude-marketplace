---
description: Auditoria somente-leitura da plataforma — AWS, Kubernetes, segurança, custo e prontidão
argument-hint: "[escopo: aws | k8s | seguranca | custo | tudo]"
---

# /pwdev-devops:auditar

## STEP 0 — Idioma e ambiente
`${CLAUDE_PLUGIN_ROOT}/references/language.md`. Confirme conta e contexto.

## STEP 1 — Escopo
`aws` · `k8s` · `seguranca` · `custo` · `prontidao` · `tudo`

## STEP 2 — Executar
Spawn do `infra-auditor` — **somente leitura, por construção**.

## STEP 3 — Reportar
Achados por severidade, cada um com o comando que comprova, impacto e correção.

Severidade pelo que a brecha permite, não pelo CVSS isolado. **Não infle** —
inflar queima a credibilidade do relatório inteiro.

## STEP 4 — Encerrar
Seção obrigatória **"não verificado"**: o que faltou por permissão ou ferramenta.

Nenhuma correção é aplicada aqui. Auditoria reporta; `/pwdev-devops:diagnosticar`
corrige, com confirmação.
