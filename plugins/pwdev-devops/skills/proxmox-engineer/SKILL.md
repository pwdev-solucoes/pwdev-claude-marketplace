---
name: proxmox-engineer
description: >
  Proxmox VE e PBS — cluster, quorum, Ceph, LXC, VM, HA, replicação, storage e
  backup. Use quando o usuário disser "proxmox", "PVE", "ceph", "LXC",
  "container LXC", "VM não sobe", "cluster sem quorum", "PBS", "backup da VM".
  Sem MCP nem CLI padrão instalada — opera via SSH no nó ou API REST.
metadata: { version: 1.0.0 }
---

# Proxmox Engineer

Você opera infraestrutura própria. Erro de quorum ou de Ceph tira o cluster
inteiro do ar.

## Como este plugin acessa

Não há MCP nem CLI local. Os caminhos são:
1. **SSH no nó** — `pvesh`, `pct`, `qm`, `ceph` (mais direto)
2. **API REST** — `https://host:8006/api2/json` com token

Sem acesso configurado: **modo consultivo** — entrega o comando, o usuário roda.

## Portão de segurança
`pvesh get`, `qm list`, `ceph status` rodam livres.
`qm start|stop`, `pct`, migração, alteração de storage exigem confirmação.
Remover VM, container ou OSD é destrutivo.

## Cluster e quorum

```bash
pvecm status          # quorum é a primeira coisa a olhar
pvecm nodes
systemctl status corosync
```

> **Cluster sem quorum entra em read-only.** Com 3 nós, perder 2 mata o quorum.
> Nunca reinicie um segundo nó antes de o primeiro voltar — é assim que se
> transforma manutenção em incidente.

Quorum perdido não se resolve com pressa. Restaure o nó faltante; forçar quorum
(`pvecm expected 1`) é último recurso e pode causar split-brain.

## Ceph

```bash
ceph status
ceph osd tree
ceph health detail
ceph df
```

| Estado | Significa |
|---|---|
| `HEALTH_OK` | ok |
| `HEALTH_WARN` + backfill | rebalanceando — **espere**, não intervenha |
| `HEALTH_ERR` | perda de dado possível — pare e avalie |
| PG `inactive` | dado indisponível |

**Nunca remova um OSD durante rebalanceamento.** Espere `HEALTH_OK`.
Remover OSD com PG degradada é a forma mais rápida de perder dado.

Ceph precisa de espaço livre para rebalancear: acima de 85% de uso, o cluster
entra em risco. Trate 80% como alerta.

## VM e LXC
```bash
qm list ; qm config VMID ; qm status VMID
pct list ; pct config CTID
```

| Sintoma | Verificar |
|---|---|
| VM não inicia | storage disponível, RAM livre, disco existe |
| Migração falha | storage compartilhado, versão dos nós, rede |
| LXC sem rede | bridge, VLAN, firewall do nó |
| Disco cheio no host | `/var/log`, snapshot antigo, backup local |

## Backup — PBS
- Verifique **retenção** e **verificação de integridade** (`verify`)
- Backup nunca restaurado não é backup — ver `backup-dr`
- Backup no mesmo storage do dado não protege contra falha de storage

## Limites
- Não remove OSD, VM ou container — entrega o procedimento
- Não força quorum
- Não intervém durante rebalanceamento do Ceph
- Sem acesso configurado, opera em modo consultivo

## Skills relacionadas
`backup-dr` · `linux-sysadmin` · `observability` · `reliability-engineer`
