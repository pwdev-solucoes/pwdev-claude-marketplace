# Roteamento de agentes

O agente de cada issue vem da config (`routing`), avaliada nesta ordem:

1. **Override na issue:** label `agent:claude`, `agent:codex` ou `agent:opencode`.
2. **Regras por label:** a primeira regra de `routing.rules` cujo `labels` tenha interseção com
   as labels da issue.
3. **Padrão:** `routing.default`.

Padrão embutido (`templates/hermes-orca.config.json`):

| Labels | Agente | Por quê |
|---|---|---|
| `bug`, `backend`, `api`, `refactor`, `chore`, `test` | `codex` | implementação focada e verificável |
| `frontend`, `ui`, `ux`, `design`, `docs` | `claude` | julgamento de UI e texto |
| (nenhuma regra casou) | `claude` | padrão |

`opencode` só entra por override ou regra explícita. Ele usa o modelo da própria configuração
(o Orca não aceita `--model` para ele).

## Modelo e esforço

`routing.models.<agente>` (opcional) vira `--model` e `routing.effort.<agente>` vira `--effort`
no `worker-start`. `--effort` exige `--model`. Omita os dois quando não configurados.

## Disponibilidade

Antes do gate, o preflight com `--agents <lista roteada>` precisa confirmar que cada agente
roteado tem `pwdev-feat ≥ 3.2.0`, a versão que traz o `feat-loop`. Agente sem o plugin ou com
versão antiga: proponha outro agente no gate ou peça ao usuário para instalar ou atualizar.
Nunca troque de agente em silêncio.
