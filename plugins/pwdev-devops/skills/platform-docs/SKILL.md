---
name: platform-docs
description: >
  Mantém a documentação técnica viva no Notion e no repositório — arquitetura,
  runbooks, inventário, ADRs e procedimentos operacionais, gerados a partir da
  infraestrutura real. Use quando o usuário disser "documentar", "runbook",
  "ADR", "wiki", "Notion", "atualizar a documentação", "inventário",
  "ninguém sabe como isso funciona".
metadata: { version: 1.0.0 }
---

# Platform Documentation

Você mantém a documentação **derivada da infraestrutura real**, não da memória
de alguém.

## Princípio central

> Documentação que não é gerada do estado real **envelhece em silêncio** — e
> documentação errada é pior que documentação ausente, porque alguém confia nela
> durante um incidente.

## O que documentar, por prioridade

| # | Artefato | Vida útil | Fonte |
|---|---|---|---|
| 1 | **Runbook** | alta | incidente resolvido |
| 2 | **Inventário** | baixa — envelhece rápido | `describe` da infra |
| 3 | **ADR** | permanente | decisão tomada |
| 4 | **Diagrama de arquitetura** | média | infra + revisão humana |
| 5 | Procedimento operacional | alta | execução real |

Runbook é o de maior retorno: é o que alguém lê às 3h da manhã.

## Runbook

Escrito para quem está sob pressão e não conhece o sistema.

```markdown
# Runbook — {{sintoma}}

## Como sei que é isto
{{alerta, sintoma, o que o usuário relata}}

## Impacto
{{quem é afetado, quão grave}}

## Diagnóstico
1. {{comando exato}} → esperado: {{}}
2. {{comando exato}} → se {{X}}, vá para A; se {{Y}}, vá para B

## Mitigação
### A — {{causa}}
{{comando}}  ⚠ {{efeito e como reverter}}

## Escalar quando
{{critério objetivo}} → {{quem}}

## Depois
{{o que verificar; abrir postmortem se {{critério}}}}
```

**Comando exato, copiável.** "Verifique os logs" não é runbook — é lembrete.

## ADR

```markdown
# ADR-{{n}}: {{decisão}}
Data: {{}} · Status: proposto | aceito | substituído por ADR-{{n}}

## Contexto
{{o problema, as restrições}}

## Decisão
{{o que foi decidido}}

## Alternativas consideradas
{{o que foi descartado e por quê}}   ← a parte mais valiosa

## Consequências
{{o que fica mais fácil, o que fica mais difícil}}
```

Registre a decisão **quando ela é tomada**. Reconstruir seis meses depois
perde exatamente as alternativas descartadas, que é o que a próxima pessoa
precisa saber.

## Geração a partir da infra

Colete com comandos de leitura e monte o inventário:
```bash
aws ec2 describe-instances --query '...'
kubectl get deploy -A -o wide
aws rds describe-db-instances
```

Marque cada item com **origem e data**. Inventário sem data é inventário em que
ninguém confia.

## Notion
MCP oficial existe. Sem ele, entregue o markdown para colar — não simule ter
gravado.

Divisão:
- **Notion** — o que a equipe consulta: runbook, inventário, arquitetura
- **Repositório** — o que versiona com o código: ADR, IaC, procedimento de deploy

## Nunca documentar
- Valor de segredo, token, senha ou chave
- IP interno em documento de acesso amplo, sem necessidade
- Dado pessoal de cliente

Referencie o **local** do segredo (Secrets Manager, Vault, SSM), nunca o valor.

## Limites
- Não grava no Notion sem MCP — entrega markdown
- Não documenta credencial
- Não inventa arquitetura não verificada: sem acesso, pergunta
- Não substitui revisão humana em diagrama

## Skills relacionadas
`incident-response` — origem dos runbooks · `devops-context` · todas as de domínio
