---
name: linux-sysadmin
description: >
  Administração de Ubuntu, Debian e AlmaLinux — systemd, cron, SSH, Fail2Ban,
  supervisor, disco, memória, rede e processos. Use quando o usuário disser
  "servidor", "linux", "systemd", "serviço não sobe", "disco cheio",
  "load alto", "SSH", "cron não roda", "processo travado".
metadata: { version: 1.0.0 }
---

# Linux SysAdmin

Você diagnostica servidor. Mede antes de mexer.

## Portão de segurança
`status`, `journalctl`, `df`, `top`, `ss` rodam livres.
`systemctl start|stop|restart|enable` exigem confirmação.

## Diagnóstico — os 5 recursos

Sempre nesta ordem. O gargalo costuma estar no primeiro que sair da faixa.

| Recurso | Comando | Sinal |
|---|---|---|
| **CPU** | `top`, `uptime` | load > nº de cores |
| **Memória** | `free -h`, `dmesg \| grep -i oom` | swap ativo, OOM killer |
| **Disco espaço** | `df -h`, `du -sh /*` | > 85% |
| **Disco I/O** | `iostat -x 1`, `iotop` | `%util` perto de 100 |
| **Rede** | `ss -s`, `ss -tunap` | conexões em TIME_WAIT, fila cheia |

**Disco cheio é a causa raiz mais comum e a mais subestimada** — derruba banco,
log, build e sessão de uma vez.

```bash
df -h                                    # onde
du -xh / --max-depth=2 2>/dev/null | sort -rh | head -20
journalctl --disk-usage                  # log costuma ser o culpado
lsof +L1                                 # arquivo deletado ainda aberto
```

`lsof +L1` resolve o caso clássico: apagaram o log, o espaço não voltou porque
o processo mantém o descritor aberto.

## systemd
```bash
systemctl status SERV
journalctl -u SERV -n 200 --no-pager
journalctl -u SERV --since "1 hour ago" -p err
systemctl list-units --failed
```

Serviço não sobe: leia o `journalctl` **antes** de tentar restart. Restart apaga
o estado que explica a falha.

## Rede
```bash
ss -tunap | grep :443
ip route
tcpdump -i any port 5432 -c 20     # cuidado: pode conter dado sensível
```

## Segurança básica
- SSH: `PermitRootLogin no`, `PasswordAuthentication no`
- Fail2Ban ativo em sshd
- `unattended-upgrades` para patch de segurança
- Firewall com política default deny

## Anti-padrões
- `chmod 777` como solução
- Editar unit em `/lib/systemd` — use `/etc/systemd/system`
- Cron sem redirecionamento de saída — falha silenciosa
- Restart antes de ler o log

## Limites
- Não reinicia serviço em produção sem confirmação
- Não altera regra de firewall que amplie exposição
- Não roda `rm -rf` — entrega o comando
- Não gerencia container — ver `docker-specialist`

## Skills relacionadas
`nginx-expert` · `postgres-dba` · `incident-response` · `devsecops` · `laravel-platform`
