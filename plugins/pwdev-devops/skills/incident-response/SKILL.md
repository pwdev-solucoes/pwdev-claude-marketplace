---
name: incident-response
description: >
  Conduz investigação de incidente — triagem, hipótese, mitigação, RCA e
  postmortem. Use quando o usuário disser "está fora do ar", "incidente",
  "caiu", "usuários reclamando", "erro em produção", "postmortem", "RCA",
  "o que aconteceu". Durante incidente, a pressa causa o segundo incidente.
metadata: { version: 1.0.0 }
---

# Incident Response

Você conduz a investigação. Sob pressão, o método é o que impede o erro.

## Princípio central

> **Nunca pule do sintoma para o comando.** "Reinicia o pod" sem hipótese
> resolve por acidente e apaga a evidência da causa.

## Ordem — não negociável

```
1. OBSERVAR    métricas, logs, eventos — só leitura
2. HIPÓTESE    o que explica TODOS os sintomas?
3. VALIDAR     leitura que confirma ou derruba
4. PROPOR      comando exato + efeito + reversão
5. CONFIRMAR   humano aprova
6. EXECUTAR    um comando por vez
7. VERIFICAR   sintoma sumiu? o que mais mudou?
```

## Triagem — primeiros 5 minutos

| Pergunta | Por quê |
|---|---|
| **O que mudou?** | deploy, config, certificado, cota, DNS — a causa está aqui em 80% dos casos |
| Quando começou? | correlaciona com o evento |
| Quem é afetado? | todos, ou um segmento? |
| Está piorando? | define urgência |
| Existe mitigação rápida? | rollback, feature flag, escala |

**"O que mudou?" é a primeira pergunta, sempre.** Sistema que funcionava e
parou raramente parou sozinho.

## Mitigar antes de entender

Restaurar o serviço vem antes de descobrir a causa. Rollback é mitigação
legítima — e a mais rápida.

Mas: **preserve a evidência antes de mitigar.**
```bash
kubectl logs POD --previous > /tmp/incidente-$(date +%s).log
kubectl describe pod POD > /tmp/incidente-describe.txt
kubectl get events -n ns --sort-by=.lastTimestamp > /tmp/incidente-events.txt
```
Restart sem salvar log destrói a única cópia da causa.

## Trilha de investigação

```
borda      ALB/Nginx: taxa de erro, latência, health do target
   ↓
aplicação  logs, exceptions, versão em execução
   ↓
dependência banco, cache, fila, API externa
   ↓
infra      CPU, memória, disco, rede, node
```

Percorra de fora para dentro. Começar pela infra é como se perde 40 minutos
quando a causa era um deploy.

## Postmortem

Sem culpado. O objetivo é o sistema, não a pessoa.

```markdown
# Incidente {{data}} — {{título}}
Duração: {{início}} → {{fim}} ({{n}} min)
Impacto: {{quem, quanto, o quê}}
Severidade: {{n}}

## Linha do tempo
{{hora}} — {{evento}} — {{quem/o quê}}

## Causa raiz
{{o mecanismo, não "erro humano"}}

## Por que não pegamos antes
{{a lacuna de detecção — costuma ser o achado mais valioso}}

## Ações
| Ação | Tipo | Dono | Prazo |
|---|---|---|---|
| ... | prevenir \| detectar \| mitigar | ... | ... |
```

"Erro humano" nunca é causa raiz. A pergunta seguinte é: **por que o sistema
permitiu?**

Toda ação precisa de dono e prazo. Postmortem sem ação é ritual.

## Limites
- Não executa mitigação sem confirmação, mesmo durante incidente
- Não reinicia serviço antes de preservar log
- Não atribui culpa a pessoa
- Não declara causa raiz sem evidência — hipótese é rotulada como hipótese

## Skills relacionadas
`observability` · `reliability-engineer` · `platform-docs` · todas as de domínio
