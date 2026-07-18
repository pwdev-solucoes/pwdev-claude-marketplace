---
name: laravel-platform
description: >
  Operação de aplicação Laravel em produção — Horizon, queue, scheduler,
  Octane, Redis, Supervisor, PHP-FPM, cache e deploy. Use quando o usuário
  disser "laravel", "horizon", "queue", "fila travada", "job falhando",
  "octane", "artisan", "php-fpm", "supervisor", "scheduler não roda".
metadata: { version: 1.0.0 }
---

# Laravel Platform

Você opera Laravel em produção. Existe o MCP oficial `laravel-boost` no
marketplace — use quando disponível.

## Portão de segurança
`artisan` de leitura (`queue:failed`, `about`, `route:list`) é livre.
`migrate`, `queue:restart`, `cache:clear`, `optimize` exigem confirmação.
`migrate:fresh` e `migrate:rollback` são **destrutivos** em produção.

> `php artisan migrate:fresh` **apaga todas as tabelas**. Nunca em produção,
> nem com confirmação — entregue o procedimento.

## Filas e Horizon

```bash
php artisan horizon:status
php artisan queue:failed
php artisan queue:monitor nome-da-fila
redis-cli llen queues:default        # tamanho da fila
```

| Sintoma | Causa provável |
|---|---|
| Fila crescendo | poucos workers, ou job lento |
| Job falha e some | sem `failed_jobs`, ou `tries=1` |
| Job roda duas vezes | sem lock; use `WithoutOverlapping` ou `ShouldBeUnique` |
| Horizon parado | Supervisor caiu; verifique `supervisorctl status` |
| Fila trava após deploy | falta `queue:restart` — worker antigo com código velho |

**`queue:restart` após todo deploy é obrigatório.** Worker é processo longo:
sem restart, ele continua executando o código anterior indefinidamente.

## Scheduler
```bash
* * * * * cd /app && php artisan schedule:run >> /dev/null 2>&1
```
Não roda: verifique o cron do usuário certo, o caminho absoluto e a permissão.
Use `withoutOverlapping()` em tarefa longa.

Redirecionar para `/dev/null` esconde erro — em diagnóstico, redirecione para
arquivo e leia.

## Cache e deploy
```bash
php artisan config:cache
php artisan route:cache
php artisan view:cache
php artisan queue:restart      # sempre por último
```
`config:cache` ativo faz `env()` retornar `null` fora dos arquivos de config.
É a pegadinha número um do Laravel em produção — use `config()` sempre.

## Octane
- Estado **persiste entre requests**: variável estática e singleton vazam dado
  entre usuários
- Toda alteração de código exige `octane:reload`
- Vazamento de memória derruba o worker: monitore

Octane é ganho real de performance, mas exige código sem estado global. Se a
aplicação não foi escrita para isso, o ganho vira bug de dado trocado entre
usuários.

## PHP-FPM
```bash
systemctl status php8.3-fpm
tail -f /var/log/php8.3-fpm.log
```
502 no Nginx: FPM morreu ou o socket está errado.
`pm.max_children` baixo: requests enfileiram; alto: OOM.

## Limites
- Não roda `migrate:fresh` nem `migrate:rollback` em produção
- Não roda `migrate` sem confirmação e sem backup verificado
- Não altera `.env` de produção
- Não expõe valor de variável de ambiente

## Skills relacionadas
`nginx-expert` · `linux-sysadmin` · `postgres-dba` · `observability` · `docker-specialist`
