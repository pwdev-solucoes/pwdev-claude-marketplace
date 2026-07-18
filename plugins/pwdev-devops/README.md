# PWDEV DevOps — Plataforma, Operação e Incidente

Framework de DevOps para Claude Code. **19 skills, 4 subagentes, 7 comandos.**

Postura de execução: **leitura livre, mutação sob confirmação, destrutivo bloqueado.**

---

## Por que este plugin é diferente dos outros

Um plugin de copy que erra escreve texto ruim. Um plugin de DevOps que erra
**derruba produção**. Por isso a camada de segurança vem antes de qualquer
funcionalidade — está em `references/execucao-segura.md` e no
`scripts/guard.sh`.

```bash
$ guard.sh --check "kubectl get pods"
✓ leitura — liberado

$ guard.sh --check "kubectl apply -f x.yaml"
⚠ MUTAÇÃO BLOQUEADA — falta --confirm

$ guard.sh --check "kubectl delete ns prod" --env prod
🛑 DESTRUTIVO BLOQUEADO

$ guard.sh --check "terraform destroy" --confirm
🛑 BLOQUEADO — comando na lista de proibidos
```

O guard é a **segunda barreira**, independente da instrução da skill: instrução
falha, trava não.

---

## Instalação

```
/plugin marketplace add pwdev-solucoes/pwdev-claude-marketplace
/plugin install pwdev-devops
/pwdev-devops:init     # mapeia ambientes — faça isto primeiro
```

`init` é obrigatório: sem o mapeamento de ambiente, o plugin trata **tudo** como
produção.

---

## Comandos

| Comando | Função |
|---|---|
| `/pwdev-devops:init` | Mapeia contas, clusters, ambientes |
| `/pwdev-devops:diagnosticar` | Roteia o sintoma para o domínio certo |
| `/pwdev-devops:incidente` | Conduz incidente em andamento |
| `/pwdev-devops:auditar` | Auditoria somente-leitura |
| `/pwdev-devops:custo` | FinOps — desperdício e otimização |
| `/pwdev-devops:documentar` | Runbook, inventário, ADR, arquitetura |
| `/pwdev-devops:status` | Contexto, ferramentas, ambiente atual |

## Subagentes

| Agente | Modelo | Papel |
|---|---|---|
| `incident-commander` | opus | Conduz incidente — propõe, nunca executa |
| `infra-auditor` | sonnet | Auditoria somente-leitura por construção |
| `db-analyst` | sonnet | PostgreSQL — plano, índice, lock, bloat |
| `platform-documenter` | sonnet | Documentação a partir da infra real |

## Skills

**Fundação:** `devops-context`

**Cloud e plataforma:** `aws-architect`, `finops`, `kubernetes-platform`, `docker-specialist`

**Sistema:** `linux-sysadmin`, `nginx-expert`, `proxmox-engineer`

**Dados:** `postgres-dba`, `backup-dr`

**Operação:** `observability`, `incident-response`, `reliability-engineer`, `performance-engineer`

**Segurança e automação:** `devsecops`, `automation-engineer`

**Aplicação e IA:** `laravel-platform`, `ai-infra`

**Documentação:** `platform-docs`

---

## Ferramentas — status real

Verificado no ambiente em 18/07/2026:

**Disponíveis:** `aws`, `kubectl`, `docker`, `gh`
**Ausentes:** `helm`, `psql`, `terraform`, `ansible`, `trivy`, `k6`, `nginx`

Ferramenta ausente = **modo consultivo**: a skill diagnostica e entrega o
comando exato, o usuário executa. É operação legítima, não falha.

### Sobre MCP

Em DevOps a maior parte da integração é **CLI via Bash, não MCP**. `kubectl`,
`docker`, `psql`, `terraform` já são interfaces excelentes e auditáveis.

MCPs que existem de fato e valem: **GitHub**, **Terraform**, **Notion**,
**Laravel Boost** (os quatro já instalados no seu marketplace), **AWS** e
**Grafana**.

Sem MCP conhecido: **Proxmox**, **Zabbix**, **n8n** — via API REST ou SSH.

Detalhes em `references/ferramentas.md`.

---

## Regras que o plugin não negocia

1. **Confirmação é por comando, não por sessão.**
2. **Ambiente indeterminado = produção.** Nunca inferir por nome de recurso.
3. **Nunca imprimir valor de segredo.**
4. **Preservar evidência antes de mitigar** durante incidente.
5. **Não pular do sintoma para o comando** — hipótese primeiro.
6. **Não ampliar exposição de segurança**, nem com confirmação.
7. **Declarar o que não foi verificado** ao fim de todo diagnóstico.
8. **Ferramenta ausente = modo consultivo**, nunca simulação.

Proibidos mesmo com confirmação: `terraform destroy`, `DROP DATABASE`,
`TRUNCATE`, rotação de credencial em produção, desabilitar backup ou auditoria.

Codificadas em `references/execucao-segura.md` e `references/anatomia-skill.md`.

---

## Família PWDEV

| Plugin | Domínio |
|---|---|
| `pwdev-devops` | plataforma e operação |
| `pwdev-copy` | texto e marketing |
| `pwdev-social-media` | criativos |

Idioma compartilhado via `.planning/config.json`. Licença Apache-2.0.
