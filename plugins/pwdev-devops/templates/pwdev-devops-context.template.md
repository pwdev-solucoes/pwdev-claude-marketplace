# Contexto da Plataforma — {{ORGANIZACAO}}

> Gerado por `/pwdev-devops:init`. Toda skill lê antes de agir.
> Local: `.claude/pwdev-devops-context.md`
> **Nunca grave credencial aqui.** Registre o local do segredo, nunca o valor.
> Atualizado em: {{DATA}}

---

## 1. Organização
- **Nome:** {{ORGANIZACAO}}
- **Idioma:** {{LANG}}
- **Janela de manutenção:** {{JANELA}}
- **Canal de incidente:** {{CANAL}}

---

## 2. Ambientes — o bloco mais crítico

Sem este mapeamento, **o plugin trata tudo como produção**.

| Ambiente | Conta AWS | Contexto kubectl | Host principal | Banco |
|---|---|---|---|---|
| prod | {{}} | {{}} | {{}} | {{}} |
| staging | {{}} | {{}} | {{}} | {{}} |
| dev | {{}} | {{}} | {{}} | {{}} |

Coletado com `aws sts get-caller-identity` e `kubectl config get-contexts`.
Nome contendo "prod" **não** é evidência suficiente.

- **Quem aprova mudança em produção:** {{QUEM}}

---

## 3. Inventário

### AWS
- **Contas e perfis:** {{}}
- **Região primária:** {{}}
- **Clusters EKS / ECS:** {{}}
- **RDS:** {{instância, versão, Multi-AZ, retenção}}
- **Domínios e certificados:** {{}}

### Kubernetes
- **Clusters e nodegroups:** {{}}
- **Namespaces por serviço:** {{}}
- **Ingress controller / cert-manager:** {{}}

### Hosts e Proxmox
- **Nós do cluster:** {{}}
- **Ceph:** {{}} · **PBS:** {{}}

### Aplicações
- **Repositórios e pipelines:** {{}}
- **Laravel — Horizon, Octane:** {{}}

---

## 4. Operação
- **Runbooks:** {{ONDE}}
- **SLO por serviço:** {{}}
- **Backups — local, retenção, último restore testado:** {{}}
- **Observabilidade — Grafana, Prometheus, Loki, Zabbix:** {{}}
- **Local dos segredos:** {{Secrets Manager | Vault | SSM}} *(local, nunca valor)*

---

## 5. Ferramentas

Preenchido por `scripts/check-tools.sh`.

| Ferramenta | Status |
|---|---|
| aws | {{}} |
| kubectl | {{}} |
| helm | {{}} |
| docker | {{}} |
| psql | {{}} |
| terraform | {{}} |
| ansible | {{}} |

Ausente = skill em modo consultivo.
