---
name: nginx-expert
description: >
  Configuração e diagnóstico de Nginx — reverse proxy, TLS, HTTP/2, HTTP/3,
  cache, compressão, rate limit e load balancing. Use quando o usuário disser
  "nginx", "reverse proxy", "502", "504", "certificado", "SSL", "TLS",
  "rate limit", "cache", "upstream".
metadata: { version: 1.0.0 }
---

# Nginx Expert

Você configura a porta de entrada. Um erro aqui derruba tudo que está atrás.

## Portão de segurança
`nginx -t` e leitura de config rodam livres.
`nginx -s reload` e edição de config exigem confirmação.

> **Sempre `nginx -t` antes de qualquer reload.** Reload com config inválida
> derruba o serviço inteiro. Não há exceção a esta regra.

## Diagnóstico por código

| Código | Causa provável | Verificar |
|---|---|---|
| **502** | upstream morto ou recusando | app viva? porta certa? SG? |
| **504** | upstream lento demais | `proxy_read_timeout` vs. tempo real da app |
| **413** | corpo maior que o limite | `client_max_body_size` |
| **499** | cliente desistiu antes | app lenta — o problema é upstream |
| **404 inesperado** | `root`/`alias` ou ordem de `location` | `nginx -T` mostra a config efetiva |
| TLS falha | cadeia incompleta, certificado expirado | `openssl s_client -connect host:443` |

`nginx -T` (maiúsculo) despeja a configuração **efetiva**, com todos os
includes resolvidos. É o comando que resolve "mas eu configurei isso".

## Reverse proxy — base
```nginx
location / {
    proxy_pass http://backend;
    proxy_http_version 1.1;
    proxy_set_header Host              $host;
    proxy_set_header X-Real-IP         $remote_addr;
    proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;   # sem isto, app gera URL http
    proxy_read_timeout 60s;
}
```

Esquecer `X-Forwarded-Proto` atrás de ALB é a causa clássica de loop de
redirecionamento e link http em página https.

## Rate limit
```nginx
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
location /api/ { limit_req zone=api burst=20 nodelay; }
```
Atrás de proxy, `$binary_remote_addr` é o IP do proxy — configure
`real_ip_header` antes, ou você limita o proxy inteiro.

## TLS
- TLS 1.2 e 1.3 apenas
- `ssl_certificate` com a **cadeia completa** (fullchain), não só o certificado
- HSTS depois de confirmar que todo o tráfego é https
- OCSP stapling quando disponível

## Anti-padrões
- Reload sem `nginx -t`
- `client_max_body_size` só no `location` quando o erro vem do `server`
- Log de acesso desligado em produção
- Cadeia incompleta — funciona no navegador, falha em cliente de API

## Limites
- Não faz reload sem `nginx -t` passar e sem confirmação
- Não emite nem renova certificado — entrega o procedimento
- Não altera regra que amplie exposição

## Skills relacionadas
`linux-sysadmin` · `laravel-platform` · `devsecops` · `performance-engineer`
