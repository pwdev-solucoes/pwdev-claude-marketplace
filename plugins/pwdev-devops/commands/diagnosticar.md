---
description: Diagnostica um problema roteando para o domínio certo — somente leitura até propor
argument-hint: "[sintoma]"
---

# /pwdev-devops:diagnosticar

## STEP 0 — Idioma
`${CLAUDE_PLUGIN_ROOT}/references/language.md`

## STEP 1 — Ambiente
Leia a seção 2 do contexto. Confirme conta e contexto:
```bash
aws sts get-caller-identity ; kubectl config current-context
```
Não determinado com confiança alta: **trate como produção** e avise.

## STEP 2 — Rotear pelo sintoma

| Sintoma | Skill |
|---|---|
| pod, deployment, ingress, CrashLoop | `kubernetes-platform` |
| 502, 504, TLS, proxy | `nginx-expert` |
| query lenta, lock, conexões | `postgres-dba` |
| disco, memória, systemd, SSH | `linux-sysadmin` |
| VPC, SG, ALB, RDS, IAM | `aws-architect` |
| imagem, build, container | `docker-specialist` |
| fila, horizon, job, artisan | `laravel-platform` |
| quorum, ceph, LXC, VM | `proxmox-engineer` |
| GPU, LLM, MCP, token | `ai-infra` |
| custo, fatura | `finops` |
| lento sob carga | `performance-engineer` |
| fora do ar agora | **`/pwdev-devops:incidente`** |

Sintoma cruzando domínios: comece pela borda e caminhe para dentro.

## STEP 3 — Investigar (somente leitura)
Siga a tabela sintoma → ordem de verificação da skill. **Não execute mutação
nesta fase.**

## STEP 4 — Propor
```
Causa provável: {{}} — confirmado | provável | hipótese
Evidência: {{comando e saída}}
Correção: {{comando exato}}
Efeito: {{}} · Reversível: {{}} · Blast radius: {{}}
```

## STEP 5 — Executar
Só após "sim" explícito **para este comando**.
Valide antes: `${CLAUDE_PLUGIN_ROOT}/scripts/guard.sh --check "<cmd>"`.

## STEP 6 — Verificar
O sintoma sumiu? O que mais mudou? Encerre com **"o que não foi verificado"**.
