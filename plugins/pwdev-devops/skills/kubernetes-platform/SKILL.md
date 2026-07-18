---
name: kubernetes-platform
description: >
  Diagnóstico e operação de Kubernetes — pods, deployments, ingress, HPA,
  PVC, StorageClass, NetworkPolicy, Secrets, Helm, ArgoCD, cert-manager.
  Use quando o usuário disser "kubernetes", "k8s", "pod", "deployment",
  "ingress", "CrashLoopBackOff", "não sobe", "escalar", "helm", "argocd".
  Leitura livre; apply, scale, delete passam pelo portão.
metadata: { version: 1.0.0 }
---

# Kubernetes Platform

Você diagnostica cluster. Lê muito antes de mudar qualquer coisa.

## Portão de segurança
`${CLAUDE_PLUGIN_ROOT}/references/execucao-segura.md`.

**Confirme o contexto antes de tudo:**
```bash
kubectl config current-context
```
Compare com a seção 2 do contexto. Não bateu ou não está mapeado: **trate como
produção** e pergunte.

## Diagnóstico por sintoma

| Sintoma | Ordem de verificação |
|---|---|
| `CrashLoopBackOff` | `logs --previous` → `describe` (exit code) → probe → recurso |
| `ImagePullBackOff` | nome da imagem → tag existe → imagePullSecret → registry |
| `Pending` | `describe` (events) → recurso do node → taint/toleration → PVC |
| `OOMKilled` | limit de memória → uso real → vazamento na app |
| Ingress 502 | endpoints do service → selector bate com label? → porta → app viva |
| PVC `Pending` | StorageClass existe → provisioner → zona do node |
| HPA não escala | metrics-server → requests definidos → limite máximo |

`describe` mostra **events** — é onde a resposta costuma estar, e é o que mais
se esquece de olhar.

## Leitura
```bash
kubectl get pods -n ns -o wide
kubectl describe pod POD -n ns
kubectl logs POD -n ns --previous --tail=200
kubectl get events -n ns --sort-by=.lastTimestamp
kubectl top pods -n ns
kubectl get endpoints SVC -n ns      # selector errado aparece aqui
```

## Mutação — sempre com portão
```bash
kubectl scale deploy/X --replicas=N     # confirmar
kubectl rollout restart deploy/X        # confirmar
kubectl apply -f arquivo.yaml           # confirmar; mostrar o diff antes
kubectl delete ...                      # destrutivo; reforçado
```

Antes de `apply`, mostre `kubectl diff -f` — aplicar sem ver o diff é como
mudança não intencional entra em produção.

## Segredos
`kubectl get secret -o yaml` **expõe base64**. Use `describe`, ou decodifique
apenas o campo pedido — e não ecoe o valor.

## Anti-padrões
- Deployment sem `resources.requests` — quebra HPA e scheduling
- Sem readiness probe — recebe tráfego antes de estar pronto
- `latest` como tag — rollback impossível
- `replicas: 1` em produção
- Secret em ConfigMap
- NetworkPolicy ausente em cluster multi-tenant

## Limites
- Não aplica sem confirmação e sem mostrar o diff
- Não deleta namespace, PVC ou StatefulSet em produção
- Não gerencia a infra do cluster — ver `aws-architect`
- Não expõe valor de secret

## Skills relacionadas
`docker-specialist` · `observability` · `incident-response` · `aws-architect` · `devsecops`
