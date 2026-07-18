---
description: Conduz incidente em andamento — preserva evidência, investiga e propõe mitigação
argument-hint: "[o que está acontecendo]"
---

# /pwdev-devops:incidente

## STEP 0 — Idioma e ambiente
`${CLAUDE_PLUGIN_ROOT}/references/language.md`. Confirme conta e contexto.

## STEP 1 — Triagem (5 min)
1. **O que mudou?** deploy, config, certificado, cota, DNS — a causa está aqui
   na maioria dos casos
2. Quando começou?
3. Quem é afetado?
4. Está piorando?
5. Existe mitigação rápida — rollback, flag, escala?

## STEP 2 — Preservar evidência ANTES de mitigar
```bash
kubectl logs POD --previous > /tmp/inc-$(date +%s).log
kubectl describe pod POD > /tmp/inc-describe.txt
kubectl get events -n NS --sort-by=.lastTimestamp > /tmp/inc-events.txt
```
Restart sem salvar log destrói a única cópia da causa.

## STEP 3 — Investigar
Spawn do `incident-commander`. Trilha: borda → app → dependência → infra.

## STEP 4 — Mitigar
Restaurar vem antes de entender. Rollback é mitigação legítima.
Mesmo em incidente, **mutação exige confirmação** — apresente comando, efeito e
reversão.

## STEP 5 — Verificar e registrar
Sintoma sumiu? Linha do tempo registrada?

## STEP 6 — Postmortem
`platform-docs` gera o esboço. Sem culpado — "erro humano" não é causa raiz;
a pergunta é por que o sistema permitiu.
