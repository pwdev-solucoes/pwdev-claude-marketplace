# Ferramentas — status verificado

Levantamento em 18/07/2026 no ambiente do usuário.

## Correção importante sobre MCP

Em DevOps, **a maior parte da integração é CLI via Bash, não MCP**. `kubectl`,
`docker`, `psql`, `terraform`, `ansible`, `aws`, `nginx -t` já são interfaces
excelentes e auditáveis. MCP só agrega onde há API sem CLI boa.

Não construa MCP para o que já tem CLI.

## CLIs no ambiente

| CLI | Status | Domínio |
|---|---|---|
| `aws` | ✅ | AWS, FinOps, Backup |
| `kubectl` | ✅ | Kubernetes |
| `docker` | ✅ | Docker |
| `gh` | ✅ | GitHub, CI/CD |
| `helm` | ❌ | Kubernetes |
| `psql` / `pg_dump` | ❌ | PostgreSQL, Backup |
| `terraform` / `tofu` | ❌ | IaC |
| `ansible` | ❌ | Automação |
| `trivy` / `hadolint` / `dive` | ❌ | DevSecOps, Docker |
| `k6` | ❌ | Performance |
| `nginx` | ❌ | Nginx |

**Ausente = skill em modo consultivo**: entrega o comando pronto, o usuário roda.
É operação legítima, não falha.

Verifique com `${CLAUDE_PLUGIN_ROOT}/scripts/check-tools.sh`.

## MCPs que existem de fato

| MCP | Status | Uso |
|---|---|---|
| **GitHub** | ✅ oficial, instalado | PR, issue, Actions, release |
| **Terraform** | ✅ oficial, instalado | módulo, provider, registry |
| **Laravel Boost** | ✅ oficial, instalado | domínio `laravel-platform` |
| **Notion** | ✅ oficial | `platform-docs` |
| **AWS** | ✅ servidores oficiais existem | complementa o CLI |
| **Grafana** | ✅ oficial | dashboard e alerta |
| **PostgreSQL** | ⚠️ referência/comunidade | `psql` costuma bastar |

## Sem MCP — via CLI ou API

| Ferramenta | Caminho |
|---|---|
| Kubernetes | `kubectl` — não precisa de MCP |
| Docker | `docker` — não precisa de MCP |
| Nginx | arquivo de config + `nginx -t` |
| Ansible | `ansible-playbook` |
| **Proxmox** | ❓ sem MCP e sem CLI padrão — SSH no nó ou API REST |
| **Zabbix** | ⚠️ API REST, sem MCP conhecido |
| **n8n** | ⚠️ API REST, sem MCP oficial confirmado |
| Prometheus | HTTP API (`/api/v1/query`) via curl |

## Degradação

Toda skill funciona sem ferramenta nenhuma, em modo consultivo:
diagnostica, explica e entrega o comando exato. Quando degradada, a skill
**declara isso** e marca o que não pôde ser verificado.
