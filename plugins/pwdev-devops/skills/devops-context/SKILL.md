---
name: devops-context
description: >
  Cria e mantém o inventário da plataforma — contas AWS, clusters, ambientes,
  bancos, hosts e o mapeamento que distingue produção de staging. Use quando o
  usuário disser "configurar devops", "mapear a infra", "qual o ambiente",
  "cadastrar cluster", ou quando qualquer skill não encontrar
  .claude/pwdev-devops-context.md. Fundação: sem este arquivo, o plugin não
  sabe o que é produção — e trata tudo como produção.
metadata: { version: 1.0.0 }
---

# Contexto da Plataforma

Você levanta o inventário uma vez para que nenhuma skill precise adivinhar depois.

## Princípio central

> A pergunta mais perigosa em DevOps é **"isso é produção?"**. Este arquivo
> existe para que ela nunca precise ser respondida por palpite.

## Passo 1 — Estado
Existe: leia, resuma, pergunte o que atualizar. Não existe: copie o template.

## Passo 2 — Mapeamento de ambiente (resolva primeiro)

O bloco mais importante. Sem ele, toda operação é tratada como produção.

```
| Ambiente | Conta AWS | Contexto kubectl | Host | Banco |
| prod     | 1234...   | arn:...prod      | ...  | ...   |
| staging  | 5678...   | arn:...stg       | ...  | ...   |
```

Colete de fato, não de memória:
- `aws sts get-caller-identity` por perfil
- `kubectl config get-contexts`

**Nome contendo "prod" não é evidência suficiente.** Exija o identificador real.

## Passo 3 — Inventário
Contas e perfis · clusters e nodegroups · bancos com versão e tamanho ·
hosts e função · domínios e certificados · repositórios e pipelines ·
janela de manutenção · quem é dono do quê.

## Passo 4 — Operação
- Quem aprova mudança em produção
- Canal de incidente
- Onde vivem os runbooks
- SLO por serviço, se existir
- Retenção e local dos backups

## Passo 5 — Ferramentas
Rode `${CLAUDE_PLUGIN_ROOT}/scripts/check-tools.sh` e registre.
Ferramenta ausente = skill em modo consultivo.

**Nunca grave credencial, token ou senha neste arquivo.** Registre o local do
segredo (Secrets Manager, Vault, SSM), nunca o valor.

## Limites
- Não executa mudança na infra
- Não armazena segredo, em nenhuma hipótese
- Não infere ambiente por nome de recurso
- Não substitui o inventário oficial — complementa

## Skills relacionadas
`platform-docs` · todas as demais consomem este arquivo
