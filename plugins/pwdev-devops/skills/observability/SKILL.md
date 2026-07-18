---
name: observability
description: >
  Métricas, logs, traces, dashboards, alertas e SLO — Prometheus, Grafana,
  Loki, Tempo, Mimir, Zabbix, Alertmanager. Use quando o usuário disser
  "dashboard", "alerta", "métrica", "PromQL", "Grafana", "SLO", "golden
  signals", "não temos visibilidade", "monitoramento".
metadata: { version: 1.0.0 }
---

# Observability

Você projeta o que é medido. Alerta ruim treina o time a ignorar alerta.

## Princípio central

> **Todo alerta precisa ter uma ação.** Alerta que não gera ação vira ruído, e
> ruído faz o time perder o alerta que importava.

## Os três métodos

| Método | Para | Sinais |
|---|---|---|
| **Golden Signals** | serviço voltado ao usuário | latência, tráfego, erro, saturação |
| **RED** | request-driven (API, web) | Rate, Errors, Duration |
| **USE** | recurso (CPU, disco, rede) | Utilization, Saturation, Errors |

Comece por RED na borda e USE na infra. Golden Signals é a união dos dois.

## PromQL — o essencial
```promql
# taxa de erro 5xx
sum(rate(http_requests_total{status=~"5.."}[5m]))
  / sum(rate(http_requests_total[5m]))

# p95 de latência
histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))

# saturação de memória do pod vs. limite
container_memory_working_set_bytes / container_spec_memory_limit_bytes
```

`rate()` sempre com janela ≥ 4× o intervalo de scrape. Janela curta demais
produz gráfico com buraco.

## Alerta que presta

```yaml
- alert: TaxaDeErroAlta
  expr: |
    sum(rate(http_requests_total{status=~"5.."}[5m]))
      / sum(rate(http_requests_total[5m])) > 0.05
  for: 10m                    # evita alarme por pico momentâneo
  labels: { severity: critical }
  annotations:
    summary: "Taxa de erro em {{ $labels.service }} acima de 5%"
    runbook: "https://.../runbook-erro-5xx"
```

Todo alerta precisa de: `for` (evita flapping), severidade, e **link do runbook**.
Alerta sem runbook é alerta que acorda alguém sem dizer o que fazer.

## SLO

```
SLI:          o que se mede (ex.: % de requests < 300ms)
SLO:          a meta          (ex.: 99,5% em 30 dias)
Error budget: 100% − SLO      (ex.: 0,5% ≈ 3h36 por mês)
```

Error budget é a ferramenta de decisão: enquanto sobra orçamento, a equipe pode
lançar; quando acaba, congela e estabiliza. **SLO sem consequência é enfeite.**

Não proponha SLO de 99,99% sem discutir custo. Cada nove multiplica o
investimento.

## Diagnóstico de lacuna
Ao auditar observabilidade, procure:
- serviço sem métrica de erro
- alerta sem runbook
- dashboard que ninguém abre
- log sem retenção ou sem estrutura
- alerta que dispara toda semana e é sempre ignorado
- ausência de trace no caminho crítico

## Anti-padrões
- Alerta em CPU alta sem impacto no usuário
- Alerta por host em vez de por serviço
- Dashboard com 40 painéis e nenhuma pergunta respondida
- Retenção infinita de log — custo sem retorno
- Alerta sem `for` — dispara em pico de 30 segundos

## Limites
- Não altera regra de alerta em produção sem confirmação
- Não silencia alerta sem registrar motivo e prazo
- Não investiga incidente — ver `incident-response`
- Não define SLO sozinho: é decisão de negócio

## Skills relacionadas
`incident-response` · `reliability-engineer` · `kubernetes-platform` · `platform-docs`
